import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    apply_global_theme,
    apply_page_css,
    render_persistent_footer,
    get_emotion_history,
    clear_emotion_history,
    export_history_to_csv
)

st.set_page_config(
    page_title="Emotion History Dashboard",
    page_icon="📊",
    layout="wide"
)

# Apply global theme and page CSS
apply_global_theme()
apply_page_css()

# Page Header
col_header_back, col_header_title = st.columns([0.5, 3])
with col_header_back:
    if st.button("⬅️ Back", key="history_back", help="Return to home"):
        st.switch_page("home.py")

with col_header_title:
    st.markdown("""
    <h1 style='font-size: 2.8em; font-weight: 800; margin: 0; padding: 0;'>📊 Emotion History Dashboard</h1>
    <p style='color: #8b9ac9; font-size: 1.05em; margin: 5px 0 0 0;'>Track your emotion patterns over time</p>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 20px 0 30px 0;'>", unsafe_allow_html=True)

# Get emotion history
history = get_emotion_history()

if not history:
    st.markdown("""
    <div style='background: rgba(99, 102, 241, 0.1); border: 2px dashed rgba(99, 102, 241, 0.3); 
                border-radius: 10px; padding: 40px; text-align: center;'>
        <div style='font-size: 2em; margin-bottom: 15px;'>📭</div>
        <div style='color: #8b9ac9; font-size: 1.05em;'>No emotion history yet. Start analyzing to see your patterns!</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    render_persistent_footer()
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(history)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')

# ============================================================================
# FILTER CONTROLS - HORIZONTAL ROW
# ============================================================================
st.markdown("**🔍 Filters**")

col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    time_range = st.selectbox(
        "📅 Time Range",
        ["Last Hour", "Last 24 Hours", "Last 7 Days", "All Time"],
        index=1,
        label_visibility="collapsed"
    )
    
    # Apply time filter
    now = datetime.now()
    if time_range == "Last Hour":
        cutoff = now - timedelta(hours=1)
    elif time_range == "Last 24 Hours":
        cutoff = now - timedelta(days=1)
    elif time_range == "Last 7 Days":
        cutoff = now - timedelta(days=7)
    else:
        cutoff = now - timedelta(days=365)
    
    df_filtered = df[df['timestamp'] >= cutoff].copy()

with col_filter2:
    sources = df['source'].unique().tolist()
    selected_sources = st.multiselect(
        "🔍 Filter by Source",
        sources,
        default=sources,
        label_visibility="collapsed"
    )
    df_filtered = df_filtered[df_filtered['source'].isin(selected_sources)]

with col_filter3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 30px 0;'>", unsafe_allow_html=True)

# ============================================================================
# SUMMARY STATS - TOP ROW
# ============================================================================
st.markdown("**📈 Summary Statistics**")

stat_col1, stat_col2, stat_col3 = st.columns(3)

with stat_col1:
    st.metric("Total Analyses", len(df_filtered))

with stat_col2:
    if len(df_filtered) > 0:
        most_common = df_filtered['emotion'].value_counts().index[0]
        st.metric("Most Common Emotion", most_common.capitalize())
    else:
        st.metric("Most Common Emotion", "N/A")

with stat_col3:
    if len(df_filtered) > 0:
        avg_confidence = df_filtered['confidence'].mean()
        st.metric("Avg Confidence", f"{avg_confidence:.0%}")
    else:
        st.metric("Avg Confidence", "N/A")

st.markdown("<hr style='border:1px solid rgba(99, 102, 241, 0.3); margin: 30px 0;'>", unsafe_allow_html=True)

# ============================================================================
# CHARTS SECTION
# ============================================================================
col_chart1, col_chart2 = st.columns(2, gap="large")

with col_chart1:
    st.subheader("📈 Emotion Timeline")
    
    if len(df_filtered) > 0:
        # Create numeric mapping for emotions for Y-axis
        emotion_mapping = {
            'Happy': 4,
            'Sad': 2,
            'Neutral': 3,
            'Angry': 1,
            'Surprise': 5,
            'Fear': 1,
            'Disgust': 1,
            'Shame': 2
        }
        
        df_chart = df_filtered.copy()
        df_chart['emotion_numeric'] = df_chart['emotion'].map(emotion_mapping)
        
        # Create line chart with Plotly
        fig = px.line(
            df_chart,
            x='timestamp',
            y='emotion_numeric',
            color='emotion',
            hover_data={
                'timestamp': ':%Y-%m-%d %H:%M:%S',
                'emotion_numeric': False,
                'confidence': ':.2f',
                'source': True,
                'emotion': True
            },
            title="Emotion Mood Over Time",
            labels={
                'timestamp': 'Time',
                'emotion_numeric': 'Mood Level',
                'emotion': 'Emotion',
                'confidence': 'Confidence'
            },
            markers=True,
            line_shape='spline'
        )
        
        # Update layout for better appearance
        fig.update_layout(
            hovermode='x unified',
            height=400,
            template='plotly_dark',
            margin=dict(l=0, r=0, t=30, b=0),
            yaxis=dict(
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['Low', 'Sad', 'Neutral', 'Happy', 'Very Happy']
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No data available for the selected filters")

with col_chart2:
    st.subheader("📊 Statistics")
    
    if len(df_filtered) > 0:
        # Emotion distribution
        emotion_counts = df_filtered['emotion'].value_counts()
        most_common = emotion_counts.index[0]
        most_common_count = emotion_counts.iloc[0]
        
        st.metric("Most Common", f"{most_common} ({most_common_count})")
        
        # Average confidence
        avg_confidence = df_filtered['confidence'].mean()
        st.metric("Avg Confidence", f"{avg_confidence:.0%}")
        
        # Source breakdown
        st.metric("Sources", len(df_filtered['source'].unique()))
        
        # Time range info
        time_span = (df_filtered['timestamp'].max() - df_filtered['timestamp'].min()).total_seconds() / 3600
        st.metric("Time Span (hours)", f"{time_span:.1f}")

st.divider()

# ============================================================================
# EMOTION DISTRIBUTION
# ============================================================================

col_pie, col_source = st.columns(2)

with col_pie:
    st.subheader("👥 Emotion Distribution")
    
    if len(df_filtered) > 0:
        emotion_dist = df_filtered['emotion'].value_counts()
        fig_pie = px.pie(
            values=emotion_dist.values,
            names=emotion_dist.index,
            template='plotly_dark',
            hole=0.3
        )
        fig_pie.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("No data available")

with col_source:
    st.subheader("🔍 Source Breakdown")
    
    if len(df_filtered) > 0:
        source_counts = df_filtered['source'].value_counts()
        
        # Custom HTML for source breakdown
        source_html = '<div style="padding: 20px;">'
        source_icons = {'text': '📝', 'face': '📷', 'voice': '🎙️'}

        for source, count in source_counts.items():
            pct = (count / len(df_filtered)) * 100
            icon = source_icons.get(source, '📊')
            source_html += (
                f'<div style="margin: 15px 0;">'
                f'<div style="display: flex; justify-content: space-between; align-items: center;">'
                f'<span><strong>{icon} {source.capitalize()}</strong></span>'
                f'<span style="color: #6366f1; font-weight: bold;">{count}</span>'
                f'</div>'
                f'<div style="background: #1e293b; height: 8px; border-radius: 4px; margin-top: 5px;">'
                f'<div style="background: linear-gradient(90deg, #6366f1, #8b5cf6); height: 100%; width: {pct}%; border-radius: 4px;"></div>'
                f'</div>'
                f'<div style="text-align: right; font-size: 0.8em; color: #888; margin-top: 3px;">{pct:.1f}%</div>'
                f'</div>'
            )

        source_html += '</div>'
        st.markdown(source_html, unsafe_allow_html=True)
    else:
        st.warning("No data available")

st.divider()

# ============================================================================
# DETAILED TABLE
# ============================================================================

st.subheader("📋 Detailed History")

if len(df_filtered) > 0:
    # Create display dataframe
    display_df = df_filtered.copy()
    display_df['timestamp_str'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df['confidence_pct'] = (display_df['confidence'] * 100).astype(int).astype(str) + '%'
    
    # Select columns to display
    display_cols = ['timestamp_str', 'emotion', 'confidence_pct', 'source']
    display_df_show = display_df[display_cols].rename(columns={
        'timestamp_str': 'Timestamp',
        'emotion': 'Emotion',
        'confidence_pct': 'Confidence',
        'source': 'Source'
    })
    
    # Reverse to show newest first
    display_df_show = display_df_show.iloc[::-1].reset_index(drop=True)
    
    st.dataframe(display_df_show, use_container_width=True, hide_index=True)
else:
    st.warning("No data available for the selected filters")

st.divider()

# ============================================================================
# ACTION BUTTONS
# ============================================================================

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("📥 Export as CSV", use_container_width=True, key="export_csv"):
        csv_content = export_history_to_csv()
        if csv_content:
            st.download_button(
                label="💾 Download CSV",
                data=csv_content,
                file_name=f"emotion_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.error("No history to export")

with col_btn2:
    if st.button("🔄 Refresh Data", use_container_width=True, key="refresh"):
        st.rerun()

with col_btn3:
    if st.button("🗑️ Clear All History", use_container_width=True, key="clear_history"):
        st.warning("⚠️ This will delete all emotion history!")
        
        col_confirm1, col_confirm2 = st.columns(2)
        with col_confirm1:
            if st.button("✅ Confirm Clear", key="confirm_clear"):
                clear_emotion_history()
                st.success("✅ History cleared!")
                st.rerun()
        with col_confirm2:
            if st.button("❌ Cancel", key="cancel_clear"):
                st.info("Cancelled")

st.divider()

# ============================================================================
# FOOTER
# ============================================================================

st.info("""
📌 **About This Dashboard:**
- Tracks all emotion detections across Text, Face, and Voice analysis
- Displays emotion mood trends over time using Plotly
- Allows filtering by time range and data source
- Supports CSV export for external analysis
- Auto-updates when you analyze content on other pages
""")

render_persistent_footer()
