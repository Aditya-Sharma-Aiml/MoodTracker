import numpy as np
import cv2
import streamlit as st
from tensorflow.keras.preprocessing.image import img_to_array
import logging
import datetime
import os

# Get the directory where the Real-Time Emotion Detection project is
realtime_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Real-Time-Emotion-Detection')
MODEL_DIR = os.path.join(realtime_dir, 'models')

# Page Configuration
st.set_page_config(
    page_title="Real-Time Emotion Detection",
    page_icon="📷",
    layout="wide"
)

# Add back button
col1, col2, col3 = st.columns([1, 10, 1])
with col1:
    if st.button("⬅️ Back", key="realtime_back_btn", help="Return to home page", use_container_width=True):
        st.switch_page("landing_page.py")

# Custom CSS
st.markdown("""
    <style>
    .emotion-result {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .face-count {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 1.2em;
        font-weight: bold;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

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
        
        # Try loading from HDF5 with custom_objects for compatibility
        try:
            # Define custom_objects for backward compatibility
            custom_objects = {
                'Sequential': Sequential
            }
            emotion_model = load_model(model_path, custom_objects=custom_objects)
            logging.info("Model loaded from HDF5 successfully with custom objects.")
            return emotion_model
        except Exception as e1:
            logging.warning(f"HDF5 load with custom_objects failed: {e1}")
            
            # Try without custom objects
            try:
                emotion_model = load_model(model_path)
                logging.info("Model loaded from HDF5 successfully (direct load).")
                return emotion_model
            except Exception as e2:
                logging.warning(f"Direct HDF5 load failed: {e2}")
                
                # Try loading from JSON + weights
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
                    logging.error(f"All loading methods failed: HDF5={e1}, Direct={e2}, JSON={e3}")
                    raise Exception(f"Model loading failed. Tried HDF5 and JSON methods. Last error: {e3}")
                
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

# Process image for emotion detection
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
            # Draw rectangle around face
            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Extract face ROI
            face_roi = frame_gray[y:y + h, x:x + w]
            face_roi = cv2.resize(face_roi, (48, 48))
            face_roi = face_roi.astype('float32') / 255.0
            face_roi = img_to_array(face_roi)
            face_roi = np.expand_dims(face_roi, axis=0)
            
            # Predict emotion
            predictions = emotion_model.predict(face_roi, verbose=0)[0]
            max_index = np.argmax(predictions)
            emotion = emotion_labels[max_index]
            confidence = float(predictions[max_index])
            
            emotions_detected.append({
                "emotion": emotion,
                "confidence": confidence,
                "position": (x, y)
            })
            
            # Put text on frame
            label = f"{emotion} ({confidence:.2f})"
            cv2.putText(
                frame_bgr,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2
            )
        
        return frame_bgr, emotions_detected
    
    except Exception as e:
        logging.error(f"Error during emotion detection: {e}")
        st.error(f"❌ Error processing image: {e}")
        return image_array, []

# Main App
def main():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: #4facfe; font-size: 3em;'>📷 Real-Time Emotion Detection</h1>
            <p style='color: #666; font-size: 1.2em;'>Detect emotions from webcam or images using Deep Learning</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Load models
    emotion_model = load_model()
    face_detector = load_face_detector()
    
    if emotion_model is None or face_detector is None:
        st.error("❌ Failed to load required models. Please ensure all model files exist.")
        st.info("ℹ️ Required files:")
        st.write("- models/face_emotion_model1.h5")
        st.write("- models/face_emotion_model1.json (optional)")
        st.write("- models/face_haarcascade_frontalface_default.xml")
        return
    
    st.success("✅ Models loaded successfully!")
    st.markdown("---")
    
    # Input method selection
    col1, col2 = st.columns(2)
    with col1:
        input_method = st.radio("Choose Input Method:", ["📷 Webcam", "📤 Upload Image"], horizontal=True)
    
    picture = None
    
    if input_method == "📷 Webcam":
        st.subheader("📷 Capture from Webcam")
        st.info("📸 Click 'Take a picture' to capture an image and detect emotions")
        picture = st.camera_input("Take a picture")
    else:
        st.subheader("📤 Upload Image")
        st.info("📁 Upload an image (JPG, PNG, BMP) to analyze emotions")
        uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'jpeg', 'png', 'bmp'])
        if uploaded_file is not None:
            picture = uploaded_file
    
    if picture is not None:
        # Convert to numpy array
        try:
            with st.spinner("🔄 Processing image..."):
                if hasattr(picture, 'read'):
                    image_bytes = picture.read()
                else:
                    image_bytes = picture.getvalue() if hasattr(picture, 'getvalue') else picture
                
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    st.error("❌ Failed to decode image. Please try another image.")
                    return
                
                # Detect emotions
                processed_image, emotions = detect_emotions(image, emotion_model, face_detector)
            
            st.success("✅ Detection Complete!")
            
            # Display results
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📸 Processed Image")
                st.image(
                    cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB),
                    caption="Detected Emotions",
                    use_column_width=True
                )
            
            with col2:
                st.subheader("📊 Detection Results")
                if emotions:
                    st.markdown(f"""
                        <div class='face-count'>
                            ✅ Detected {len(emotions)} face(s)
                        </div>
                    """, unsafe_allow_html=True)
                    
                    for i, result in enumerate(emotions, 1):
                        emotion = result['emotion']
                        confidence = result['confidence']
                        
                        emotion_emojis = {
                            'Angry': '😠',
                            'Happy': '😊',
                            'Neutral': '😐',
                            'Sad': '😢',
                            'Surprise': '😮'
                        }
                        
                        emoji = emotion_emojis.get(emotion, '😐')
                        
                        st.markdown(f"""
                            <div class='emotion-result'>
                                <h3>👤 Face {i}: {emoji} {emotion}</h3>
                                <p style='font-size: 1.1em; margin: 5px 0;'>
                                    <strong>Confidence: {confidence:.2%}</strong>
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("ℹ️ No faces detected in the image. Try uploading a clearer image with visible faces.")
        
        except Exception as e:
            st.error(f"❌ Error processing image: {e}")
            logging.error(f"Image processing error: {e}")
    
    st.markdown("---")
    
    # Features section
    st.subheader("💡 Features:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **😊 5 Emotion Categories:**
        - 😠 Angry
        - 😊 Happy
        - 😐 Neutral
        - 😢 Sad
        - 😮 Surprise
        """)
    
    with col2:
        st.markdown("""
        **🎯 Advanced Detection:**
        - Real-time face detection
        - Multi-face support
        - Confidence scores
        - Haar Cascade classifier
        """)
    
    with col3:
        st.markdown("""
        **⚡ Performance:**
        - Fast processing
        - Deep learning model
        - High accuracy
        - GPU compatible
        """)
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px; color: #666; border-top: 1px solid #eee;'>
        <p><strong>🎭 MoodTracker - Real-Time Emotion Detection</strong></p>
        <p>Powered by TensorFlow & OpenCV | Made by Aditya Sharma</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    logging.info("Application running successfully.")
