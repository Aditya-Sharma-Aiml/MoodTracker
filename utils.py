"""
Shared utilities for MoodTracker emotion detection projects
Common functions and helpers used across all modules
"""

import os
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import streamlit as st

# ============================================================================
# THEME & STYLING UTILITIES
# ============================================================================

def apply_global_theme():
    """
    Apply consistent dark theme with sidebar styling across all pages.
    Call this at the beginning of each page file.
    """
    st.markdown("""
        <style>
        /* Root Variables */
        :root {
            --navy-dark: #0f172a;
            --navy-light: #1e293b;
            --indigo-accent: #6366f1;
            --slate-light: #f1f5f9;
        }

        /* Global Transitions */
        * {
            transition: all 0.3s ease;
        }

        /* Smooth scrolling */
        html {
            scroll-behavior: smooth;
        }

        /* ============================================================================
           SIDEBAR STYLING
           ============================================================================ */
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--navy-dark) 0%, var(--navy-light) 100%);
            border-right: 2px solid rgba(99, 102, 241, 0.2);
            box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
        }

        [data-testid="stSidebar"] > div:first-child {
            background: transparent !important;
        }

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

        /* Sidebar Animations */
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
           PAGE TRANSITIONS
           ============================================================================ */

        .stMainBlockContainer {
            animation: fadeIn 0.5s ease-out;
            padding-bottom: 70px !important;
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
            .persistent-footer {
                flex-direction: column;
                height: auto;
                padding: 10px 15px;
                gap: 10px;
            }

            .footer-author {
                text-align: center;
                font-size: 0.75em;
            }

            .stMainBlockContainer {
                padding-bottom: 100px !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)


def render_persistent_footer():
    """
    Render the persistent footer that appears on all pages.
    Call this at the end of each page file.
    """
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


def apply_page_css():
    """
    Apply page-specific CSS for two-column layouts and emotion cards.
    Call this on each feature page after apply_global_theme().
    """
    st.markdown("""
        <style>
        /* ============================================================================
           PAGE HEADER & BUTTONS
           ============================================================================ */

        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(99, 102, 241, 0.05);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 15px;
        }

        .page-title {
            font-size: 2.2em;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .back-button-pill {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }

        .back-button-pill:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
        }

        /* ============================================================================
           TWO-COLUMN LAYOUT - INPUT & RESULTS
           ============================================================================ */

        .input-panel {
            background: rgba(255, 255, 255, 0.03);
            border: 2px solid rgba(99, 102, 241, 0.2);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            height: fit-content;
            position: sticky;
            top: 100px;
        }

        .input-panel:hover {
            border-color: rgba(99, 102, 241, 0.4);
            background: rgba(255, 255, 255, 0.05);
        }

        .input-label {
            font-size: 1.1em;
            font-weight: 600;
            color: var(--slate-light);
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .input-instruction {
            font-size: 0.9em;
            color: #a8b8d8;
            margin-bottom: 20px;
            line-height: 1.6;
        }

        .results-panel {
            min-height: 300px;
        }

        /* ============================================================================
           EMOTION RESULT CARDS
           ============================================================================ */

        .emotion-card {
            background: rgba(255, 255, 255, 0.03);
            border: 2px solid;
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(15px);
            transition: all 0.5s cubic-bezier(0.23, 1, 0.320, 1);
            animation: fadeInScale 0.6s ease-out;
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
        }

        .emotion-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, transparent, rgba(255, 255, 255, 0.05), transparent);
            pointer-events: none;
        }

        .emotion-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
        }

        @keyframes fadeInScale {
            from {
                opacity: 0;
                transform: scale(0.95) translateY(20px);
            }
            to {
                opacity: 1;
                transform: scale(1) translateY(0);
            }
        }

        /* Emotion-specific colors */
        .emotion-card.happy {
            border-color: rgba(16, 185, 129, 0.5);
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(16, 185, 129, 0.02) 100%);
        }

        .emotion-card.sad {
            border-color: rgba(59, 130, 246, 0.5);
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(59, 130, 246, 0.02) 100%);
        }

        .emotion-card.angry {
            border-color: rgba(239, 68, 68, 0.5);
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(239, 68, 68, 0.02) 100%);
        }

        .emotion-card.neutral {
            border-color: rgba(107, 114, 128, 0.5);
            background: linear-gradient(135deg, rgba(107, 114, 128, 0.05) 0%, rgba(107, 114, 128, 0.02) 100%);
        }

        .emotion-card.surprise {
            border-color: rgba(139, 92, 246, 0.5);
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(139, 92, 246, 0.02) 100%);
        }

        .emotion-card.fear {
            border-color: rgba(249, 115, 22, 0.5);
            background: linear-gradient(135deg, rgba(249, 115, 22, 0.05) 0%, rgba(249, 115, 22, 0.02) 100%);
        }

        .emotion-card.disgust {
            border-color: rgba(234, 179, 8, 0.5);
            background: linear-gradient(135deg, rgba(234, 179, 8, 0.05) 0%, rgba(234, 179, 8, 0.02) 100%);
        }

        .emotion-card.shame {
            border-color: rgba(79, 70, 229, 0.5);
            background: linear-gradient(135deg, rgba(79, 70, 229, 0.05) 0%, rgba(79, 70, 229, 0.02) 100%);
        }

        .emotion-emoji {
            font-size: 4em;
            text-align: center;
            margin-bottom: 15px;
            animation: bounce 2s ease-in-out infinite;
        }

        .emotion-name {
            font-size: 2em;
            font-weight: 700;
            text-align: center;
            margin-bottom: 15px;
            color: var(--slate-light);
        }

        .emotion-name.happy { color: #10b981; }
        .emotion-name.sad { color: #3b82f6; }
        .emotion-name.angry { color: #ef4444; }
        .emotion-name.neutral { color: #6b7280; }
        .emotion-name.surprise { color: #8b5cf6; }
        .emotion-name.fear { color: #f97316; }
        .emotion-name.disgust { color: #eab308; }
        .emotion-name.shame { color: #4f46e5; }

        .confidence-section {
            margin-top: 20px;
        }

        .confidence-label {
            font-size: 0.95em;
            color: #a8b8d8;
            margin-bottom: 10px;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
        }

        /* Custom HTML Progress Bar */
        .progress-bar {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            height: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .progress-fill {
            height: 100%;
            border-radius: 20px;
            transition: width 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            position: relative;
            overflow: hidden;
        }

        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            right: 0;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            animation: shimmer 2s infinite;
        }

        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        /* Color gradient per emotion */
        .progress-fill.happy { background: linear-gradient(90deg, #10b981 0%, #059669 100%); }
        .progress-fill.sad { background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%); }
        .progress-fill.angry { background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%); }
        .progress-fill.neutral { background: linear-gradient(90deg, #6b7280 0%, #4b5563 100%); }
        .progress-fill.surprise { background: linear-gradient(90deg, #8b5cf6 0%, #6d28d9 100%); }
        .progress-fill.fear { background: linear-gradient(90deg, #f97316 0%, #d97706 100%); }
        .progress-fill.disgust { background: linear-gradient(90deg, #eab308 0%, #ca8a04 100%); }
        .progress-fill.shame { background: linear-gradient(90deg, #4f46e5 0%, #3730a3 100%); }

        .confidence-value {
            font-size: 1.1em;
            font-weight: 700;
            color: var(--indigo-accent);
        }

        /* ============================================================================
           EMOTION DISTRIBUTION / RESULTS SUMMARY
           ============================================================================ */

        .results-summary {
            background: rgba(99, 102, 241, 0.05);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .summary-title {
            font-size: 1.1em;
            font-weight: 700;
            color: var(--slate-light);
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .emotion-stat {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.05);
            padding: 8px 14px;
            border-radius: 10px;
            margin-right: 10px;
            margin-bottom: 10px;
            font-size: 0.9em;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }

        /* ============================================================================
           LOADING & PLACEHOLDER
           ============================================================================ */

        .loading-spinner {
            text-align: center;
            padding: 40px;
            color: var(--indigo-accent);
        }

        .placeholder-box {
            background: rgba(255, 255, 255, 0.03);
            border: 2px dashed rgba(99, 102, 241, 0.2);
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            color: #a8b8d8;
        }

        .placeholder-box p {
            margin: 0;
            line-height: 1.6;
        }

        /* ============================================================================
           RESPONSIVE
           ============================================================================ */

        @media (max-width: 768px) {
            .input-panel {
                position: relative;
                top: 0;
            }

            .emotion-emoji {
                font-size: 3em;
            }

            .emotion-name {
                font-size: 1.5em;
            }

            .page-header {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }

            .page-title {
                font-size: 1.8em;
            }
        }
        </style>
    """, unsafe_allow_html=True)

# ============================================================================
def setup_logging(log_file: Optional[str] = None, level=logging.INFO):
    """Configure logging for the application"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if log_file:
        logging.basicConfig(
            level=level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(level=level, format=log_format)
    
    return logging.getLogger(__name__)

# File Management
def ensure_file_exists(file_path: str, error_message: str = None) -> bool:
    """Check if file exists, raise error if not"""
    if not os.path.exists(file_path):
        msg = error_message or f"Required file not found: {file_path}"
        raise FileNotFoundError(msg)
    return True

def ensure_directory_exists(dir_path: str) -> str:
    """Create directory if it doesn't exist"""
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    return dir_path

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path) / (1024 * 1024)
    return 0.0

# Model Loading & Validation
def validate_model_path(model_path: str) -> bool:
    """Validate if model file exists and is accessible"""
    try:
        ensure_file_exists(model_path, f"Model file not found: {model_path}")
        size = get_file_size_mb(model_path)
        if size < 0.1:  # Model should be at least 100KB
            raise ValueError(f"Model file seems corrupted (size: {size}MB)")
        return True
    except Exception as e:
        logging.error(f"Model validation failed: {e}")
        return False

# Emotion Prediction Helpers
def get_top_predictions(prediction_array: np.ndarray, emotions: List[str], top_n: int = 3) -> Dict[str, float]:
    """Get top N predictions from emotion prediction array"""
    try:
        indices = np.argsort(prediction_array)[::-1][:top_n]
        result = {}
        for idx in indices:
            if idx < len(emotions):
                result[emotions[idx]] = float(prediction_array[idx])
        return result
    except Exception as e:
        logging.error(f"Error getting top predictions: {e}")
        return {}

def get_emotion_confidence(prediction_array: np.ndarray, emotion_index: int) -> float:
    """Get confidence score for a specific emotion"""
    try:
        if 0 <= emotion_index < len(prediction_array):
            return float(prediction_array[emotion_index])
        return 0.0
    except Exception as e:
        logging.error(f"Error getting emotion confidence: {e}")
        return 0.0

def get_dominant_emotion(prediction_array: np.ndarray, emotions: List[str]) -> Tuple[str, float]:
    """Get the dominant emotion and its confidence"""
    try:
        if len(prediction_array) != len(emotions):
            raise ValueError("Prediction array size doesn't match emotions list")
        
        max_idx = np.argmax(prediction_array)
        emotion = emotions[max_idx]
        confidence = float(prediction_array[max_idx])
        return emotion, confidence
    except Exception as e:
        logging.error(f"Error determining dominant emotion: {e}")
        return "Unknown", 0.0

# Text Processing
def validate_text_input(text: str, max_length: int = 2000, min_length: int = 1) -> Tuple[bool, str]:
    """Validate text input for emotion classification"""
    if not text:
        return False, "Text cannot be empty"
    
    if len(text.strip()) < min_length:
        return False, f"Text must be at least {min_length} character(s)"
    
    if len(text) > max_length:
        return False, f"Text exceeds maximum length of {max_length} characters"
    
    return True, "Valid"

def preprocess_text(text: str) -> str:
    """Basic text preprocessing"""
    # Remove leading/trailing whitespace
    text = text.strip()
    # Replace multiple spaces with single space
    text = ' '.join(text.split())
    return text

# Image Processing Helpers
def get_image_info(image_path: str) -> Dict[str, Any]:
    """Get information about an image file"""
    try:
        from PIL import Image as PILImage
        if not os.path.exists(image_path):
            return {'error': 'File not found'}
        
        img = PILImage.open(image_path)
        return {
            'format': img.format,
            'size': img.size,
            'mode': img.mode,
            'file_size_mb': get_file_size_mb(image_path)
        }
    except Exception as e:
        logging.error(f"Error getting image info: {e}")
        return {'error': str(e)}

def validate_image_format(file_path: str, allowed_formats: List[str] = ['jpg', 'jpeg', 'png', 'bmp']) -> bool:
    """Validate if image format is supported"""
    try:
        from PIL import Image as PILImage
        ext = Path(file_path).suffix.lower().lstrip('.')
        if ext not in allowed_formats:
            return False
        
        img = PILImage.open(file_path)
        img.verify()
        return True
    except Exception as e:
        logging.error(f"Image validation failed: {e}")
        return False

# Data Analysis
def calculate_emotion_statistics(predictions: List[Dict]) -> Dict[str, Any]:
    """Calculate statistics from emotion predictions"""
    try:
        if not predictions:
            return {'error': 'No predictions provided'}
        
        emotions = [p['emotion'] for p in predictions]
        confidences = [p.get('confidence', 0) for p in predictions]
        
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        return {
            'total_predictions': len(predictions),
            'emotion_counts': emotion_counts,
            'average_confidence': np.mean(confidences),
            'max_confidence': np.max(confidences),
            'min_confidence': np.min(confidences),
            'most_common': max(emotion_counts, key=emotion_counts.get)
        }
    except Exception as e:
        logging.error(f"Error calculating statistics: {e}")
        return {'error': str(e)}

# Configuration Validation
def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration dictionary"""
    required_fields = ['model_path', 'emotions']
    for field in required_fields:
        if field not in config:
            logging.warning(f"Missing required config field: {field}")
            return False
    
    # Check if model file exists
    if not os.path.exists(config['model_path']):
        logging.warning(f"Model file not found: {config['model_path']}")
        return False
    
    return True

# Caching helpers
def save_cache(data: Dict, cache_path: str) -> bool:
    """Save data to JSON cache file"""
    try:
        ensure_directory_exists(os.path.dirname(cache_path))
        with open(cache_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Cache save failed: {e}")
        return False

def load_cache(cache_path: str) -> Optional[Dict]:
    """Load data from JSON cache file"""
    try:
        if not os.path.exists(cache_path):
            return None
        with open(cache_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Cache load failed: {e}")
        return None


# ============================================================================
# EMOTION CARD RENDERING HELPERS
# ============================================================================

EMOTION_EMOJIS = {
    'Happy': '😊',
    'happy': '😊',
    'Sad': '😢',
    'sad': '😢',
    'Angry': '😠',
    'angry': '😠',
    'Neutral': '😐',
    'neutral': '😐',
    'Surprise': '😮',
    'surprise': '😮',
    'Fear': '😨',
    'fear': '😨',
    'Disgust': '🤮',
    'disgust': '🤮',
    'Shame': '😳',
    'shame': '😳'
}


def render_emotion_card(emotion: str, confidence: float, container=None):
    """
    Render a styled emotion result card with emoji, name, and confidence bar.
    
    Args:
        emotion: Emotion name (e.g., 'Happy', 'Sad')
        confidence: Confidence score (0-1)
        container: Streamlit container to render in (default: st)
    """
    if container is None:
        container = st
    
    emotion_lower = emotion.lower()
    emoji = EMOTION_EMOJIS.get(emotion, '😐')
    confidence_pct = int(confidence * 100)
    
    # Create progress bar HTML
    progress_html = f"""
    <div class="emotion-card {emotion_lower}">
        <div class="emotion-emoji">{emoji}</div>
        <div class="emotion-name {emotion_lower}">{emotion}</div>
        <div class="confidence-section">
            <div class="confidence-label">
                <span>Confidence Level</span>
                <span class="confidence-value">{confidence_pct}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill {emotion_lower}" style="width: {confidence_pct}%"></div>
            </div>
        </div>
    </div>
    """
    
    container.markdown(progress_html, unsafe_allow_html=True)


def render_emotion_summary(emotions_dict: Dict[str, float], container=None):
    """
    Render a summary of all emotion detections.
    
    Args:
        emotions_dict: Dictionary of {emotion: confidence}
        container: Streamlit container to render in (default: st)
    """
    if container is None:
        container = st
    
    summary_html = '<div class="results-summary"><div class="summary-title">📊 Emotion Scores</div>'
    
    for emotion, confidence in sorted(emotions_dict.items(), key=lambda x: x[1], reverse=True):
        emoji = EMOTION_EMOJIS.get(emotion, '😐')
        confidence_pct = int(confidence * 100)
        summary_html += f'<div class="emotion-stat">{emoji} {emotion}: <strong>{confidence_pct}%</strong></div>'
    
    summary_html += '</div>'
    
    container.markdown(summary_html, unsafe_allow_html=True)


def render_placeholder_results():
    """Render a placeholder message when no results are available"""
    st.markdown("""
    <div class="placeholder-box">
        <p>👉 <strong>No results yet!</strong></p>
        <p>Use the input panel on the left to analyze text, upload an image, or record audio.</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# EMOTION HISTORY TRACKING UTILITIES
# ============================================================================

def initialize_emotion_history():
    """Initialize emotion history in session state"""
    if 'emotion_history' not in st.session_state:
        st.session_state.emotion_history = []


def add_emotion_to_history(emotion: str, confidence: float, source: str):
    """
    Add an emotion detection entry to the history.
    
    Args:
        emotion: Detected emotion name
        confidence: Confidence score (0-1)
        source: Source of detection ('text', 'face', or 'voice')
    """
    from datetime import datetime
    
    initialize_emotion_history()
    
    entry = {
        'timestamp': datetime.now(),
        'emotion': emotion,
        'confidence': confidence,
        'source': source
    }
    
    st.session_state.emotion_history.append(entry)


def get_emotion_history():
    """Get all emotion history entries"""
    initialize_emotion_history()
    return st.session_state.emotion_history


def initialize_total_analyses():
    """Initialize total analyses counter in session state"""
    if 'total_analyses' not in st.session_state:
        st.session_state.total_analyses = 0


def increment_total_analyses():
    """Increment the total analyses counter"""
    initialize_total_analyses()
    st.session_state.total_analyses += 1


def get_total_analyses():
    """Get the total number of analyses run"""
    initialize_total_analyses()
    return st.session_state.total_analyses


def clear_emotion_history():
    """Clear all emotion history"""
    st.session_state.emotion_history = []


def export_history_to_csv():
    """Export emotion history as CSV string"""
    import csv
    import io
    
    history = get_emotion_history()
    
    if not history:
        return None
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Timestamp', 'Emotion', 'Confidence', 'Source'])
    
    # Write data
    for entry in history:
        writer.writerow([
            entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            entry['emotion'],
            f"{entry['confidence']:.2f}",
            entry['source']
        ])
    
    return output.getvalue()


def render_emotion_timeline():
    """
    Render a scrollable timeline card showing recent emotion history.
    Call this at the bottom of each feature page.
    """
    history = get_emotion_history()
    
    if not history:
        return
    
    st.markdown("---")
    st.subheader("📜 Recent Emotion History")
    
    # Show recent 5 entries
    recent_entries = history[-5:]
    
    timeline_html = '<div style="max-height: 300px; overflow-y: auto; border: 2px solid #6366f1; border-radius: 12px; padding: 15px; background: rgba(99, 102, 241, 0.05);">'
    
    for entry in reversed(recent_entries):
        emotion_emoji = EMOTION_EMOJIS.get(entry['emotion'], '😐')
        source_icon = {'text': '📝', 'face': '📷', 'voice': '🎙️'}.get(entry['source'], '📊')
        confidence_pct = int(entry['confidence'] * 100)
        time_str = entry['timestamp'].strftime('%H:%M:%S')
        
        timeline_html += f'<div style="padding: 10px; margin: 8px 0; background: white; border-left: 4px solid #6366f1; border-radius: 6px;"><div style="display: flex; justify-content: space-between; align-items: center;"><div><strong>{emotion_emoji} {entry["emotion"]}</strong> <span style="color: #666; font-size: 0.9em;">({confidence_pct}%)</span></div><div style="font-size: 0.85em; color: #888;">{source_icon} {entry["source"]} @ {time_str}</div></div></div>'
    
    timeline_html += '</div>'
    
    st.markdown(timeline_html, unsafe_allow_html=True)
    
    # Show history link
    st.caption("📈 View full history and analytics in the [History Dashboard](/?page=4_history_dashboard)")


# Emotion emoji mapping
EMOTION_EMOJIS = {
    'Happy': '😊',
    'Sad': '😢',
    'Angry': '😠',
    'Neutral': '😐',
    'Surprise': '😮',
    'Fear': '😨',
    'Disgust': '🤢',
    'Shame': '😳'
}
