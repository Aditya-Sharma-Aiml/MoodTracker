import numpy as np
import pandas as pd
import cv2
import streamlit as st
from tensorflow.keras.preprocessing.image import img_to_array
import plotly.express as px
import logging
import datetime
import os
import sys
from PIL import Image

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_global_theme, 
    apply_page_css,
    render_persistent_footer, 
    render_emotion_card,
    render_placeholder_results,
    initialize_emotion_history,
    add_emotion_to_history,
    increment_total_analyses,
    render_emotion_timeline
)

# Get the directory where the Real-Time Emotion Detection project is
realtime_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Real-Time-Emotion-Detection')
MODEL_DIR = os.path.join(realtime_dir, 'models')

# Page Configuration
st.set_page_config(
    page_title="Real-Time Emotion Detection",
    page_icon="📷",
    layout="wide"
)

# Apply global theme and page CSS
apply_global_theme()
apply_page_css()

# Initialize emotion history tracking
initialize_emotion_history()

# Logging setup
log_filename = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Real-Time Emotion Detection Application started.")

# Emotion labels
emotion_labels = {0: 'Angry', 1: 'Happy', 2: 'Neutral', 3: 'Sad', 4: 'Surprise'}

# Load Model
@st.cache_resource
def load_model():
    try:
        import tensorflow as tf
        from tensorflow.keras.models import load_model, model_from_json, Sequential
        
        model_path = os.path.join(MODEL_DIR, 'face_emotion_model1.h5')
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        try:
            custom_objects = {'Sequential': Sequential}
            emotion_model = load_model(model_path, custom_objects=custom_objects)
            logging.info("Model loaded from HDF5 successfully with custom objects.")
            return emotion_model
        except Exception as e1:
            try:
                emotion_model = load_model(model_path)
                logging.info("Model loaded from HDF5 successfully (direct load).")
                return emotion_model
            except Exception as e2:
                try:
                    json_path = os.path.join(MODEL_DIR, 'face_emotion_model1.json')
                    if not os.path.exists(json_path):
                        raise FileNotFoundError(f"JSON file not found: {json_path}")
                    
                    with open(json_path, 'r') as f:
                        model_structure = f.read()
                    
                    emotion_model = model_from_json(model_structure, custom_objects=custom_objects)
                    emotion_model.load_weights(model_path)
                    logging.info("Model loaded from JSON+weights successfully.")
                    return emotion_model
                except Exception as e3:
                    logging.error(f"All loading methods failed: {e1}, {e2}, {e3}")
                    raise Exception(f"Model loading failed. Last error: {e3}")
                
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        st.error(f"❌ Error loading model: {e}")
        return None

# Load Haar Cascade
@st.cache_resource
def load_face_detector():
    try:
        cascade_path = os.path.join(MODEL_DIR, 'face_haarcascade_frontalface_default.xml')
        
        if not os.path.exists(cascade_path):
            raise FileNotFoundError(f"Cascade file not found: {cascade_path}")
        
        face_detector = cv2.CascadeClassifier(cascade_path)
        
        if face_detector.empty():
            raise ValueError("Cascade classifier failed to load")
        
        logging.info("Haar Cascade loaded successfully.")
        return face_detector
    except Exception as e:
        logging.error(f"Error loading cascade: {e}")
        st.error(f"❌ Error loading face detector: {e}")
        return None

# Detect emotions in image
def detect_emotions(image_array, emotion_model, face_detector):
    """Detect emotions in image"""
    try:
        if image_array is None or emotion_model is None or face_detector is None:
            return image_array, []
        
        frame_bgr = image_array.copy()
        frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        
        faces = face_detector.detectMultiScale(
            frame_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        emotions_detected = []
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            face_roi = frame_gray[y:y + h, x:x + w]
            face_roi = cv2.resize(face_roi, (48, 48))
            face_roi = face_roi.astype('float32') / 255.0
            face_roi = img_to_array(face_roi)
            face_roi = np.expand_dims(face_roi, axis=0)
            
            predictions = emotion_model.predict(face_roi, verbose=0)[0]
            max_index = np.argmax(predictions)
            emotion = emotion_labels[max_index]
            confidence = float(predictions[max_index])
            
            emotions_detected.append({
                "emotion": emotion,
                "confidence": confidence,
                "position": (x, y)
            })
            
            label = f"{emotion} ({confidence:.2f})"
            cv2.putText(frame_bgr, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        return frame_bgr, emotions_detected
    
    except Exception as e:
        logging.error(f"Error during emotion detection: {e}")
        st.error(f"❌ Error processing image: {e}")
        return image_array, []

# Initialize session state
if 'detected_emotions' not in st.session_state:
    st.session_state.detected_emotions = None
if 'detected_image' not in st.session_state:
    st.session_state.detected_image = None

# Page Header
col_header_back, col_header_title = st.columns([0.5, 3])
with col_header_back:
    if st.button("⬅️ Back", key="face_back", help="Return to home"):
        st.switch_page("home.py")

with col_header_title:
    st.markdown("""
    <h1 style='font-size: 2.8em; font-weight: 800; margin: 0; padding: 0;'>📷 Face Emotion Detection</h1>
    <p style='color: #8b9ac9; font-size: 1.05em; margin: 5px 0 0 0;'>Detect emotions from faces using deep learning</p>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 20px 0 30px 0;'>", unsafe_allow_html=True)

# Load models
emotion_model = load_model()
face_detector = load_face_detector()

if emotion_model is None or face_detector is None:
    st.error("❌ Failed to load required models. Please ensure all model files exist.")
    st.info("ℹ️ Required files:")
    st.write("- models/face_emotion_model1.h5")
    st.write("- models/face_emotion_model1.json (optional)")
    st.write("- models/face_haarcascade_frontalface_default.xml")
    st.stop()

# Main layout: Two columns
col_input, col_results = st.columns([1, 1], gap="large")

# LEFT COLUMN - INPUT PANEL
with col_input:
    st.markdown("**📷 Capture Emotions**")
    st.caption("Choose webcam or upload to detect faces")
    
    input_method = st.radio(
        "Input Method:",
        ["📷 Webcam", "📤 Upload Image"],
        label_visibility="collapsed",
        horizontal=False
    )
    
    picture = None
    
    if input_method == "📷 Webcam":
        st.markdown("**📸 Webcam Capture**")
        picture = st.camera_input("Webcam", label_visibility="collapsed")
    else:
        st.markdown("**📁 Image Upload**")
        st.caption("JPG, PNG, BMP supported")
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=['jpg', 'jpeg', 'png', 'bmp'],
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            picture = uploaded_file
    
    # Analyze button
    if st.button("🔍 Detect Emotions", use_container_width=True, type="primary"):
        if picture is not None:
            with st.spinner("🔄 Detecting faces..."):
                try:
                    if isinstance(picture, Image.Image):
                        image_array = cv2.cvtColor(np.array(picture), cv2.COLOR_RGB2BGR)
                    else:
                        image_bytes = picture.read()
                        nparr = np.frombuffer(image_bytes, np.uint8)
                        image_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    processed_image, emotions = detect_emotions(image_array, emotion_model, face_detector)
                    
                    st.session_state.detected_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
                    st.session_state.detected_emotions = emotions
                    
                    # Log each detected emotion to global history
                    for emotion_data in emotions:
                        add_emotion_to_history(
                            emotion_data['emotion'],
                            emotion_data['confidence'],
                            'face'
                        )
                    
                    # Increment total analyses counter
                    increment_total_analyses()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)[:100]}")
                    logging.error(f"Image processing error: {e}")
        else:
            st.error("❌ Please capture or upload an image first")

# RIGHT COLUMN - RESULTS PANEL
with col_results:
    if st.session_state.detected_emotions is None:
        st.markdown("""
        <div style='background: rgba(99, 102, 241, 0.1); border: 2px dashed rgba(99, 102, 241, 0.3); 
                    border-radius: 10px; padding: 40px; text-align: center;'>
            <div style='font-size: 3em; margin-bottom: 15px;'>📸</div>
            <div style='color: #a8b8d8; font-size: 1.1em;'>Capture or upload an image on the left</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        emotions = st.session_state.detected_emotions
        
        if len(emotions) == 0:
            st.warning("⚠️ No faces detected. Try a clearer image with visible faces.")
        else:
            if st.session_state.detected_image is not None:
                st.image(st.session_state.detected_image, use_column_width=True, caption="Processed Image with Detections")
            
            st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.2); margin: 20px 0;'>", unsafe_allow_html=True)
            st.markdown(f"**👥 {len(emotions)} Face(s) Detected**")
            
            # Display each detected face result
            for idx, emotion_data in enumerate(emotions, 1):
                emotion_emoji_map = {
                    'Angry': '😠', 'Happy': '😊', 'Neutral': '😐', 
                    'Sad': '😢', 'Surprise': '😮'
                }
                emoji = emotion_emoji_map.get(emotion_data['emotion'], '😐')
                
                st.markdown(f"""
                <div style='background: rgba(99, 102, 234, 0.08); border: 1px solid rgba(99, 102, 234, 0.3); 
                            border-radius: 10px; padding: 15px; margin-bottom: 10px;'>
                    <div style='font-size: 1.5em; margin-bottom: 8px;'>{emoji} Face {idx}</div>
                    <div style='font-size: 1.1em; font-weight: 600; color: #667eea;'>
                        {emotion_data['emotion']} • {emotion_data['confidence']:.0%}
                    </div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0 30px 0;'>", unsafe_allow_html=True)

# FULL WIDTH - STATS AND CHARTS
if st.session_state.detected_emotions is not None and len(st.session_state.detected_emotions) > 0:
    emotions = st.session_state.detected_emotions
    
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    with stat_col1:
        st.metric("👥 Faces Detected", len(emotions))
    with stat_col2:
        avg_confidence = np.mean([e['confidence'] for e in emotions])
        st.metric("📊 Avg Confidence", f"{avg_confidence:.0%}")
    with stat_col3:
        emotion_labels_detected = [e['emotion'] for e in emotions]
        most_common = max(set(emotion_labels_detected), key=emotion_labels_detected.count)
        st.metric("😊 Most Detected", most_common)
    
    st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.2); margin: 30px 0;'>", unsafe_allow_html=True)
    
    # Emotion distribution chart
    emotion_dist = {}
    for emotion_data in emotions:
        emotion = emotion_data['emotion']
        emotion_dist[emotion] = emotion_dist.get(emotion, 0) + 1
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        emotion_df = pd.DataFrame(list(emotion_dist.items()), columns=['Emotion', 'Count'])
        emotion_colors = {
            'Angry': '#ef4444', 'Happy': '#10b981', 'Neutral': '#6b7280',
            'Sad': '#3b82f6', 'Surprise': '#8b5cf6'
        }
        fig_dist = px.bar(
            emotion_df,
            x='Emotion',
            y='Count',
            color='Emotion',
            color_discrete_map=emotion_colors,
            title="Detected Emotions"
        )
        fig_dist.update_layout(
            height=300,
            showlegend=False,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9')
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with chart_col2:
        conf_data = [{'Face': f"Face {i+1}", 'Confidence': e['confidence'] * 100} for i, e in enumerate(emotions)]
        conf_df = pd.DataFrame(conf_data)
        fig_conf = px.bar(
            conf_df,
            x='Face',
            y='Confidence',
            title="Confidence Scores",
            labels={'Confidence': 'Confidence (%)'}
        )
        fig_conf.update_layout(
            height=300,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9'),
            yaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig_conf, use_container_width=True)

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)
render_emotion_timeline()
st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)
render_persistent_footer()
