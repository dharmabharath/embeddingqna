import streamlit as st
from streamlit_chat import message
from utilities.helper import LLMHelper
import regex as re
import os
from random import randint

with open('chat.css', 'r') as css_file:
    custom_css = css_file.read()
def clear_chat_data():
    st.session_state['chat_history'] = []
    st.session_state['chat_source_documents'] = []
    st.session_state['chat_askedquestion'] = ''
    st.session_state['chat_question'] = ''
    st.session_state['chat_followup_questions'] = []
    answer_with_citations = ""

def questionAsked():
    st.session_state.chat_askedquestion = st.session_state["input"+str(st.session_state ['input_message_key'])]
    st.session_state["input"+str(st.session_state ['input_message_key'])] = ""
    st.session_state.chat_question = st.session_state.chat_askedquestion

# Callback to assign the follow-up question is selected by the user
def ask_followup_question(followup_question):
    st.session_state.chat_askedquestion = followup_question
    st.session_state['input_message_key'] = st.session_state['input_message_key'] + 1

try :
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
    st.text('Chat')
    # Initialize chat history
    if 'chat_question' not in st.session_state:
            st.session_state['chat_question'] = ''
    if 'chat_askedquestion' not in st.session_state:
        st.session_state.chat_askedquestion = ''
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'chat_source_documents' not in st.session_state:
        st.session_state['chat_source_documents'] = []
    if 'chat_followup_questions' not in st.session_state:
        st.session_state['chat_followup_questions'] = []
    if 'input_message_key' not in st.session_state:
        st.session_state ['input_message_key'] = 1

    # Initialize Chat Icons
    ai_avatar_style = os.getenv("CHAT_AI_AVATAR_STYLE", "icons")
    ai_seed = os.getenv("CHAT_AI_SEED", "oliver&backgroundColor=495495")
    user_avatar_style = os.getenv("CHAT_USER_AVATAR_STYLE", "shapes")
    user_seed = os.getenv("CHAT_USER_SEED", "oscar")

    llm_helper = LLMHelper()

    # Chat 
    # clear_chat = st.button("Clear chat", key="clear_chat", on_click=clear_chat_data)
    input_text = st.text_input(" ", placeholder="Type your question here", key="input"+str(st.session_state ['input_message_key']), on_change=questionAsked)


    # If a question is asked execute the request to get the result, context, sources and up to 3 follow-up questions proposals
    if st.session_state.chat_askedquestion:
        st.session_state['chat_question'] = st.session_state.chat_askedquestion
        st.session_state.chat_askedquestion = ""
        st.session_state['chat_question'], result, context, sources = llm_helper.get_semantic_answer_lang_chain(st.session_state['chat_question'], st.session_state['chat_history'])    
        result, chat_followup_questions_list = llm_helper.extract_followupquestions(result)
        st.session_state['chat_history'].append((st.session_state['chat_question'], result))
        st.session_state['chat_source_documents'].append(sources)
        st.session_state['chat_followup_questions'] = chat_followup_questions_list


    # Displays the chat history
    if st.session_state['chat_history']:
        history_range = range(len(st.session_state['chat_history'])-1, -1, -1)
        for i in range(len(st.session_state['chat_history'])):

            # This history entry is the latest one - also show follow-up questions, buttons to access source(s) context(s) 
            # question_avatar_style = (os.path.join('images','user.png'))
            answer_with_citations = re.sub(r'\$\^\{(.*?)\}\$', r'(\1)', st.session_state['chat_history'][i][1]) # message() does not get Latex nor html
            # with st.chat_message("user"):
            #     st.write(st.session_state['chat_history'][i][0])
            message(st.session_state['chat_history'][i][0], is_user=True, key=str(i)+'user' + '_user',avatar_style=user_avatar_style,seed=user_seed)
            # <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180" fill="none" shape-rendering="auto" width="512" height="512"><metadata xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/"><rdf:RDF><rdf:Description><dc:title>Bottts</dc:title><dc:creator>Pablo Stanley</dc:creator><dc:source xsi:type="dcterms:URI">https://bottts.com/</dc:source><dcterms:license xsi:type="dcterms:URI">https://bottts.com/</dcterms:license><dc:rights>Remix of „Bottts” (https://bottts.com/) by „Pablo Stanley”, licensed under „Free for personal and commercial use” (https://bottts.com/)</dc:rights></rdf:Description></rdf:RDF></metadata><mask id="viewboxMask"><rect width="180" height="180" rx="0" ry="0" x="0" y="0" fill="#fff" /></mask><g mask="url(#viewboxMask)"><g transform="scale(-1 1) translate(-180 0)"><g transform="translate(0 66)"><mask id="sidesAntenna01-a" style="mask-type:luminance" maskUnits="userSpaceOnUse" x="6" y="11" width="156" height="51"><g fill="#fff"><rect x="6" y="31" width="36" height="14" rx="4"/><rect x="18" y="14" width="36" height="48" rx="4"/><rect x="126" y="28" width="36" height="24" rx="4"/><path d="M11 11h2v20h-2z"/></g></mask><g mask="url(#sidesAntenna01-a)"><path d="M0 0h180v76H0V0Z" fill="#3949ab"/><path fill="#fff" fill-opacity=".3" d="M0 0h180v76H0z"/><path fill="#000" fill-opacity=".1" d="M0 38h180v38H0z"/></g><path fill="#fff" fill-opacity=".4" d="M11 11h2v20h-2z"/><circle cx="12" cy="8" r="4" fill="#FFEA8F"/><circle cx="13" cy="7" r="2" fill="#fff"/></g><g transform="translate(41)"><mask id="topAntennaCrooked-a" style="mask-type:luminance" maskUnits="userSpaceOnUse" x="38" y="12" width="24" height="40"><g fill="#fff"><path d="M55.54 34.39 51 45h-3.74l4.92-10.44-6.05-10.43 3.22-11.84 2.9.8-2.9 10.62 6.2 10.68Z"/><path d="M38 39h24v13H38z"/></g></mask><g mask="url(#topAntennaCrooked-a)"><path d="M0 0h100v52H0V0Z" fill="#3949ab"/><path d="M0 6h100v52H0V6Z" fill="#fff" fill-opacity=".3"/><path fill="#fff" fill-opacity=".2" d="M38 39h24v13H38z"/></g><circle cx="50" cy="8" r="8" fill="#FFE65C"/><circle cx="53" cy="5" r="3" fill="#fff"/></g><g transform="translate(25 44)"><mask id="faceSquare01-a" style="mask-type:luminance" maskUnits="userSpaceOnUse" x="0" y="0" width="130" height="120"><rect width="130" height="120" rx="18" fill="#fff"/></mask><g mask="url(#faceSquare01-a)"><path d="M-2-2h134v124H-2V-2Z" fill="#3949ab"/><g transform="translate(-1 -1)"></g></g></g><g transform="translate(52 124)"><rect x="24" y="6" width="27" height="8" rx="4" fill="#000" fill-opacity=".8"/></g><g transform="translate(38 76)"><rect x="8" y="10" width="88" height="36" rx="4" fill="#000" fill-opacity=".8"/><rect x="28" y="21" width="10" height="17" rx="2" fill="#5EF2B8"/><rect x="66" y="21" width="10" height="17" rx="2" fill="#5EF2B8"/><path fill-rule="evenodd" clip-rule="evenodd" d="M83 10h5L76 46h-5l12-36Z" fill="#fff" fill-opacity=".4"/></g></g></g></svg>
            # with st.chat_message("user"):
            #     st.write(answer_with_citations)
            message(answer_with_citations ,key=str(i)+'answers', avatar_style=ai_avatar_style, seed=ai_seed)
            # st.markdown(f'\n\nSources: {st.session_state["chat_source_documents"][i]}')


            if i == history_range.start:
                answer_with_citations, sourceList, matchedSourcesList, linkList, filenameList = llm_helper.get_links_filenames(st.session_state['chat_history'][i][1], st.session_state['chat_source_documents'][i])
                st.session_state['chat_history'][i] = st.session_state['chat_history'][i][:1] + (answer_with_citations,)

                answer_with_citations = re.sub(r'\$\^\{(.*?)\}\$', r'(\1)', st.session_state['chat_history'][i][1]).strip() # message() does not get Latex nor html

                # Display proposed follow-up questions which can be clicked on to ask that question automatically
                if len(st.session_state['chat_followup_questions']) > 0:
                    st.markdown('Proposed follow-up questions:')
                with st.container():
                    # st.markdown('**Proposed follow-up questions:**')
                    for questionId, followup_question in enumerate(st.session_state['chat_followup_questions']):
                        if followup_question:
                            
                            str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)
                            st.button(str_followup_question, key=randint(1000,99999), on_click=ask_followup_question, args=(followup_question, ))
                    
                for questionId, followup_question in enumerate(st.session_state['chat_followup_questions']):
                    if followup_question:
                        str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)

            
       

except Exception:
    st.error(traceback.format_exc())
