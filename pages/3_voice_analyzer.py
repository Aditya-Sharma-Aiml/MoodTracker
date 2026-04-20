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

warnings.filterwarnings('ignore')

st.set_page_config(page_title='Voice Mood Analyzer', page_icon='🎙️', layout='wide')

col1, col2, col3 = st.columns([1, 10, 1])
with col1:
    if st.button('⬅️ Back', key='va_back_btn_final'):
        st.switch_page('landing_page.py')

if 'recordings' not in st.session_state:
    st.session_state.recordings = []
if 'mood_data' not in st.session_state:
    st.session_state.mood_data = {'Happy': 0, 'Sad': 0, 'Neutral': 0}
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False

def get_mood(polarity):
    return 'Happy' if polarity > 0.1 else 'Sad' if polarity < -0.1 else 'Neutral'

def get_emoji(mood):
    return {'Happy': '😊', 'Sad': '😢', 'Neutral': '😐'}.get(mood, '😐')

def process_audio(audio_path):
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        wav_path = audio_path.rsplit('.', 1)[0] + '_converted.wav'
        audio.export(wav_path, format='wav')
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
        return audio_data, None
    except Exception as e:
        return None, str(e)

def save_recording(text, mood, polarity, source):
    st.session_state.recordings.append({'text': text, 'mood': mood, 'polarity': polarity, 'source': source, 'timestamp': datetime.now()})
    st.session_state.mood_data[mood] += 1

st.title('🎙️ Voice Mood Analyzer')
st.markdown('**Analyze Your Mood Through Voice**')
st.info('📝 Record your voice or upload audio. We will analyze your mood!')

tab1, tab2 = st.tabs(['🎤 Live Recording', '📤 Upload Audio'])

with tab1:
    st.subheader('🎤 Record Your Voice')
    st.write('Click **START**, speak, then **STOP** to analyze.')
    col_s, col_x, _ = st.columns([1, 1, 3])
    with col_s:
        if st.button('🔴 START', key='start_btn_final'):
            st.session_state.is_recording = True
            st.rerun()
    with col_x:
        if st.button('⏹️ STOP', key='stop_btn_final'):
            st.session_state.is_recording = False
            st.rerun()
    if st.session_state.is_recording:
        st.info('🎙️ Recording...')
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            st.session_state.is_recording = False
            with st.spinner('Processing...'):
                try:
                    text = recognizer.recognize_google(audio)
                    polarity = TextBlob(text).sentiment.polarity
                    mood = get_mood(polarity)
                    save_recording(text, mood, polarity, 'Live')
                    st.success('✅ Done!')
                    col_m, col_t = st.columns(2)
                    with col_m:
                        st.metric('Mood', f'{get_emoji(mood)} {mood}')
                    with col_t:
                        st.write(f'**Text:** _{text}_')
                except sr.UnknownValueError:
                    st.error('❌ Could not understand audio!')
                except sr.RequestError as e:
                    st.error(f'❌ Error: {e}')
        except Exception as e:
            st.error(f'❌ Mic Error: {e}')
            st.session_state.is_recording = False
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric('Total', len(st.session_state.recordings))
    with c2:
        st.metric('😊 Happy', st.session_state.mood_data['Happy'])
    with c3:
        st.metric('😢 Sad', st.session_state.mood_data['Sad'])
    with c4:
        st.metric('😐 Neutral', st.session_state.mood_data['Neutral'])

with tab2:
    st.subheader('📤 Upload Audio')
    uploaded = st.file_uploader('Choose file', type=['wav', 'mp3', 'ogg', 'm4a', 'flac'], key='uploader_final')
    if uploaded:
        st.audio(uploaded)
        if st.button('🔍 Analyze', key='analyze_btn_final'):
            with st.spinner('Processing...'):
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded.name.split(".")[-1]}') as f:
                    f.write(uploaded.getbuffer())
                    tmp_path = f.name
                try:
                    recognizer = sr.Recognizer()
                    audio, err = process_audio(tmp_path)
                    if err:
                        st.error(f'❌ {err}')
                    elif audio:
                        text = recognizer.recognize_google(audio)
                        polarity = TextBlob(text).sentiment.polarity
                        mood = get_mood(polarity)
                        save_recording(text, mood, polarity, 'Upload')
                        st.success('✅ Done!')
                        col_m, col_t = st.columns(2)
                        with col_m:
                            st.metric('Mood', f'{get_emoji(mood)} {mood}')
                        with col_t:
                            st.write(f'**Text:** _{text}_')
                    else:
                        st.error('❌ Could not process file!')
                except Exception as e:
                    st.error(f'❌ {e}')
                finally:
                    if os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except:
                            pass

st.divider()
if st.session_state.recordings:
    st.subheader('📊 Analytics')
    col_p, col_l = st.columns(2)
    with col_p:
        st.subheader('Mood Distribution')
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#43e97b', '#fa709a', '#30cfd0']
        sizes = list(st.session_state.mood_data.values())
        labels = list(st.session_state.mood_data.keys())
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
        for autotext in autotexts:
            autotext.set_color('white')
        ax.axis('equal')
        st.pyplot(fig)
    with col_l:
        st.subheader('Sentiment Over Time')
        df = pd.DataFrame({'Rec': range(1, len(st.session_state.recordings) + 1), 'Score': [r['polarity'] for r in st.session_state.recordings]})
        chart = alt.Chart(df).mark_line(point=True, color='#43e97b').encode(x='Rec:Q', y=alt.Y('Score:Q', scale=alt.Scale(domain=[-1, 1]))).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    st.divider()
    st.subheader('Recent Recordings')
    for i, record in enumerate(reversed(st.session_state.recordings[-5:]), 1):
        idx = len(st.session_state.recordings) - i
        with st.expander(f'#{idx + 1} - {get_emoji(record["mood"])} {record["mood"]}'):
            st.write(f'**Text:** {record["text"]}')
            st.write(f'**Source:** {record["source"]}')
            st.write(f'**Score:** {record["polarity"]:.2f}')

st.divider()
st.markdown('<p style=\"text-align: center; color: #888;\">🎙️ Voice Mood Analyzer v3.2 | © 2026 MoodTracker</p>', unsafe_allow_html=True)
