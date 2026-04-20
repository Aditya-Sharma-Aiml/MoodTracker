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

# Setup Logging
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
