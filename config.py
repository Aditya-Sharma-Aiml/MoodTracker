"""
MoodTracker Project Configuration
Configuration settings for all three emotion detection modules
"""

import os

# Project Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
EMOTION_DETECTOR_DIR = os.path.join(PROJECT_ROOT, 'Emotion_Dectector')
NLP_EMOTION_DIR = os.path.join(PROJECT_ROOT, 'NLP-Text-Emotion')
REALTIME_EMOTION_DIR = os.path.join(PROJECT_ROOT, 'Real-Time-Emotion-Detection')

# ========== EMOTION_DETECTOR Configuration ==========
EMOTION_DETECTOR_CONFIG = {
    'name': 'Emotion Detector (Computer Vision)',
    'description': 'Real-time facial emotion detection using CNN',
    'model_path': os.path.join(EMOTION_DETECTOR_DIR, 'model.h5'),
    'cascade_path': os.path.join(EMOTION_DETECTOR_DIR, 'haarcascade_frontalface_default.xml'),
    'emotions': ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise'],
    'input_size': (48, 48),
    'port': 8501,
    'confidence_threshold': 0.5
}

# ========== NLP_EMOTION Configuration ==========
NLP_EMOTION_CONFIG = {
    'name': 'NLP Text Emotion Classifier',
    'description': 'Text-based emotion classification with 93% accuracy',
    'model_path': os.path.join(NLP_EMOTION_DIR, 'models', 'emotion_classifier_pipe_lr_03_jan_2022.pkl'),
    'dataset_path': os.path.join(NLP_EMOTION_DIR, 'data', 'emotion_dataset_2.csv'),
    'emotions': ['anger', 'disgust', 'fear', 'happy', 'joy', 'neutral', 'sad', 'sadness', 'shame', 'surprise'],
    'max_text_length': 2000,
    'accuracy': 0.93,
    'port': 8502,
}

# ========== REALTIME_EMOTION Configuration ==========
REALTIME_EMOTION_CONFIG = {
    'name': 'Real-Time Emotion Detection',
    'description': 'Real-time webcam-based emotion detection',
    'model_path': os.path.join(REALTIME_EMOTION_DIR, 'models', 'face_emotion_model1.h5'),
    'model_json_path': os.path.join(REALTIME_EMOTION_DIR, 'models', 'face_emotion_model1.json'),
    'cascade_path': os.path.join(REALTIME_EMOTION_DIR, 'models', 'face_haarcascade_frontalface_default.xml'),
    'emotions': {0: 'Angry', 1: 'Happy', 2: 'Neutral', 3: 'Sad', 4: 'Surprise'},
    'input_size': (48, 48),
    'port': 8503,
    'confidence_threshold': 0.5,
    'face_detection_scale': 1.1,
    'min_neighbors': 5,
}

# ========== Global Settings ==========
GLOBAL_CONFIG = {
    'project_name': 'MoodTracker',
    'version': '1.0.0',
    'author': 'Aditya Sharma',
    'year': 2024,
    'log_level': 'INFO',
    'debug_mode': False,
}

# ========== Emotion Emojis for UI ==========
EMOTION_EMOJIS = {
    'anger': '😠',
    'angry': '😠',
    'disgust': '🤮',
    'fear': '😨😱',
    'happy': '🤗',
    'joy': '😂',
    'neutral': '😐',
    'sad': '😔',
    'sadness': '😔',
    'shame': '😳',
    'surprise': '😮',
}

def get_config(module_name):
    """Get configuration for a specific module"""
    configs = {
        'emotion_detector': EMOTION_DETECTOR_CONFIG,
        'nlp_emotion': NLP_EMOTION_CONFIG,
        'realtime_emotion': REALTIME_EMOTION_CONFIG,
    }
    return configs.get(module_name)
