"""
app/services/mock_translator.py

Fallback translation service using a predefined multilingual dictionary.

This engine is used automatically when no Google API key is configured.
It handles common English phrases and returns realistic translated equivalents
for demonstration and development purposes.
"""

from app.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Phrase dictionary: { target_language: { english_phrase: translated_phrase } }
# All keys are lower-cased for case-insensitive lookup.
# ---------------------------------------------------------------------------
_PHRASE_DICT: dict[str, dict[str, str]] = {
    "hi": {  # Hindi
        "hello": "नमस्ते",
        "hello, how are you?": "नमस्ते, आप कैसे हैं?",
        "how are you?": "आप कैसे हैं?",
        "good morning": "सुप्रभात",
        "good night": "शुभ रात्रि",
        "good evening": "शुभ संध्या",
        "thank you": "धन्यवाद",
        "thank you very much": "बहुत बहुत धन्यवाद",
        "you are welcome": "आपका स्वागत है",
        "please": "कृपया",
        "sorry": "माफ़ करना",
        "yes": "हाँ",
        "no": "नहीं",
        "my name is": "मेरा नाम है",
        "what is your name?": "आपका नाम क्या है?",
        "i love india": "मुझे भारत से प्यार है",
        "water": "पानी",
        "food": "खाना",
        "help": "मदद",
        "where is the hospital?": "अस्पताल कहाँ है?",
        "i don't understand": "मैं नहीं समझता",
        "translation": "अनुवाद",
        "language": "भाषा",
    },
    "ta": {  # Tamil
        "hello": "வணக்கம்",
        "hello, how are you?": "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?",
        "how are you?": "நீங்கள் எப்படி இருக்கிறீர்கள்?",
        "good morning": "காலை வணக்கம்",
        "good night": "இரவு வணக்கம்",
        "good evening": "மாலை வணக்கம்",
        "thank you": "நன்றி",
        "thank you very much": "மிக்க நன்றி",
        "you are welcome": "வரவேற்கிறோம்",
        "please": "தயவுசெய்து",
        "sorry": "மன்னிக்கவும்",
        "yes": "ஆம்",
        "no": "இல்லை",
        "water": "தண்ணீர்",
        "food": "உணவு",
        "help": "உதவி",
        "translation": "மொழிபெயர்ப்பு",
        "language": "மொழி",
    },
    "kn": {  # Kannada
        "hello": "ನಮಸ್ಕಾರ",
        "hello, how are you?": "ನಮಸ್ಕಾರ, ನೀವು ಹೇಗಿದ್ದೀರಿ?",
        "how are you?": "ನೀವು ಹೇಗಿದ್ದೀರಿ?",
        "good morning": "ಶುಭೋದಯ",
        "good night": "ಶುಭ ರಾತ್ರಿ",
        "good evening": "ಶುಭ ಸಂಜೆ",
        "thank you": "ಧನ್ಯವಾದಗಳು",
        "thank you very much": "ತುಂಬಾ ಧನ್ಯವಾದಗಳು",
        "you are welcome": "ಸ್ವಾಗತ",
        "please": "ದಯವಿಟ್ಟು",
        "sorry": "ಕ್ಷಮಿಸಿ",
        "yes": "ಹೌದು",
        "no": "ಇಲ್ಲ",
        "water": "ನೀರು",
        "food": "ಆಹಾರ",
        "help": "ಸಹಾಯ",
        "translation": "ಅನುವಾದ",
        "language": "ಭಾಷೆ",
    },
    "bn": {  # Bengali
        "hello": "হ্যালো",
        "hello, how are you?": "হ্যালো, আপনি কেমন আছেন?",
        "how are you?": "আপনি কেমন আছেন?",
        "good morning": "সুপ্রভাত",
        "good night": "শুভ রাত্রি",
        "good evening": "শুভ সন্ধ্যা",
        "thank you": "ধন্যবাদ",
        "thank you very much": "অনেক ধন্যবাদ",
        "you are welcome": "আপনাকে স্বাগতম",
        "please": "অনুগ্রহ করে",
        "sorry": "দুঃখিত",
        "yes": "হ্যাঁ",
        "no": "না",
        "water": "জল",
        "food": "খাবার",
        "help": "সাহায্য",
        "translation": "অনুবাদ",
        "language": "ভাষা",
    },
    "te": {  # Telugu
        "hello": "నమస్కారం",
        "how are you?": "మీరు ఎలా ఉన్నారు?",
        "good morning": "శుభోదయం",
        "good night": "శుభ రాత్రి",
        "thank you": "ధన్యవాదాలు",
        "please": "దయచేసి",
        "sorry": "క్షమించండి",
        "yes": "అవును",
        "no": "కాదు",
        "water": "నీరు",
        "food": "ఆహారం",
        "translation": "అనువాదం",
        "language": "భాష",
    },
    "mr": {  # Marathi
        "hello": "नमस्कार",
        "how are you?": "तुम्ही कसे आहात?",
        "good morning": "सुप्रभात",
        "good night": "शुभ रात्री",
        "thank you": "धन्यवाद",
        "please": "कृपया",
        "sorry": "माफ करा",
        "yes": "हो",
        "no": "नाही",
        "water": "पाणी",
        "food": "अन्न",
        "translation": "भाषांतर",
        "language": "भाषा",
    },
    "gu": {  # Gujarati
        "hello": "નમસ્તે",
        "how are you?": "તમે કેમ છો?",
        "good morning": "સુપ્રભાત",
        "good night": "શુભ રાત્રિ",
        "thank you": "આભાર",
        "please": "કૃપા કરીને",
        "sorry": "માફ કરો",
        "yes": "હા",
        "no": "ના",
        "water": "પાણી",
        "food": "ખોરાક",
        "translation": "અનુવાદ",
        "language": "ભાષા",
    },
    "ml": {  # Malayalam
        "hello": "നമസ്കാരം",
        "how are you?": "സുഖമാണോ?",
        "good morning": "സുപ്രഭാതം",
        "good night": "ശുഭ രാത്രി",
        "thank you": "നന്ദി",
        "please": "ദയവായി",
        "sorry": "ക്ഷമിക്കണം",
        "yes": "അതെ",
        "no": "ഇല്ല",
        "water": "വെള്ളം",
        "food": "ഭക്ഷണം",
        "translation": "വിവർത്തനം",
        "language": "ഭാഷ",
    },
    "pa": {  # Punjabi
        "hello": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ",
        "how are you?": "ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ?",
        "good morning": "ਸ਼ੁਭ ਸਵੇਰ",
        "good night": "ਸ਼ੁਭ ਰਾਤ",
        "thank you": "ਧੰਨਵਾਦ",
        "please": "ਕਿਰਪਾ ਕਰਕੇ",
        "sorry": "ਮਾਫ਼ ਕਰੋ",
        "yes": "ਹਾਂ",
        "no": "ਨਹੀਂ",
        "water": "ਪਾਣੀ",
        "food": "ਖਾਣਾ",
        "translation": "ਅਨੁਵਾਦ",
        "language": "ਭਾਸ਼ਾ",
    },
    "ur": {  # Urdu
        "hello": "السلام علیکم",
        "how are you?": "آپ کیسے ہیں؟",
        "good morning": "صبح بخیر",
        "good night": "شب بخیر",
        "thank you": "شکریہ",
        "please": "براہ کرم",
        "sorry": "معاف کریں",
        "yes": "ہاں",
        "no": "نہیں",
        "water": "پانی",
        "food": "کھانا",
        "translation": "ترجمہ",
        "language": "زبان",
    },
    "fr": {  # French
        "hello": "Bonjour",
        "hello, how are you?": "Bonjour, comment allez-vous ?",
        "how are you?": "Comment allez-vous ?",
        "good morning": "Bonjour",
        "good night": "Bonne nuit",
        "good evening": "Bonsoir",
        "thank you": "Merci",
        "thank you very much": "Merci beaucoup",
        "you are welcome": "De rien",
        "please": "S'il vous plaît",
        "sorry": "Désolé",
        "yes": "Oui",
        "no": "Non",
        "water": "Eau",
        "food": "Nourriture",
        "help": "Aide",
        "translation": "Traduction",
        "language": "Langue",
    },
    "de": {  # German
        "hello": "Hallo",
        "how are you?": "Wie geht es Ihnen?",
        "good morning": "Guten Morgen",
        "good night": "Gute Nacht",
        "good evening": "Guten Abend",
        "thank you": "Danke",
        "thank you very much": "Vielen Dank",
        "you are welcome": "Bitte",
        "please": "Bitte",
        "sorry": "Entschuldigung",
        "yes": "Ja",
        "no": "Nein",
        "water": "Wasser",
        "food": "Essen",
        "translation": "Übersetzung",
        "language": "Sprache",
    },
    "es": {  # Spanish
        "hello": "Hola",
        "how are you?": "¿Cómo estás?",
        "good morning": "Buenos días",
        "good night": "Buenas noches",
        "good evening": "Buenas tardes",
        "thank you": "Gracias",
        "thank you very much": "Muchas gracias",
        "you are welcome": "De nada",
        "please": "Por favor",
        "sorry": "Lo siento",
        "yes": "Sí",
        "no": "No",
        "water": "Agua",
        "food": "Comida",
        "help": "Ayuda",
        "translation": "Traducción",
        "language": "Idioma",
    },
}


def mock_translate(text: str, target_language: str) -> str:
    """
    Perform a mock translation by looking up the text in the phrase dictionary.

    Strategy
    --------
    1. Exact match (case-insensitive) in the dictionary.
    2. Partial token matching for multi-word inputs.
    3. Fallback: return the original text with a language-tagged prefix to
       indicate that no dictionary entry was found.

    Parameters
    ----------
    text            : Input text to translate.
    target_language : ISO 639-1 target language code.

    Returns
    -------
    Translated string (or annotated fallback).
    """
    lang_dict = _PHRASE_DICT.get(target_language.lower(), {})
    normalised = text.lower().strip()

    # ── Exact match ────────────────────────────────────────────────────────
    if normalised in lang_dict:
        return lang_dict[normalised]

    # ── Partial match: try progressively shorter substrings ────────────────
    for phrase, translation in lang_dict.items():
        if phrase in normalised:
            # Replace the matched portion; leave surrounding text unchanged
            translated = text.replace(phrase, translation)
            logger.debug("Partial mock match for lang=%s phrase='%s'", target_language, phrase)
            return translated

    # ── Fallback ───────────────────────────────────────────────────────────
    logger.debug(
        "No dictionary match for lang=%s text='%.50s…' — returning annotated fallback",
        target_language, text,
    )
    return f"[{target_language.upper()}] {text}"


def is_language_supported_in_mock(language_code: str) -> bool:
    """Return True if the mock dictionary contains entries for this language."""
    return language_code.lower() in _PHRASE_DICT
