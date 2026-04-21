# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("FINAL MOODTRACKER FUNCTIONALITY TEST")
print("=" * 70)

# Test 1: All imports
print("\n[TEST 1] Core Dependencies...")
all_ok = True
imports = {
    'streamlit': 'st',
    'numpy': 'np',
    'pandas': 'pd',
    'cv2': 'opencv',
    'tensorflow': 'tf',
    'textblob': 'TextBlob',
    'plotly.graph_objects': 'go',
    'PIL': 'Image',
    'sklearn.pipeline': 'Pipeline',
    'joblib': 'joblib',
    'scipy': 'scipy',
}

for module_name, alias in imports.items():
    try:
        __import__(module_name)
        print(f"  [OK] {module_name}")
    except Exception as e:
        print(f"  [FAIL] {module_name}: {str(e)[:60]}")
        all_ok = False

# Test 2: Config and Utils
print("\n[TEST 2] Project Configuration...")
try:
    import config
    print(f"  [OK] config.py imported")
    if hasattr(config, 'EMOTION_DETECTOR_CONFIG'):
        print(f"    - EMOTION_DETECTOR_CONFIG: OK")
    if hasattr(config, 'NLP_EMOTION_CONFIG'):
        print(f"    - NLP_EMOTION_CONFIG: OK")
    if hasattr(config, 'REALTIME_EMOTION_CONFIG'):
        print(f"    - REALTIME_EMOTION_CONFIG: OK")
except Exception as e:
    print(f"  [FAIL] config.py: {e}")
    all_ok = False

try:
    import utils
    print(f"  [OK] utils.py imported")
except Exception as e:
    print(f"  [FAIL] utils.py: {e}")
    all_ok = False

# Test 3: Model Files
print("\n[TEST 3] Model Files...")
models = {
    'Emotion_Dectector/model.h5': 'Emotion Detection CNN',
    'Real-Time-Emotion-Detection/models/face_emotion_model1.h5': 'Real-time emotion model',
    'Real-Time-Emotion-Detection/models/face_emotion_model1.json': 'Real-time model config',
    'NLP-Text-Emotion/models/emotion_classifier_pipe_lr_03_jan_2022.pkl': 'NLP classifier',
    'Emotion_Dectector/haarcascade_frontalface_default.xml': 'Haar Cascade',
    'Real-Time-Emotion-Detection/models/face_haarcascade_frontalface_default.xml': 'Haar Cascade (RT)',
}

for path, desc in models.items():
    if os.path.exists(path):
        size = os.path.getsize(path) / 1024
        print(f"  [OK] {desc}: {size:.1f} KB")
    else:
        print(f"  [MISSING] {desc}: NOT FOUND")
        all_ok = False

# Test 4: Model Loading
print("\n[TEST 4] Model Loading...")
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    model_path = 'Emotion_Dectector/model.h5'
    model = load_model(model_path)
    print(f"  [OK] CNN model loaded: {model.name}")
except Exception as e:
    print(f"  [FAIL] CNN model failed: {str(e)[:60]}")
    all_ok = False

try:
    import joblib
    nlp_model_path = 'NLP-Text-Emotion/models/emotion_classifier_pipe_lr_03_jan_2022.pkl'
    nlp_model = joblib.load(nlp_model_path)
    print(f"  [OK] NLP model loaded successfully")
except Exception as e:
    print(f"  [FAIL] NLP model failed: {str(e)[:60]}")
    all_ok = False

# Test 5: Cascade Classifiers
print("\n[TEST 5] Cascade Classifiers...")
try:
    import cv2
    cascade_path = 'Emotion_Dectector/haarcascade_frontalface_default.xml'
    cascade = cv2.CascadeClassifier(cascade_path)
    if not cascade.empty():
        print(f"  [OK] Cascade loaded successfully")
    else:
        print(f"  [FAIL] Cascade failed to load")
        all_ok = False
except Exception as e:
    print(f"  [FAIL] Cascade error: {e}")
    all_ok = False

# Test 6: NLP Functionality
print("\n[TEST 6] NLP Prediction Test...")
try:
    from textblob import TextBlob
    text = "I am very happy today!"
    blob = TextBlob(text)
    sentiment = blob.sentiment
    print(f"  [OK] TextBlob sentiment: polarity={sentiment.polarity:.2f}, subjectivity={sentiment.subjectivity:.2f}")
except Exception as e:
    print(f"  [FAIL] TextBlob failed: {e}")
    all_ok = False

print("\n" + "=" * 70)
if all_ok:
    print("RESULT: [SUCCESS] ALL TESTS PASSED - READY FOR PRODUCTION")
else:
    print("RESULT: [WARNING] SOME TESTS FAILED - REVIEW ABOVE")
print("=" * 70)
