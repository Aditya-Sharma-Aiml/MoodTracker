import streamlit as st

# Page config
st.set_page_config(
    page_title="MoodTracker - Emotion Analysis Hub",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #FF6B6B;
        font-size: 3.5em;
        font-weight: bold;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .subtitle {
        text-align: center;
        color: #4ECDC4;
        font-size: 1.3em;
        margin-bottom: 30px;
    }
    .project-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 10px;
        color: white;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    .project-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    .project-card-title {
        font-size: 1.8em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .project-card-desc {
        font-size: 1em;
        margin-bottom: 15px;
        line-height: 1.6;
    }
    .features-list {
        font-size: 0.95em;
        margin: 10px 0;
    }
    .features-list li {
        margin: 5px 0;
    }
    .link-button {
        display: inline-block;
        background-color: #FFE66D;
        color: #333;
        padding: 12px 28px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 10px;
        cursor: pointer;
        font-size: 1.1em;
    }
    .link-button:hover {
        background-color: #FFD93D;
        transform: scale(1.05);
    }
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
    }
    .stats-box {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='main-title'>🎭 MoodTracker</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Multi-Modal Emotion Analysis Hub</div>", unsafe_allow_html=True)

# Hero Section
st.markdown("""
    <div class='hero-section'>
        <h2>Analyze Your Emotions in Multiple Ways</h2>
        <p>Detect emotions from text, facial expressions, or voice with cutting-edge AI technology</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Stats Section
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
        <div class='stats-box'>
            <h3>📷 3</h3>
            <p>Active Projects</p>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class='stats-box'>
            <h3>🎯 93%</h3>
            <p>Max Accuracy</p>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div class='stats-box'>
            <h3>⚡ Real-Time</h3>
            <p>Processing</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Projects Section
st.markdown("## 🚀 Active Projects")

# Project 1: NLP Text Emotion
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("""
        <div class='project-card' style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'>
            <div class='project-card-title'>📝 NLP Text Emotion Classifier</div>
            <div class='project-card-desc'>
                Predict emotions from text with 93% accuracy using advanced NLP techniques.
            </div>
            <div class='features-list'>
                <strong>✨ Features:</strong>
                <ul>
                    <li>📊 Real-time emotion detection from text</li>
                    <li>💯 Confidence scores and probability distribution</li>
                    <li>📈 Beautiful visualization with charts</li>
                    <li>🎯 10 emotion categories</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🚀 Launch", key="btn_nlp", help="Open NLP Text Emotion Classifier", use_container_width=True):
        st.switch_page("pages/1_nlp_text_emotion.py")

st.markdown("")

# Project 2: Real-Time Face Detection
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("""
        <div class='project-card' style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);'>
            <div class='project-card-title'>📷 Real-Time Emotion Detection</div>
            <div class='project-card-desc'>
                Detect emotions from webcam or upload images with deep learning (NEW: Image Upload Feature ✨)
            </div>
            <div class='features-list'>
                <strong>✨ Features:</strong>
                <ul>
                    <li>🎥 Live webcam emotion detection</li>
                    <li>📤 Upload and analyze images (NEW!)</li>
                    <li>😊 5 emotion categories</li>
                    <li>⚡ Real-time processing</li>
                    <li>🔍 Multi-face detection</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🚀 Launch", key="btn_realtime", help="Open Real-Time Emotion Detection", use_container_width=True):
        st.switch_page("pages/2_realtime_detection.py")

st.markdown("")

# Project 3: Voice Mood Analyzer
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("""
        <div class='project-card' style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);'>
            <div class='project-card-title'>🎙️ Voice Mood Analyzer</div>
            <div class='project-card-desc'>
                Analyze your mood from voice using speech recognition and sentiment analysis.
            </div>
            <div class='features-list'>
                <strong>✨ Features:</strong>
                <ul>
                    <li>🎤 Speech-to-text conversion</li>
                    <li>💭 Real-time sentiment analysis</li>
                    <li>📊 Mood classification</li>
                    <li>📈 Voice analytics dashboard</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🚀 Launch", key="btn_voice", help="Open Voice Mood Analyzer", use_container_width=True):
        st.switch_page("pages/3_voice_analyzer.py")

st.markdown("---")

# Info Section
st.markdown("## 📋 Project Information")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### ✅ Available Projects
    
    - **📝 NLP Text Emotion**: Analyze emotions from text (93% accuracy)
    - **📷 Real-Time Detection**: Detect emotions from webcam or images
    - **🎙️ Voice Mood Analyzer**: Analyze mood from voice input
    
    ### 🎯 Current Status
    ✅ All projects integrated and ready to use!
    ✅ Multi-page Streamlit navigation enabled
    """)

with col2:
    st.markdown("""
    ### 🚀 How to Use
    
    1. Click any "🚀 Launch" button above
    2. Navigate seamlessly between projects
    3. All features available in one app!
    
    ### 💡 Tips
    - Keep webcam in good lighting for best results
    - Supported image formats: JPG, PNG, BMP
    - Text analysis supports up to 2000 characters
    - Voice recording requires microphone access
    """)

st.markdown("---")

# Footer
st.markdown("""
    <div style='text-align: center; padding: 20px; color: #666; border-top: 1px solid #eee;'>
        <p><strong>🎭 MoodTracker v1.0</strong></p>
        <p>Made by Aditya Sharma | © 2024 All rights reserved</p>
        <p style='font-size: 0.9em;'>Production Ready • AI Powered • Real-Time Processing</p>
    </div>
""", unsafe_allow_html=True)

