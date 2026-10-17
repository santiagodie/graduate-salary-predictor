<p align="center"><img src="assets/banner.svg" width="100%" alt="Graduate Salary Predictor · University of La Rioja" /></p>

<p align="center">A web application that estimates the expected salary of a recent graduate from their profile, with a scikit-learn Random Forest served through a Flask REST API.</p>

<p align="center">
  <img src="https://img.shields.io/badge/language-Python-C9A227?style=flat-square&labelColor=0B1F3A" alt="Language: Python" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-C9A227?style=flat-square&labelColor=0B1F3A" alt="License: MIT" /></a>
  <a href="https://santiagodie.github.io/graduate-salary-predictor/"><img src="https://img.shields.io/badge/live%20demo-GitHub%20Pages-C9A227?style=flat-square&labelColor=0B1F3A" alt="Live demo" /></a>
</p>

## Table of Contents

- [About the Project](#about-the-project)
- [Live Demo](#live-demo)
- [Features](#features)
- [Built With](#built-with)
- [How It Works](#how-it-works)
- [Results](#results)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Known Limitations](#known-limitations)
- [Credits](#credits)
- [License](#license)
- [Contact](#contact)

## About the Project

A web application that estimates the expected salary of a recent graduate from their profile (age, country of origin, degree, field of study, English level, university ranking, region of study, GPA and internship experience). Predictions come from a scikit-learn Random Forest served through a Flask REST API, with an interactive front end that compares the result against other profiles.

Graduates often have little reference for what salary to expect, and the answer depends on many interacting factors. The goal of the project was to train a regression model on graduate outcome data and wrap it in an application that non-technical users can try: fill in a form, get an estimate, and see how changing one factor (degree, country, field) moves it.

> This was a **group project by a team of four** (see [Team](#team)). The original repository is [alhidalgb/Predictor_sueldos](https://github.com/alhidalgb/Predictor_sueldos).

## Live Demo

**[santiagodie.github.io/graduate-salary-predictor](https://santiagodie.github.io/graduate-salary-predictor/)**: a static version of the app that runs the same trained model in your browser with ONNX (onnxruntime-web), with no server involved.

## Features

- Salary prediction from a two-step form with server-side validation
- Comparison charts (Chart.js) against average profiles by country, degree and field of study, computed by querying the model itself
- Filters on the results page that recompute the comparisons for a different profile
- Interface in Spanish, English and French
- Currency display in USD, EUR or GBP
- Prediction history stored in the browser (localStorage)
- JSON REST API usable independently of the web interface

## Built With

- Python 3.11, Flask (application factory, blueprints, Jinja2 templates)
- Pydantic v2 for request validation
- scikit-learn 1.4.2 (`Pipeline`, `ColumnTransformer`, `RandomForestRegressor`)
- Chart.js for the comparison charts
- ONNX (onnxruntime-web) for the static demo

## How It Works

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

## Results

- **Data:** a dataset of 300,000 graduate records provided for the course (not included in this repository). It has 15 columns, of which `Visa_Type` and `Job_Sector` were discarded.
- **Preprocessing:** GPA converted from a 0–4 to a 0–10 scale, the UK region merged into EU, and rows with a salary of 0 removed (47.8% of the data). Employment status was not used as a feature.
- **Training:** to keep training fast, the model was trained on a **random sample of 1,000 rows** with an 80/20 train/test split.
- **Results on the 200-row test set:** **R² = 0.919**, **MAE ≈ 4,122**.

Because of the small training sample, these figures should be read as indicative only. In the trained model, education level is by far the most influential feature.

## Getting Started

### Prerequisites

Requires **Python 3.11**. The model was serialized with scikit-learn 1.4.2, so the dependency versions are pinned.

### Installation

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

### Usage

The application runs at <http://localhost:5000>.

Example request:

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"edad": 28, "pais": "Alemania", "genero": "Mujer", "titulacion": "Master",
       "aniosDesdeObtencion": 3, "campoEstudio": "IT", "nivelIngles": "Avanzado",
       "universidadRanking": "Alto", "regionEstudio": "Europa", "notaMedia": 8.5,
       "practicas": true}'
```

## Project Structure

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
└── tests/                  # Manual check scripts (see Known Limitations)
demo/                       # Static ONNX version published to GitHub Pages
```

## Known Limitations

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

## Credits

### Team

- [@alhidalgb](https://github.com/alhidalgb)
- [@jojimez03](https://github.com/jojimez03)
- [@isteres](https://github.com/isteres)
- [@santiagodie](https://github.com/santiagodie)

See also [CONTRIBUTORS.md](CONTRIBUTORS.md).

## License

Released under the [MIT License](LICENSE).

## Contact

Santiago Die · [GitHub](https://github.com/santiagodie) · [LinkedIn](https://www.linkedin.com/in/santiago-die-morejon)

---

Built for the Professional Practice in Computer Engineering course at the University of La Rioja (2025–26).
