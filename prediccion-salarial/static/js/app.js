// app.js - JavaScript principal de la aplicación

// Sistema de traducciones simple
const translations = {
    es: {
        'hero.title': 'Predice tu Salario como Graduado',
        'hero.subtitle': 'Descubre cuánto podrías ganar basándonos en tu formación, experiencia y ubicación',
        'hero.start': 'Comenzar Predicción',
        'hero.more': 'Más Información',
        'features.analysis.title': 'Análisis Inteligente',
        'features.analysis.desc': 'Algoritmo basado en datos reales del mercado laboral internacional',
        'features.global.title': 'Perspectiva Global',
        'features.global.desc': 'Compara tu perfil con graduados de todo el mundo',
        'features.instant.title': 'Resultados Instantáneos',
        'features.instant.desc': 'Obtén tu predicción salarial en menos de 2 minutos',
        'stats.predictions': 'Predicciones Realizadas',
        'stats.countries': 'Países Analizados',
        'stats.accuracy': 'Precisión Media',
        'form.step': 'Paso',
        'form.personal.title': 'Datos Personales',
        'form.personal.name': 'Nombre (Opcional)',
        'form.personal.age': 'Edad',
        'form.personal.country': 'País',
        'form.personal.gender': 'Género',
        'form.education.title': 'Datos de Formación',
        'form.next': 'Siguiente',
        'form.back': 'Atrás',
        'form.submit': 'Finalizar',
        'form.processing': 'Procesando tu predicción...',
        'result.title': 'Tu Salario Estimado',
        'result.annual': 'Anual',
        'result.new': 'Nueva Predicción',
        'result.home': 'Volver al Inicio'
    },
    en: {
        'hero.title': 'Predict Your Graduate Salary',
        'hero.subtitle': 'Discover how much you could earn based on your education, experience and location',
        'hero.start': 'Start Prediction',
        'hero.more': 'More Information',
        'features.analysis.title': 'Smart Analysis',
        'features.analysis.desc': 'Algorithm based on real international job market data',
        'features.global.title': 'Global Perspective',
        'features.global.desc': 'Compare your profile with graduates worldwide',
        'features.instant.title': 'Instant Results',
        'features.instant.desc': 'Get your salary prediction in less than 2 minutes',
        'stats.predictions': 'Predictions Made',
        'stats.countries': 'Countries Analyzed',
        'stats.accuracy': 'Average Accuracy',
        'form.step': 'Step',
        'form.personal.title': 'Personal Data',
        'form.personal.name': 'Name (Optional)',
        'form.personal.age': 'Age',
        'form.personal.country': 'Country',
        'form.personal.gender': 'Gender',
        'form.education.title': 'Education Data',
        'form.next': 'Next',
        'form.back': 'Back',
        'form.submit': 'Submit',
        'form.processing': 'Processing your prediction...',
        'result.title': 'Your Estimated Salary',
        'result.annual': 'Annual',
        'result.new': 'New Prediction',
        'result.home': 'Back to Home'
    },
    fr: {
        'hero.title': 'Prédisez Votre Salaire de Diplômé',
        'hero.subtitle': 'Découvrez combien vous pourriez gagner selon votre formation, expérience et localisation',
        'hero.start': 'Commencer la Prédiction',
        'hero.more': 'Plus d\'Informations',
        'features.analysis.title': 'Analyse Intelligente',
        'features.analysis.desc': 'Algorithme basé sur des données réelles du marché du travail international',
        'features.global.title': 'Perspective Globale',
        'features.global.desc': 'Comparez votre profil avec des diplômés du monde entier',
        'features.instant.title': 'Résultats Instantanés',
        'features.instant.desc': 'Obtenez votre prédiction salariale en moins de 2 minutes',
        'stats.predictions': 'Prédictions Réalisées',
        'stats.countries': 'Pays Analysés',
        'stats.accuracy': 'Précision Moyenne',
        'form.step': 'Étape',
        'form.personal.title': 'Données Personnelles',
        'form.personal.name': 'Nom (Optionnel)',
        'form.personal.age': 'Âge',
        'form.personal.country': 'Pays',
        'form.personal.gender': 'Genre',
        'form.education.title': 'Données de Formation',
        'form.next': 'Suivant',
        'form.back': 'Retour',
        'form.submit': 'Terminer',
        'form.processing': 'Traitement de votre prédiction...',
        'result.title': 'Votre Salaire Estimé',
        'result.annual': 'Annuel',
        'result.new': 'Nouvelle Prédiction',
        'result.home': 'Retour à l\'Accueil'
    }
};

// Idioma actual
let currentLanguage = localStorage.getItem('language') || 'es';

// Función para cambiar idioma
function changeLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    applyTranslations();
}

// Aplicar traducciones
function applyTranslations() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[currentLanguage] && translations[currentLanguage][key]) {
            element.textContent = translations[currentLanguage][key];
        }
    });
}

// Inicializar selector de idioma
document.addEventListener('DOMContentLoaded', () => {
    const languageSelector = document.getElementById('languageSelector');
    if (languageSelector) {
        languageSelector.value = currentLanguage;
        languageSelector.addEventListener('change', (e) => {
            changeLanguage(e.target.value);
        });
    }
    applyTranslations();
});

// Variables del formulario
let currentStep = 1;
let formData = {};

// Funciones del formulario
function nextStep() {
    if (!validateStep(1)) {
        showErrors(1);
        return;
    }
    
    // Guardar datos del paso 1
    saveStepData(1);
    
    // Cambiar al paso 2
    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.remove('hidden');
    document.getElementById('progressBar').style.width = '100%';
    document.getElementById('currentStep').textContent = '2';
    currentStep = 2;
    
    // Scroll al inicio del formulario
    window.scrollTo({ top: 100, behavior: 'smooth' });
}

function previousStep() {
    // Guardar datos del paso 2
    saveStepData(2);
    
    // Cambiar al paso 1
    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step1').classList.remove('hidden');
    document.getElementById('progressBar').style.width = '50%';
    document.getElementById('currentStep').textContent = '1';
    currentStep = 1;
    
    // Scroll al inicio del formulario
    window.scrollTo({ top: 100, behavior: 'smooth' });
}

function validateStep(step) {
    const stepElement = document.getElementById(`step${step}`);
    const requiredFields = stepElement.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (field.type === 'radio') {
            const radioGroup = stepElement.querySelectorAll(`input[name="${field.name}"]`);
            const isChecked = Array.from(radioGroup).some(radio => radio.checked);
            if (!isChecked) {
                isValid = false;
            }
        } else if (!field.value) {
            isValid = false;
        }
    });
    
    return isValid;
}

function showErrors(step) {
    const stepElement = document.getElementById(`step${step}`);
    const requiredFields = stepElement.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        const errorMsg = field.parentElement.querySelector('.error-msg');
        
        if (field.type === 'radio') {
            const radioGroup = stepElement.querySelectorAll(`input[name="${field.name}"]`);
            const isChecked = Array.from(radioGroup).some(radio => radio.checked);
            if (!isChecked && errorMsg) {
                errorMsg.classList.remove('hidden');
            }
        } else if (!field.value) {
            if (errorMsg) {
                errorMsg.classList.remove('hidden');
            }
            field.classList.add('border-red-500');
        }
    });
}

function saveStepData(step) {
    const stepElement = document.getElementById(`step${step}`);
    const inputs = stepElement.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        if (input.type === 'radio') {
            if (input.checked) {
                formData[input.name] = input.value;
            }
        } else if (input.type === 'checkbox') {
            formData[input.name] = input.checked;
        } else {
            formData[input.name] = input.value;
        }
    });
    
    // Guardar en sessionStorage
    sessionStorage.setItem('formData', JSON.stringify(formData));
}

function loadFormData() {
    const savedData = sessionStorage.getItem('formData');
    if (savedData) {
        formData = JSON.parse(savedData);
        
        // Rellenar formulario con datos guardados
        Object.keys(formData).forEach(key => {
            const input = document.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'radio') {
                    const radio = document.querySelector(`[name="${key}"][value="${formData[key]}"]`);
                    if (radio) radio.checked = true;
                } else if (input.type === 'checkbox') {
                    input.checked = formData[key];
                } else {
                    input.value = formData[key];
                }
            }
        });
    }
}

function submitForm() {
    if (!validateStep(2)) {
        showErrors(2);
        return;
    }
    
    // Guardar datos del paso 2
    saveStepData(2);
    
    // Mostrar spinner
    document.getElementById('loadingSpinner').classList.remove('hidden');
    
    // Añadir form_id a los datos
    if (typeof formId !== 'undefined') {
        formData.form_id = formId;
    }
    
    // Enviar datos al servidor
    fetch('/api/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        // Limpiar datos guardados
        sessionStorage.removeItem('formData');
        
        // Redireccionar a resultados
        const resultFormId = data.form_id || formId || 'new';
        window.location.href = `/formulario/resultado/${resultFormId}`;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('loadingSpinner').classList.add('hidden');
        alert('Hubo un error al procesar tu predicción. Por favor, intenta de nuevo.');
    });
}

// Cargar datos guardados al iniciar
if (document.getElementById('predictionForm')) {
    document.addEventListener('DOMContentLoaded', loadFormData);
}

// Limpiar errores al escribir
document.addEventListener('input', (e) => {
    if (e.target.classList.contains('border-red-500')) {
        e.target.classList.remove('border-red-500');
    }
    const errorMsg = e.target.parentElement.querySelector('.error-msg');
    if (errorMsg) {
        errorMsg.classList.add('hidden');
    }
});
