
import numpy as np
import cv2
import streamlit as st
from tensorflow.keras.models import model_from_json
from tensorflow.keras.preprocessing.image import img_to_array
import logging
import datetime
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, 'models')

# Page Configuration
st.set_page_config(
    page_title="Emotion Detection", 
    page_icon="😊", 
    layout="centered"
)

# Logging setup
log_filename = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
logging.basicConfig(
    filename=log_filename, 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Application started.")

# Emotion labels
emotion_labels = {0: 'Angry', 1: 'Happy', 2: 'Neutral', 3: 'Sad', 4: 'Surprise'}

# Load Model
@st.cache_resource
def load_model():
    try:
        import tensorflow as tf
        from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Dropout, Flatten, Dense
        
        # Try method 1: Load from HDF5 with custom objects
        try:
            model_path = os.path.join(MODEL_DIR, 'face_emotion_model1.h5')
            emotion_model = tf.keras.models.load_model(
                model_path,
                custom_objects={'Sequential': tf.keras.models.Sequential}
            )
            logging.info("Model loaded from HDF5 successfully.")
            return emotion_model
        except Exception as e1:
            logging.warning(f"Method 1 failed: {e1}")
            
            # Method 2: Reconstruct model from JSON and load weights
            json_path = os.path.join(MODEL_DIR, 'face_emotion_model1.json')
            with open(json_path, 'r') as f:
                model_structure = f.read()
            
            emotion_model = tf.keras.models.model_from_json(
                model_structure,
                custom_objects={'Sequential': tf.keras.models.Sequential}
            )
            weight_path = os.path.join(MODEL_DIR, 'face_emotion_model1.h5')
            emotion_model.load_weights(weight_path)
            logging.info("Model loaded from JSON+HDF5 successfully.")
            return emotion_model
            
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        st.error(f"❌ Error loading model: {e}")
        return None

# Load Haar Cascade
@st.cache_resource
def load_face_detector():
    try:
        cascade_path = os.path.join(MODEL_DIR, 'face_haarcascade_frontalface_default.xml')
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
    st.title("🎥 Real-Time Emotion Detection")
    st.markdown("---")
    
    # Load models
    emotion_model = load_model()
    face_detector = load_face_detector()
    
    if emotion_model is None or face_detector is None:
        st.error("❌ Failed to load required models. Please check the errors above.")
        return
    
    st.success("✅ Models loaded successfully!")
    st.markdown("---")
    
    # Input method selection
    col1, col2 = st.columns(2)
    with col1:
        input_method = st.radio("Choose Input Method", ["📷 Webcam", "📤 Upload Image"])
    
    picture = None
    
    if input_method == "📷 Webcam":
        st.subheader("📷 Capture from Webcam")
        picture = st.camera_input("Take a picture")
    else:
        st.subheader("📤 Upload Image")
        uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'jpeg', 'png', 'bmp'])
        if uploaded_file is not None:
            picture = uploaded_file
    
    if picture is not None:
        # Convert to numpy array
        try:
            if hasattr(picture, 'read'):
                image_bytes = picture.read()
            else:
                image_bytes = picture.getvalue() if hasattr(picture, 'getvalue') else picture
            
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Detect emotions
            processed_image, emotions = detect_emotions(image, emotion_model, face_detector)
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(
                    cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB),
                    caption="Detected Emotions",
                    use_column_width=True
                )
            
            with col2:
                st.subheader("📊 Results")
                if emotions:
                    st.success(f"✅ Detected {len(emotions)} face(s)")
                    for i, result in enumerate(emotions, 1):
                        st.write(f"**Face {i}:**")
                        st.write(f"- Emotion: **{result['emotion']}**")
                        st.write(f"- Confidence: **{result['confidence']:.2%}**")
                        st.divider()
                else:
                    st.info("ℹ️ No faces detected in the image.")
        except Exception as e:
            st.error(f"❌ Error processing image: {e}")
            logging.error(f"Image processing error: {e}")
    
    st.markdown("---")
    st.markdown("""
    ### 💡 Features:
    - 😊 Detect emotions: Angry, Happy, Neutral, Sad, Surprise
    - 🎯 Real-time face detection using Haar Cascade
    - 🧠 Deep Learning model for accurate classification
    """)
    
    st.markdown("""
    **📝 Note:** Click "Take a photo" to capture an image from your webcam and detect emotions in real-time.
    """)

if __name__ == "__main__":
    main()
    logging.info("Application running successfully.")