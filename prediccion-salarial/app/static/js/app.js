// app.js - Frontend logic for salary prediction form

// ============================================================================
// TRANSLATIONS
// ============================================================================
const translations = {
    es: {
        // Navigation
        'nav.home': 'Inicio',
        'nav.info': 'Información',

        // Hero Section (Inicio)
        'hero.title': 'Predice tu Salario como Graduado',
        'hero.subtitle': 'Descubre cuánto podrías ganar basándonos en tu formación, experiencia y ubicación',
        'hero.start': 'Comenzar Predicción',
        'hero.more': 'Más Información',

        // Features (Inicio)
        'features.analysis.title': 'Análisis Inteligente',
        'features.analysis.desc': 'Algoritmo basado en datos reales del mercado laboral internacional',
        'features.global.title': 'Perspectiva Global',
        'features.global.desc': 'Compara tu perfil con graduados de todo el mundo',
        'features.instant.title': 'Resultados Instantáneos',
        'features.instant.desc': 'Obtén tu predicción salarial en menos de 2 minutos',

        // Stats (Inicio)
        'stats.predictions': 'Predicciones Realizadas',
        'stats.countries': 'Países Analizados',
        'stats.accuracy': 'Precisión Media',

        // Form
        'form.step': 'Paso',
        'form.of': 'de',
        'form.next': 'Siguiente',
        'form.previous': 'Anterior',
        'form.submit': 'Obtener Predicción',
        'form.required': 'Este campo es obligatorio',
        'form.select': 'Selecciona...',

        // Form Step 1
        'form.personal.title': 'Datos Personales',
        'form.personal.name': 'Nombre (Opcional)',
        'form.personal.age': 'Edad *',
        'form.personal.country': 'País *',
        'form.personal.gender': 'Género *',
        'form.personal.gender.male': 'Hombre',
        'form.personal.gender.female': 'Mujer',
        'form.personal.gender.other': 'Otro',

        // Form Step 2
        'form.education.title': 'Datos de Formación',
        'form.education.degree': 'Titulación *',
        'form.education.field': 'Campo de estudio *',
        'form.education.english': 'Nivel de inglés *',
        'form.education.ranking': 'Ranking Universidad *',
        'form.education.region': 'Región de estudios *',
        'form.education.grade': 'Nota Media (sobre 10) *',
        'form.education.internship': 'Realicé prácticas profesionales',

        // Education Degrees
        'degree.bachelor': 'Grado',
        'degree.master': 'Master',
        'degree.phd': 'PHD',
        'degree.fp': 'FP',

        // Fields of Study
        'field.arts': 'Artes',
        'field.engineering': 'Ingeniería',
        'field.it': 'IT',
        'field.health': 'Salud',
        'field.social': 'Ciencias Sociales',
        'field.business': 'Empresa',

        // English Levels
        'english.basic': 'Básico',
        'english.intermediate': 'Intermedio',
        'english.advanced': 'Avanzado',
        'english.fluent': 'Fluido',

        // University Ranking
        'ranking.high': 'Alto',
        'ranking.medium': 'Medio',
        'ranking.low': 'Bajo',

        // Regions
        'region.usa': 'USA',
        'region.europe': 'Europa',
        'region.australia': 'Australia',

        // Results
        'result.title': 'Tu Salario Estimado',
        'result.annual': 'Anual',
        'result.confidence': 'Confianza',
        'result.range': 'Rango',
        'result.new': 'Nueva Predicción',
        'result.home': 'Volver al Inicio',
        'result.filters': 'Filtrar comparaciones por:',
        'result.filter.apply': 'Aplicar Filtros',
        'result.filter.allCountries': 'Todos los países',
        'result.filter.allGenders': 'Todos los géneros',
        'result.filter.allEducation': 'Toda formación',
        'result.filter.allFields': 'Todos los campos',

        // Comparison Charts
        'chart.age.title': 'Edad',
        'chart.age.yours': 'Tu edad',
        'chart.age.average': 'Media (con filtros aplicados)',
        'chart.country.title': 'País',
        'chart.country.yours': 'Tu país',
        'chart.country.average': 'Salario medio en',
        'chart.education.title': 'Formación',
        'chart.education.yours': 'Tu nivel',
        'chart.education.average': 'Salario medio',
        'chart.field.title': 'Campo de Estudio',
        'chart.field.yours': 'Tu campo',
        'chart.field.comparison': 'Comparación por género (con filtros)',
        'chart.field.male': 'Hombre',
        'chart.field.female': 'Mujer',
        'chart.grade.title': 'Nota Media',
        'chart.grade.yours': 'Tu nota',
        'chart.grade.average': 'Media (con filtros aplicados)',
        'chart.countries.title': 'Comparación de Salarios por País',
        'chart.countries.subtitle': 'Salarios promedio calculados con el perfil actual + filtros aplicados',

        // Loading
        'loading.processing': 'Procesando tu predicción...',
        'loading.calculating': 'Calculando...',

        // Errors
        'error.fillRequired': 'Por favor, completa todos los campos requeridos del paso',
        'error.predictionFailed': 'Hubo un error al procesar tu predicción.',

        // Notifications
        'notification.filtersApplied': 'Filtros aplicados correctamente',
        'notification.filtersError': 'Error al aplicar filtros',

        // Countries
        'country.brasil': '🇧🇷 Brasil',
        'country.china': '🇨🇳 China',
        'country.espana': '🇪🇸 España',
        'country.pakistan': '🇵🇰 Pakistán',
        'country.usa': '🇺🇸 USA',
        'country.india': '🇮🇳 India',
        'country.vietnam': '🇻🇳 Vietnam',
        'country.nigeria': '🇳🇬 Nigeria',

        // Info Page
        'info.title': 'Cómo Funciona Realmente Nuestro Modelo',
        'info.factors.title': 'Factores que Influyen en la Predicción',
        'info.factor.education.title': 'Formación Académica (90%)',
        'info.factor.education.desc': 'Este es el factor dominante. Casi el 85% de la predicción se basa en el Nivel de Estudios (Doctorado o Máster). El ranking universitario y el campo de estudio tienen un impacto menor.',
        'info.factor.skills.title': 'Competencias (5%)',
        'info.factor.skills.desc': 'La nota media (GPA) es el segundo factor individual más importante (casi 3%), seguido por el nivel de idioma (1.2%).',
        'info.factor.experience.title': 'Experiencia (2.5%)',
        'info.factor.experience.desc': 'Los años desde la graduación y la realización de prácticas tienen un impacto leve en la predicción de este modelo.',
        'info.factor.location.title': 'Ubicación Geográfica (1.5%)',
        'info.factor.location.desc': 'El país de origen y la región donde estudiaste. Tienen una influencia muy baja en el resultado.',
        'info.factor.demographics.title': 'Datos Demográficos (1.5%)',
        'info.factor.demographics.desc': 'La edad y el género del graduado también son considerados por el modelo, aunque con un impacto bajo.',
        'info.methodology.title': 'Metodología',
        'info.methodology.text': 'Nuestro modelo utiliza técnicas de aprendizaje automático entrenadas con datos de más de 300,000 graduados internacionales. El algoritmo considera múltiples variables y sus interacciones para proporcionar una estimación precisa.',
        'info.methodology.note': '<strong>Nota:</strong> Las predicciones son estimaciones basadas en los datos de entrenamiento y no garantizan salarios específicos. Como has visto, este modelo prioriza enormemente el nivel educativo por encima de todos los demás factores.',
        'info.start': 'Comenzar Predicción',

        // Error Page
        'error.404.title': 'Página no encontrada',
        'error.404.message': 'La página que buscas no existe o ha sido movida.',
        'error.500.title': 'Error del servidor',
        'error.500.message': 'Hubo un problema con nuestro servidor. Por favor, intenta de nuevo más tarde.',
        'error.timeout.title': 'Tiempo de espera agotado',
        'error.timeout.message': 'La solicitud tardó demasiado tiempo. Por favor, verifica tu conexión e intenta de nuevo.',
        'error.offline.title': 'Sin conexión',
        'error.offline.message': 'Parece que no tienes conexión a internet. Verifica tu conexión e intenta de nuevo.',
        'error.generic.title': 'Algo salió mal',
        'error.code': 'Código de error:',
        'error.home': 'Volver al Inicio',

        // History Sidebar
        'history.title': 'Historial de Predicciones',
        'history.button': 'Historial',
        'history.empty': 'No hay predicciones guardadas',
        'history.view': 'Ver',
        'history.delete': 'Eliminar',
        'history.clear': 'Limpiar todo',
        'history.prediction': 'Predicción',
        'history.date': 'Fecha'
    },
    en: {
        // Navigation
        'nav.home': 'Home',
        'nav.info': 'Information',

        // Hero Section
        'hero.title': 'Predict Your Salary as a Graduate',
        'hero.subtitle': 'Discover how much you could earn based on your education, experience, and location',
        'hero.start': 'Start Prediction',
        'hero.more': 'More Information',

        // Features
        'features.analysis.title': 'Intelligent Analysis',
        'features.analysis.desc': 'Algorithm based on real international labor market data',
        'features.global.title': 'Global Perspective',
        'features.global.desc': 'Compare your profile with graduates from around the world',
        'features.instant.title': 'Instant Results',
        'features.instant.desc': 'Get your salary prediction in less than 2 minutes',

        // Stats
        'stats.predictions': 'Predictions Made',
        'stats.countries': 'Countries Analyzed',
        'stats.accuracy': 'Average Accuracy',

        // Form
        'form.step': 'Step',
        'form.of': 'of',
        'form.next': 'Next',
        'form.previous': 'Previous',
        'form.submit': 'Get Prediction',
        'form.required': 'This field is required',
        'form.select': 'Select...',

        // Form Step 1
        'form.personal.title': 'Personal Information',
        'form.personal.name': 'Name (Optional)',
        'form.personal.age': 'Age *',
        'form.personal.country': 'Country *',
        'form.personal.gender': 'Gender *',
        'form.personal.gender.male': 'Male',
        'form.personal.gender.female': 'Female',
        'form.personal.gender.other': 'Other',

        // Form Step 2
        'form.education.title': 'Education Information',
        'form.education.degree': 'Degree *',
        'form.education.field': 'Field of Study *',
        'form.education.english': 'English Level *',
        'form.education.ranking': 'University Ranking *',
        'form.education.region': 'Study Region *',
        'form.education.grade': 'GPA (out of 10) *',
        'form.education.internship': 'I completed professional internships',

        // Education Degrees
        'degree.bachelor': 'Bachelor',
        'degree.master': 'Master',
        'degree.phd': 'PhD',
        'degree.fp': 'Vocational Training',

        // Fields of Study
        'field.arts': 'Arts',
        'field.engineering': 'Engineering',
        'field.it': 'IT',
        'field.health': 'Health',
        'field.social': 'Social Sciences',
        'field.business': 'Business',

        // English Levels
        'english.basic': 'Basic',
        'english.intermediate': 'Intermediate',
        'english.advanced': 'Advanced',
        'english.fluent': 'Fluent',

        // University Ranking
        'ranking.high': 'High',
        'ranking.medium': 'Medium',
        'ranking.low': 'Low',

        // Regions
        'region.usa': 'USA',
        'region.europe': 'Europe',
        'region.australia': 'Australia',

        // Results
        'result.title': 'Your Estimated Salary',
        'result.annual': 'Annual',
        'result.confidence': 'Confidence',
        'result.range': 'Range',
        'result.new': 'New Prediction',
        'result.home': 'Back to Home',
        'result.filters': 'Filter comparisons by:',
        'result.filter.apply': 'Apply Filters',
        'result.filter.allCountries': 'All countries',
        'result.filter.allGenders': 'All genders',
        'result.filter.allEducation': 'All education',
        'result.filter.allFields': 'All fields',

        // Comparison Charts
        'chart.age.title': 'Age',
        'chart.age.yours': 'Your age',
        'chart.age.average': 'Average (with applied filters)',
        'chart.country.title': 'Country',
        'chart.country.yours': 'Your country',
        'chart.country.average': 'Average salary in',
        'chart.education.title': 'Education',
        'chart.education.yours': 'Your level',
        'chart.education.average': 'Average salary',
        'chart.field.title': 'Field of Study',
        'chart.field.yours': 'Your field',
        'chart.field.comparison': 'Gender comparison (with filters)',
        'chart.field.male': 'Male',
        'chart.field.female': 'Female',
        'chart.grade.title': 'Grade Average',
        'chart.grade.yours': 'Your grade',
        'chart.grade.average': 'Average (with applied filters)',
        'chart.countries.title': 'Salary Comparison by Country',
        'chart.countries.subtitle': 'Average salaries calculated with current profile + applied filters',

        // Loading
        'loading.processing': 'Processing your prediction...',
        'loading.calculating': 'Calculating...',

        // Errors
        'error.fillRequired': 'Please complete all required fields in step',
        'error.predictionFailed': 'There was an error processing your prediction.',

        // Notifications
        'notification.filtersApplied': 'Filters applied successfully',
        'notification.filtersError': 'Error applying filters',

        // Countries
        'country.brasil': '🇧🇷 Brazil',
        'country.china': '🇨🇳 China',
        'country.espana': '🇪🇸 Spain',
        'country.pakistan': '🇵🇰 Pakistan',
        'country.usa': '🇺🇸 USA',
        'country.india': '🇮🇳 India',
        'country.vietnam': '🇻🇳 Vietnam',
        'country.nigeria': '🇳🇬 Nigeria',

        // Info Page
        'info.title': 'How Our Model Really Works',
        'info.factors.title': 'Factors Influencing the Prediction',
        'info.factor.education.title': 'Academic Background (90%)',
        'info.factor.education.desc': 'This is the dominant factor. Almost 85% of the prediction is based on the Level of Studies (PhD or Master\'s). University ranking and field of study have a smaller impact.',
        'info.factor.skills.title': 'Skills (5%)',
        'info.factor.skills.desc': 'GPA is the second most important individual factor (almost 3%), followed by language level (1.2%).',
        'info.factor.experience.title': 'Experience (2.5%)',
        'info.factor.experience.desc': 'Years since graduation and completion of internships have a slight impact on this model\'s prediction.',
        'info.factor.location.title': 'Geographic Location (1.5%)',
        'info.factor.location.desc': 'Country of origin and region where you studied. They have a very low influence on the result.',
        'info.factor.demographics.title': 'Demographics (1.5%)',
        'info.factor.demographics.desc': 'Age and gender of the graduate are also considered by the model, although with a low impact.',
        'info.methodology.title': 'Methodology',
        'info.methodology.text': 'Our model uses machine learning techniques trained with data from over 300,000 international graduates. The algorithm considers multiple variables and their interactions to provide an accurate estimate.',
        'info.methodology.note': '<strong>Note:</strong> Predictions are estimates based on training data and do not guarantee specific salaries. As you can see, this model heavily prioritizes educational level above all other factors.',
        'info.start': 'Start Prediction',

        // Error Page
        'error.404.title': 'Page not found',
        'error.404.message': 'The page you are looking for does not exist or has been moved.',
        'error.500.title': 'Server error',
        'error.500.message': 'There was a problem with our server. Please try again later.',
        'error.timeout.title': 'Request timeout',
        'error.timeout.message': 'The request took too long. Please check your connection and try again.',
        'error.offline.title': 'No connection',
        'error.offline.message': 'It seems you have no internet connection. Check your connection and try again.',
        'error.generic.title': 'Something went wrong',
        'error.code': 'Error code:',
        'error.home': 'Back to Home',

        // History Sidebar
        'history.title': 'Prediction History',
        'history.button': 'History',
        'history.empty': 'No saved predictions',
        'history.view': 'View',
        'history.delete': 'Delete',
        'history.clear': 'Clear all',
        'history.prediction': 'Prediction',
        'history.date': 'Date'
    },
    fr: {
        // Navigation
        'nav.home': 'Accueil',
        'nav.info': 'Information',

        // Hero Section
        'hero.title': 'Prédisez Votre Salaire en tant que Diplômé',
        'hero.subtitle': 'Découvrez combien vous pourriez gagner en fonction de votre formation, expérience et localisation',
        'hero.start': 'Commencer la Prédiction',
        'hero.more': 'Plus d\'Information',

        // Features
        'features.analysis.title': 'Analyse Intelligente',
        'features.analysis.desc': 'Algorithme basé sur des données réelles du marché du travail international',
        'features.global.title': 'Perspective Mondiale',
        'features.global.desc': 'Comparez votre profil avec des diplômés du monde entier',
        'features.instant.title': 'Résultats Instantanés',
        'features.instant.desc': 'Obtenez votre prédiction salariale en moins de 2 minutes',

        // Stats
        'stats.predictions': 'Prédictions Réalisées',
        'stats.countries': 'Pays Analysés',
        'stats.accuracy': 'Précision Moyenne',

        // Form
        'form.step': 'Étape',
        'form.of': 'de',
        'form.next': 'Suivant',
        'form.previous': 'Précédent',
        'form.submit': 'Obtenir la Prédiction',
        'form.required': 'Ce champ est obligatoire',
        'form.select': 'Sélectionnez...',

        // Form Step 1
        'form.personal.title': 'Informations Personnelles',
        'form.personal.name': 'Nom (Optionnel)',
        'form.personal.age': 'Âge *',
        'form.personal.country': 'Pays *',
        'form.personal.gender': 'Genre *',
        'form.personal.gender.male': 'Homme',
        'form.personal.gender.female': 'Femme',
        'form.personal.gender.other': 'Autre',

        // Form Step 2
        'form.education.title': 'Informations sur la Formation',
        'form.education.degree': 'Diplôme *',
        'form.education.field': 'Domaine d\'études *',
        'form.education.english': 'Niveau d\'anglais *',
        'form.education.ranking': 'Classement de l\'Université *',
        'form.education.region': 'Région d\'études *',
        'form.education.grade': 'Note Moyenne (sur 10) *',
        'form.education.internship': 'J\'ai effectué des stages professionnels',

        // Education Degrees
        'degree.bachelor': 'Licence',
        'degree.master': 'Master',
        'degree.phd': 'Doctorat',
        'degree.fp': 'Formation Professionnelle',

        // Fields of Study
        'field.arts': 'Arts',
        'field.engineering': 'Ingénierie',
        'field.it': 'Informatique',
        'field.health': 'Santé',
        'field.social': 'Sciences Sociales',
        'field.business': 'Commerce',

        // English Levels
        'english.basic': 'Basique',
        'english.intermediate': 'Intermédiaire',
        'english.advanced': 'Avancé',
        'english.fluent': 'Courant',

        // University Ranking
        'ranking.high': 'Élevé',
        'ranking.medium': 'Moyen',
        'ranking.low': 'Faible',

        // Regions
        'region.usa': 'USA',
        'region.europe': 'Europe',
        'region.australia': 'Australie',

        // Results
        'result.title': 'Votre Salaire Estimé',
        'result.annual': 'Annuel',
        'result.confidence': 'Confiance',
        'result.range': 'Fourchette',
        'result.new': 'Nouvelle Prédiction',
        'result.home': 'Retour à l\'Accueil',
        'result.filters': 'Filtrer les comparaisons par:',
        'result.filter.apply': 'Appliquer les Filtres',
        'result.filter.allCountries': 'Tous les pays',
        'result.filter.allGenders': 'Tous les genres',
        'result.filter.allEducation': 'Toute formation',
        'result.filter.allFields': 'Tous les domaines',

        // Comparison Charts
        'chart.age.title': 'Âge',
        'chart.age.yours': 'Votre âge',
        'chart.age.average': 'Moyenne (avec filtres appliqués)',
        'chart.country.title': 'Pays',
        'chart.country.yours': 'Votre pays',
        'chart.country.average': 'Salaire moyen en',
        'chart.education.title': 'Formation',
        'chart.education.yours': 'Votre niveau',
        'chart.education.average': 'Salaire moyen',
        'chart.field.title': 'Domaine d\'Études',
        'chart.field.yours': 'Votre domaine',
        'chart.field.comparison': 'Comparaison par genre (avec filtres)',
        'chart.field.male': 'Homme',
        'chart.field.female': 'Femme',
        'chart.grade.title': 'Note Moyenne',
        'chart.grade.yours': 'Votre note',
        'chart.grade.average': 'Moyenne (avec filtres appliqués)',
        'chart.countries.title': 'Comparaison des Salaires par Pays',
        'chart.countries.subtitle': 'Salaires moyens calculés avec le profil actuel + filtres appliqués',

        // Loading
        'loading.processing': 'Traitement de votre prédiction...',
        'loading.calculating': 'Calcul en cours...',

        // Errors
        'error.fillRequired': 'Veuillez remplir tous les champs requis de l\'étape',
        'error.predictionFailed': 'Une erreur s\'est produite lors du traitement de votre prédiction.',

        // Notifications
        'notification.filtersApplied': 'Filtres appliqués avec succès',
        'notification.filtersError': 'Erreur lors de l\'application des filtres',

        // Countries
        'country.brasil': '🇧🇷 Brésil',
        'country.china': '🇨🇳 Chine',
        'country.espana': '🇪🇸 Espagne',
        'country.pakistan': '🇵🇰 Pakistan',
        'country.usa': '🇺🇸 USA',
        'country.india': '🇮🇳 Inde',
        'country.vietnam': '🇻🇳 Vietnam',
        'country.nigeria': '🇳🇬 Nigeria',

        // Info Page
        'info.title': 'Comment Fonctionne Réellement Notre Modèle',
        'info.factors.title': 'Facteurs Influençant la Prédiction',
        'info.factor.education.title': 'Formation Académique (90%)',
        'info.factor.education.desc': 'C\'est le facteur dominant. Près de 85% de la prédiction est basée sur le Niveau d\'Études (Doctorat ou Master). Le classement universitaire et le domaine d\'étude ont un impact moindre.',
        'info.factor.skills.title': 'Compétences (5%)',
        'info.factor.skills.desc': 'La moyenne générale (GPA) est le deuxième facteur individuel le plus important (près de 3%), suivi du niveau de langue (1.2%).',
        'info.factor.experience.title': 'Expérience (2.5%)',
        'info.factor.experience.desc': 'Les années depuis l\'obtention du diplôme et la réalisation de stages ont un impact léger sur la prédiction de ce modèle.',
        'info.factor.location.title': 'Localisation Géographique (1.5%)',
        'info.factor.location.desc': 'Pays d\'origine et région où vous avez étudié. Ils ont une influence très faible sur le résultat.',
        'info.factor.demographics.title': 'Données Démographiques (1.5%)',
        'info.factor.demographics.desc': 'L\'âge et le sexe du diplômé sont également pris en compte par le modèle, bien qu\'avec un faible impact.',
        'info.methodology.title': 'Méthodologie',
        'info.methodology.text': 'Notre modèle utilise des techniques d\'apprentissage automatique entraînées avec des données de plus de 300 000 diplômés internationaux. L\'algorithme considère plusieurs variables et leurs interactions pour fournir une estimation précise.',
        'info.methodology.note': '<strong>Note:</strong> Les prédictions sont des estimations basées sur les données d\'entraînement et ne garantissent pas de salaires spécifiques. Comme vous pouvez le voir, ce modèle priorise énormément le niveau éducatif par rapport à tous les autres facteurs.',
        'info.start': 'Commencer la Prédiction',

        // Error Page
        'error.404.title': 'Page non trouvée',
        'error.404.message': 'La page que vous recherchez n\'existe pas ou a été déplacée.',
        'error.500.title': 'Erreur du serveur',
        'error.500.message': 'Il y a eu un problème avec notre serveur. Veuillez réessayer plus tard.',
        'error.timeout.title': 'Délai d\'attente dépassé',
        'error.timeout.message': 'La requête a pris trop de temps. Veuillez vérifier votre connexion et réessayer.',
        'error.offline.title': 'Pas de connexion',
        'error.offline.message': 'Il semble que vous n\'ayez pas de connexion Internet. Vérifiez votre connexion et réessayez.',
        'error.generic.title': 'Quelque chose s\'est mal passé',
        'error.code': 'Code d\'erreur:',
        'error.home': 'Retour à l\'Accueil',

        // History Sidebar
        'history.title': 'Historique des Prédictions',
        'history.button': 'Historique',
        'history.empty': 'Aucune prédiction enregistrée',
        'history.view': 'Voir',
        'history.delete': 'Supprimer',
        'history.clear': 'Tout effacer',
        'history.prediction': 'Prédiction',
        'history.date': 'Date'
    }
};

let currentLang = 'es';

function changeLanguage(lang) {
    currentLang = lang;

    // Manejar traducciones de texto normal
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });

    // Manejar traducciones con HTML
    document.querySelectorAll('[data-i18n-html]').forEach(element => {
        const key = element.getAttribute('data-i18n-html');
        if (translations[lang] && translations[lang][key]) {
            element.innerHTML = translations[lang][key];
        }
    });
}

// ============================================================================
// CURRENCY CONVERSION
// ============================================================================

// Exchange rates (base: USD = 1.0)
const exchangeRates = {
    USD: 1.0,
    EUR: 0.92,    // 1 USD = 0.92 EUR
    GBP: 0.79     // 1 USD = 0.79 GBP
};

const currencySymbols = {
    USD: '$',
    EUR: '€',
    GBP: '£'
};

let currentCurrency = 'USD';

function convertCurrency(amountUSD, targetCurrency) {
    return amountUSD * exchangeRates[targetCurrency];
}

function formatCurrency(amount, currency) {
    const symbol = currencySymbols[currency];
    const convertedAmount = convertCurrency(amount, currency);

    // Format with proper thousands separator and 0 decimals
    const formatted = Math.round(convertedAmount).toLocaleString('en-US');

    // EUR and GBP typically have symbol after the number in some locales,
    // but for consistency we'll use symbol before
    return `${symbol}${formatted}`;
}

function changeCurrency(currency) {
    currentCurrency = currency;

    // Update all salary displays
    document.querySelectorAll('[data-salary]').forEach(element => {
        const salaryUSD = parseFloat(element.getAttribute('data-salary'));
        element.textContent = formatCurrency(salaryUSD, currency);
    });

    // Trigger chart updates if we're on the results page
    if (typeof updateChartsWithCurrency === 'function') {
        updateChartsWithCurrency(currency);
    }
}

// ============================================================================
// FORM LOGIC
// ============================================================================

let currentStep = 1;
let formData = {};

function nextStep() {
    console.log('Intentando ir al siguiente paso...');
    if (!validateStep(1)) {
        console.log('Validación del paso 1 falló');
        showErrors(1);
        return;
    }

    console.log('Validación del paso 1 exitosa');
    saveStepData(1);

    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.remove('hidden');
    document.getElementById('progressBar').style.width = '100%';
    document.getElementById('currentStep').textContent = '2';
    currentStep = 2;

    window.scrollTo({ top: 100, behavior: 'smooth' });
}

function previousStep() {
    saveStepData(2);

    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step1').classList.remove('hidden');
    document.getElementById('progressBar').style.width = '50%';
    document.getElementById('currentStep').textContent = '1';
    currentStep = 1;

    window.scrollTo({ top: 100, behavior: 'smooth' });
}

function validateStep(step) {
    console.log('Validando paso', step);
    const stepElement = document.getElementById('step' + step);
    if (!stepElement) {
        console.error('No se encontró el elemento step' + step);
        return false;
    }

    const requiredFields = stepElement.querySelectorAll('[required]');
    let isValid = true;

    console.log('Campos requeridos encontrados:', requiredFields.length);

    requiredFields.forEach(field => {
        if (field.type === 'radio') {
            const radioGroup = stepElement.querySelectorAll('input[name="' + field.name + '"]');
            const isChecked = Array.from(radioGroup).some(radio => radio.checked);
            console.log('Radio ' + field.name + ': ' + (isChecked ? 'OK' : 'FALTA'));
            if (!isChecked) {
                isValid = false;
            }
        } else if (!field.value || field.value === '') {
            console.log('Campo ' + field.name + ': FALTA (valor: "' + field.value + '")');
            isValid = false;
        } else {
            console.log('Campo ' + field.name + ': OK (valor: "' + field.value + '")');
        }
    });

    console.log('Resultado validación:', isValid);
    return isValid;
}

function showErrors(step) {
    const stepElement = document.getElementById('step' + step);
    const requiredFields = stepElement.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        const errorMsg = field.parentElement.querySelector('.error-msg');

        if (field.type === 'radio') {
            const radioGroup = stepElement.querySelectorAll('input[name="' + field.name + '"]');
            const isChecked = Array.from(radioGroup).some(radio => radio.checked);
            if (!isChecked && errorMsg) {
                errorMsg.classList.remove('hidden');
            }
        } else if (!field.value || field.value === '') {
            if (errorMsg) {
                errorMsg.classList.remove('hidden');
            }
            field.classList.add('border-red-500');
        }
    });

    const errorMessage = (translations[currentLang]['error.fillRequired'] || 'Por favor, completa todos los campos requeridos del paso') + ' ' + step;
    alert(errorMessage);
}

function saveStepData(step) {
    console.log('Guardando datos del paso', step);
    const stepElement = document.getElementById('step' + step);
    const inputs = stepElement.querySelectorAll('input, select');

    inputs.forEach(input => {
        if (input.type === 'radio') {
            if (input.checked) {
                formData[input.name] = input.value;
            }
        } else if (input.type === 'checkbox') {
            formData[input.name] = input.checked;
        } else if (input.value) {
            formData[input.name] = input.value;
        }
    });

    sessionStorage.setItem('formData', JSON.stringify(formData));
    console.log('Datos guardados:', formData);
}

function loadFormData() {
    const savedData = sessionStorage.getItem('formData');
    if (savedData) {
        formData = JSON.parse(savedData);

        Object.keys(formData).forEach(key => {
            const input = document.querySelector('[name="' + key + '"]');
            if (input) {
                if (input.type === 'radio') {
                    const radio = document.querySelector('[name="' + key + '"][value="' + formData[key] + '"]');
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
    console.log('Enviando formulario...');
    if (!validateStep(2)) {
        console.log('Validación del paso 2 falló');
        showErrors(2);
        return;
    }

    console.log('Validación del paso 2 exitosa');
    saveStepData(2);

    document.getElementById('loadingSpinner').classList.remove('hidden');

    if (typeof formId !== 'undefined') {
        formData.form_id = formId;
    }

    console.log('Datos a enviar:', formData);

    fetch('/api/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        console.log('Respuesta recibida, status:', response.status);
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(JSON.stringify(err));
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Predicción exitosa:', data);

        // Guardar en el historial
        if (typeof savePredictionToHistory === 'function') {
            const historyEntry = {
                form_id: data.form_id || formId || 'new',
                salary: data.salary || 0,
                nombre: formData.nombre || '',
                pais: formData.pais || '',
                campoEstudio: formData.campoEstudio || '',
                edad: formData.edad || ''
            };
            savePredictionToHistory(historyEntry);
        }

        sessionStorage.removeItem('formData');

        const resultFormId = data.form_id || formId || 'new';
        window.location.href = '/formulario/resultado/' + resultFormId;
    })
    .catch(error => {
        console.error('Error completo:', error);
        document.getElementById('loadingSpinner').classList.add('hidden');

        let errorMsg = translations[currentLang]['error.predictionFailed'] || 'Hubo un error al procesar tu predicción.';
        try {
            const errorData = JSON.parse(error.message);
            console.error('Detalles del error:', errorData);
            if (errorData.details) {
                errorMsg += '\n\nDetalles: ' + JSON.stringify(errorData.details, null, 2);
            }
        } catch (e) {
            errorMsg += '\n\n' + error.message;
        }

        alert(errorMsg);
    });
}

// Load form data on page load
if (document.getElementById('predictionForm')) {
    document.addEventListener('DOMContentLoaded', loadFormData);
}

// Clear errors on input
document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('border-red-500');
            const errorMsg = this.parentElement.querySelector('.error-msg');
            if (errorMsg) {
                errorMsg.classList.add('hidden');
            }
        });

        input.addEventListener('change', function() {
            this.classList.remove('border-red-500');
            const errorMsg = this.parentElement.querySelector('.error-msg');
            if (errorMsg) {
                errorMsg.classList.add('hidden');
            }
        });
    });

    // Language Selector
    const languageSelector = document.getElementById('languageSelector');
    if (languageSelector) {
        // Recuperar idioma guardado o usar 'es' por defecto
        const savedLang = localStorage.getItem('selectedLanguage') || 'es';
        currentLang = savedLang;
        languageSelector.value = savedLang;
        changeLanguage(savedLang);

        languageSelector.addEventListener('change', function() {
            const selectedLang = this.value;
            localStorage.setItem('selectedLanguage', selectedLang);
            changeLanguage(selectedLang);

            // Actualizar historial si el sidebar está abierto
            const sidebar = document.getElementById('historySidebar');
            if (sidebar && sidebar.classList.contains('open')) {
                loadHistory();
            }
        });
    }

    // Currency Selector (Global - en base.html)
    const globalCurrencySelector = document.getElementById('currencySelector');
    if (globalCurrencySelector) {
        // Recuperar moneda guardada o usar 'USD' por defecto
        const savedCurrency = localStorage.getItem('selectedCurrency') || 'USD';
        currentCurrency = savedCurrency;
        globalCurrencySelector.value = savedCurrency;

        // Aplicar moneda guardada si estamos en la página de resultados
        if (typeof updateChartsWithCurrency === 'function') {
            updateChartsWithCurrency(savedCurrency);
        }

        globalCurrencySelector.addEventListener('change', function() {
            const selectedCurrency = this.value;
            localStorage.setItem('selectedCurrency', selectedCurrency);
            changeCurrency(selectedCurrency);

            // Actualizar historial si el sidebar está abierto
            const sidebar = document.getElementById('historySidebar');
            if (sidebar && sidebar.classList.contains('open')) {
                loadHistory();
            }
        });
    }

    // ============================================================================
    // HISTORY SIDEBAR
    // ============================================================================

    const historySidebar = document.getElementById('historySidebar');
    const historyToggle = document.getElementById('historyToggle');
    const sidebarHistoryButton = document.getElementById('sidebarHistoryButton');
    const closeSidebar = document.getElementById('closeSidebar');
    const clearHistoryBtn = document.getElementById('clearHistory');

    // Función para abrir el sidebar
    function openHistorySidebar() {
        if (historySidebar && historyToggle && sidebarHistoryButton) {
            // Abrir sidebar
            historySidebar.classList.add('open');

            // Ocultar botón del header con animación
            historyToggle.style.opacity = '0';
            historyToggle.style.transform = 'translateX(-20px)';

            // Mostrar botón en el sidebar con delay
            setTimeout(() => {
                sidebarHistoryButton.style.opacity = '1';
            }, 150);

            loadHistory();
        }
    }

    // Función para cerrar el sidebar
    function closeHistorySidebar() {
        if (historySidebar && historyToggle && sidebarHistoryButton) {
            // Ocultar botón del sidebar
            sidebarHistoryButton.style.opacity = '0';

            // Cerrar sidebar
            historySidebar.classList.remove('open');

            // Mostrar botón del header con delay
            setTimeout(() => {
                historyToggle.style.opacity = '1';
                historyToggle.style.transform = 'translateX(0)';
            }, 150);
        }
    }

    // Event listeners para abrir/cerrar
    if (historyToggle) {
        historyToggle.addEventListener('click', openHistorySidebar);
    }

    if (closeSidebar) {
        closeSidebar.addEventListener('click', closeHistorySidebar);
    }

    // Mapeo de valores a claves de traducción
    const countryTranslationMap = {
        'Brasil': 'country.brasil',
        'Brazil': 'country.brasil',
        'China': 'country.china',
        'España': 'country.espana',
        'Spain': 'country.espana',
        'Pakistán': 'country.pakistan',
        'Pakistan': 'country.pakistan',
        'USA': 'country.usa',
        'India': 'country.india',
        'Vietnam': 'country.vietnam',
        'Nigeria': 'country.nigeria'
    };

    const fieldTranslationMap = {
        'Artes': 'field.arts',
        'Arts': 'field.arts',
        'Ing': 'field.engineering',
        'Ingeniería': 'field.engineering',
        'Engineering': 'field.engineering',
        'IT': 'field.it',
        'Salud': 'field.health',
        'Health': 'field.health',
        'S.Sociales': 'field.social',
        'Ciencias Sociales': 'field.social',
        'Social Sciences': 'field.social',
        'Empresa': 'field.business',
        'Business': 'field.business',
        'Commerce': 'field.business'
    };

    // Función para obtener traducción de país
    function getTranslatedCountry(country) {
        const key = countryTranslationMap[country];
        return key && translations[currentLang] ? translations[currentLang][key] : country;
    }

    // Función para obtener traducción de campo
    function getTranslatedField(field) {
        const key = fieldTranslationMap[field];
        return key && translations[currentLang] ? translations[currentLang][key] : field;
    }

    // Función para cargar el historial
    function loadHistory() {
        const historyList = document.getElementById('historyList');
        const emptyHistory = document.getElementById('emptyHistory');

        if (!historyList) return;

        // Obtener historial del localStorage
        const history = JSON.parse(localStorage.getItem('predictionHistory') || '[]');

        if (history.length === 0) {
            if (emptyHistory) emptyHistory.classList.remove('hidden');
            return;
        }

        if (emptyHistory) emptyHistory.classList.add('hidden');

        // Limpiar lista actual
        historyList.innerHTML = '';

        // Renderizar cada predicción (más reciente primero)
        history.reverse().forEach((prediction, index) => {
            const card = document.createElement('div');
            card.className = 'bg-white rounded-lg p-4 border-2 border-gray-100 hover:border-blue-300 hover:shadow-md transition-all duration-200 group';

            const date = new Date(prediction.timestamp);
            const formattedDate = date.toLocaleDateString(currentLang, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            const salaryFormatted = formatCurrency(prediction.salary, currentCurrency);

            card.innerHTML = `
                <div class="flex justify-between items-start mb-3">
                    <div class="flex-1">
                        <div class="font-bold text-xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                            ${salaryFormatted}
                        </div>
                        <div class="text-xs text-gray-400 mt-1 flex items-center gap-1">
                            <span>🕒</span>
                            <span>${formattedDate}</span>
                        </div>
                    </div>
                    <button onclick="deleteHistoryItem(${history.length - 1 - index})"
                            class="text-gray-300 hover:text-red-500 hover:bg-red-50 p-2 rounded-lg transition-all duration-200"
                            title="${translations[currentLang]['history.delete'] || 'Eliminar'}">
                        <span class="text-xl">🗑️</span>
                    </button>
                </div>

                <div class="space-y-1 mb-3 text-sm">
                    ${prediction.nombre ? `
                        <div class="flex items-center gap-2 text-gray-700">
                            <span class="text-blue-500">👤</span>
                            <span class="font-medium">${prediction.nombre}</span>
                        </div>
                    ` : ''}
                    <div class="flex items-center gap-2 text-gray-600">
                        <span>🌍</span>
                        <span>${getTranslatedCountry(prediction.pais)}</span>
                    </div>
                    <div class="flex items-center gap-2 text-gray-600">
                        <span>📚</span>
                        <span>${getTranslatedField(prediction.campoEstudio)}</span>
                    </div>
                </div>

                <a href="/formulario/resultado/${prediction.form_id}"
                   class="block w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white text-center py-2.5 rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all shadow-sm hover:shadow-md text-sm font-semibold group-hover:scale-[1.02] transform duration-200">
                    ${translations[currentLang] && translations[currentLang]['history.view'] ? translations[currentLang]['history.view'] : 'Ver'} →
                </a>
            `;

            historyList.appendChild(card);
        });
    }

    // Función para eliminar un elemento del historial
    window.deleteHistoryItem = function(index) {
        const history = JSON.parse(localStorage.getItem('predictionHistory') || '[]');
        history.splice(index, 1);
        localStorage.setItem('predictionHistory', JSON.stringify(history));
        loadHistory();
    };

    // Limpiar todo el historial
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', function() {
            if (confirm(translations[currentLang]['history.clear'] + '?')) {
                localStorage.removeItem('predictionHistory');
                loadHistory();
            }
        });
    }

    // Guardar predicción en el historial (llamar después de obtener predicción)
    window.savePredictionToHistory = function(predictionData) {
        const history = JSON.parse(localStorage.getItem('predictionHistory') || '[]');

        // Agregar timestamp y datos relevantes
        const entry = {
            timestamp: Date.now(),
            form_id: predictionData.form_id || 'unknown',
            salary: predictionData.salary,
            nombre: predictionData.nombre || '',
            pais: predictionData.pais || '',
            campoEstudio: predictionData.campoEstudio || '',
            edad: predictionData.edad || ''
        };

        history.push(entry);

        // Limitar a 50 predicciones máximo
        if (history.length > 50) {
            history.shift();
        }

        localStorage.setItem('predictionHistory', JSON.stringify(history));
    };
});

console.log('app.js cargado correctamente');
