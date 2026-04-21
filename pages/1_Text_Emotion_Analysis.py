import streamlit as st
import numpy as np
import pandas as pd
import joblib
import altair as alt
import plotly.graph_objects as go
import plotly.express as px
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_global_theme, 
    apply_page_css,
    render_persistent_footer, 
    render_emotion_card,
    render_emotion_summary,
    render_placeholder_results,
    initialize_emotion_history,
    add_emotion_to_history,
    increment_total_analyses,
    render_emotion_timeline
)

# Page config
st.set_page_config(
    page_title="NLP Text Emotion Classifier",
    page_icon="📝",
    layout="wide"
)

# Apply global theme and page CSS
apply_global_theme()
apply_page_css()

# Initialize emotion history tracking
initialize_emotion_history()

# ============================================================================
# EMOTION COLOR MAPPING
# ============================================================================
EMOTION_COLORS = {
    'anger': '#ef4444',        # Red
    'disgust': '#eab308',      # Yellow
    'fear': '#f97316',         # Orange
    'happy': '#10b981',        # Green
    'joy': '#10b981',          # Green
    'neutral': '#6b7280',      # Gray
    'sad': '#3b82f6',          # Blue
    'sadness': '#3b82f6',      # Blue
    'shame': '#4f46e5',        # Indigo
    'surprise': '#8b5cf6'      # Purple
}

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

# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

# ============================================================================
# PAGE HEADER
# ============================================================================
col_header_back, col_header_title = st.columns([0.5, 3])
with col_header_back:
    if st.button("⬅️ Back", key="nlp_back", help="Return to home"):
        st.switch_page("home.py")

with col_header_title:
    st.markdown("""
    <h1 style='font-size: 2.8em; font-weight: 800; margin: 0; padding: 0;'>📝 Text Emotion Analyzer</h1>
    <p style='color: #8b9ac9; font-size: 1.05em; margin: 5px 0 0 0;'>Analyze emotional content with advanced NLP</p>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 20px 0 30px 0;'>", unsafe_allow_html=True)

# Main layout: Two columns (Input | Results)
col_input, col_results = st.columns([1, 1], gap="large")

# ============================================================================
# LEFT COLUMN - INPUT PANEL
# ============================================================================
with col_input:
    st.markdown("**📝 Enter Your Text**")
    st.caption("Analyze text to detect emotions with high accuracy")
    
    raw_text = st.text_area(
        "Text Input:",
        placeholder="Type or paste your text here...\n\nExamples:\n- 'I'm so happy today!'\n- 'This is terrible...'",
        height=250,
        label_visibility="collapsed"
    )
    
    # Character counter
    char_count = len(raw_text) if raw_text else 0
    st.caption(f"Characters: {char_count} / 2000")
    
    # Analyze button
    analyze_btn = st.button(
        "🔍 Analyze Emotion",
        use_container_width=True,
        type="primary",
        key="analyze_btn_nlp"
    )
    
    if analyze_btn:
        if not raw_text or len(raw_text.strip()) == 0:
            st.error("❌ Please enter some text to analyze")
        elif char_count > 2000:
            st.error("❌ Text exceeds 2000 character limit")
        else:
            # Perform analysis
            with st.spinner("🔄 Analyzing..."):
                prediction = predict_emotions(raw_text)
                probability = get_prediction_proba(raw_text)
                
                # Create emotions dictionary
                emotions_dict = {}
                for emotion_class, prob in zip(pipe_lr.classes_, probability[0]):
                    emotions_dict[emotion_class] = prob
                
                # Save to session state
                st.session_state.current_analysis = {
                    'text': raw_text,
                    'emotion': prediction[0],
                    'confidence': np.max(probability),
                    'all_emotions': emotions_dict
                }
                
                # Save to local history
                st.session_state.analysis_history.append(st.session_state.current_analysis)
                
                # Save to global emotion history tracking
                add_emotion_to_history(prediction[0], float(np.max(probability)), 'text')
                increment_total_analyses()
            
            st.success("✅ Analysis Complete!")
            st.rerun()

# RIGHT COLUMN - RESULTS PANEL
with col_results:
    if st.session_state.current_analysis is None:
        st.markdown("""
        <div style='background: rgba(99, 102, 241, 0.1); border: 2px dashed rgba(99, 102, 241, 0.3); 
                    border-radius: 10px; padding: 40px; text-align: center;'>
            <div style='font-size: 3em; margin-bottom: 15px;'>👈</div>
            <div style='color: #a8b8d8; font-size: 1.1em;'>Enter text on the left and click <strong>Analyze</strong></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        analysis = st.session_state.current_analysis
        emotion = analysis.get('emotion') or analysis.get('label') or analysis.get('predicted_emotion') or 'neutral'
        confidence = analysis.get('confidence', 0)
        analyzed_text = analysis.get('text', '')
        
        # Display dominant emotion card with large emoji
        emotion_emoji_map = {
            'anger': '😠', 'disgust': '🤮', 'fear': '😨', 
            'happy': '😊', 'joy': '😂', 'neutral': '😐', 
            'sad': '😢', 'sadness': '😢', 'shame': '😳', 'surprise': '😮'
        }
        emoji = emotion_emoji_map.get(str(emotion).lower(), '😐')
        
        st.markdown(f"""
        <div style='background: rgba(99, 102, 241, 0.1); border: 2px solid rgba(99, 102, 241, 0.5); 
                    border-radius: 15px; padding: 30px; text-align: center; margin-bottom: 20px;'>
            <div style='font-size: 72px; margin-bottom: 15px;'>{emoji}</div>
            <div style='font-size: 1.8em; font-weight: 700; color: #f1f5f9; margin-bottom: 10px;'>
                {str(emotion).capitalize()}
            </div>
            <div style='font-size: 1.5em; font-weight: 600; color: #667eea; margin-bottom: 5px;'>
                {confidence:.0%}
            </div>
            <div style='font-size: 0.9em; color: #8b9ac9;'>Confidence Score</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Divider
        st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.2); margin: 20px 0;'>", unsafe_allow_html=True)
        
        # Display analyzed text
        st.markdown("**📋 Analyzed Text:**")
        st.text_area("", value=analyzed_text, disabled=True, height=150, label_visibility="collapsed")

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0 30px 0;'>", unsafe_allow_html=True)

# ============================================================================
# FULL WIDTH - PROBABILITY CHART
# ============================================================================
if st.session_state.current_analysis is not None:
    analysis = st.session_state.current_analysis
    all_emotions = analysis.get('all_emotions', {})
    
    st.markdown("**📈 Emotion Probability Distribution**")
    
    emotions_list = list(all_emotions.keys())
    probabilities = [all_emotions[e] * 100 for e in emotions_list]
    colors = [EMOTION_COLORS.get(e.lower(), '#6366f1') for e in emotions_list]
    
    fig_bar = go.Figure(data=[
        go.Bar(
            y=emotions_list,
            x=probabilities,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='white', width=1)
            ),
            text=[f"{p:.1f}%" for p in probabilities],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Probability: %{x:.1f}%<extra></extra>',
            showlegend=False
        )
    ])
    
    fig_bar.update_layout(
        xaxis=dict(
            title="Probability (%)",
            range=[0, 100],
            gridcolor='rgba(99, 102, 241, 0.1)'
        ),
        yaxis=dict(title=""),
        height=350,
        margin=dict(l=120, r=20, t=20, b=50),
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='closest',
        font=dict(color='#f1f5f9'),
        xaxis_ticksuffix='%'
    )
    
    st.plotly_chart(fig_bar, use_container_width=True, key="bar_chart")
    
    st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0 30px 0;'>", unsafe_allow_html=True)

# ============================================================================
# ANALYSIS HISTORY & STATISTICS
# ============================================================================
if st.session_state.analysis_history:
    st.markdown("**📈 Session Statistics**")
    
    history_df = pd.DataFrame(st.session_state.analysis_history)
    emotion_counts = history_df['emotion'].value_counts()
    
    # Stats row
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("Total Analyses", len(st.session_state.analysis_history))
    
    with stat_col2:
        st.metric("Most Common", emotion_counts.index[0].capitalize() if len(emotion_counts) > 0 else "N/A")
    
    with stat_col3:
        avg_confidence = history_df['confidence'].mean()
        st.metric("Avg. Confidence", f"{avg_confidence:.0%}")
    
    with stat_col4:
        st.metric("Unique Emotions", len(emotion_counts))
    
    st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 30px 0;'>", unsafe_allow_html=True)
    
    # Charts side by side
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        emotion_dist = pd.DataFrame({
            'Emotion': emotion_counts.index.str.capitalize(),
            'Count': emotion_counts.values
        })
        
        fig_pie = px.pie(
            emotion_dist,
            values='Count',
            names='Emotion',
            hole=0.3
        )
        
        fig_pie.update_traces(
            marker=dict(
                colors=[EMOTION_COLORS.get(e.lower(), '#6366f1') for e in emotion_counts.index],
                line=dict(color='white', width=2)
            ),
            textposition='inside',
            textinfo='label+percent'
        )
        
        fig_pie.update_layout(
            title="Emotion Distribution",
            height=350,
            margin=dict(l=0, r=0, t=40, b=0),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9'),
            hovermode='closest'
        )
        
        st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart")
    
    with chart_col2:
        history_with_idx = history_df.copy()
        history_with_idx['Analysis #'] = range(1, len(history_with_idx) + 1)
        
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=history_with_idx['Analysis #'],
            y=history_with_idx['confidence'] * 100,
            mode='lines+markers',
            name='Confidence',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#667eea', line=dict(color='white', width=2)),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)',
            hovertemplate='<b>Analysis #%{x}</b><br>Confidence: %{y:.0f}%<extra></extra>'
        ))
        
        fig_trend.update_layout(
            title="Confidence Trend",
            xaxis_title="Analysis #",
            yaxis_title="Confidence (%)",
            height=350,
            margin=dict(l=60, r=20, t=40, b=50),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',
            font=dict(color='#f1f5f9'),
            yaxis=dict(range=[0, 100]),
            xaxis=dict(gridcolor='rgba(99, 102, 241, 0.1)'),
            yaxis_gridcolor='rgba(99, 102, 241, 0.1)'
        )
        
        st.plotly_chart(fig_trend, use_container_width=True, key="trend_chart")

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)
render_emotion_timeline()
st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)
render_persistent_footer()
