import sys
import os
sys.path.insert(0, os.getcwd())

print("=" * 60)
print("IMPORT VALIDATION TEST")
print("=" * 60)

# Test 1: Core imports (skip streamlit and tensorflow for now)
print("\n[1] Testing Core Modules...")
try:
    import numpy as np
    print("  ✓ numpy")
except Exception as e:
    print(f"  ✗ numpy: {e}")

try:
    import pandas as pd
    print("  ✓ pandas")
except Exception as e:
    print(f"  ✗ pandas: {e}")

try:
    import cv2
    print("  ✓ opencv-python")
except Exception as e:
    print(f"  ✗ opencv-python: {e}")

# Test 2: NLP and Audio imports
print("\n[2] Testing NLP & Audio Modules...")
try:
    from textblob import TextBlob
    print("  ✓ textblob")
except Exception as e:
    print(f"  ✗ textblob: {e}")

try:
    import speech_recognition as sr
    print("  ✓ SpeechRecognition")
except Exception as e:
    print(f"  ✗ SpeechRecognition: {e}")

try:
    from pydub import AudioSegment
    print("  ✓ pydub")
except Exception as e:
    print(f"  ✗ pydub: {e}")

# Test 3: Visualization imports
print("\n[3] Testing Visualization Modules...")
try:
    import plotly.graph_objects as go
    print("  ✓ plotly")
except Exception as e:
    print(f"  ✗ plotly: {e}")

try:
    import matplotlib.pyplot as plt
    print("  ✓ matplotlib")
except Exception as e:
    print(f"  ✗ matplotlib: {e}")

try:
    import altair as alt
    print("  ✓ altair")
except Exception as e:
    print(f"  ✗ altair: {e}")

# Test 4: ML imports
print("\n[4] Testing ML Modules...")
try:
    from sklearn.pipeline import Pipeline
    print("  ✓ scikit-learn")
except Exception as e:
    print(f"  ✗ scikit-learn: {e}")

try:
    import joblib
    print("  ✓ joblib")
except Exception as e:
    print(f"  ✗ joblib: {e}")

try:
    import scipy
    print("  ✓ scipy")
except Exception as e:
    print(f"  ✗ scipy: {e}")

# Test 5: Image imports
print("\n[5] Testing Image Modules...")
try:
    from PIL import Image
    print("  ✓ Pillow")
except Exception as e:
    print(f"  ✗ Pillow: {e}")

# Test 6: Utilities
print("\n[6] Testing Utility Modules...")
try:
    import requests
    print("  ✓ requests")
except Exception as e:
    print(f"  ✗ requests: {e}")

try:
    from dateutil import parser
    print("  ✓ python-dateutil")
except Exception as e:
    print(f"  ✗ python-dateutil: {e}")

# Test 7: Check for model files
print("\n[7] Checking Model Files...")
model_files = [
    ("Emotion_Dectector/model.h5", "Emotion Detection CNN Model"),
    ("Emotion_Dectector/haarcascade_frontalface_default.xml", "Haar Cascade"),
    ("Real-Time-Emotion-Detection/models/face_emotion_model1.h5", "Real-time emotion model"),
    ("Real-Time-Emotion-Detection/models/face_emotion_model1.json", "Real-time emotion model config"),
    ("NLP-Text-Emotion/models/emotion_classifier_pipe_lr_03_jan_2022.pkl", "NLP emotion classifier"),
]

for file_path, description in model_files:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path) / (1024*1024)
        print(f"  ✓ {description}: {file_path} ({size:.2f} MB)")
    else:
        print(f"  ✗ {description}: {file_path} (MISSING)")

# Test 8: Import project modules
print("\n[8] Testing Project Modules...")
try:
    import config
    print("  ✓ config.py")
except Exception as e:
    print(f"  ✗ config.py: {e}")

try:
    import utils
    print("  ✓ utils.py")
except Exception as e:
    print(f"  ✗ utils.py: {e}")

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)
