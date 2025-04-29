import os
from flask import Flask, request, jsonify
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from flask_cors import CORS
import datetime
from pymongo import MongoClient
import time
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('ml_service.log', maxBytes=1000000, backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Download stopwords if not already present
try:
    nltk.download('stopwords')
    logger.info("NLTK stopwords downloaded successfully")
except Exception as e:
    logger.error(f"Failed to download NLTK stopwords: {e}")
    raise

app = Flask(__name__)
CORS(app)

# MongoDB Connection with Retry Logic
def connect_to_mongo(max_retries=5, retry_delay=2):
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://root:example@mongo:27017/mydb?authSource=admin')
    for attempt in range(max_retries):
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            return client
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed to connect to MongoDB: {e}")
            if attempt == max_retries - 1:
                logger.error("Max retries reached. Failed to connect to MongoDB")
                raise
            time.sleep(retry_delay)

try:
    mongo_client = connect_to_mongo()
    db = mongo_client.mydb
    predictions_collection = db.predictions
except Exception as e:
    logger.error(f"Failed to initialize MongoDB: {e}")
    raise

# Load the spam classifier model
try:
    model = joblib.load('spam_model.joblib')
    model_status = "Loaded successfully"
    logger.info("Model loaded successfully")
except Exception as e:
    model_status = f"Load failed: {str(e)}"
    logger.error(f"Failed to load model: {e}")
    raise RuntimeError(f"Failed to load model: {e}")

# Preprocess function to clean and stem text
def preprocess_text(text):
    try:
        text = re.sub(r'[^a-zA-Z]', ' ', text)
        text = text.lower().split()
        stemmer = PorterStemmer()
        filtered = [stemmer.stem(word) for word in text if word not in stopwords.words('english')]
        return ' '.join(filtered)
    except Exception as e:
        logger.error(f"Text preprocessing failed: {e}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Verify MongoDB connection
        mongo_client.admin.command('ping')
        
        # Verify model status
        if "failed" in model_status.lower():
            raise RuntimeError(model_status)
            
        return jsonify({
            'status': 'OK',
            'message': 'ML Service is operational',
            'model_status': model_status,
            'mongo_status': 'Connected',
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'ERROR',
            'message': 'Service unavailable',
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 503

@app.route('/')
def home():
    return jsonify({
        'service': 'Spam Detection API',
        'status': 'running',
        'endpoints': {
            'health_check': '/health (GET)',
            'prediction': '/predict (POST)'
        }
    })

@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()
    prediction_data = {
        'timestamp': datetime.datetime.utcnow(),
        'status': 'pending',
        'input_text': None,
        'prediction': None,
        'confidence': None,
        'processing_time': None
    }

    try:
        data = request.get_json()
        if not data or 'text' not in data:
            raise ValueError('Invalid input, "text" key is required.')

        raw_text = data['text']
        prediction_data['input_text'] = raw_text

        processed_text = preprocess_text(raw_text)
        
        try:
            prediction = model.predict([processed_text])[0]
            confidence = model.predict_proba([processed_text])[0].max()
            
            prediction_data.update({
                'status': 'success',
                'prediction': prediction,
                'confidence': float(confidence),
                'processing_time': time.time() - start_time
            })
            
            # Store prediction in MongoDB
            try:
                predictions_collection.insert_one(prediction_data)
                logger.info("Prediction stored in MongoDB")
            except Exception as e:
                logger.error(f"Failed to store prediction in MongoDB: {e}")

            return jsonify({
                'isSpam': prediction == 'spam',
                'confidence': round(float(confidence), 4),
                'processing_time': round(time.time() - start_time, 4)
            })

        except Exception as e:
            prediction_data['status'] = 'error'
            prediction_data['error'] = str(e)
            logger.error(f"Prediction failed: {e}")
            return jsonify({'error': f'Prediction failed: {e}'}), 500

    except Exception as e:
        logger.error(f"Request processing failed: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port)