// Static demo runtime.
//
// Replaces the Flask REST API (prediccion-salarial/app/routes/api.py and
// app/utils/helpers.py) with an in-browser implementation that runs the same
// Random Forest through onnxruntime-web. Responses have the same shape as the
// Flask endpoints, so the page scripts can use them unchanged.
(function () {
    'use strict';

    const ORT_BASE = 'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.19.2/dist/';
    const MODEL_URL = 'model/salary_rf.onnx.gz';
    const FEATURES_URL = 'model/features.json';
    const REPO_URL = 'https://github.com/santiagodie/graduate-salary-predictor';
    const MODEL_VERSION = '1.0.0';            // load_meta() default (no metadata.json)
    const SESSION_ID = 'static-demo';         // A static site never "restarts"
    const PREDICTIONS_KEY = 'demoPredictions';
    const MAX_STORED_PREDICTIONS = 50;

    // ------------------------------------------------------------------------
    // Translations for the demo-only texts
    // ------------------------------------------------------------------------

    const repoLink = (text) => `<a href="${REPO_URL}" class="underline">${text}</a>`;
    Object.assign(translations.es, {
        'demo.notice': `Demo estática: el modelo se ejecuta en tu navegador. La versión completa es una app Flask (${repoLink('ver repositorio')}).`,
        'demo.model.loading': 'Cargando modelo…',
        'demo.model.ready': 'Modelo listo',
        'demo.model.error': 'No se pudo cargar el modelo'
    });
    Object.assign(translations.en, {
        'demo.notice': `Static demo: the model runs in your browser. The full version is a Flask app (${repoLink('see repository')}).`,
        'demo.model.loading': 'Loading model…',
        'demo.model.ready': 'Model ready',
        'demo.model.error': 'The model could not be loaded'
    });
    Object.assign(translations.fr, {
        'demo.notice': `Démo statique : le modèle s'exécute dans votre navigateur. La version complète est une application Flask (${repoLink('voir le dépôt')}).`,
        'demo.model.loading': 'Chargement du modèle…',
        'demo.model.ready': 'Modèle prêt',
        'demo.model.error': 'Impossible de charger le modèle'
    });

    const t = (key) => (translations[currentLang] || translations.es)[key];

    // ------------------------------------------------------------------------
    // Reference data (app/utils/helpers.py, app/models/schema.py)
    // ------------------------------------------------------------------------

    const COUNTRY_MAP = {
        'brasil': 'Brazil', 'china': 'China', 'alemania': 'Germany',
        'pakistán': 'Pakistan', 'usa': 'USA', 'india': 'India',
        'vietnam': 'Vietnam', 'nigeria': 'Nigeria'
    };
    const GENDER_MAP = { 'hombre': 'Male', 'mujer': 'Female', 'otro': 'Other' };
    const EDUCATION_MAP = { 'fp': 'Diploma', 'grado': "Bachelor's", 'master': "Master's", 'phd': 'PhD' };
    const FIELD_MAP = {
        'artes': 'Arts', 'ing': 'Engineering', 'it': 'IT',
        'salud': 'Health', 's.sociales': 'Social Sciences', 's sociales': 'Social Sciences',
        'empresa': 'Business'
    };
    const LANGUAGE_MAP = {
        'básico': 'Basic', 'basico': 'Basic',
        'intermedio': 'Intermediate',
        'avanzado': 'Advanced',
        'fluido': 'Fluent'
    };
    const RANKING_MAP = { 'alto': 'High', 'medio': 'Medium', 'bajo': 'Low' };
    const REGION_MAP = { 'australia': 'Australia', 'europa': 'EU', 'canadá': 'Canada', 'canada': 'Canada' };
    const FIELD_AVERAGES = {
        'Artes': { age: 26, grade: 7.2 },
        'Ing': { age: 27, grade: 7.8 },
        'IT': { age: 25, grade: 7.5 },
        'Salud': { age: 28, grade: 8.0 },
        'S.Sociales': { age: 27, grade: 7.3 },
        'Empresa': { age: 26, grade: 7.6 }
    };
    const DEFAULT_FIELD_AVERAGES = { age: 27, grade: 7.5 };

    const COUNTRIES = ['Brazil', 'China', 'Germany', 'Pakistan', 'USA', 'India', 'Vietnam', 'Nigeria'];
    const EDUCATION_LEVELS = ['Diploma', "Bachelor's", "Master's", 'PhD'];
    const FIELDS = ['Arts', 'Engineering', 'IT', 'Health', 'Social Sciences', 'Business'];

    // Python's dict.get(key, default)
    function get(map, key, fallback) {
        return key != null && Object.prototype.hasOwnProperty.call(map, key) ? map[key] : fallback;
    }

    // Python's random.randint (inclusive)
    function randint(a, b) {
        return a + Math.floor(Math.random() * (b - a + 1));
    }

    // datetime.now().isoformat()
    function isoNow() {
        const d = new Date();
        const pad = (n, w = 2) => String(n).padStart(w, '0');
        return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
               `T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}` +
               `.${pad(d.getMilliseconds() * 1000, 6)}`;
    }

    // Flask's jsonify sorts object keys
    function sortKeys(obj) {
        return Object.fromEntries(Object.keys(obj).sort().map(k => [k, obj[k]]));
    }

    function jsonResponse(body, status = 200) {
        return new Response(JSON.stringify(body), {
            status: status,
            headers: { 'Content-Type': 'application/json' }
        });
    }

    // ------------------------------------------------------------------------
    // Model loading
    // ------------------------------------------------------------------------

    let modelPromise = null;
    let runQueue = Promise.resolve();
    let statsCache = { by_country: {}, by_education: {}, by_field: {}, last_updated: null };

    function loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = () => reject(new Error('Could not load ' + src));
            document.head.appendChild(script);
        });
    }

    async function download(url, onProgress) {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status} for ${url}`);
        const total = Number(response.headers.get('Content-Length')) || 0;
        const reader = response.body.getReader();
        const chunks = [];
        let received = 0;
        for (;;) {
            const { done, value } = await reader.read();
            if (done) break;
            chunks.push(value);
            received += value.length;
            if (total) onProgress(Math.min(99, Math.round(received / total * 100)));
        }
        const blob = new Blob(chunks);
        const head = new Uint8Array(await blob.slice(0, 2).arrayBuffer());
        // The model is stored gzip-compressed; some servers decompress it on the fly
        const isGzip = head[0] === 0x1f && head[1] === 0x8b;
        const stream = isGzip ? blob.stream().pipeThrough(new DecompressionStream('gzip')) : blob.stream();
        return new Uint8Array(await new Response(stream).arrayBuffer());
    }

    function loadModel() {
        if (!modelPromise) {
            modelPromise = (async () => {
                setBadge('loading', 0);
                await loadScript(ORT_BASE + 'ort.wasm.min.js');
                ort.env.wasm.wasmPaths = ORT_BASE;
                ort.env.wasm.numThreads = 1;

                const [layout, bytes] = await Promise.all([
                    fetch(FEATURES_URL).then(r => {
                        if (!r.ok) throw new Error(`HTTP ${r.status} for ${FEATURES_URL}`);
                        return r.json();
                    }),
                    download(MODEL_URL, p => setBadge('loading', p))
                ]);
                const session = await ort.InferenceSession.create(bytes);
                const model = { layout, session };
                await calculateAverageSalariesFromModel(model);
                setBadge('ready');
                return model;
            })().catch(error => {
                console.error('[ERROR] No se pudo cargar el modelo:', error);
                setBadge('error');
                modelPromise = null;
                throw error;
            });
        }
        return modelPromise;
    }

    // One-hot encoding as in the scikit-learn pipeline (unknown category -> zeros),
    // then the numeric features rounded to float32 as scikit-learn does.
    async function predictRows(model, rows) {
        const { layout, session } = model;
        const nf = layout.n_features;
        const data = new Float64Array(rows.length * nf);
        rows.forEach((row, i) => {
            let j = i * nf;
            for (const col of layout.categorical) {
                const k = col.categories.indexOf(row[col.name]);
                if (k >= 0) data[j + k] = 1;
                j += col.categories.length;
            }
            for (const name of layout.numeric) {
                data[j++] = Math.fround(Number(row[name]));
            }
        });
        const run = runQueue.then(() => session.run({
            [session.inputNames[0]]: new ort.Tensor('float64', data, [rows.length, nf])
        }));
        runQueue = run.catch(() => {});
        const output = await run;
        return Array.from(output[session.outputNames[0]].data, Number);
    }

    // calculate_average_salaries_from_model() (run once, like at Flask startup)
    async function calculateAverageSalariesFromModel(model) {
        const base = { Age: 28.0, Years_Since_Graduation: 3.0, GPA_10: 7.5, Internship_Experience: 'Yes' };
        const common = {
            Country_of_Origin: 'Germany', Gender: 'Male', Education_Level: "Bachelor's",
            Field_of_Study: 'IT', Language_Proficiency: 'Intermediate',
            University_Ranking: 'Medium', Region_of_Study: 'EU'
        };
        const rows = [
            ...COUNTRIES.map(c => ({ ...base, ...common, Country_of_Origin: c })),
            ...EDUCATION_LEVELS.map(e => ({ ...base, ...common, Education_Level: e })),
            ...FIELDS.map(f => ({ ...base, ...common, Field_of_Study: f }))
        ];
        const salaries = await predictRows(model, rows);
        let i = 0;
        COUNTRIES.forEach(c => { statsCache.by_country[c] = salaries[i++]; });
        EDUCATION_LEVELS.forEach(e => { statsCache.by_education[e] = salaries[i++]; });
        FIELDS.forEach(f => { statsCache.by_field[f] = salaries[i++]; });
        statsCache.last_updated = isoNow();
    }

    // ------------------------------------------------------------------------
    // Request validation (PredictRequest in app/models/schema.py, Pydantic v2)
    // ------------------------------------------------------------------------

    const PYDANTIC_URL = 'https://errors.pydantic.dev/2.14/v/';
    const SCHEMA = [
        { name: 'nombre', type: 'str', optional: true },
        { name: 'edad', type: 'float', ge: 18, le: 100 },
        { name: 'pais', type: 'str', valid: ['Brasil', 'China', 'Alemania', 'Pakistán', 'USA', 'India', 'Vietnam', 'Nigeria'] },
        { name: 'genero', type: 'str', valid: ['Hombre', 'Mujer', 'Otro'] },
        { name: 'titulacion', type: 'str', valid: ['Grado', 'Master', 'PHD', 'FP'] },
        { name: 'anios_desde_obtencion', alias: 'aniosDesdeObtencion', type: 'float', default: 2.0, ge: 0, le: 50 },
        { name: 'campo_estudio', alias: 'campoEstudio', type: 'str', valid: ['Artes', 'Ing', 'IT', 'Salud', 'S.Sociales', 'Empresa'] },
        { name: 'nivel_ingles', alias: 'nivelIngles', type: 'str', valid: ['Básico', 'Intermedio', 'Avanzado', 'Fluido'] },
        { name: 'universidad_ranking', alias: 'universidadRanking', type: 'str' },
        { name: 'region_estudio', alias: 'regionEstudio', type: 'str' },
        { name: 'nota_media', alias: 'notaMedia', type: 'float', ge: 0, le: 10 },
        { name: 'practicas', type: 'bool', default: false }
    ];
    const NUMBER_RE = /^[+-]?(\d[\d_]*\.?\d*|\.\d+)([eE][+-]?\d+)?$/;
    const TRUE_STRINGS = ['1', 'on', 't', 'true', 'y', 'yes'];
    const FALSE_STRINGS = ['0', 'off', 'f', 'false', 'n', 'no'];

    function coerce(field, value) {
        if (field.type === 'str') {
            if (typeof value === 'string') return { value };
            return { error: ['string_type', 'Input should be a valid string'] };
        }
        if (field.type === 'float') {
            if (typeof value === 'number' || typeof value === 'boolean') return { value: Number(value) };
            if (typeof value === 'string') {
                const s = value.trim();
                if (NUMBER_RE.test(s)) return { value: Number(s.replace(/_/g, '')) };
                return { error: ['float_parsing', 'Input should be a valid number, unable to parse string as a number'] };
            }
            return { error: ['float_type', 'Input should be a valid number'] };
        }
        // bool
        if (typeof value === 'boolean') return { value };
        if (value === 0 || value === 1) return { value: value === 1 };
        if (typeof value === 'string') {
            const s = value.trim().toLowerCase();
            if (TRUE_STRINGS.includes(s)) return { value: true };
            if (FALSE_STRINGS.includes(s)) return { value: false };
            return { error: ['bool_parsing', 'Input should be a valid boolean, unable to interpret input'] };
        }
        return { error: ['bool_type', 'Input should be a valid boolean'] };
    }

    // Returns { data } or { errors, validatorFailed }
    function validatePredictRequest(payload) {
        const data = {};
        const errors = [];
        let validatorFailed = false;

        for (const field of SCHEMA) {
            const key = field.alias && field.alias in payload ? field.alias
                      : field.name in payload ? field.name : null;
            const loc = [field.alias || field.name];

            if (key === null) {
                if (field.optional) { data[field.name] = null; continue; }
                if ('default' in field) { data[field.name] = field.default; continue; }
                errors.push({ type: 'missing', loc, msg: 'Field required', input: payload, url: PYDANTIC_URL + 'missing' });
                continue;
            }

            const raw = payload[key];
            if (field.optional && raw === null) { data[field.name] = null; continue; }

            const { value, error } = coerce(field, raw);
            if (error) {
                errors.push({ type: error[0], loc, msg: error[1], input: raw, url: PYDANTIC_URL + error[0] });
                continue;
            }
            if (field.ge !== undefined && !(value >= field.ge)) {
                errors.push({ type: 'greater_than_equal', loc, msg: `Input should be greater than or equal to ${field.ge}`,
                              input: raw, ctx: { ge: field.ge }, url: PYDANTIC_URL + 'greater_than_equal' });
                continue;
            }
            if (field.le !== undefined && !(value <= field.le)) {
                errors.push({ type: 'less_than_equal', loc, msg: `Input should be less than or equal to ${field.le}`,
                              input: raw, ctx: { le: field.le }, url: PYDANTIC_URL + 'less_than_equal' });
                continue;
            }
            if (field.valid && !field.valid.includes(value)) {
                validatorFailed = true;
                errors.push({ type: 'value_error', loc, msg: 'Value error', input: raw });
                continue;
            }
            data[field.name] = value;
        }
        return errors.length ? { errors, validatorFailed } : { data };
    }

    // ------------------------------------------------------------------------
    // helpers.py
    // ------------------------------------------------------------------------

    function translateFeaturesToEnglish(data) {
        const paisLower = data.pais.toLowerCase();
        const generoLower = data.genero.toLowerCase();
        const titulacionLower = data.titulacion.toLowerCase();
        const campoLower = data.campo_estudio.toLowerCase().replaceAll('.', ' ');
        const inglesLower = data.nivel_ingles.toLowerCase();
        const rankingLower = data.universidad_ranking.toLowerCase();
        const regionLower = data.region_estudio.toLowerCase();

        return {
            Age: Number(data.edad),
            Country_of_Origin: get(COUNTRY_MAP, paisLower, data.pais),
            Gender: get(GENDER_MAP, generoLower, data.genero),
            Education_Level: get(EDUCATION_MAP, titulacionLower, data.titulacion),
            Years_Since_Graduation: Number(data.anios_desde_obtencion),
            Field_of_Study: get(FIELD_MAP, campoLower, data.campo_estudio),
            Language_Proficiency: get(LANGUAGE_MAP, inglesLower, data.nivel_ingles),
            University_Ranking: get(RANKING_MAP, rankingLower, 'Low'),
            Region_of_Study: get(REGION_MAP, regionLower, data.region_estudio),
            GPA_10: Number(data.nota_media),
            Internship_Experience: data.practicas ? 'Yes' : 'No'
        };
    }

    function calculatePercentile(value, minVal, maxVal) {
        if (maxVal === minVal) return 50;
        const percentile = ((value - minVal) / (maxVal - minVal)) * 100;
        return Math.max(0, Math.min(100, Math.trunc(percentile)));
    }

    function buildComparisons(requestData, salary) {
        const countryEng = get(COUNTRY_MAP, (requestData.pais || '').toLowerCase(), 'Germany');
        const educationEng = get(EDUCATION_MAP, (requestData.titulacion || '').toLowerCase(), "Bachelor's");
        const fieldEng = get(FIELD_MAP, (requestData.campo_estudio || '').toLowerCase(), 'IT');

        const countryAvg = get(statsCache.by_country, countryEng, 35000);
        const educationAvg = get(statsCache.by_education, educationEng, 40000);
        const fieldAvg = get(statsCache.by_field, fieldEng, 40000);
        const userField = requestData.campo_estudio ?? 'IT';
        const fieldStats = get(FIELD_AVERAGES, userField, DEFAULT_FIELD_AVERAGES);

        return {
            edad: {
                user: requestData.edad ?? 25,
                average: fieldStats.age,
                field: userField,
                percentile: calculatePercentile(requestData.edad ?? 25, 22, 35)
            },
            pais: {
                user: requestData.pais,
                average_salary: countryAvg,
                percentile: calculatePercentile(salary, countryAvg - 5000, countryAvg + 15000)
            },
            genero: {
                user: requestData.genero,
                distribution: { 'Hombre': 55, 'Mujer': 40, 'Otro': 5 }
            },
            formacion: {
                user: requestData.titulacion,
                average_salary: educationAvg
            },
            campoEstudio: {
                user: userField,
                average_salary: fieldAvg
            },
            notaMedia: {
                user: requestData.nota_media ?? 7,
                average: fieldStats.grade,
                field: userField
            },
            universidadRanking: {
                user: requestData.universidad_ranking,
                impact: { 'Alto': '+15%', 'Medio': '+5%', 'Bajo': '0%' }
            },
            regionEstudio: {
                user: requestData.region_estudio,
                average_by_region: { 'USA': 60000, 'Europa': 38000, 'Australia': 45000 }
            }
        };
    }

    // ------------------------------------------------------------------------
    // Stored predictions (the Flask app keeps them in memory)
    // ------------------------------------------------------------------------

    function loadPredictions() {
        try {
            return JSON.parse(localStorage.getItem(PREDICTIONS_KEY) || '{}');
        } catch (e) {
            return {};
        }
    }

    function storePrediction(result) {
        const predictions = loadPredictions();
        predictions[result.form_id] = result;
        const ids = Object.keys(predictions).sort((a, b) =>
            predictions[a].timestamp < predictions[b].timestamp ? -1 : 1);
        ids.slice(0, Math.max(0, ids.length - MAX_STORED_PREDICTIONS)).forEach(id => delete predictions[id]);
        try {
            localStorage.setItem(PREDICTIONS_KEY, JSON.stringify(predictions));
        } catch (e) {
            console.error('[ERROR] No se pudo guardar la predicción:', e);
        }
    }

    // ------------------------------------------------------------------------
    // API (app/routes/api.py)
    // ------------------------------------------------------------------------

    let redirecting = false;

    const DemoApi = {
        // GET /api/health
        health() {
            return Promise.resolve(jsonResponse({
                status: 'ok',
                timestamp: isoNow(),
                version: MODEL_VERSION,
                server_session_id: SESSION_ID
            }));
        },

        // POST /api/predict (without the artificial one-second delay)
        async predict(payload) {
            payload = payload || {};
            const validation = validatePredictRequest(payload);
            if (validation.errors) {
                if (validation.validatorFailed) {
                    // The Flask app fails to serialize these errors (see Known limitations)
                    return jsonResponse({
                        error: 'server_error',
                        details: '500 Internal Server Error: Object of type ValueError is not JSON serializable'
                    }, 500);
                }
                return jsonResponse({ error: 'validation_error', details: validation.errors }, 422);
            }
            const data = validation.data;
            const formId = `pred_${Math.floor(Date.now() / 1000)}`;
            const features = translateFeaturesToEnglish(data);

            let salary;
            try {
                const model = await loadModel();
                [salary] = await predictRows(model, [features]);
            } catch (e) {
                console.error('[ERROR] Error en prediccion:', e);
                return jsonResponse({ error: 'prediction_error', details: String(e && e.message || e) }, 500);
            }

            const result = {
                salary: salary,
                form_id: formId,
                model_version: MODEL_VERSION,
                timestamp: isoNow(),
                using_real_model: true,
                comparisons: buildComparisons(data, salary),
                statistics: {
                    total_predictions: randint(1000, 5000),
                    confidence: randint(75, 95),
                    salary_range: { min: salary - 5000, max: salary + 8000 }
                }
            };
            storePrediction(result);
            return jsonResponse(result);
        },

        // POST /api/statistics
        async statistics(filters) {
            if (redirecting) return new Promise(() => {});
            filters = filters || {};
            const model = await loadModel();

            const baseProfile = {
                Age: 28.0,
                Years_Since_Graduation: 3.0,
                GPA_10: 7.5,
                Internship_Experience: 'Yes',
                Gender: 'Male',
                Education_Level: "Bachelor's",
                Field_of_Study: 'IT',
                Language_Proficiency: 'Intermediate',
                University_Ranking: 'Medium',
                Region_of_Study: 'EU'
            };
            baseProfile.Country_of_Origin = filters.pais ? get(COUNTRY_MAP, filters.pais.toLowerCase(), 'Germany') : 'Germany';
            if (filters.genero) baseProfile.Gender = get(GENDER_MAP, filters.genero.toLowerCase(), 'Male');
            if (filters.formacion) baseProfile.Education_Level = get(EDUCATION_MAP, filters.formacion.toLowerCase(), "Bachelor's");
            if (filters.campoEstudio) baseProfile.Field_of_Study = get(FIELD_MAP, filters.campoEstudio.toLowerCase(), 'IT');

            const genders = ['Male', 'Female'];
            const rows = [
                ...COUNTRIES.map(c => ({ ...baseProfile, Country_of_Origin: c })),
                ...EDUCATION_LEVELS.map(e => ({ ...baseProfile, Education_Level: e })),
                ...FIELDS.map(f => ({ ...baseProfile, Field_of_Study: f })),
                ...genders.map(g => ({ ...baseProfile, Gender: g }))
            ];
            const salaries = await predictRows(model, rows);
            let i = 0;
            const byCountry = {}, byEducation = {}, byField = {}, byGender = {};
            COUNTRIES.forEach(c => { byCountry[c] = salaries[i++]; });
            EDUCATION_LEVELS.forEach(e => { byEducation[e] = salaries[i++]; });
            FIELDS.forEach(f => { byField[f] = salaries[i++]; });
            genders.forEach(g => { byGender[g] = salaries[i++]; });

            const fieldKey = 'campoEstudio' in filters ? filters.campoEstudio : 'IT';
            const fieldStats = get(FIELD_AVERAGES, fieldKey, DEFAULT_FIELD_AVERAGES);
            const countryValues = Object.values(byCountry);

            return jsonResponse({
                average_salary: countryValues.reduce((a, b) => a + b, 0) / countryValues.length,
                total_graduates: randint(800, 1200),
                by_country: sortKeys(byCountry),
                by_education: sortKeys(byEducation),
                by_field: sortKeys(byField),
                by_gender: sortKeys(byGender),
                average_age: fieldStats.age,
                average_grade: fieldStats.grade
            });
        }
    };
    window.DemoApi = DemoApi;

    // ------------------------------------------------------------------------
    // Model loading indicator
    // ------------------------------------------------------------------------

    let badge = null;
    let badgeState = null;
    let badgeProgress = 0;

    function renderBadge() {
        if (!badge || !badgeState) return;
        const styles = {
            loading: 'bg-white text-gray-700 border-gray-200',
            ready: 'bg-green-50 text-green-700 border-green-200',
            error: 'bg-red-50 text-red-700 border-red-200'
        };
        badge.className = 'fixed bottom-4 left-4 z-50 px-4 py-2 rounded-full shadow-md border text-sm ' +
                          'flex items-center gap-2 transition-opacity duration-500 ' + styles[badgeState];
        if (badgeState === 'loading') {
            badge.innerHTML = '<span class="inline-block w-4 h-4 border-2 border-blue-600 border-b-transparent rounded-full animate-spin"></span>';
            badge.append(`${t('demo.model.loading')} ${badgeProgress}%`);
        } else {
            badge.textContent = (badgeState === 'ready' ? '✓ ' : '⚠️ ') + t('demo.model.' + badgeState);
        }
    }

    function setBadge(state, progress) {
        if (!badge) {
            badge = document.createElement('div');
            badge.setAttribute('role', 'status');
            document.body.appendChild(badge);
        }
        badgeState = state;
        if (progress !== undefined) badgeProgress = progress;
        badge.style.opacity = '1';
        renderBadge();
        if (state === 'ready') {
            setTimeout(() => { badge.style.opacity = '0'; }, 2000);
        }
    }

    // Keep the indicator in the selected language
    const originalChangeLanguage = window.changeLanguage;
    window.changeLanguage = function (lang) {
        originalChangeLanguage(lang);
        renderBadge();
    };

    // ------------------------------------------------------------------------
    // Result page: fill in the stored prediction (Flask renders it server-side)
    // ------------------------------------------------------------------------

    // Values that are floats in Python and render as "28.0" in the template
    const FLOAT_PATHS = new Set([
        'salary', 'statistics.salary_range.min', 'statistics.salary_range.max',
        'comparisons.edad.user', 'comparisons.notaMedia.user', 'comparisons.notaMedia.average'
    ]);

    function pythonStr(path, value) {
        if (typeof value === 'number' && FLOAT_PATHS.has(path) && Number.isInteger(value)) {
            return value.toFixed(1);
        }
        return String(value);
    }

    function fillPlaceholders(prediction) {
        const lookup = (path) => path.split('.').reduce((obj, key) => obj[key], prediction);
        const replace = (text) => text.replace(/__P:([\w.]+)__/g, (_, path) => pythonStr(path, lookup(path)));

        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
            const node = walker.currentNode;
            if (node.nodeValue.includes('__P:')) node.nodeValue = replace(node.nodeValue);
        }
        document.querySelectorAll('[data-salary]').forEach(el => {
            el.setAttribute('data-salary', replace(el.getAttribute('data-salary')));
        });
    }

    const page = document.body.dataset.page;

    if (page === 'resultado') {
        const id = new URLSearchParams(window.location.search).get('id');
        const prediction = id ? loadPredictions()[id] : null;
        if (prediction) {
            window.DEMO_PREDICTION = prediction;
            fillPlaceholders(prediction);
        } else {
            // Same as the Flask view: unknown id -> error page. A placeholder keeps
            // the page script from failing before the browser navigates away.
            redirecting = true;
            const zero = { user: '', average: 0, average_salary: 0 };
            window.DEMO_PREDICTION = {
                salary: 0,
                statistics: { confidence: 0, salary_range: { min: 0, max: 0 } },
                comparisons: { edad: zero, pais: zero, formacion: zero, campoEstudio: zero, notaMedia: zero }
            };
            window.location.replace('error.html');
        }
    }

    // Start downloading the model on the pages that use it
    if (page === 'formulario' || (page === 'resultado' && !redirecting)) {
        document.addEventListener('DOMContentLoaded', () => {
            loadModel().catch(() => {});
        });
    }
})();
