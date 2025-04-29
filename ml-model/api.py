from flask import Flask, request, jsonify
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from flask_cors import CORS
import datetime  # ADDED FOR TIMESTAMP

# Download stopwords if not already present
nltk.download('stopwords')

app = Flask(__name__)
CORS(app)

# Load the spam classifier model
try:
    model = joblib.load('spam_model.joblib')
    model_status = "Loaded successfully"  # Track model load status
except Exception as e:
    model_status = f"Load failed: {str(e)}"
    raise RuntimeError(f"Failed to load model: {e}")

# Preprocess function to clean and stem text
def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = text.lower().split()
    stemmer = PorterStemmer()
    filtered = [stemmer.stem(word) for word in text if word not in stopwords.words('english')]
    return ' '.join(filtered)

# Health check endpoint (ADDED THIS)
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'OK',
        'message': 'ML Service is operational',
        'model_status': model_status,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }), 200

# Homepage route
@app.route('/')
def home():
    return "Spam Detection API is running! Please POST to /predict."

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid input, "text" key is required.'}), 400

    raw_text = data['text']
    processed_text = preprocess_text(raw_text)
    
    try:
        prediction = model.predict([processed_text])[0]
        confidence = model.predict_proba([processed_text])[0].max()
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {e}'}), 500

    return jsonify({
        'isSpam': prediction == 'spam',
        'confidence': round(float(confidence), 4)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  # Changed to 0.0.0.0 for Docker compatibility