import streamlit as st
import streamlit.components.v1 as components
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import initialize_total_analyses, get_total_analyses

# Page config
st.set_page_config(
    page_title="MoodTracker - Emotion Analysis Hub",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CUSTOM CSS - Dark Theme with Glassmorphism & Animations
# ============================================================================
st.markdown("""
    <style>
    /* Root Variables */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --success-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --navy-dark: #0f172a;
        --navy-light: #1e293b;
        --indigo-accent: #6366f1;
        --slate-light: #f1f5f9;
    }

    /* Smooth scrolling & global transitions */
    html {
        scroll-behavior: smooth;
    }

    * {
        transition: all 0.3s ease;
    }

    /* ============================================================================
       SIDEBAR STYLING
       ============================================================================ */
    
    /* Sidebar Container */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--navy-dark) 0%, var(--navy-light) 100%);
        border-right: 2px solid rgba(99, 102, 241, 0.2);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }

    /* Sidebar Section Container */
    .streamlit-expanderHeader {
        background: rgba(99, 102, 241, 0.05) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(99, 102, 241, 0.1) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
    }

    /* Sidebar Text & Links */
    [data-testid="stSidebar"] label {
        color: var(--slate-light) !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.75em !important;
    }

    [data-testid="stSidebar"] p {
        color: var(--slate-light) !important;
    }

    /* Sidebar Links & Navigation */
    [data-testid="stSidebar"] a {
        color: var(--slate-light) !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stSidebar"] a:hover {
        color: var(--indigo-accent) !important;
        text-decoration: none !important;
    }

    /* Active page indicator */
    [data-testid="stSidebar"] [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.25) !important;
        border-left: 3px solid var(--indigo-accent) !important;
        border-radius: 6px !important;
    }

    [data-testid="stSidebar"] [aria-selected="true"] p {
        color: var(--indigo-accent) !important;
        font-weight: 600 !important;
    }

    /* Sidebar Buttons */
    [data-testid="stSidebar"] button {
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        color: var(--slate-light) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stSidebar"] button:hover {
        background: rgba(99, 102, 241, 0.2) !important;
        border-color: var(--indigo-accent) !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }

    /* Sidebar Divider */
    [data-testid="stSidebar"] hr {
        border-color: rgba(99, 102, 241, 0.2) !important;
        margin: 15px 0 !important;
    }

    /* Sidebar Collapse Animation */
    [data-testid="stSidebar"] {
        animation: slideIn 0.4s ease-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* ============================================================================
       PAGE TRANSITIONS & ANIMATIONS
       ============================================================================ */

    /* Main content fade-in */
    .stMainBlockContainer {
        animation: fadeIn 0.5s ease-out;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Main container background */
    .stMainBlockContainer {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #ffffff;
    }

    body {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%) fixed;
        color: #ffffff;
    }

    /* Sticky Navigation Bar */
    .navbar-sticky {
        position: fixed;
        top: 0;
        width: 100%;
        padding: 15px 30px;
        background: rgba(15, 12, 41, 0.95);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(102, 126, 234, 0.3);
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
    }

    .navbar-brand {
        font-size: 1.8em;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 1px;
    }

    .navbar-links {
        display: flex;
        gap: 20px;
    }

    .navbar-link {
        color: #b8c5d6;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.3s ease;
        padding: 8px 12px;
    }

    .navbar-link:hover {
        color: #667eea;
        transform: translateY(-2px);
    }

    /* Hero Section - Animated Gradient Title */
    .hero-section {
        margin-top: 80px;
        padding: 80px 40px;
        text-align: center;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 20px;
        border: 1px solid rgba(102, 126, 234, 0.3);
        margin-bottom: 60px;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 400px;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 50% 50%, rgba(102, 126, 234, 0.1), transparent 70%);
        pointer-events: none;
    }

    .hero-title {
        font-size: 4.5em;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 8s ease infinite;
        position: relative;
        z-index: 1;
        text-align: center;
        display: block;
        width: 100%;
    }

    @keyframes gradientShift {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }

    .hero-subtitle {
        font-size: 1.4em;
        color: #b8c5d6;
        margin-bottom: 30px;
        font-weight: 300;
        letter-spacing: 0.5px;
        position: relative;
        z-index: 1;
        text-align: center;
        display: block;
        width: 100%;
    }

    .hero-description {
        font-size: 1.1em;
        color: #8b9ac9;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.8;
        position: relative;
        z-index: 1;
        text-align: center;
        display: block;
        width: 100%;
    }

    /* Stats Section */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 60px 0;
    }

    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.3);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
    }

    .stat-card:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(102, 126, 234, 0.6);
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
    }

    .stat-value {
        font-size: 2.5em;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
    }

    .stat-label {
        color: #b8c5d6;
        font-size: 1em;
        font-weight: 500;
    }

    /* Feature Cards - Glassmorphism */
    .feature-cards-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        grid-template-rows: auto auto;
        gap: 28px;
        margin: 60px auto;
        width: 100%;
        padding: 0 20px;
        max-width: 1400px;
        align-items: stretch;
        justify-items: stretch;
    }
    
    @media (max-width: 1024px) {
        .feature-cards-container {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .feature-cards-container {
            grid-template-columns: 1fr;
        }
    }

    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(102, 126, 234, 0.3);
        border-radius: 20px;
        padding: 40px;
        color: white;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.320, 1);
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }

    .feature-card:hover {
        border-color: rgba(102, 126, 234, 0.8);
        background: rgba(255, 255, 255, 0.08);
        transform: translateY(-10px);
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3),
                    inset 0 0 30px rgba(102, 126, 234, 0.1);
    }

    .card-icon {
        font-size: 3.5em;
        margin-bottom: 15px;
        animation: bounce 2s ease-in-out infinite;
        position: relative;
        z-index: 1;
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    .card-title {
        font-size: 1.8em;
        font-weight: 700;
        margin-bottom: 15px;
        position: relative;
        z-index: 1;
    }

    .card-subtitle {
        font-size: 0.9em;
        color: #b8c5d6;
        margin-bottom: 20px;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }

    .accuracy-badge {
        display: inline-block;
        background: rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(102, 126, 234, 0.6);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        color: #667eea;
        margin-bottom: 15px;
        position: relative;
        z-index: 1;
    }

    .card-description {
        font-size: 0.95em;
        color: #a8b8d8;
        line-height: 1.6;
        margin-bottom: 20px;
        flex-grow: 1;
        position: relative;
        z-index: 1;
    }

    .features-list {
        font-size: 0.9em;
        margin-bottom: 25px;
        position: relative;
        z-index: 1;
    }

    .features-list li {
        color: #b8c5d6;
        margin-bottom: 8px;
        padding-left: 8px;
        line-height: 1.5;
    }

    .launch-btn {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 14px 32px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 600;
        cursor: pointer;
        border: none;
        font-size: 1em;
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
        width: 100%;
        text-align: center;
        margin-top: auto;
    }

    .launch-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4),
                    0 0 20px rgba(102, 126, 234, 0.6);
    }

    .launch-btn:active {
        transform: scale(0.98);
    }

    /* Info Section */
    .info-section {
        margin: 60px 0;
        padding: 60px 40px;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
        border: 1px solid rgba(102, 126, 234, 0.4);
        border-radius: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
    }

    .info-title {
        font-size: 2.5em;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 40px;
        text-align: center;
        letter-spacing: 1px;
    }

    .info-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1.5px solid rgba(102, 126, 234, 0.3);
        border-radius: 15px;
        padding: 35px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(31, 38, 135, 0.08);
    }

    .info-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(102, 126, 234, 0.6);
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.2);
    }

    .info-subtitle {
        font-size: 1.3em;
        font-weight: 700;
        color: #667eea;
        margin-top: 0;
        margin-bottom: 15px;
        letter-spacing: 0.5px;
    }

    .info-text {
        color: #b8c5d6;
        line-height: 1.8;
        font-size: 0.98em;
        margin: 0;
    }

    .info-text br {
        line-height: 2;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 40px;
        margin-top: 60px;
        border-top: 1px solid rgba(102, 126, 234, 0.3);
        color: #8b9ac9;
        background: rgba(15, 12, 41, 0.8);
        border-radius: 15px;
    }

    .footer-title {
        font-size: 1.3em;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 10px;
    }

    .footer-credits {
        font-size: 0.9em;
        margin-bottom: 5px;
    }

    .footer-badge {
        display: inline-block;
        padding: 6px 12px;
        background: rgba(102, 126, 234, 0.2);
        border: 1px solid rgba(102, 126, 234, 0.4);
        border-radius: 20px;
        font-size: 0.8em;
        margin-top: 10px;
        margin-right: 5px;
    }

    /* ============================================================================
       PERSISTENT FOOTER
       ============================================================================ */

    .persistent-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        width: 100%;
        height: 60px;
        background: linear-gradient(90deg, var(--navy-dark) 0%, var(--navy-light) 50%, var(--navy-dark) 100%);
        border-top: 1px solid rgba(99, 102, 241, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 30px;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3);
        z-index: 9999;
        backdrop-filter: blur(10px);
    }

    .footer-section {
        display: flex;
        align-items: center;
        gap: 20px;
        flex: 0;
    }

    .footer-brand {
        font-size: 1.1em;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.5px;
    }

    .footer-version {
        font-size: 0.8em;
        color: var(--slate-light);
        background: rgba(99, 102, 241, 0.2);
        padding: 4px 12px;
        border-radius: 12px;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    .footer-author {
        font-size: 0.85em;
        color: #a8b8d8;
        text-align: center;
        flex: 1;
    }

    .footer-right {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .footer-divider {
        width: 1px;
        height: 30px;
        background: rgba(99, 102, 241, 0.3);
        margin: 0 10px;
    }

    /* Adjust main content to avoid footer overlap */
    .stMainBlockContainer {
        padding-bottom: 70px !important;
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(102, 126, 234, 0.1);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.8);
    }

    /* Responsive */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5em;
        }

        .hero-section {
            padding: 40px 20px;
            margin-top: 100px;
        }

        .feature-cards-container {
            grid-template-columns: 1fr;
        }

        .navbar-links {
            display: none;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# HERO SECTION - Custom HTML Component
# ============================================================================
hero_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div class="hero-section">
        <h1 class="hero-title">🎭 MoodTracker</h1>
        <p class="hero-subtitle">Multi-Modal Emotion Analysis Hub</p>
        <p class="hero-description">
            Detect emotions from text, facial expressions, or voice with cutting-edge AI technology.
            Powered by deep learning and real-time processing.
        </p>
    </div>
</body>
</html>
"""

st.markdown(hero_html, unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================
initialize_total_analyses()

# ============================================================================
# STATS SECTION
# ============================================================================
total_analyses = get_total_analyses()

stats_html = f"""
<div class="stats-container">
    <div class="stat-card">
        <div class="stat-value">📊 3</div>
        <div class="stat-label">Active Projects</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">🎯 93%</div>
        <div class="stat-label">Max Accuracy</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">⚡ Real-Time</div>
        <div class="stat-label">Processing</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">🔢 {total_analyses}</div>
        <div class="stat-label">Total Analyses</div>
    </div>
</div>
"""
st.markdown(stats_html, unsafe_allow_html=True)

# ============================================================================
# FEATURE CARDS SECTION
# ============================================================================
# ============================================================================
# FEATURE CARDS SECTION - HORIZONTAL 3-COLUMN LAYOUT
# ============================================================================
st.markdown("<div style='text-align: center; margin: 40px 0;'><h2 style='font-size: 2.5em; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🚀 Explore Our Features</h2></div>", unsafe_allow_html=True)

# Feature Cards - Three columns with equal width and height
col_text, col_face, col_voice = st.columns(3, gap="large")

# Card 1: Text Emotion
with col_text:
    st.markdown("""
    <div class='feature-card'>
        <div class='card-icon'>📝</div>
        <h3 class='card-title'>NLP Text Emotion</h3>
        <div class='card-subtitle'>Text Analysis</div>
        <div class='accuracy-badge'>✓ 93% Accuracy</div>
        <p class='card-description'>Predict emotions from text with advanced NLP. Get sentiment analysis with confidence scores.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Launch Text Emotion", key="home_text_launch", use_container_width=True):
        st.switch_page("pages/1_Text_Emotion_Analysis.py")

# Card 2: Face Detection
with col_face:
    st.markdown("""
    <div class='feature-card'>
        <div class='card-icon'>📷</div>
        <h3 class='card-title'>Real-Time Detection</h3>
        <div class='card-subtitle'>Facial Recognition</div>
        <div class='accuracy-badge'>✓ Deep Learning CNN</div>
        <p class='card-description'>Detect emotions from webcam or images. Multi-face detection with instant processing.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Launch Face Detection", key="home_face_launch", use_container_width=True):
        st.switch_page("pages/2_Face_Emotion_Detection.py")

# Card 3: Voice Analyzer
with col_voice:
    st.markdown("""
    <div class='feature-card'>
        <div class='card-icon'>🎙️</div>
        <h3 class='card-title'>Voice Mood Analyzer</h3>
        <div class='card-subtitle'>Speech Analysis</div>
        <div class='accuracy-badge'>✓ Real-Time Processing</div>
        <p class='card-description'>Analyze mood from voice. Get speech-to-text and sentiment analysis insights.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Launch Voice Analyzer", key="home_voice_launch", use_container_width=True):
        st.switch_page("pages/3_Voice_Emotion_Analysis.py")

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)


# ============================================================================
# INFO SECTION
# ============================================================================
info_html = """
<div class="info-section">
    <h2 class="info-title">📊 Dashboard & Tools</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; margin-top: 40px;">
        <div class="info-card">
            <h3 class="info-subtitle">🎭 Emotion Comparison</h3>
            <p class="info-text">Compare results from all three modalities side-by-side with consensus voting logic.</p>
        </div>
        <div class="info-card">
            <h3 class="info-subtitle">📊 History Dashboard</h3>
            <p class="info-text">Track your emotion history with comprehensive analytics and beautiful visualizations.</p>
        </div>
        <div class="info-card">
            <h3 class="info-subtitle">ℹ️ About Project</h3>
            <p class="info-text">Learn more about the MoodTracker project, technology stack, and features.</p>
        </div>
    </div>
</div>
"""
st.write(info_html, unsafe_allow_html=True)

# Additional navigation
col_nav1, col_nav2, col_nav3 = st.columns(3, gap="medium")
with col_nav1:
    if st.button("🎭 Emotion Comparison", key="home_compare", use_container_width=True):
        st.switch_page("pages/5_Emotion_Comparison.py")
with col_nav2:
    if st.button("📊 History Dashboard", key="home_history", use_container_width=True):
        st.switch_page("pages/4_history_dashboard.py")
with col_nav3:
    if st.button("ℹ️ About MoodTracker", key="home_about", use_container_width=True):
        st.switch_page("pages/6_about.py")

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)

# ============================================================================
# PERSISTENT FOOTER
# ============================================================================
st.markdown("""
<div class="persistent-footer">
    <div class="footer-author">
        Made by <strong>Aditya Sharma</strong> | © 2026 All rights reserved | Production Ready • AI Powered • Real-Time
    </div>
    <div class="footer-right">
        <span class="footer-brand">🎭 MoodTracker</span>
        <div class="footer-divider"></div>
        <span class="footer-version">v2.0</span>
    </div>
</div>
""", unsafe_allow_html=True)

