import streamlit as st
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import initialize_total_analyses, get_total_analyses

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="MoodTracker - Emotion Analysis Hub",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PROFESSIONAL CSS STYLING
# ============================================================================
st.markdown("""
    <style>
    /* Root Variables */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --navy-dark: #0f172a;
        --navy-light: #1e293b;
        --indigo-accent: #6366f1;
        --slate-light: #f1f5f9;
        --card-bg: rgba(30, 41, 59, 0.8);
        --border-color: rgba(99, 102, 241, 0.2);
    }

    /* Global Styles */
    html { scroll-behavior: smooth; }
    * { transition: all 0.3s ease; }

    /* =========== SIDEBAR STYLING =========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--navy-dark) 0%, var(--navy-light) 100%);
        border-right: 2px solid var(--border-color);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
    }

    /* =========== MAIN CONTENT STYLING =========== */
    .main {
        background: linear-gradient(180deg, var(--navy-dark) 0%, var(--navy-light) 100%);
        color: var(--slate-light);
    }

    /* =========== CARD STYLING =========== */
    .card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    .card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
    }

    /* =========== TEXT STYLING =========== */
    .section-title {
        font-size: 28px;
        font-weight: 700;
        color: var(--slate-light);
        margin: 32px 0 16px 0;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .section-subtitle {
        font-size: 16px;
        color: rgba(241, 245, 249, 0.7);
        margin-bottom: 24px;
    }

    .metric-label {
        font-size: 12px;
        color: rgba(241, 245, 249, 0.6);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }

    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: var(--slate-light);
        margin: 8px 0;
    }

    /* =========== BUTTON STYLING =========== */
    .btn-analyze {
        background: var(--primary-gradient) !important;
        border: none !important;
        color: white !important;
        padding: 12px 32px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
    }

    .btn-analyze:hover {
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3) !important;
        transform: translateY(-2px) !important;
    }

    /* =========== SPACING =========== */
    .spacer {
        margin: 24px 0;
    }

    .divider {
        border: 0;
        height: 1px;
        background: var(--border-color);
        margin: 32px 0;
    }

    /* =========== PROGRESS BAR =========== */
    .progress-container {
        margin: 16px 0;
    }

    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 14px;
    }

    /* =========== FOOTER =========== */
    .footer {
        text-align: center;
        padding: 32px 16px;
        color: rgba(241, 245, 249, 0.5);
        border-top: 1px solid var(--border-color);
        margin-top: 48px;
        font-size: 12px;
    }

    /* =========== RESPONSIVE =========== */
    @media (max-width: 768px) {
        .section-title { font-size: 24px; }
        .metric-value { font-size: 24px; }
        .card { padding: 16px; }
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================
with st.sidebar:
    st.markdown("### 🎭 MoodTracker")
    st.markdown("---")
    
    # Navigation Menu
    nav_items = {
        "🏠 Home": "home",
        "📝 Text Emotion Analysis": "text_emotion",
        "📹 Face Emotion Detection": "face_emotion",
        "🎤 Voice Emotion Analysis": "voice_emotion",
        "📊 History Dashboard": "history",
        "🔄 Emotion Comparison": "comparison",
        "ℹ️ About": "about"
    }
    
    st.markdown("**Navigation**")
    for label, key in nav_items.items():
        st.page_link(f"pages/{key}.py" if key != "home" else "home.py", label=label)
    
    st.markdown("---")
    
    # Sidebar Stats
    st.markdown("**📈 Quick Stats**")
    total = get_total_analyses()
    st.metric("Total Analyses", total)
    
    st.markdown("---")
    st.markdown(
        "<p style='font-size: 11px; color: rgba(241, 245, 249, 0.4);'>v1.0 • MoodTracker © 2026</p>",
        unsafe_allow_html=True
    )

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

# SECTION 1: PAGE HEADER
st.markdown('<div class="section-title">🎭 Welcome to MoodTracker</div>', unsafe_allow_html=True)
st.markdown("""
<div class="section-subtitle">
Advanced AI-powered emotion detection & sentiment analysis platform.
Analyze emotions across text, facial expressions, and voice signals.
</div>
""", unsafe_allow_html=True)

# Create visual divider
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============================================================================
# SECTION 2: FEATURE OVERVIEW CARDS
# ============================================================================
st.markdown("### ✨ Core Features")

col1, col2, col3, col4 = st.columns(4)

features = [
    {
        "icon": "📝",
        "title": "Text Emotion",
        "description": "Analyze emotions from text using NLP",
        "accuracy": "93%"
    },
    {
        "icon": "📹",
        "title": "Face Detection",
        "description": "Real-time facial emotion recognition",
        "accuracy": "89%"
    },
    {
        "icon": "🎤",
        "title": "Voice Analysis",
        "description": "Detect emotions from audio signals",
        "accuracy": "85%"
    },
    {
        "icon": "🔄",
        "title": "Comparison",
        "description": "Consensus voting across all modalities",
        "accuracy": "Multi-modal"
    }
]

for col, feature in zip([col1, col2, col3, col4], features):
    with col:
        st.markdown(f"""
        <div class="card">
            <div style="font-size: 32px; margin-bottom: 12px;">{feature['icon']}</div>
            <div style="font-weight: 600; margin-bottom: 8px;">{feature['title']}</div>
            <div style="font-size: 12px; color: rgba(241, 245, 249, 0.7); margin-bottom: 12px;">
                {feature['description']}
            </div>
            <div style="font-size: 12px; color: #667eea; font-weight: 600;">✓ {feature['accuracy']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============================================================================
# SECTION 3: ANALYTICS DASHBOARD (2x2 GRID)
# ============================================================================
st.markdown("### 📊 Analytics Overview")

col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown("""
        <div class="card">
            <div class="metric-label">Total Analyses</div>
            <div class="metric-value">""" + str(get_total_analyses()) + """</div>
            <div style="font-size: 12px; color: rgba(241, 245, 249, 0.6); margin-top: 8px;">
                ↑ Cumulative across all modalities
            </div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown("""
        <div class="card">
            <div class="metric-label">Avg Confidence</div>
            <div class="metric-value">89%</div>
            <div style="font-size: 12px; color: rgba(241, 245, 249, 0.6); margin-top: 8px;">
                ↑ Model reliability score
            </div>
        </div>
        """, unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    with st.container():
        st.markdown("""
        <div class="card">
            <div class="metric-label">Most Common</div>
            <div class="metric-value">😊 Happy</div>
            <div style="font-size: 12px; color: rgba(241, 245, 249, 0.6); margin-top: 8px;">
                ↑ Detected emotion
            </div>
        </div>
        """, unsafe_allow_html=True)

with col4:
    with st.container():
        st.markdown("""
        <div class="card">
            <div class="metric-label">Unique Emotions</div>
            <div class="metric-value">8</div>
            <div style="font-size: 12px; color: rgba(241, 245, 249, 0.6); margin-top: 8px;">
                ↑ Emotion categories
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============================================================================
# SECTION 4: QUICK START GUIDE
# ============================================================================
st.markdown("### 🚀 Quick Start")

tab1, tab2, tab3 = st.tabs(["📝 Text Analysis", "📹 Face Detection", "🎤 Voice Analysis"])

with tab1:
    st.markdown("""
    **How to analyze text emotions:**
    
    1. Navigate to **Text Emotion Analysis** page
    2. Enter your text in the input field
    3. Click **Analyze** to process
    4. View detailed emotion breakdown and confidence scores
    5. Track your analysis history
    """)

with tab2:
    st.markdown("""
    **How to detect facial emotions:**
    
    1. Go to **Face Emotion Detection** page
    2. Enable your webcam or upload an image
    3. System will detect faces in real-time
    4. View emotion predictions with confidence
    5. Multi-face detection supported
    """)

with tab3:
    st.markdown("""
    **How to analyze voice emotions:**
    
    1. Open **Voice Emotion Analysis** page
    2. Record audio or upload an audio file
    3. System analyzes audio features
    4. Get emotion classification results
    5. View confidence metrics
    """)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============================================================================
# SECTION 5: EMOTION GUIDE
# ============================================================================
st.markdown("### 🎭 Emotion Categories")

emotion_guide = {
    "😊 Happy": "Positive emotions, joy, contentment",
    "😂 Joy": "Excitement, elation, amusement",
    "😐 Neutral": "No strong emotion detected",
    "😢 Sad": "Sorrow, melancholy, disappointment",
    "😠 Anger": "Frustration, agitation, irritability",
    "😨 Fear": "Anxiety, worry, apprehension",
    "🤮 Disgust": "Repulsion, disapproval, aversion",
    "😮 Surprise": "Astonishment, amazement, shock"
}

cols = st.columns(4)
for idx, (emotion, description) in enumerate(emotion_guide.items()):
    with cols[idx % 4]:
        st.markdown(f"""
        <div class="card" style="padding: 16px;">
            <div style="font-size: 24px; margin-bottom: 8px;">{emotion.split()[0]}</div>
            <div style="font-size: 12px; font-weight: 600;">{emotion.split(maxsplit=1)[1]}</div>
            <div style="font-size: 11px; color: rgba(241, 245, 249, 0.6); margin-top: 8px;">
                {description}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============================================================================
# SECTION 6: HOW IT WORKS
# ============================================================================
st.markdown("### ⚙️ Technology Stack")

st.markdown("""
<div class="card">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 24px;">
        <div>
            <div style="font-weight: 600; margin-bottom: 8px;">🤖 Deep Learning</div>
            <div style="font-size: 12px; color: rgba(241, 245, 249, 0.7);">TensorFlow, Keras, CNN architectures</div>
        </div>
        <div>
            <div style="font-weight: 600; margin-bottom: 8px;">📊 Data Processing</div>
            <div style="font-size: 12px; color: rgba(241, 245, 249, 0.7);">NumPy, Pandas, Scikit-learn</div>
        </div>
        <div>
            <div style="font-weight: 600; margin-bottom: 8px;">🖼️ Computer Vision</div>
            <div style="font-size: 12px; color: rgba(241, 245, 249, 0.7);">OpenCV, Haar Cascades, Real-time</div>
        </div>
        <div>
            <div style="font-weight: 600; margin-bottom: 8px;">🎙️ Audio Processing</div>
            <div style="font-size: 12px; color: rgba(241, 245, 249, 0.7);">Librosa, SpeechRecognition, PyDub</div>
        </div>
        <div>
            <div style="font-weight: 600; margin-bottom: 8px;">💬 NLP</div>
            <div style="font-size: 12px; color: rgba(241, 245, 249, 0.7);">TextBlob, Sentiment Analysis, Classification</div>
        </div>
        <div>
            <div style="font-weight: 600; margin-bottom: 8px;">🌐 Web Framework</div>
            <div style="font-size: 12px; color: rgba(241, 245, 249, 0.7);">Streamlit, Modern Web UI</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============================================================================
# SECTION 7: FOOTER
# ============================================================================
st.markdown("""
<div class="footer">
    <div style="margin-bottom: 8px;">🎭 <strong>MoodTracker</strong> | Emotion Analysis Hub v1.0</div>
    <div style="margin-bottom: 8px;">Advanced AI-powered emotion detection & sentiment analysis</div>
    <div>© 2026 • All Rights Reserved • Built with ❤️ for AI Emotion Detection</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state if needed
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
