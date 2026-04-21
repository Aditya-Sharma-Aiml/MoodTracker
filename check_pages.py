import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("PAGE ERROR DETECTION SCRIPT")
print("=" * 70)

# Check 1: Try importing each page as a module
print("\n[1] Checking Page Files for Import Errors...")
page_files = [
    "pages/1_nlp_text_emotion.py",
    "pages/2_realtime_detection.py",
    "pages/3_voice_analyzer.py",
    "pages/4_history_dashboard.py",
    "pages/5_compare.py",
    "pages/6_about.py",
]

for page_file in page_files:
    try:
        with open(page_file, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
            compile(code, page_file, 'exec')
            print(f"  [OK] {page_file}: Syntax OK")
    except Exception as e:
        print(f"  [ERROR] {page_file}: {type(e).__name__}: {str(e)[:80]}")

# Check 2: Test model loading
print("\n[2] Checking Model Files...")
import tensorflow as tf

model_files = [
    ("Emotion_Dectector/model.h5", "Emotion Detection CNN"),
    ("Real-Time-Emotion-Detection/models/face_emotion_model1.h5", "Real-time emotion model"),
]

for model_path, description in model_files:
    try:
        if os.path.exists(model_path):
            model = tf.keras.models.load_model(model_path)
            print(f"  [OK] {description}: Loaded successfully")
        else:
            print(f"  [MISSING] {description}: File not found at {model_path}")
    except Exception as e:
        print(f"  [ERROR] {description}: {type(e).__name__}: {str(e)[:80]}")

# Check 3: Test NLP model loading
print("\n[3] Checking NLP Model...")
try:
    import joblib
    nlp_model_path = "NLP-Text-Emotion/models/emotion_classifier_pipe_lr_03_jan_2022.pkl"
    if os.path.exists(nlp_model_path):
        nlp_model = joblib.load(nlp_model_path)
        print(f"  [OK] NLP Emotion Classifier: Loaded successfully")
    else:
        print(f"  [MISSING] NLP Model: File not found")
except Exception as e:
    print(f"  [ERROR] NLP Model: {type(e).__name__}: {str(e)[:80]}")

# Check 4: Test utility functions
print("\n[4] Checking Utility Functions...")
try:
    import config
    print("  [OK] config.py: Imported successfully")
except Exception as e:
    print(f"  [ERROR] config.py: {type(e).__name__}: {str(e)[:80]}")

try:
    import utils
    print("  [OK] utils.py: Imported successfully")
    # Check specific functions
    funcs = [
        'apply_global_theme',
        'apply_page_css',
        'initialize_emotion_history',
        'add_emotion_to_history',
        'increment_total_analyses',
        'render_emotion_card'
    ]
    for func in funcs:
        if hasattr(utils, func):
            print(f"    [OK] Function '{func}' exists")
        else:
            print(f"    [MISSING] Function '{func}' NOT FOUND")
except Exception as e:
    print(f"  [ERROR] utils.py: {type(e).__name__}: {str(e)[:80]}")

print("\n" + "=" * 70)
print("PAGE ERROR DETECTION COMPLETE")
print("=" * 70)
