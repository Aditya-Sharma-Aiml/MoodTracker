import streamlit as st
import numpy as np
import pandas as pd
import joblib
import cv2
import speech_recognition as sr
from textblob import TextBlob
from tensorflow.keras.preprocessing.image import img_to_array
import plotly.graph_objects as go
import plotly.express as px
import logging
import datetime
import os
import sys
import tempfile
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
    render_emotion_timeline,
    EMOTION_EMOJIS
)

st.set_page_config(
    page_title="Multi-Modal Emotion Comparison",
    page_icon="🎭",
    layout="wide"
)

# Apply global theme and page CSS
apply_global_theme()
apply_page_css()

# Initialize emotion history
initialize_emotion_history()

# ============================================================================
# MODEL LOADING
# ============================================================================

@st.cache_resource
def load_nlp_model():
    """Load NLP emotion classifier"""
    try:
        nlp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NLP-Text-Emotion')
        model_path = os.path.join(nlp_dir, 'models', 'emotion_classifier_pipe_lr_03_jan_2022.pkl')
        
        if not os.path.exists(model_path):
            st.error(f"❌ NLP model not found")
            return None
        
        with open(model_path, 'rb') as f:
            model = joblib.load(f)
        return model
    except Exception as e:
        st.error(f"❌ Error loading NLP model: {e}")
        return None

@st.cache_resource
def load_face_model():
    """Load face emotion model"""
    try:
        from tensorflow.keras.models import load_model, model_from_json
        
        realtime_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Real-Time-Emotion-Detection')
        model_dir = os.path.join(realtime_dir, 'models')
        model_path = os.path.join(model_dir, 'face_emotion_model1.h5')
        
        if not os.path.exists(model_path):
            return None
        
        try:
            model = load_model(model_path, custom_objects={'Sequential': None})
            return model
        except:
            try:
                model = load_model(model_path)
                return model
            except:
                return None
    except Exception as e:
        return None

@st.cache_resource
def load_face_cascade():
    """Load Haar cascade classifier"""
    try:
        realtime_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Real-Time-Emotion-Detection')
        cascade_path = os.path.join(realtime_dir, 'models', 'face_haarcascade_frontalface_default.xml')
        
        if not os.path.exists(cascade_path):
            return None
        
        cascade = cv2.CascadeClassifier(cascade_path)
        return cascade if not cascade.empty() else None
    except:
        return None

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_text(text, nlp_model):
    """Analyze text emotion"""
    try:
        if not text or not nlp_model:
            return None
        
        prediction = nlp_model.predict([text])[0]
        probability = nlp_model.predict_proba([text])[0]
        
        emotions_dict = {}
        for emotion_class, prob in zip(nlp_model.classes_, probability):
            emotions_dict[emotion_class] = float(prob)
        
        confidence = float(np.max(probability))
        
        return {
            'emotion': prediction,
            'confidence': confidence,
            'all_emotions': emotions_dict,
            'source': 'text'
        }
    except Exception as e:
        st.error(f"❌ Text analysis error: {e}")
        return None

def analyze_face(image_bytes, face_model, cascade):
    """Analyze face emotion"""
    try:
        if not image_bytes or not face_model or not cascade:
            return None
        
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return None
        
        emotion_labels = {0: 'Angry', 1: 'Happy', 2: 'Neutral', 3: 'Sad', 4: 'Surprise'}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
        
        if len(faces) == 0:
            return None
        
        # Analyze first detected face
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y + h, x:x + w]
        face_roi = cv2.resize(face_roi, (48, 48))
        face_roi = face_roi.astype('float32') / 255.0
        face_roi = img_to_array(face_roi)
        face_roi = np.expand_dims(face_roi, axis=0)
        
        predictions = face_model.predict(face_roi, verbose=0)[0]
        max_idx = np.argmax(predictions)
        emotion = emotion_labels[max_idx]
        confidence = float(predictions[max_idx])
        
        emotions_dict = {emotion_labels[i]: float(predictions[i]) for i in range(len(emotion_labels))}
        
        return {
            'emotion': emotion,
            'confidence': confidence,
            'all_emotions': emotions_dict,
            'source': 'face',
            'faces_detected': len(faces)
        }
    except Exception as e:
        return None

def analyze_voice(audio_bytes, source_format='wav'):
    """Analyze voice emotion"""
    try:
        if not audio_bytes:
            return None
        
        # Save audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{source_format}') as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            recognizer = sr.Recognizer()
            
            # Try to recognize speech
            try:
                with sr.AudioFile(temp_path) as source:
                    audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
            except:
                return None
            
            # Analyze sentiment
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Map polarity to mood
            if polarity > 0.1:
                mood = 'Happy'
            elif polarity < -0.1:
                mood = 'Sad'
            else:
                mood = 'Neutral'
            
            confidence = abs(polarity)
            
            return {
                'emotion': mood,
                'confidence': confidence,
                'text': text,
                'polarity': polarity,
                'all_emotions': {
                    'Happy': max(0, polarity),
                    'Neutral': 1 - abs(polarity),
                    'Sad': max(0, -polarity)
                },
                'source': 'voice'
            }
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return None

def calculate_consensus(text_result, face_result, voice_result):
    """Calculate majority consensus"""
    emotions = []
    
    if text_result:
        emotions.append(text_result['emotion'])
    if face_result:
        emotions.append(face_result['emotion'])
    if voice_result:
        emotions.append(voice_result['emotion'])
    
    if not emotions:
        return None, None
    
    # Count occurrences
    emotion_counts = {}
    for emotion in emotions:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # Check for consensus (2/3 or 3/3)
    max_count = max(emotion_counts.values())
    if max_count >= 2:
        consensus_emotion = [e for e, c in emotion_counts.items() if c == max_count][0]
        agreement = max_count
        return consensus_emotion, agreement
    else:
        return 'Mixed signals', 0

# ============================================================================
# PAGE LAYOUT
# ============================================================================

# Page Layout
col_header_back, col_header_title = st.columns([0.5, 3])
with col_header_back:
    if st.button("⬅️ Back", key="compare_back", help="Return to home"):
        st.switch_page("home.py")

with col_header_title:
    st.markdown("""
    <h1 style='font-size: 2.8em; font-weight: 800; margin: 0; padding: 0;'>🎭 Emotion Comparison</h1>
    <p style='color: #8b9ac9; font-size: 1.05em; margin: 5px 0 0 0;'>Analyze across text, face, and voice simultaneously</p>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 20px 0 30px 0;'>", unsafe_allow_html=True)

# Load models
nlp_model = load_nlp_model()
face_model = load_face_model()
face_cascade = load_face_cascade()

# Input Section - Three columns
st.markdown("**📥 Provide Inputs**")

input_col1, input_col2, input_col3 = st.columns(3, gap="large")

with input_col1:
    st.markdown("**📝 Text**")
    text_input = st.text_area(
        "Enter text:",
        placeholder="Type your text here...",
        height=150,
        label_visibility="collapsed",
        key="compare_text"
    )

with input_col2:
    st.markdown("**📷 Image**")
    image_input = st.file_uploader(
        "Upload image:",
        type=['jpg', 'jpeg', 'png', 'bmp'],
        label_visibility="collapsed",
        key="compare_image"
    )
    if image_input:
        st.image(image_input, use_column_width=True, caption="Selected image")

with input_col3:
    st.markdown("**🎙️ Audio**")
    audio_input = st.file_uploader(
        "Upload audio:",
        type=['wav', 'mp3', 'ogg', 'm4a', 'flac'],
        label_visibility="collapsed",
        key="compare_audio"
    )
    if audio_input:
        st.audio(audio_input)

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 30px 0;'>", unsafe_allow_html=True)

# Analyze Button
if st.button("🚀 Analyze All Modalities", use_container_width=True, type="primary", key="analyze_all"):
    has_input = bool(text_input or image_input or audio_input)
    
    if not has_input:
        st.error("❌ Please provide at least one input")
    else:
        with st.spinner("🔄 Analyzing all modalities..."):
            st.session_state.compare_results = {
                'text': analyze_text(text_input, load_nlp_model()) if text_input else None,
                'face': analyze_face(image_input.read(), load_face_model(), load_face_cascade()) if image_input else None,
                'voice': analyze_voice(audio_input.read()) if audio_input else None
            }
        st.success("✅ Analysis Complete!")
        st.rerun()

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)

# Initialize session state for results
if 'compare_results' not in st.session_state:
    st.session_state.compare_results = None

# Results Section
if st.session_state.compare_results:
    results = st.session_state.compare_results
    text_result = results['text']
    face_result = results['face']
    voice_result = results['voice']
    
    # THREE-COLUMN RESULTS
    st.markdown("**📊 Individual Results**")
    
    res_col1, res_col2, res_col3 = st.columns(3, gap="large")
    
    with res_col1:
        st.markdown("**📝 Text Analysis**")
        if text_result:
            emotion_emoji = {'anger': '😠', 'disgust': '🤮', 'fear': '😨', 'happy': '😊', 'joy': '😂', 'neutral': '😐', 'sad': '😢', 'sadness': '😢', 'shame': '😳', 'surprise': '😮'}.get(text_result['emotion'].lower(), '😐')
            st.markdown(f"""
            <div style='background: rgba(99, 102, 234, 0.1); border: 2px solid rgba(99, 102, 234, 0.5); border-radius: 12px; padding: 20px; text-align: center;'>
                <div style='font-size: 48px; margin-bottom: 10px;'>{emotion_emoji}</div>
                <div style='font-size: 1.3em; font-weight: 700; color: #f1f5f9;'>{text_result['emotion'].capitalize()}</div>
                <div style='font-size: 1em; font-weight: 600; color: #667eea;'>{text_result['confidence']:.0%}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ No text provided")
    
    with res_col2:
        st.markdown("**📷 Face Analysis**")
        if face_result:
            emotion_emoji = {'Angry': '😠', 'Happy': '😊', 'Neutral': '😐', 'Sad': '😢', 'Surprise': '😮'}.get(face_result['emotion'], '😐')
            st.markdown(f"""
            <div style='background: rgba(99, 102, 234, 0.1); border: 2px solid rgba(99, 102, 234, 0.5); border-radius: 12px; padding: 20px; text-align: center;'>
                <div style='font-size: 48px; margin-bottom: 10px;'>{emotion_emoji}</div>
                <div style='font-size: 1.3em; font-weight: 700; color: #f1f5f9;'>{face_result['emotion']}</div>
                <div style='font-size: 1em; font-weight: 600; color: #667eea;'>{face_result['confidence']:.0%}</div>
                <div style='font-size: 0.85em; color: #8b9ac9; margin-top: 8px;'>👥 {face_result.get('faces_detected', 0)} face(s)</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ No face detected")
    
    with res_col3:
        st.markdown("**🎙️ Voice Analysis**")
        if voice_result:
            emotion_emoji = {'Happy': '😊', 'Sad': '😢', 'Neutral': '😐'}.get(voice_result['emotion'], '😐')
            st.markdown(f"""
            <div style='background: rgba(99, 102, 234, 0.1); border: 2px solid rgba(99, 102, 234, 0.5); border-radius: 12px; padding: 20px; text-align: center;'>
                <div style='font-size: 48px; margin-bottom: 10px;'>{emotion_emoji}</div>
                <div style='font-size: 1.3em; font-weight: 700; color: #f1f5f9;'>{voice_result['emotion']}</div>
                <div style='font-size: 1em; font-weight: 600; color: #667eea;'>{voice_result['confidence']:.0%}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ No speech detected")
    
    st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)
    
    # CONSENSUS SECTION - FULL WIDTH, CENTERED
    consensus_emotion, agreement = calculate_consensus(text_result, face_result, voice_result)
    
    st.markdown("**🎯 Consensus & Insights**")
    
    if consensus_emotion == 'Mixed signals':
        st.warning("⚠️ **Mixed Signals** - Emotions disagree across modalities (1/3 agreement). Check individual results above.")
    else:
        col_consensus, col_chart = st.columns([2, 1])
        
        with col_consensus:
            emoji = EMOTION_EMOJIS.get(consensus_emotion, '😐')
            st.success(f"✅ **Consensus: {emoji} {consensus_emotion}** ({agreement}/3 agreement)")
        
        with col_chart:
            modality_agreement = {'Text': 1 if text_result else 0, 'Face': 1 if face_result else 0, 'Voice': 1 if voice_result else 0}
            fig_agree = go.Figure(data=[go.Bar(x=list(modality_agreement.keys()), y=list(modality_agreement.values()), marker_color=['#667eea', '#8b5cf6', '#d946ef'], showlegend=False)])
            fig_agree.update_layout(height=200, yaxis=dict(range=[0, 1]), template='plotly_dark', margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#f1f5f9'))
            st.plotly_chart(fig_agree, use_container_width=True)

st.markdown("<hr style='border:1px solid rgba(99, 102, 941, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)
render_emotion_timeline()
st.markdown("<hr style='border:1px solid rgba(99, 102, 941, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)
render_persistent_footer()

