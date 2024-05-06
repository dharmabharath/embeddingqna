import streamlit as st
from utilities.helper import LLMHelper
import os
import traceback

with open('documentsummary.css', 'r') as css_file:
    custom_css = css_file.read()
def summarize():
    response = llm_helper.get_completion(get_prompt())
    st.session_state['summary'] = response

def clear_summary():
    st.session_state['summary'] = ""

def get_prompt():
    text = st.session_state['text']
    if text is None or text == '':
        text = '{}'
    if summary_type == "Basic Summary":
        prompt = "Summarize the following text:\n\n{}\n\nSummary:".format(text)
    elif summary_type == "Bullet Points":
        prompt = "Summarize the following text into bullet points:\n\n{}\n\nSummary:".format(text)
    elif summary_type == "Explain it to a second grader":
        prompt = "Explain the following text to a second grader:\n\n{}\n\nSummary:".format(text)

    return prompt

try:
    st.set_page_config(
        page_title="QuadraopenAI",
        page_icon="images/quadrafavicon.png",
        layout="wide"
    )
    st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)
    st.markdown("""<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.2.1/dist/css/bootstrap.min.css" integrity="sha384-GJzZqFGwb1QTTN6wy59ffF1BuGJpLSa9DkKMp0DgiMDm4iYMj70gZWKYbI706tWS" crossorigin="anonymous">
                <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
                <script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.6/dist/umd/popper.min.js" integrity="sha384-wHAiFfRlMFy6i5SRaxvfOCifBUQy1xHdJ/yoi7FRNXMRBu5WHdZYu1hA6ZOblgut" crossorigin="anonymous"></script>
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.2.1/dist/js/bootstrap.min.js" integrity="sha384-B0UglyR+jN6CkvvICOB2joaf5I4l3gm9GU6Hc1og6Ls7i6U/mkkaduKaBhlAXv9k" crossorigin="anonymous"></script>
                """
                ,unsafe_allow_html=True)
    logo_url = 'images/quadralogo.png'
    st.sidebar.image(logo_url)

    st.text('Utilis Document Summary')
    # Set page layout to wide screen and menu item
    menu_items = {
    'Get help': None,
    'Report a bug': None,
    'About': '''
     ## Embeddings App
     Embedding testing application.
    '''
    }
    # st.set_page_config(layout="wide", menu_items=menu_items)

    llm_helper = LLMHelper()

    st.markdown("Summarization")
    # radio buttons for summary type
    summary_type = st.radio(
        "Select a type of summarization",
        ["Basic Summary", "Bullet Points", "Explain it to a second grader"],
        key="visibility"
    )
    # text area for user to input text
    st.session_state['text'] = st.text_area(label="Enter some text to summarize",value='A neutron star is the collapsed core of a massive supergiant star, which had a total mass of between 10 and 25 solar masses, possibly more if the star was especially metal-rich.[1] Neutron stars are the smallest and densest stellar objects, excluding black holes and hypothetical white holes, quark stars, and strange stars.[2] Neutron stars have a radius on the order of 10 kilometres (6.2 mi) and a mass of about 1.4 solar masses.[3] They result from the supernova explosion of a massive star, combined with gravitational collapse, that compresses the core past white dwarf star density to that of atomic nuclei.', height=200)
    st.button(label="Summarize", on_click=summarize)

    # if summary doesn't exist in the state, make it an empty string
    summary = ""
    if 'summary' in st.session_state:
        summary = st.session_state['summary']

    # displaying the summary
    st.text_area(label="Summary result", value=summary, height=200)
    st.button(label="Clear summary", on_click=clear_summary)

    # displaying the prompt that was used to generate the summary
    st.text_area(label="Prompt",value=get_prompt(), height=400)
    st.button(label="Summarize with updated prompt")

except Exception as e:
    st.error(traceback.format_exc())
