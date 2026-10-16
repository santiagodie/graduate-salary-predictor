"""
Export the trained Random Forest to ONNX for the static demo.

The scikit-learn pipeline is split in two:
  - the one-hot encoding of the categorical features is replicated in
    JavaScript (demo/js/model.js), using the categories written to
    demo/model/features.json;
  - only the RandomForestRegressor is exported to ONNX, with a single
    numeric input, so it runs with onnxruntime-web without string tensors.

The trees are exported in double precision (ai.onnx.ml opset 3). Inputs are
rounded to float32 first, as scikit-learn does internally; the output is
float32, so predictions match the original model to within float32 rounding.

The model is written gzip-compressed (about 15 MB -> 1.7 MB) because GitHub
Pages does not compress .onnx files; the demo decompresses it in the browser.

The script then checks that ONNX predictions match the original pipeline.

Requirements (Python 3.11):
    pip install scikit-learn==1.4.2 numpy==1.26.4 pandas==2.2.3 \
                skl2onnx==1.17.0 onnx==1.16.2 onnxruntime==1.19.2 protobuf==4.25.5

Usage (from the repository root):
    python demo/tools/export_onnx.py
"""

import gzip
import json
import pickle
import warnings
from pathlib import Path

import numpy as np
import onnxruntime as ort
import pandas as pd
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import DoubleTensorType, FloatTensorType

warnings.filterwarnings('ignore', category=UserWarning)

ROOT = Path(__file__).resolve().parents[2]
PKL = ROOT / 'prediccion-salarial' / 'data' / 'modelo_entrenado.pkl'
OUT_DIR = ROOT / 'demo' / 'model'
ONNX_FILE = OUT_DIR / 'salary_rf.onnx.gz'
FEATURES_FILE = OUT_DIR / 'features.json'


def load_pipeline():
    with open(PKL, 'rb') as f:
        return pickle.load(f)


def feature_layout(pipeline):
    """Categorical columns with their categories, then numeric columns."""
    pre = pipeline.named_steps['pre']
    cat_cols = list(pre.transformers_[0][2])
    num_cols = list(pre.transformers_[1][2])
    ohe = pre.named_transformers_['cat'].named_steps['ohe']
    if any(inf is not None for inf in ohe.infrequent_categories_):
        raise RuntimeError('Infrequent categories are not supported by the JS encoder')
    categories = {col: [str(c) for c in cats] for col, cats in zip(cat_cols, ohe.categories_)}
    n_features = sum(len(c) for c in categories.values()) + len(num_cols)
    return {
        'categorical': [{'name': col, 'categories': categories[col]} for col in cat_cols],
        'numeric': num_cols,
        'n_features': n_features,
    }


def encode(rows, layout):
    """Same encoding as the JS side: one-hot (unknown -> all zeros), then numerics."""
    out = np.zeros((len(rows), layout['n_features']), dtype=np.float64)
    for i, row in enumerate(rows):
        j = 0
        for col in layout['categorical']:
            cats = col['categories']
            if row[col['name']] in cats:
                out[i, j + cats.index(row[col['name']])] = 1.0
            j += len(cats)
        for name in layout['numeric']:
            out[i, j] = np.float32(row[name])
            j += 1
    return out


def sample_profiles(layout, n, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        row = {c['name']: str(rng.choice(c['categories'])) for c in layout['categorical']}
        row['Age'] = float(rng.integers(18, 101))
        row['Years_Since_Graduation'] = float(rng.integers(0, 51))
        row['GPA_10'] = float(np.round(rng.uniform(0, 10), 1))
        rows.append(row)
    return rows


def degree_profiles():
    base = {
        'Age': 28.0, 'Country_of_Origin': 'Germany', 'Gender': 'Male',
        'Years_Since_Graduation': 3.0, 'Field_of_Study': 'IT',
        'Language_Proficiency': 'Advanced', 'University_Ranking': 'High',
        'Region_of_Study': 'EU', 'GPA_10': 8.5, 'Internship_Experience': 'Yes',
    }
    return [dict(base, Education_Level=e) for e in ['Diploma', "Bachelor's", "Master's", 'PhD']]


def main():
    pipeline = load_pipeline()
    layout = feature_layout(pipeline)
    rf = pipeline.named_steps['reg']

    onx = convert_sklearn(
        rf,
        initial_types=[('input', DoubleTensorType([None, layout['n_features']]))],
        # onnxruntime always returns float32 from TreeEnsembleRegressor;
        # thresholds, leaf values and the accumulation stay in double.
        final_types=[('variable', FloatTensorType([None, 1]))],
        target_opset={'': 13, 'ai.onnx.ml': 3},
    )
    model_bytes = onx.SerializeToString()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ONNX_FILE.write_bytes(gzip.compress(model_bytes, mtime=0))
    FEATURES_FILE.write_text(json.dumps(layout, indent=2), encoding='utf-8')
    print(f'ONNX model: {len(model_bytes) / 1024 / 1024:.2f} MB '
          f'({ONNX_FILE.stat().st_size / 1024 / 1024:.2f} MB gzipped)')

    rows = sample_profiles(layout, 500) + degree_profiles()
    df = pd.DataFrame(rows)

    # The JS encoder must reproduce the pipeline's preprocessing exactly
    pre_out = pipeline.named_steps['pre'].transform(df)
    pre_out = pre_out.toarray() if hasattr(pre_out, 'toarray') else pre_out
    X = encode(rows, layout)
    assert np.array_equal(pre_out.astype(np.float32), X.astype(np.float32)), 'Encoding mismatch'

    expected = pipeline.predict(df)
    sess = ort.InferenceSession(gzip.decompress(ONNX_FILE.read_bytes()),
                                providers=['CPUExecutionProvider'])
    got = sess.run(None, {'input': X})[0].ravel()

    abs_err = np.abs(got - expected)
    print(f'Profiles checked: {len(rows)}')
    print(f'Max absolute error: {abs_err.max():.6f}')
    print(f'Max relative error: {(abs_err / np.abs(expected).clip(min=1)).max():.2e}')
    for row, e, g in zip(rows[-4:], expected[-4:], got[-4:]):
        print(f"  {row['Education_Level']:<10} pkl={e:.4f}  onnx={g:.4f}")
    assert abs_err.max() < 0.01, 'ONNX predictions differ from the pickled pipeline'


if __name__ == '__main__':
    main()
