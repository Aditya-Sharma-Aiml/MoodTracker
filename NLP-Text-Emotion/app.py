import streamlit as st
import numpy as np
import pandas as pd
import joblib
import altair as alt
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, 'models', 'emotion_classifier_pipe_lr_03_jan_2022.pkl')

# Load the model with error handling
try:
    if not os.path.exists(model_path):
        st.error(f"❌ Model file not found at: {model_path}")
        st.stop()
    with open(model_path, 'rb') as f:
        pipe_lr = joblib.load(f)
except FileNotFoundError as e:
    st.error(f"❌ Model file not found: {model_path}")
    st.stop()
except Exception as e:
    st.error(f"❌ Error loading model: {str(e)}")
    st.stop()

#function to read the emotion
def predict_emotions(docx):
    results=pipe_lr.predict([docx] )
    return results

def get_prediction_proba(docx):
    results=pipe_lr.predict_proba([docx] )
    return results

emotions_emoji_dict = {"anger":"😠","disgust":"🤮", "fear":"😨😱", "happy":"🤗", "joy":"😂", "neutral":"😐", "sad":"😔", "sadness":"😔", "shame":"😳", "surprise":"😮"}

def main():
    st.title('Emotion Classifier App')
    menu=["Home", "Monitor", "About"]
    choice=st.sidebar.selectbox("Menu",menu)

    if choice == "Home":
        st.subheader("Home-Emotion in text")

        with st.form(key='emotion_clf_form'):
            raw_text = st.text_area("Please enter your text")
            submit_text = st.form_submit_button(label="Submit")

        if submit_text:
            if not raw_text or len(raw_text.strip()) == 0:
                st.error("❌ Please enter some text")
            elif len(raw_text) > 2000:
                st.warning("⚠️ Text is quite long (>2000 chars). Processing might take a moment...")
                col1, col2 = st.columns(2)
                prediction = predict_emotions(raw_text)
                probability = get_prediction_proba(raw_text)
            else:
                col1, col2 = st.columns(2)
                prediction = predict_emotions(raw_text)
                probability = get_prediction_proba(raw_text)
            with col1:
                st.success('Original text')
                st.write(raw_text)

                st.success("Prediction")
                emoji_icon = emotions_emoji_dict[prediction[0]]
                st.write("{}:{}".format(prediction[0], emoji_icon))
                st.write("Confidence: {}".format(np.max(probability)))

            with col2:
                st.success('Prediction Probability')
                st.write(probability)
                proba_df=pd.DataFrame(probability,columns=pipe_lr.classes_)
                st.write(proba_df.transpose())
                proba_df_clean=proba_df.transpose().reset_index()
                proba_df_clean.columns=["emotions","probability"]

            fig=alt.Chart(proba_df_clean).mark_bar().encode(x='emotions', y='probability',color='emotions')
            st.altair_chart(fig,use_container_width=True)
                

    elif choice == "Monitor":
        st.subheader("Monitor App")
    else:
        st.subheader("About")
        st.write("This is an NLP powered webapp that can predict emotion from text recognition with 93% accuracy. Many Python libraries like Numpy, Pandas, Seaborn, Scikit-learn, Scipy, Joblib, eli5, lime, neattext, altair, and streamlit were used. Streamlit was used for front-end development, and a Linear regression model from the scikit-learn library was used to train a dataset containing speeches and their respective emotions.")
        st.divider()
        st.markdown("""
            <div style='text-align: center; padding: 20px; color: #666; border-top: 1px solid #eee;'>
                <p><strong>Made by Aditya Sharma</strong></p>
                <p>© 2024 MoodTracker. All rights reserved.</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
