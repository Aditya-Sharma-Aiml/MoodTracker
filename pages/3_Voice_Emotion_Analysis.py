import streamlit as st
import speech_recognition as sr
from textblob import TextBlob
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import altair as alt
import os
import tempfile
import warnings
import sys
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy import signal
from scipy.io import wavfile
import io
import shutil
from pydub import AudioSegment
import shutil
from pydub import AudioSegment

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
    render_emotion_timeline
)

warnings.filterwarnings('ignore')

# FFmpeg check
if not shutil.which("ffmpeg"):
    st.error("❌ ffmpeg not found. Run: `winget install ffmpeg` (Windows) or `brew install ffmpeg` (Mac), then restart app.")
    st.stop()

st.set_page_config(page_title='Voice Mood Analyzer', page_icon='🎙️', layout='wide')

# Apply global theme and page CSS
apply_global_theme()
apply_page_css()

# ============================================================================
# PULSING ANIMATION CSS
# ============================================================================
st.markdown("""
<style>
@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
        transform: scale(1);
    }
    50% {
        box-shadow: 0 0 0 20px rgba(239, 68, 68, 0);
        transform: scale(1.05);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
        transform: scale(1);
    }
}

.pulse-circle {
    display: inline-block;
    width: 40px;
    height: 40px;
    background-color: #ef4444;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
    margin: 10px 0;
}

.recording-indicator {
    text-align: center;
    padding: 20px;
    background: rgba(239, 68, 68, 0.1);
    border-radius: 12px;
    border: 2px solid #ef4444;
}
</style>
""", unsafe_allow_html=True)

# Initialize emotion history tracking
initialize_emotion_history()

# Initialize session state
if 'recordings' not in st.session_state:
    st.session_state.recordings = []
if 'mood_data' not in st.session_state:
    st.session_state.mood_data = {'Happy': 0, 'Sad': 0, 'Neutral': 0}
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'raw_audio_data' not in st.session_state:
    st.session_state.raw_audio_data = None
if 'audio_sample_rate' not in st.session_state:
    st.session_state.audio_sample_rate = None

def get_mood(polarity):
    """Get mood from sentiment polarity"""
    if polarity > 0.1:
        return 'Happy'
    elif polarity < -0.1:
        return 'Sad'
    else:
        return 'Neutral'

def get_polarity_score(text):
    """Get sentiment polarity"""
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except:
        return 0.0

def process_audio(audio_path):
    """Process audio file"""
    try:
        # Load and convert audio to WAV
        audio = AudioSegment.from_file(audio_path)
        
        # Ensure audio is mono and at appropriate sample rate (16000 Hz for Google API)
        if audio.channels > 1:
            audio = audio.set_channels(1)
        if audio.frame_rate != 16000:
            audio = audio.set_frame_rate(16000)
        
        # Export to WAV
        wav_path = audio_path.rsplit('.', 1)[0] + '_converted.wav'
        audio.export(wav_path, format='wav')
        
        # Load audio with SpeechRecognition
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 4000  # Adjust sensitivity
        
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
        
        # Clean up temp file
        try:
            os.remove(wav_path)
        except:
            pass
        
        return audio_data, None
    except Exception as e:
        return None, f"Audio processing error: {str(e)}"

def process_uploaded_audio(uploaded_file):
    """Process uploaded audio file with format conversion"""
    format_map = {"m4a": "mp4", "mp3": "mp3", "ogg": "ogg", "flac": "flac", "wav": "wav"}
    file_ext = uploaded_file.name.split(".")[-1].lower()
    fmt = format_map.get(file_ext, file_ext)
    
    try:
        audio_segment = AudioSegment.from_file(io.BytesIO(uploaded_file.read()), format=fmt)
        
        # Normalize audio format for Google Speech API
        audio_segment = audio_segment.set_channels(1)  # Convert to mono
        audio_segment = audio_segment.set_frame_rate(16000)  # Set to 16000 Hz
        audio_segment = audio_segment.set_sample_width(2)  # Set to 16-bit PCM (2 bytes)
        
        wav_buffer = io.BytesIO()
        audio_segment.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_buffer) as source:
            audio_data = recognizer.record(source)
        
        text = recognizer.recognize_google(audio_data)
        return text, None
    except sr.UnknownValueError:
        return None, "Speech not clear, please try again."
    except sr.RequestError as e:
        return None, f"Google API error: {e}"
    except Exception as e:
        return None, f"Audio processing error: {e}"

def save_recording(text, mood, polarity, source):
    """Save recording to session state"""
    st.session_state.recordings.append({
        'text': text,
        'mood': mood,
        'polarity': polarity,
        'source': source,
        'timestamp': datetime.now()
    })
    st.session_state.mood_data[mood] += 1

def plot_waveform(audio_data, sample_rate):
    """Generate matplotlib waveform plot from audio data"""
    try:
        # Handle different audio formats
        if isinstance(audio_data, sr.AudioData):
            # Convert speech_recognition AudioData to numpy array
            audio_array = np.frombuffer(audio_data.get_raw_data(), np.int16)
            sample_rate = audio_data.sample_rate
        else:
            audio_array = audio_data
        
        # Normalize audio
        audio_array = audio_array.astype(float) / np.max(np.abs(audio_array))
        
        # Time axis
        time_axis = np.linspace(0, len(audio_array) / sample_rate, num=len(audio_array))
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 3))
        ax.plot(time_axis, audio_array, linewidth=0.5, color='#667eea')
        ax.fill_between(time_axis, audio_array, alpha=0.3, color='#667eea')
        ax.set_xlabel('Time (s)', fontsize=10, color='#f1f5f9')
        ax.set_ylabel('Amplitude', fontsize=10, color='#f1f5f9')
        ax.set_title('Audio Waveform', fontsize=12, fontweight='bold', color='#f1f5f9')
        ax.grid(True, alpha=0.2, color='#6366f1')
        
        # Dark theme
        ax.set_facecolor('#1e293b')
        fig.patch.set_facecolor('#0f172a')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#6366f1')
        ax.spines['bottom'].set_color('#6366f1')
        ax.tick_params(colors='#f1f5f9')
        
        return fig
    except Exception as e:
        st.error(f"Error plotting waveform: {e}")
        return None

# Page Header
col_header_back, col_header_title = st.columns([0.5, 3])
with col_header_back:
    if st.button("⬅️ Back", key="voice_back", help="Return to home"):
        st.switch_page("home.py")

with col_header_title:
    st.markdown("""
    <h1 style='font-size: 2.8em; font-weight: 800; margin: 0; padding: 0;'>🎙️ Voice Mood Analyzer</h1>
    <p style='color: #8b9ac9; font-size: 1.05em; margin: 5px 0 0 0;'>Detect mood and emotion from voice analysis</p>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 20px 0 30px 0;'>", unsafe_allow_html=True)

# Main layout: Two columns
col_input, col_transcript = st.columns([1, 1], gap="large")

# LEFT COLUMN - INPUT PANEL
with col_input:
    st.markdown("**🎙️ Record or Upload**")
    st.caption("Choose your input method")
    
    input_method = st.radio(
        "Select Input:",
        ["🎤 Live Recording", "📤 Upload Audio"],
        label_visibility="collapsed"
    )
    
    if input_method == "🎤 Live Recording":
        st.markdown("**🎤 Record Live**")
        st.caption("Click Start, speak, then Stop")
        
        col_start, col_stop = st.columns(2)
        with col_start:
            start_btn = st.button("🔴 START", use_container_width=True, key="live_start")
        with col_stop:
            stop_btn = st.button("⏹️ STOP", use_container_width=True, key="live_stop")
        
        if start_btn:
            st.session_state.is_recording = True
            st.rerun()
        
        if stop_btn:
            st.session_state.is_recording = False
        
        if st.session_state.is_recording:
            # Display pulsing recording indicator
            st.markdown("""
            <div class="recording-indicator">
                <div class="pulse-circle"></div>
                <p style="color: #ef4444; font-weight: bold; margin: 10px 0;">🎙️ Recording... Speak now!</p>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=15, phrase_time_limit=20)
                
                # Store raw audio data
                st.session_state.raw_audio_data = audio
                st.session_state.audio_sample_rate = audio.sample_rate
                
                st.session_state.is_recording = False
                
                with st.spinner("🔄 Processing audio..."):
                    try:
                        # Retry logic for Google API
                        text = None
                        for attempt in range(2):
                            try:
                                text = recognizer.recognize_google(audio, language='en-US')
                                break
                            except sr.RequestError as e:
                                if attempt == 0:
                                    st.warning(f"Retrying speech recognition... ({str(e)[:50]})")
                                    continue
                                else:
                                    raise
                        
                        if text:
                            polarity = get_polarity_score(text)
                            mood = get_mood(polarity)
                            
                            save_recording(text, mood, polarity, 'Live')
                            st.session_state.current_analysis = {
                                'text': text,
                                'mood': mood,
                                'polarity': polarity,
                                'source': 'Live Recording'
                            }
                            # Log to global emotion history (use polarity as confidence: 0-1 range)
                            confidence = abs(polarity)  # Convert polarity to confidence
                            add_emotion_to_history(mood, confidence, 'voice')
                            increment_total_analyses()
                            st.success("✅ Analysis Complete!")
                            st.rerun()
                    except sr.UnknownValueError:
                        st.error("❌ Could not understand audio. Try again.")
                    except sr.RequestError as e:
                        st.error(f"❌ API Error: {e}")
            except Exception as e:
                st.error(f"❌ Mic Error: {e}")
                st.session_state.is_recording = False
    
    else:  # Upload Audio
        st.markdown("**📤 Upload Audio File**")
        st.caption("Supported: WAV, MP3, OGG, M4A, FLAC")
        
        uploaded_file = st.file_uploader(
            "Choose audio file",
            type=['wav', 'mp3', 'ogg', 'm4a', 'flac'],
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            st.audio(uploaded_file)
            
            if st.button("🔍 Analyze Audio", use_container_width=True, type="primary"):
                with st.spinner("🔄 Processing..."):
                    text, error = process_uploaded_audio(uploaded_file)
                    
                    if error:
                        st.error(f"❌ {error}")
                    elif text:
                        polarity = get_polarity_score(text)
                        mood = get_mood(polarity)
                        
                        save_recording(text, mood, polarity, 'Upload')
                        st.session_state.current_analysis = {
                            'text': text,
                            'mood': mood,
                            'polarity': polarity,
                            'source': 'File Upload'
                        }
                        # Log to global emotion history
                        confidence = abs(polarity)  # Convert polarity to confidence
                        add_emotion_to_history(mood, confidence, 'voice')
                        increment_total_analyses()
                        st.success("✅ Analysis Complete!")
                    else:
                        st.error("❌ Could not process file!")

# RIGHT COLUMN - TRANSCRIPTION PANEL
with col_transcript:
    st.markdown("**📝 Transcribed Text**")
    
    if st.session_state.current_analysis is None:
        st.markdown("""
        <div style='background: rgba(99, 102, 241, 0.1); border: 2px dashed rgba(99, 102, 241, 0.3); 
                    border-radius: 10px; padding: 40px; text-align: center;'>
            <div style='font-size: 2em; margin-bottom: 15px;'>🎤</div>
            <div style='color: #a8b8d8; font-size: 0.95em;'>Transcript appears here</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        analysis = st.session_state.current_analysis
        st.text_area("", value=analysis.get('text', ''), disabled=True, height=300, label_visibility="collapsed")

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0 30px 0;'>", unsafe_allow_html=True)

# RESULTS SECTION - THREE COLUMNS
if st.session_state.current_analysis is not None:
    analysis = st.session_state.current_analysis
    
    st.markdown("**📊 Analysis Results**")
    
    col_mood, col_polar, col_subj = st.columns(3, gap="large")
    
    with col_mood:
        mood_emoji = {'Happy': '😊', 'Sad': '😢', 'Neutral': '😐'}.get(analysis.get('mood', 'Neutral'), '😐')
        st.markdown(f"""
        <div style='background: rgba(99, 102, 234, 0.1); border: 2px solid rgba(99, 102, 234, 0.5); 
                    border-radius: 15px; padding: 25px; text-align: center;'>
            <div style='font-size: 64px; margin-bottom: 15px;'>{mood_emoji}</div>
            <div style='font-size: 1.5em; font-weight: 700; color: #f1f5f9; margin-bottom: 8px;'>
                {analysis.get('mood', 'Unknown')}
            </div>
            <div style='font-size: 0.9em; color: #8b9ac9;'>Detected Mood</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_polar:
        polarity = analysis.get('polarity', 0)
        st.markdown(f"""
        <div style='background: rgba(99, 102, 234, 0.1); border: 2px solid rgba(99, 102, 234, 0.5); 
                    border-radius: 15px; padding: 25px; text-align: center;'>
            <div style='font-size: 1.1em; color: #8b9ac9; margin-bottom: 15px;'>Polarity</div>
            <div style='font-size: 2.2em; font-weight: 700; color: #667eea; margin-bottom: 8px;'>
                {polarity:.2f}
            </div>
            <div style='font-size: 0.85em; color: #8b9ac9;'>Sentiment Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_subj:
        try:
            blob = TextBlob(analysis.get('text', ''))
            subjectivity = blob.sentiment.subjectivity
        except:
            subjectivity = 0.5
        
        st.markdown(f"""
        <div style='background: rgba(99, 102, 234, 0.1); border: 2px solid rgba(99, 102, 234, 0.5); 
                    border-radius: 15px; padding: 25px; text-align: center;'>
            <div style='font-size: 1.1em; color: #8b9ac9; margin-bottom: 15px;'>Subjectivity</div>
            <div style='font-size: 2.2em; font-weight: 700; color: #667eea; margin-bottom: 8px;'>
                {subjectivity:.2f}
            </div>
            <div style='font-size: 0.85em; color: #8b9ac9;'>Opinion Level</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 30px 0;'>", unsafe_allow_html=True)

    # Recording history charts
    if st.session_state.recordings:
        st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 30px 0;'>", unsafe_allow_html=True)
        st.markdown("**📊 Recording History**")
        
        history_df = pd.DataFrame(st.session_state.recordings)
        mood_counts = history_df['mood'].value_counts()
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("Total Recordings", len(st.session_state.recordings))
        with stat_col2:
            avg_polarity = history_df['polarity'].mean()
            st.metric("Avg Polarity", f"{avg_polarity:.2f}")
        with stat_col3:
            most_common = mood_counts.index[0] if len(mood_counts) > 0 else "N/A"
            st.metric("Most Common", most_common)
        
        mood_colors = {'Happy': '#10b981', 'Sad': '#3b82f6', 'Neutral': '#6b7280'}
        
        # Charts side by side
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            mood_dist = pd.DataFrame({'Mood': mood_counts.index, 'Count': mood_counts.values})
            fig_pie = px.pie(mood_dist, values='Count', names='Mood', hole=0.3, title="Mood Distribution")
            fig_pie.update_traces(marker=dict(colors=[mood_colors.get(m, '#6366f1') for m in mood_counts.index]))
            fig_pie.update_layout(height=300, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#f1f5f9'))
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with chart_col2:
            history_df['Index'] = range(len(history_df))
            fig_trend = go.Figure(data=[go.Scatter(x=history_df['Index'], y=history_df['polarity'], mode='lines+markers', line=dict(color='#667eea', width=3), marker=dict(size=8))])
            fig_trend.update_layout(title="Polarity Trend", xaxis_title="Recording", yaxis_title="Polarity", height=300, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#f1f5f9'), yaxis=dict(range=[-1, 1]))
            st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)
render_emotion_timeline()
st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)
render_persistent_footer()
