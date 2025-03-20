import re
import nltk
import joblib
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob

nltk.download('stopwords')
nltk.download('wordnet')

LABEL_MAP = {0: "Neutral", 1: "Offensive", 2: "Cyberbullying"}

positive_words = {'pretty', 'informative', 'good', 'great', 'excellent', 
                  'amazing', 'wonderful','awesome','hello','hi','hey','greetings','good morning',
                  'good afternoon','good evening','good night','nice','beautiful','handsome','attractive',
                  'charming','cute','adorable','lovely','delightful','pleasant','enjoyable','fun',
                  'entertaining','marvelous','fabulous','fantastic','terrific','superb','splendid',
                  'exquisite','exceptional','perfect','flawless','impeccable','outstanding','remarkable',
                  'extraordinary','incredible','unbelievable','unimaginable'}
negative_words = {
    "suck", "dick", "idiot", "ugly", "bastard", "stupid", "dumb", "loser", "fat","ass",
    "jerk", "moron", "retard", "bitch", "asshole", "trash", "useless", "worthless",
    "hate", "disgusting", "pathetic", "horrible", "kill", "die", "fuck", "shit"
}


def preprocess_text(text, stop_words, lemmatizer):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\'s', 'is', text)
    text = re.sub(r'n\'t', 'not', text)
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(words)


def sentiment_score(text):
    blob = TextBlob(text)
    return {
        'polarity': blob.sentiment.polarity,
        'subjectivity': blob.sentiment.subjectivity,
        'word_count': len(text.split()),
        'contains_positive': any(word in text.lower() for word in positive_words),
        'contains_negative': any(word in text.lower() for word in negative_words)
    }


def analyze_text(metrics, text):
    if metrics['contains_negative']:
        return False
    if metrics['contains_positive']:
        return True
    if metrics['polarity'] > 0.3 and metrics['subjectivity'] < 0.5:
        return True
    if metrics['word_count'] < 2 and not metrics['contains_negative']:
        return True
    return False


def load_model_and_predict(model_filename, vectorizer_filename, text):
    classifier = joblib.load(model_filename)
    vectorizer = joblib.load(vectorizer_filename)
    stop_words = set(stopwords.words('english')) - {"not", "no"}
    lemmatizer = WordNetLemmatizer()
    text_lower = text.lower()
    text_words = set(text_lower.split())
    if text_words.intersection(negative_words):
        if len(text.split()) < 3:
            return "Cyberbullying"
        else:
            pass

    metrics = sentiment_score(text)
    if analyze_text(metrics, text):
        return 'Neutral'
    processed_text = preprocess_text(text, stop_words, lemmatizer)
    if not processed_text:
        processed_text = text_lower
    text_vectorized = vectorizer.transform([processed_text])
    prediction = classifier.predict(text_vectorized)[0]
    if metrics['polarity'] > 0.6:
        return "Neutral"
    return LABEL_MAP.get(prediction, "Unknown")


def main():
    while True:
        text = input("Enter text (or 'quit' to exit): ")
        if text.lower() == 'quit':
            break
        prediction = load_model_and_predict("cyberbullying_model.pkl", "vectorizer.pkl", text)
        print("Classification:", prediction)


if __name__ == "_main_":
    main()