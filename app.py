# app.py: Main Streamlit app for Movie/Drama Story Summarizer. Creates UI to input movie/drama titles, calls summarizer.py to fetch and process Wikipedia data, displays auto-corrected title, plot, genre, year. Supports Enter key, loads in ~1-2s.
import streamlit as st
from summarizer import get_summary

st.set_page_config(page_title="Movie/Drama Story Summarizer", page_icon="🎥")
st.title("🎥 Movie/Drama Story Summarizer")

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

with st.form(key='title_form'):
    title = st.text_input("Enter movie or drama title:", placeholder="e.g., Mr Queen, Evil Dead Rise")
    submit_button = st.form_submit_button("Get Story")

    if submit_button or st.session_state.submitted:
        if title:
            with st.spinner("Fetching story..."):
                result = get_summary(title)
            if 'error' in result:
                st.error(result['error'])
            else:
                st.markdown(f"**Story:** {result['summary']}")
                st.success(f"**Title:** {result['title']}")
                st.info(f"**Genre:** {result['genre']} | **Year:** {result['year']}")
        else:
            st.warning("Please enter a title.")
        st.session_state.submitted = False
