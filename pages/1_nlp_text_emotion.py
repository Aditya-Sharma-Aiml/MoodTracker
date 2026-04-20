import streamlit as st
import numpy as np
import pandas as pd
import joblib
import altair as alt
import os

# Page config
st.set_page_config(
    page_title="NLP Text Emotion Classifier",
    page_icon="📝",
    layout="wide"
)

# Add back button
col1, col2, col3 = st.columns([1, 10, 1])
with col1:
    if st.button("⬅️ Back", key="nlp_back_btn", help="Return to home page", use_container_width=True):
        st.switch_page("landing_page.py")

# Custom CSS
st.markdown("""
    <style>
    .emotion-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .confidence-box {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Get the directory of the NLP project
nlp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NLP-Text-Emotion')
model_path = os.path.join(nlp_dir, 'models', 'emotion_classifier_pipe_lr_03_jan_2022.pkl')

# Load the model with error handling
@st.cache_resource
def load_model():
    try:
        if not os.path.exists(model_path):
            st.error(f"❌ Model file not found at: {model_path}")
            return None
        with open(model_path, 'rb') as f:
            pipe_lr = joblib.load(f)
        return pipe_lr
    except Exception as e:
        st.error(f"❌ Error loading model: {str(e)}")
        return None

# Load model
pipe_lr = load_model()

if pipe_lr is None:
    st.warning("⚠️ Model could not be loaded. Please ensure the model file exists.")
    st.stop()

# Function to predict emotions
def predict_emotions(docx):
    results = pipe_lr.predict([docx])
    return results

def get_prediction_proba(docx):
    results = pipe_lr.predict_proba([docx])
    return results

emotions_emoji_dict = {
    "anger": "😠",
    "disgust": "🤮",
    "fear": "😨😱",
    "happy": "🤗",
    "joy": "😂",
    "neutral": "😐",
    "sad": "😔",
    "sadness": "😔",
    "shame": "😳",
    "surprise": "😮"
}

# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# Header
st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='color: #f5576c; font-size: 3em;'>📝 NLP Text Emotion Classifier</h1>
        <p style='color: #666; font-size: 1.2em;'>Detect Emotions from Text with 93% Accuracy</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Info box
st.info("🎯 **How it works:** Enter any text and our advanced NLP model will analyze it to determine the emotion with high accuracy. Get confidence scores and probability distributions for each emotion category.")

# Main form
with st.form(key='emotion_clf_form'):
    raw_text = st.text_area("📝 Enter your text here:", placeholder="Type something and I'll analyze the emotion...", height=150)
    submit_text = st.form_submit_button(label="🔍 Analyze Emotion", use_container_width=True)

if submit_text:
    if not raw_text or len(raw_text.strip()) == 0:
        st.error("❌ Please enter some text to analyze")
    else:
        with st.spinner("🔄 Analyzing emotion..."):
            prediction = predict_emotions(raw_text)
            probability = get_prediction_proba(raw_text)
            
            # Save to history
            st.session_state.analysis_history.append({
                'text': raw_text,
                'emotion': prediction[0],
                'confidence': np.max(probability)
            })
        
        st.success("✅ Analysis Complete!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Original Text")
            st.write(raw_text)
            
            st.subheader("🎯 Predicted Emotion")
            emoji_icon = emotions_emoji_dict.get(prediction[0], "😐")
            st.markdown(f"""
                <div class='emotion-card'>
                    <h2>{emoji_icon} {prediction[0].upper()}</h2>
                    <p style='font-size: 1.2em; margin: 10px 0;'>Confidence: <strong>{np.max(probability):.2%}</strong></p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📊 Emotion Probability Distribution")
            proba_df = pd.DataFrame(probability, columns=pipe_lr.classes_)
            proba_df_clean = proba_df.transpose().reset_index()
            proba_df_clean.columns = ["Emotion", "Probability"]
            
            # Sort by probability descending
            proba_df_clean = proba_df_clean.sort_values('Probability', ascending=False)
            
            st.dataframe(proba_df_clean.style.format({'Probability': '{:.2%}'}), use_container_width=True)
            
            # Chart
            fig = alt.Chart(proba_df_clean).mark_bar().encode(
                x=alt.X('Emotion:N', title='Emotion'),
                y=alt.Y('Probability:Q', title='Probability'),
                color=alt.Color('Emotion:N', title='Emotion')
            ).interactive()
            
            st.altair_chart(fig, use_container_width=True)

st.markdown("---")

# Statistics
if st.session_state.analysis_history:
    st.subheader("📈 Analysis History")
    
    history_df = pd.DataFrame(st.session_state.analysis_history)
    emotion_counts = history_df['emotion'].value_counts()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Analyses", len(st.session_state.analysis_history))
    
    with col2:
        st.metric("Most Common", emotion_counts.index[0] if len(emotion_counts) > 0 else "N/A")
    
    with col3:
        avg_confidence = history_df['confidence'].mean()
        st.metric("Avg. Confidence", f"{avg_confidence:.2%}")
    
    st.write("**Recent Analyses:**")
    for idx, item in enumerate(reversed(st.session_state.analysis_history[-5:])):
        st.write(f"- **{item['emotion'].upper()}** ({item['confidence']:.2%}): _{item['text'][:50]}..._")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 20px; color: #666; border-top: 1px solid #eee;'>
        <p><strong>🎭 MoodTracker - NLP Text Emotion Classifier</strong></p>
        <p>Powered by Scikit-learn | 93% Accuracy | Made by Aditya Sharma</p>
    </div>
""", unsafe_allow_html=True)
