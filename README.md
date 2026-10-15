# Graduate Salary Predictor

A web application that estimates the expected salary of a recent graduate from their profile (age, country of origin, degree, field of study, English level, university ranking, region of study, GPA and internship experience). Predictions come from a scikit-learn Random Forest served through a Flask REST API, with an interactive front end that compares the result against other profiles.

> This was a **group project by a team of four** (see [Team](#team)). The original repository is [alhidalgb/Predictor_sueldos](https://github.com/alhidalgb/Predictor_sueldos).

## The problem

Graduates often have little reference for what salary to expect, and the answer depends on many interacting factors. The goal of the project was to train a regression model on graduate outcome data and wrap it in an application that non-technical users can try: fill in a form, get an estimate, and see how changing one factor (degree, country, field) moves it.

## Features

- Salary prediction from a two-step form with server-side validation
- Comparison charts (Chart.js) against average profiles by country, degree and field of study, computed by querying the model itself
- Filters on the results page that recompute the comparisons for a different profile
- Interface in Spanish, English and French
- Currency display in USD, EUR or GBP
- Prediction history stored in the browser (localStorage)
- JSON REST API usable independently of the web interface

## Architecture

```
prediccion-salarial/
├── run.py                  # Entry point
├── config.py               # Environment-based configuration
├── requirements.txt
├── data/
│   └── modelo_entrenado.pkl   # Trained scikit-learn pipeline
├── app/
│   ├── __init__.py         # Application factory (create_app), CORS, blueprints
│   ├── models/
│   │   ├── schema.py       # Pydantic request/response models
│   │   └── predictor.py    # Model loading
│   ├── routes/
│   │   ├── views.py        # HTML pages (Jinja2)
│   │   └── api.py          # REST API
│   ├── utils/helpers.py    # Input → model feature mapping, comparison statistics
│   ├── templates/          # Jinja2 templates
│   └── static/             # JavaScript, CSS, images
└── tests/                  # Manual check scripts (see Known limitations)
```

- **Layers.** HTML views and the REST API live in separate Flask blueprints. Model loading is isolated in `app/models`, and the translation from form values to the model's feature space is in `app/utils/helpers.py`.
- **Validation.** Incoming requests are parsed into a Pydantic v2 model (`PredictRequest`) with typed fields, numeric ranges, closed sets of allowed values and camelCase aliases for the JavaScript client.
- **Model.** A scikit-learn `Pipeline` with a `ColumnTransformer` (imputation + one-hot encoding for categorical features, median imputation for numeric ones) followed by a `RandomForestRegressor` with 400 trees.

### REST API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service status and model version |
| `GET` | `/api/model/info` | Model metadata and expected features |
| `POST` | `/api/predict` | Validates a profile and returns the predicted salary plus comparison data |
| `POST` | `/api/statistics` | Model-based averages by country, degree, field and gender for a filtered profile |
| `GET` | `/api/prediction/<form_id>` | Retrieves a previous prediction from the current server session |

Example request:

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"edad": 28, "pais": "Alemania", "genero": "Mujer", "titulacion": "Master",
       "aniosDesdeObtencion": 3, "campoEstudio": "IT", "nivelIngles": "Avanzado",
       "universidadRanking": "Alto", "regionEstudio": "Europa", "notaMedia": 8.5,
       "practicas": true}'
```

## Getting started

Requires **Python 3.11**. The model was serialized with scikit-learn 1.4.2, so the dependency versions are pinned.

```bash
git clone https://github.com/santiagodie/graduate-salary-predictor.git
cd graduate-salary-predictor/prediccion-salarial

python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
python run.py
```

The application runs at <http://localhost:5000>.

## Model and results

- **Data:** a dataset of 300,000 graduate records provided for the course (not included in this repository). It has 15 columns, of which `Visa_Type` and `Job_Sector` were discarded.
- **Preprocessing:** GPA converted from a 0–4 to a 0–10 scale, the UK region merged into EU, and rows with a salary of 0 removed (47.8% of the data). Employment status was not used as a feature.
- **Training:** to keep training fast, the model was trained on a **random sample of 1,000 rows** with an 80/20 train/test split.
- **Results on the 200-row test set:** **R² = 0.919**, **MAE ≈ 4,122**.

Because of the small training sample, these figures should be read as indicative only. In the trained model, education level is by far the most influential feature.

## Team

- [@alhidalgb](https://github.com/alhidalgb)
- [@jojimez03](https://github.com/jojimez03)
- [@isteres](https://github.com/isteres)
- [@santiagodie](https://github.com/santiagodie)

## Known limitations

- **Small training sample.** The model was trained on 1,000 of roughly 156,000 usable rows.
- **Categories limited to the training data.** The model has no data for Spain as a country of origin or the USA as a region of study, so the form offers Germany and Canada instead. The Spanish vocational degree (FP) is mapped to the model's closest category, "Diploma". The dataset does not document its currency; the interface treats predictions as USD.
- **Placeholder values in the results.** The "confidence" and "total predictions" figures are random numbers, and some comparison values (average age and grade by field, gender distribution, exchange rates) are hard-coded.
- **Artificial delay.** `/api/predict` waits one second on purpose (`time.sleep(1)`).
- **In-memory storage.** Predictions are stored in memory and lost when the server restarts.
- **Validation errors.** Values rejected by the Pydantic validators (for example, an unsupported country) produce an HTTP 500 instead of a 422, because the error details cannot be serialized to JSON.
- **Dead code.** `app/models/predictor.py` still contains an unused manual encoding path (`predict_one`, `ENCODING_MAPS`, scaler and metadata loading); predictions are made directly with the scikit-learn pipeline.
- **No automated tests.** The files in `tests/` are manual check scripts, not pytest tests; `test_prediccion.py` requires the server to be running.
- **Development defaults.** Debug mode is on by default, the server listens on `0.0.0.0`, and `SECRET_KEY` falls back to a development value. Set `FLASK_ENV=production` and `SECRET_KEY` before exposing it.
- **Model compatibility.** The model is stored as a pickle tied to scikit-learn 1.4.2.
- **Spanish identifiers.** Code identifiers, comments and API field names are in Spanish.

## License

Released under the [MIT License](LICENSE).

---

Built for the Professional Practice in Computer Engineering course at the University of La Rioja (2025–26).
