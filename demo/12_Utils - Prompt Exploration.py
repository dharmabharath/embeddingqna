import streamlit as st
import os
import traceback
from utilities.helper import LLMHelper
with open('promptexploration.css', 'r') as css_file:
    custom_css = css_file.read()
def get_prompt():
    return f"{st.session_state['doc_text']}\n{st.session_state['input_prompt']}"
   
def customcompletion():
    response = llm_helper.get_completion(get_prompt())
    st.session_state['prompt_result']= response.encode().decode()

def process_all(data):
    llm_helper.vector_store.delete_prompt_results('prompt*')
    data_to_process = data[data.filename.isin(st.session_state['selected_docs'])]
    for doc in data_to_process.to_dict('records'):
        prompt = f"{doc['content']}\n{st.session_state['input_prompt']}\n\n"
        response = llm_helper.get_completion(prompt)
        llm_helper.vector_store.add_prompt_result(doc['key'], response.encode().decode(), doc['filename'], st.session_state['input_prompt'])
    st.session_state['data_processed'] = llm_helper.vector_store.get_prompt_results().to_csv(index=False)

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

    st.text('Utilis Prompt Exploration')
    # Set page layout to wide screen and m
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

    if not 'data_processed' in st.session_state:
        st.session_state['data_processed'] = None

    llm_helper = LLMHelper()

    # Query RediSearch to get all the embeddings
    data = llm_helper.get_all_documents(k=1000)

    if len(data) == 0:
        st.warning("No embeddings found. Go to the 'Add Document' tab to insert your docs.")
    else:
        st.dataframe(data, use_container_width=True)

        # displaying a box for a custom prompt
        st.text_area(label="Document", height=400, key="doc_text")
        st.text_area(label="Prompt", height=100, key="input_prompt")
        st.button(label="Execute tasks", on_click=customcompletion)
        # displaying the summary
        result = ""
        if 'prompt_result' in st.session_state:
            result = st.session_state['prompt_result']
            st.text_area(label="Result", value=result, height=400)

        cols = st.columns([1,1,1,2])
        with cols[1]:
            st.multiselect("Select documents", sorted(set(data.filename.tolist())), key="selected_docs")
        with cols[2]:
            st.text("-")
            st.button("Execute task on docs", on_click=process_all, args=(data,)) 
        with cols[3]:
            st.text("-")
            download_data = st.session_state['data_processed'] if st.session_state['data_processed'] is not None else ""
            st.download_button(label="Download results", data=download_data, file_name="results.csv", mime="text/csv", disabled=st.session_state['data_processed'] is None)

except Exception as e:
    st.error(traceback.format_exc())
