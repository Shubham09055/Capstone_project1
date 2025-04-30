from flask import Flask, request, jsonify
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer 
from flask_cors import CORS  # If you want to allow cross-origin requests (useful for frontend hosted on different port)

# Download stopwords if not already present
nltk.download('stopwords')

app = Flask(__name__)
CORS(app)  # This will enable CORS (cross-origin resource sharing), if needed for your frontend

# Load the spam classifier model
try:
    model = joblib.load('spam_model.joblib')
except Exception as e:
    raise RuntimeError(f"Failed to load model: {e}")

# Preprocess function to clean and stem text
def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z]', ' ', text)  # Remove non-alphabetic characters
    text = text.lower().split()  # Convert text to lowercase and split into words
    stemmer = PorterStemmer()
    filtered = [stemmer.stem(word) for word in text if word not in stopwords.words('english')]
    return ' '.join(filtered)

# Homepage route to ensure the server is running
@app.route('/')
def home():
    return "Spam Detection API is running! Please POST to /predict."

# Prediction route for text classification
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Check if the request has the required 'text' key
    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid input, "text" key is required.'}), 400

    raw_text = data['text']
    processed_text = preprocess_text(raw_text)
    
    try:
        prediction = model.predict([processed_text])[0]  # Predict class (spam/ham)
        confidence = model.predict_proba([processed_text])[0].max()  # Get the highest probability
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {e}'}), 500

    return jsonify({
        'isSpam': prediction == 'spam',  # Return whether the email is spam
        'confidence': round(float(confidence), 4)  # Round confidence to 4 decimal places
    })

# Run server
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
