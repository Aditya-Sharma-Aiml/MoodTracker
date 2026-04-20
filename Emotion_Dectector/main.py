import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import warnings
import os
from PIL import Image
import logging

warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)

# Page config
st.set_page_config(
    page_title="Emotion Detector",
    page_icon="😊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .title {
        text-align: center;
        color: #4ECDC4;
        font-size: 2.5em;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .emotion-box {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.2em;
        font-weight: bold;
        text-align: center;
    }
    .stat-box {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin: 10px;
        border-left: 4px solid #4ECDC4;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<div class='title'>😊 Real-Time Emotion Detector</div>", unsafe_allow_html=True)
st.markdown("Detect emotions from facial expressions using AI")
st.markdown("---")

# Load cascade classifier and model
@st.cache_resource
def load_models():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cascade_path = os.path.join(script_dir, 'haarcascade_frontalface_default.xml')
    model_path = os.path.join(script_dir, 'model.h5')
    
    if not os.path.exists(cascade_path):
        raise FileNotFoundError(f"Cascade classifier not found at: {cascade_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    
    face_classifier = cv2.CascadeClassifier(cascade_path)
    
    # Load model with better error handling
    try:
        classifier = keras.saving.load_model(model_path)
    except:
        try:
            classifier = keras.models.load_model(model_path, compile=False)
        except:
            classifier = tf.keras.models.load_model(model_path)
    
    return face_classifier, classifier

emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

try:
    face_classifier, classifier = load_models()
    
    # Options
    col1, col2 = st.columns(2)
    
    with col1:
        option = st.radio("Choose Input Method", ["📸 Capture from Camera", "📤 Upload Image"])
    
    detected_image = None
    detected_emotions_list = []
    
    if option == "📸 Capture from Camera":
        st.subheader("📷 Camera Capture")
        
        picture = st.camera_input("Take a picture")
        
        if picture is not None:
            # Read the image from camera
            img_pil = Image.open(picture)
            img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            detected_image = img.copy()
            
            st.success("✓ Photo captured successfully!")
    
    else:
        st.subheader("📤 Upload Image")
        
        uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'jpeg', 'png', 'bmp'])
        
        if uploaded_file is not None:
            img_pil = Image.open(uploaded_file)
            img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            detected_image = img.copy()
            
            st.success("✓ Image uploaded successfully!")
    
    # Process image if available
    if detected_image is not None:
        st.markdown("---")
        st.markdown("## 🔍 Processing Image...")
        
        # Convert to grayscale
        gray = cv2.cvtColor(detected_image, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
        
        # Process each face
        for (x, y, w, h) in faces:
            cv2.rectangle(detected_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_gray = cv2.resize(roi_gray, (48, 48))
            
            if np.sum([roi_gray]) != 0:
                roi = roi_gray.astype('float') / 255.0
                roi = np.expand_dims(roi, axis=0)
                roi = np.expand_dims(roi, axis=-1)
                
                try:
                    prediction = classifier.predict(roi, verbose=0)[0]
                except (ValueError, RuntimeError) as e:
                    logging.warning(f"Prediction verbose=0 failed: {e}. Retrying...")
                    try:
                        prediction = classifier.predict(roi)[0]
                    except Exception as e:
                        st.error(f"Failed to predict emotion: {e}")
                        prediction = None
                
                emotion_idx = np.argmax(prediction)
                label = emotion_labels[emotion_idx]
                confidence = np.max(prediction)
                
                detected_emotions_list.append({
                    'emotion': label,
                    'confidence': confidence,
                    'probabilities': dict(zip(emotion_labels, prediction))
                })
                
                # Draw on image
                label_position = (x, y - 10)
                cv2.putText(detected_image, f"{label}", label_position, 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(detected_image, f"{confidence:.2f}", (x, y + h + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        # Display results
        st.markdown("---")
        st.markdown("## 📊 Results")
        
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.subheader("🖼️ Detected Image")
            detected_image_rgb = cv2.cvtColor(detected_image, cv2.COLOR_BGR2RGB)
            st.image(detected_image_rgb, use_column_width=True)
        
        with col2:
            st.subheader("👤 Detection Summary")
            
            if detected_emotions_list:
                total_faces = len(detected_emotions_list)
                st.metric("Faces Detected", total_faces)
                
                st.markdown("### Emotions Detected:")
                for i, detection in enumerate(detected_emotions_list, 1):
                    st.markdown(f"**Face {i}:** {detection['emotion']}")
                    st.metric(f"Confidence (Face {i})", f"{detection['confidence']:.2%}")
            else:
                st.warning("⚠️ No faces detected in the image. Try another image with clear face visibility.")
        
        # Detailed Analysis
        if detected_emotions_list:
            st.markdown("---")
            st.markdown("## 📈 Detailed Analysis")
            
            for i, detection in enumerate(detected_emotions_list, 1):
                with st.expander(f"Face {i} - {detection['emotion']} ({detection['confidence']:.2%})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### All Probabilities")
                        probs = detection['probabilities']
                        for emotion, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
                            st.write(f"**{emotion}**: {prob:.4f}")
                            st.progress(prob)
                    
                    with col2:
                        # Pie chart
                        fig, ax = plt.subplots(figsize=(6, 4))
                        colors = plt.cm.Set3(np.linspace(0, 1, len(emotion_labels)))
                        ax.pie(detection['probabilities'].values(), 
                               labels=detection['probabilities'].keys(), 
                               autopct='%1.1f%%',
                               colors=colors,
                               startangle=90)
                        ax.set_title(f"Emotion Distribution - Face {i}")
                        st.pyplot(fig, use_container_width=True)
            
            # Overall Statistics
            st.markdown("---")
            st.markdown("## 📊 Overall Statistics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                emotion_counts = {}
                for detection in detected_emotions_list:
                    emotion = detection['emotion']
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                
                most_common = max(emotion_counts.items(), key=lambda x: x[1])[0]
                st.markdown(f"<div class='stat-box'>Most Common<br><strong>{most_common}</strong></div>", 
                           unsafe_allow_html=True)
            
            with col2:
                avg_confidence = np.mean([d['confidence'] for d in detected_emotions_list])
                st.markdown(f"<div class='stat-box'>Average Confidence<br><strong>{avg_confidence:.2%}</strong></div>", 
                           unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"<div class='stat-box'>Total Faces Detected<br><strong>{len(detected_emotions_list)}</strong></div>", 
                           unsafe_allow_html=True)
            
            # Emotion distribution chart
            emotion_counts = {}
            for detection in detected_emotions_list:
                emotion = detection['emotion']
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            fig, ax = plt.subplots(figsize=(10, 5))
            colors = plt.cm.Set3(np.linspace(0, 1, len(emotion_labels)))
            all_emotions = emotion_labels
            counts = [emotion_counts.get(e, 0) for e in all_emotions]
            
            bars = ax.bar(all_emotions, counts, color=colors)
            ax.set_xlabel("Emotion", fontsize=12)
            ax.set_ylabel("Count", fontsize=12)
            ax.set_title("Emotion Distribution Across Detected Faces", fontsize=14, fontweight='bold')
            plt.xticks(rotation=45)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

except FileNotFoundError as e:
    st.error(f"❌ Error: {str(e)}")
    st.warning("Make sure model.h5 and haarcascade_frontalface_default.xml are in the Emotion_Dectector folder")
except Exception as e:
    st.error(f"❌ An error occurred: {str(e)}")
    st.info("Try refreshing the page and uploading another image")

st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 20px; color: #666;'>
        <p><strong>Emotion Detector v2.0</strong></p>
        <p>Made with ❤️ by Aditya Sharma | 2026</p>
    </div>
""", unsafe_allow_html=True)
import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import warnings
warnings.filterwarnings('ignore')
from keras.preprocessing.image import img_to_array
import os
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="Emotion Detector - Webcam",
    page_icon="📷",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .emotion-display {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        font-size: 2em;
        margin: 10px;
    }
    .title {
        text-align: center;
        color: #4ECDC4;
        font-size: 2.5em;
        margin-bottom: 20px;
    }
    .stat-box {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Load cascade classifier and model
@st.cache_resource
def load_models():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cascade_path = os.path.join(script_dir, 'haarcascade_frontalface_default.xml')
    model_path = os.path.join(script_dir, 'model.h5')
    
    if not os.path.exists(cascade_path):
        raise FileNotFoundError(f"Cascade classifier not found at: {cascade_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    
    face_classifier = cv2.CascadeClassifier(cascade_path)
    
    # Load model with better error handling
    try:
        # Try modern approach first
        classifier = keras.saving.load_model(model_path)
    except Exception as e1:
        try:
            # Try legacy HDF5 format
            classifier = keras.models.load_model(model_path, compile=False)
        except Exception as e2:
            try:
                # Try with TensorFlow directly
                classifier = tf.keras.models.load_model(model_path)
            except Exception as e3:
                raise Exception(f"Could not load model with any method. Errors:\n1. {str(e1)}\n2. {str(e2)}\n3. {str(e3)}")
    
    return face_classifier, classifier

emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

# Header
st.markdown("""
    <div class='title'>📷 Real-Time Emotion Detector</div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center; color: #666; margin-bottom: 30px;'>
        <p>Detect emotions from facial expressions using your webcam</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

try:
    face_classifier, classifier = load_models()
    
    # Initialize session state for emotion stats
    if 'emotion_counts' not in st.session_state:
        st.session_state.emotion_counts = {emotion: 0 for emotion in emotion_labels}
    if 'detected_emotions' not in st.session_state:
        st.session_state.detected_emotions = []
    
    # Two main options
    option = st.radio("Select Detection Mode", ["Real-Time Webcam", "Upload Image"])
    
    if option == "Real-Time Webcam":
        st.subheader("🎥 Webcam Stream")
        
        # RTCConfiguration for WebRTC
        rtc_configuration = RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )
        
        class EmotionProcessor:
            def recv(self, frame):
                img = frame.to_ndarray(format="bgr24")
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_classifier.detectMultiScale(gray)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
                    
                    if np.sum([roi_gray]) != 0:
                        roi = roi_gray.astype('float') / 255.0
                        roi = img_to_array(roi)
                        roi = np.expand_dims(roi, axis=0)
                        
                        try:
                            prediction = classifier.predict(roi, verbose=0)[0]
                        except TypeError:
                            # Fallback for older Keras versions
                            prediction = classifier.predict(roi)[0]
                        
                        emotion_idx = prediction.argmax()
                        label = emotion_labels[emotion_idx]
                        confidence = np.max(prediction)
                        
                        # Update statistics
                        st.session_state.emotion_counts[label] += 1
                        st.session_state.detected_emotions.append(label)
                        
                        label_position = (x, y - 10)
                        cv2.putText(img, f"{label} ({confidence:.2f})", label_position, 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    else:
                        cv2.putText(img, 'No Face', (30, 80), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                return av.VideoFrame.from_ndarray(img, format="bgr24")
        
        webrtc_ctx = webrtc_streamer(
            key="emotion-detection",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc_configuration,
            video_processor_factory=EmotionProcessor,
            media_stream_constraints={"video": {"width": {"ideal": 640}}, "audio": False},
            async_processing=True,
        )
        
        st.info("💡 Tip: Make sure your camera is accessible and properly lit for better emotion detection accuracy.")
        
    else:
        st.subheader("📸 Upload an Image")
        
        uploaded_file = st.file_uploader("Choose an image file", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_file is not None:
            # Read image
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_classifier.detectMultiScale(gray)
            
            detected_emotions_list = []
            
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 255), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
                
                if np.sum([roi_gray]) != 0:
                    roi = roi_gray.astype('float') / 255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)
                    
                    try:
                        prediction = classifier.predict(roi, verbose=0)[0]
                    except TypeError:
                        # Fallback for older Keras versions
                        prediction = classifier.predict(roi)[0]
                    
                    emotion_idx = prediction.argmax()
                    label = emotion_labels[emotion_idx]
                    confidence = np.max(prediction)
                    
                    detected_emotions_list.append((label, confidence))
                    
                    label_position = (x, y - 10)
                    cv2.putText(img, f"{label} ({confidence:.2f})", label_position, 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Detected Image")
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                st.image(img_rgb, use_column_width=True)
            
            with col2:
                st.subheader("📊 Detection Results")
                if detected_emotions_list:
                    for emotion, confidence in detected_emotions_list:
                        st.write(f"**{emotion}**: {confidence:.2f} confidence")
                        st.progress(confidence)
                else:
                    st.warning("No faces detected in the image.")

    st.markdown("---")
    
    # Statistics section
    if sum(st.session_state.emotion_counts.values()) > 0:
        st.subheader("📈 Emotion Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 6))
            emotions = list(st.session_state.emotion_counts.keys())
            counts = list(st.session_state.emotion_counts.values())
            colors = plt.cm.Set3(np.linspace(0, 1, len(emotions)))
            ax.bar(emotions, counts, color=colors)
            ax.set_xlabel("Emotion")
            ax.set_ylabel("Count")
            ax.set_title("Detected Emotions Distribution")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.markdown("### Detection Summary")
            total_detections = sum(st.session_state.emotion_counts.values())
            st.metric("Total Detections", total_detections)
            
            st.markdown("### Emotion Breakdown")
            for emotion, count in st.session_state.emotion_counts.items():
                if count > 0:
                    percentage = (count / total_detections) * 100
                    st.write(f"{emotion}: {count} ({percentage:.1f}%)")

except FileNotFoundError as e:
    st.error(f"❌ Error: {str(e)}")
    st.warning("Make sure the model files are in the correct directory")

st.markdown("---")

# Footer
st.markdown("""
    <div style='text-align: center; padding: 20px; color: #666; border-top: 1px solid #eee; margin-top: 30px;'>
        <p><strong>Webcam Emotion Detector v1.0</strong></p>
        <p>Made by <strong>Aditya Sharma</strong></p>
        <p>© 2024 MoodTracker. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)