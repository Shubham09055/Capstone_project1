import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
import re
import joblib

nltk.download('stopwords')

# Load dataset
df = pd.read_csv(r'C:\Users\gargs\Desktop\email-spam-detector\ml-model\spam.csv', encoding='latin-1')
df = df[['v1', 'v2']]
df.columns = ['label', 'message']

# Preprocessing
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    text = re.sub('[^a-zA-Z]', ' ', text)
    text = text.lower()
    text = text.split()
    text = [stemmer.stem(word) for word in text if word not in stop_words]
    return ' '.join(text)

df['processed_message'] = df['message'].apply(preprocess_text)

# Split data
X_train, X_test, y_train, y_test = train_test_split(df['processed_message'], df['label'], test_size=0.2)

# Create pipeline
model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('classifier', MultinomialNB())
])

# Train model
model.fit(X_train, y_train)

# Save model
joblib.dump(model, 'spam_model.joblib')

# Test accuracy
print("Accuracy:", model.score(X_test, y_test))