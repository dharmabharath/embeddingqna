import streamlit as st
import os
import traceback
from utilities.helper import LLMHelper


with open('indexmanagement.css', 'r') as css_file:
    custom_css = css_file.read()

def delete_embedding():
    llm_helper.vector_store.delete_keys([f"{st.session_state['embedding_to_drop']}"])
    if 'data_embeddings' in st.session_state:
        del st.session_state['data_embeddings'] 

def delete_file_embeddings():
    if st.session_state['data_embeddings'].shape[0] != 0:
        file_to_delete = st.session_state['file_to_drop']
        embeddings_to_delete = st.session_state['data_embeddings'][st.session_state['data_embeddings']['filename'] == file_to_delete]['key'].tolist()
        embeddings_to_delete = list(map(lambda x: f"{x}", embeddings_to_delete))
        if len(embeddings_to_delete) > 0:
            llm_helper.vector_store.delete_keys(embeddings_to_delete)
            # remove all embeddings lines for the filename from session state
            st.session_state['data_embeddings'] = st.session_state['data_embeddings'].drop(st.session_state['data_embeddings'][st.session_state['data_embeddings']['filename'] == file_to_delete].index)

def delete_all():
    embeddings_to_delete = st.session_state['data_embeddings'].key.tolist()
    embeddings_to_delete = list(map(lambda x: f"{x}", embeddings_to_delete))
    llm_helper.vector_store.delete_keys(embeddings_to_delete)   



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
    st.text('Index Management')
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

    # Query RediSearch to get all the embeddings
    st.session_state['data_embeddings'] = llm_helper.get_all_documents(k=1000)

    nb_embeddings = len(st.session_state['data_embeddings'])

    if nb_embeddings == 0:
        st.warning("No embeddings found. Go to the 'Add Document' tab to insert your docs.")
    else:
        st.dataframe(st.session_state['data_embeddings'], use_container_width=True)
        st.text("")
        st.text("")
        st.download_button("Download data", st.session_state['data_embeddings'].to_csv(index=False).encode('utf-8'), "embeddings.csv", "text/csv", key='download-embeddings')

        st.text("")
        st.text("")
        col1, col2, col3 = st.columns([3,1,3])
        with col1:
            st.selectbox("Embedding id to delete", st.session_state['data_embeddings'].get('key',[]), key="embedding_to_drop")
            st.text("")
            st.button("Delete embedding", on_click=delete_embedding)
        with col2:
            st.text("")
        with col3:
            st.selectbox("File name to delete its embeddings", set(st.session_state['data_embeddings'].get('filename',[])), key="file_to_drop")
            st.text("")
            st.button("Delete file embeddings", on_click=delete_file_embeddings)

        st.text("")
        st.text("")
        st.button("Delete all embeddings", type="secondary", on_click=delete_all)
 
except Exception as e:
    st.error(traceback.format_exc())
