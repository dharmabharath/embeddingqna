from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import traceback
from utilities.helper import LLMHelper
import regex as re

import logging
logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)



with open('opeanaiquer.css', 'r') as css_file:
    custom_css = css_file.read()


def check_deployment():
    # Check if the deployment is working
    #\ 1. Check if the llm is working
    try:
        llm_helper = LLMHelper()
        llm_helper.get_completion("Generate a joke!")
        st.toast("LLM is working!",icon="✅")
    except Exception as e:
        st.toast(f"""LLM is not working.  
            Please check you have a deployment name {llm_helper.deployment_name} in your Azure OpenAI resource {llm_helper.api_base}.  
            If you are using an Instructions based deployment (text-davinci-003), please check you have an environment variable OPENAI_DEPLOYMENT_TYPE=Text or delete the environment variable OPENAI_DEPLOYMENT_TYPE.  
            If you are using a Chat based deployment (gpt-35-turbo or gpt-4-32k or gpt-4), please check you have an environment variable OPENAI_DEPLOYMENT_TYPE=Chat.  
            Then restart your application.
            """,icon="❌")
        st.error(traceback.format_exc())
    #\ 2. Check if the embedding is working
    try:
        llm_helper = LLMHelper()
        llm_helper.embeddings.embed_documents(texts=["This is a test"])
        st.toast("Embedding is working!" ,icon="✅")
    except Exception as e:
        st.toast(f"""Embedding model is not working.  
            Please check you have a deployment named "text-embedding-ada-002" for "text-embedding-ada-002" model in your Azure OpenAI resource {llm_helper.api_base}.  
            Then restart your application.
            """,icon="❌")
        st.error(traceback.format_exc())
    #\ 3. Check if the translation is working
    try:
        llm_helper = LLMHelper()
        llm_helper.translator.translate("This is a test", "it")
        st.toast("Translation is working!",icon="✅")
    except Exception as e:
        st.toast(f"""Translation model is not working.  
            Please check your Azure Translator key in the App Settings.  
            Then restart your application.  
            """,icon="❌")
        st.error(traceback.format_exc())
    #\ 4. Check if the VectorStore is working with previous version of data
    try:
        llm_helper = LLMHelper()
        if llm_helper.vector_store_type == "AzureSearch":
            try:
                llm_helper.vector_store.index_exists()
                st.toast("Azure Cognitive Search is working!",icon="✅")
            except Exception as e:
                st.error("""Azure Cognitive Search is not working.  
                    Please check your Azure Cognitive Search service name and service key in the App Settings.  
                    Then restart your application.  
                    """)
                st.error(traceback.format_exc())
        elif llm_helper.vector_store_type == "PGVector":
            try:
                llm_helper.vector_store.__post_init__()
                st.toast("PGVector is working!",icon="✅")
            except Exception as e:
                st.toast("""PGVector is not working.  
                    Please check your Azure PostgreSQL server, database, user name and password in the App Settings.
                    Make sure the network settings(firewall rule) allow your app to access the Azure PostgreSQL service.
                    Then restart your application.  
                    """,icon="❌")
                st.error(traceback.format_exc())
        else:
            if llm_helper.vector_store.check_existing_index("embeddings-index"):
                st.warning("""Seems like you're using a Redis with an old data structure.  
                If you want to use the new data structure, you can start using the app and go to "Add Document" -> "Add documents in Batch" and click on "Convert all files and add embeddings" to reprocess your documents.  
                To remove this working, please delete the index "embeddings-index" from your Redis.  
                If you prefer to use the old data structure, please change your Web App container image to point to the docker image: fruocco/oai-embeddings:2023-03-27_25. 
                """)
            else:
                st.toast("Redis is working!",icon="✅")
    except Exception as e:
        st.toast(f"""Redis is not working. 
            Please check your Redis connection string in the App Settings.  
            Then restart your application.
            """,icon="❌")
        st.error(traceback.format_exc())


def check_variables_in_prompt():
    # Check if "summaries" is present in the string custom_prompt
    if "{summaries}" not in st.session_state.custom_prompt:
        st.warning("""Your custom prompt doesn't contain the variable "{summaries}".  
        This variable is used to add the content of the documents retrieved from the VectorStore to the prompt.  
        Please add it to your custom prompt to use the app.  
        Reverting to default prompt.
        """)
        st.session_state.custom_prompt = ""
    if "{question}" not in st.session_state.custom_prompt:
        st.warning("""Your custom prompt doesn't contain the variable "{question}".  
        This variable is used to add the user's question to the prompt.  
        Please add it to your custom prompt to use the app.  
        Reverting to default prompt.  
        """)
        st.session_state.custom_prompt = ""
    

 # Callback to assign the follow-up question is selected by the user
def ask_followup_question(followup_question):
    st.session_state.askedquestion = followup_question
    st.session_state['input_message_key'] = st.session_state['input_message_key'] + 1

def questionAsked():
    st.session_state.askedquestion = st.session_state["input"+str(st.session_state ['input_message_key'])]

@st.cache_data()
def get_languages():
    return llm_helper.translator.get_available_languages()

try:
    st.set_page_config(
        page_title="QuadraopenAI",
        page_icon="images/quadrafavicon.png",
        layout="wide"
    )
# Display button with custom styling
    st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)
    st.markdown("""<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.2.1/dist/css/bootstrap.min.css" integrity="sha384-GJzZqFGwb1QTTN6wy59ffF1BuGJpLSa9DkKMp0DgiMDm4iYMj70gZWKYbI706tWS" crossorigin="anonymous">
                <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
                <script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.6/dist/umd/popper.min.js" integrity="sha384-wHAiFfRlMFy6i5SRaxvfOCifBUQy1xHdJ/yoi7FRNXMRBu5WHdZYu1hA6ZOblgut" crossorigin="anonymous"></script>
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.2.1/dist/js/bootstrap.min.js" integrity="sha384-B0UglyR+jN6CkvvICOB2joaf5I4l3gm9GU6Hc1og6Ls7i6U/mkkaduKaBhlAXv9k" crossorigin="anonymous"></script>
                """
                ,unsafe_allow_html=True)
    logo_url = 'images/quadralogo.png'
    st.sidebar.image(logo_url)
#     card="""
# <div class="row row-cols-1 row-cols-md-2 g-2">
#   <div class="col">
#     <div class="card">
#       <img src="https://cdn.thenewstack.io/media/2021/11/28de6660-screen-shot-2021-11-29-at-6.46.11-am.png" class="card-img-top" alt=",icrosoft">
#       <div class="card-body">
#         <h5 class="card-title">Improved Internal Knowledge Sharing</h5>
#         <p class="card-text">Easily search through vast technical documents, manuals, and reports to find relevant information for troubleshooting, design reference, or regulatory compliance.
#         </p>
#       </div>
#     </div>
#   </div>
#   <div class="col">
#     <div class="card">
#       <img src="https://cdn.thenewstack.io/media/2021/11/28de6660-screen-shot-2021-11-29-at-6.46.11-am.png" class="card-img-top" alt="...">
#       <div class="card-body">
#         <h5 class="card-title">Efficient Research and Development</h5>
#         <p class="card-text">Researchers can rapidly search through scientific literature, clinical trial data, and regulatory documents to find relevant information for drug development and approval processes.
#         </p>
#       </div>
#     </div>
#   </div>
#   <div class="col">
#     <div class="card">
#       <img src="https://cdn.thenewstack.io/media/2021/11/28de6660-screen-shot-2021-11-29-at-6.46.11-am.png" class="card-img-top" alt="...">
#       <div class="card-body">
#         <h5 class="card-title">Empowered Sales Staff</h5>
#         <p class="card-text">Sales representatives can leverage the search tool to quickly access product specifications, marketing materials, and competitor information to better serve customers.
#         </p>
#       </div>
#     </div>
#   </div>

# </div>
# """
#     st.markdown(card, unsafe_allow_html= True)
    # def set_background():
    #     page_bg_img = '''
    #     <style>
    #     .css-uf99v8 {
    #     background-image: url("data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAsJCQcJCQcJCQkJCwkJCQkJCQsJCwsMCwsLDA0QDBEODQ4MEhkSJRodJR0ZHxwpKRYlNzU2GioyPi0pMBk7IRP/2wBDAQcICAsJCxULCxUsHRkdLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCz/wAARCAEaAacDASIAAhEBAxEB/8QAGwABAQADAQEBAAAAAAAAAAAAAAECBQYEAwf/xABNEAACAQMCBAMDAw8KAwkAAAAAAQIDBBEFEgYhMVETFEEiYXEVgZEWIzI0NUJUcnN0oaKxs9EHJTM2UnWytMHwJENVYmOUo8PE0uHx/8QAGgEBAQEAAwEAAAAAAAAAAAAAAQIAAwQGBf/EAC0RAQEAAgEDAwMDAgcAAAAAAAABAhEDEiExBBNRIkFxFDJhI5EFFUJDRFKB/9oADAMBAAIRAxEAPwD9BlKWXzJufcS6sxBa7n3JufcEBS7n3I5PuQGMXc+5Nz7sgArufcm59yAyork+fMm6XchGC4y3PuTc+5iDFdz7jL7kAKNz7jc+5BkCu59ybn3IQy1cn3G59yMgFdz7sm592CGVF3PuxufchAMXc+5NzDIC4u59ybn3IDKi7n3JuZBkCu59ybmQGUu5k3MgBSuT7kyyAFLl5Jlk9SGK5YyyZICouWHJkIZUXcw2+5ACoZZMsEYKXcxlkIYruYyyEBTJN5BF1BlN3LqyCXVkO88kAgMqAYIwVDkQAxgQDIKH6kDZDGAABcAQZA6CAhlhCk5AQcgQyoAEBUUgyQDIEAMoAICggBlBAAVoIByBQQPBDFSAgKgAQyopAAMCBgFxGAQxACcgUDkOXYhlaVdQF1AKbuXVmJZPmyHfeS0AZJkFDZAQxkUgJkFaMkKQygAAZAgGQVoyQEMvQTJckAgBMmVoAICgmRkAZAgyDKgQDIK0EyMkBUgADK0ZIAZWjkTIyQCDIbJkFaACGVIAEyCpFICZMdDYBAVIAMgKgM+4mQZWggAK0q6gibyAOm8l1ZBLqyHfeTCAGOggAKgQEMrQAAMgQpGZUgyAgLkCcy8yAQAhlaCFIB0BhkBUgQAytBCkBUgQAFSBADGQIAC9BMsEMQAgK0AEMrSkABUgQEMYcwCArQAxzBUiAMhlaAQArQTmABVdQRdQCm8l1ZiWXVkPoPJaCAArQRh+hDKkAABkCAGVIMgICpAgYBQB85GZWgAgEIykBUgQpDL0EAAhB3IBkUgBl6CAfOCpAgZDEAAK0gBDK0AEBWlICMCAEMqQAICpAMMhlSBAwCtBAAIQAytKuoIuoBWm8k+bMSy6sjO+8mgBDEAAKkAQZAyGSAhlSDIUgKACGVoGQQDoGRkxBWlIAZegA8d7dVbRUJqnGdOU3CpltSXLKw+hNupty8XHeXKYY+XryQ89veW1yl4c/bfWnLlNfBep6P8AfM0sveNnx5cd1nNUIDCpLbHk/afJe4LZDjhcr0w3xc9q9OnxMjyZfX16nphJTSfqlzIxy35dvm4Pbks8MiZ6Bk/3zLdaAPrTo1KmMLEe8uX0CtTjScYptvGZZMfvp8QCZBegAgK0pAQFaX1ICGMgMjJAVID5xkhlSAIMgqQyQMgHSkAMrQQEyCtMk1kEXUArTdyfNkyWXVmJ9B5IAAK0EAYGGSAhlyBBkAQcgQyoAEAhMlICtBADLCFIBGfG6oq4t61LHOUW4/jrmj6joFm5pyYZXDKZT7OSWU+zT6rk012ZsLbVLiniNZOrDpnOJx+f1PlqNHwbqptS2VfrsMdOfVfMeT3HzOrLjuo9vMOL1fFMspvbpqVzb14udOaeOcovlOPxR8pScpNv4fBHPLk8rk85TXX6T2Ub6pDCqreu6+yRze91dq+f/lns25cd22hlCW1+71PjTrUqqzCSfddGvij6Fy/Dr54bnTk9sKVSp9iko+kn0PVTt6cGm/al3fT5keSyr7JeFJ+zL7DPpLsbLqdnCyx8TlwvHl005L4Jc38OZq6k985y7vl8Ee25nsptLrP2V+1mv+BqMJ9wAhLm0AEAmQCGUAEBUgTPuLkhlSBCkBUgyAAUABlaCAZBSZAIZWlXUBdQBbuXVkLLqyHfeTACP0AwZAQygZGWQFABMmMAGQFQBGAVAgBlBCkBQyDJDKikAeQMa/VaPiUFUS9qhLLx/YlyZo8nVSjGcZQlzjKLjJPph8jn6mn31OTjGjKcctRlHGGvpydPnwu9yPS/4T6nGYXjzuteHlDZ6PJX/wCDVP1f4jyV/wDg1T9X+J1+jL4fa/UcX/af3j4Rk4vdGTi+6eGeyjqE1hVluXTdFJP50fLyV/8Ag1T9X+I8lf8A4NU/V/iMmc+zh5MuDk/dlP7xtYVadRZhNP1ys5RubWv41PEvs48pf6NHJwtNSg1KFCrFr1Tiv9TZ2VXUKdSLq0HDanmeY7WuzidnjzynmPi+t9Px3G3DKX/1sbqe+q0ukFt+f1PgMtvL6vmwdh8mTU0EBMkrACGIAyApSZY9SGMCZABcCDLAEIAZUCAjBS5ZAQygAgFknzBF1BlN5LqzEsur+JGd55IZAQywMjAEAIZUACAQMMgKgQDMYqUpyUIRjKc5vpGMVubZldtdxJt4SbfZdS7an9mX0M4Weq8S8UXdzbaLU8jplB4nWcpQbT6SrTj7bk+qisYM3wlr9OPiUuIajuFzWfMwi3+Oqjf6pfT81wzlt/ZjuO1Icdpmu6xYalDReIMSlUcKdC5lhzUp8qblOPKUJdE8JpnZJZkk/V4f8CMsbjXNhnMpuIQ0eicQLWbjUKCs/L+UjBqXi+J4ilOcOa2rHQ3gWWeXJhZl3gwTPwAOTQRggHQAQDIAEMuQAICooIQFaACGI2knKTjGMVmUpNRil3bfIxjOE1uhOE4vKUoSUotrs48jWcR4+Q9Xzj+ip9fysTycIYWiUcel1edPypfTvHqcXua5fb19m/bSltbjuxu27o7sd3HrgjOZhw/qUeInqru6bt/MzueUp+POMk8UJRa24XTrjCOguq3lbW8udu9W1vVruGdu504uWM+8MsfElXhyZWXLPHWn2IazRdV+WLWvc+X8v4Vw6GzxPEzinGe7O1d/0GzIynTdOXjzmeMyx8UICEuRSAhlRQQjBSsgIZUACAo5gEAquoC6gym8l1ZiWXVmJ33kwAgEAIzKgCAFAJkgGRSAGXA8eqQq1dL1mnSz4tSwuY08Zy5bG8I9Yzj1NL321x3NOP4EubR2d5YqUI3SuncRg2lOrTnThFOCfXbhpo69pp800zldU4NtbqtO70648ncSlKo6bi3Q3vm5Q2tSjn1w2eDyH8o+np+XvZXNOHSMLmNbOOi8O5SZyWTLvK62GWXFj05Y9nR6toNhrFSzq3NS4p1LRONOVtKMG4uaqJTyn69Ca1dcSW6svkSzhczqOv5nfCE3BRUdmN8o/wDaNHYcX3lG5jZa9aqhNyjB14wlSlTlJ7Yyq0nycffE7OOcx6fHr6dUTdyzblx6eSXo8vy7QLniK3uNRej2cK9acIK7U6cJeGt8msKUljnk77R6+tV7SrV1i3hb3aqV9lOEYRi6UI5i2oya/ScxwT9v8QfiUv31U7jHs1PydT/AyuTLv4R6bCzDq38uKsOMqqttTuNThQnVpSt6dhb20PDnXqVN2d2MvasLPL195stD1DizUL2U9QsfL2ErecqMVQVLNVzgoJOTdR8s9TQcFWVCvqF7eVYqTsaVNW6kk1GrWcvrnP1SXL4nb6jcTtNP1S7g8VLe0r1abfPFTG2L+lr6DZ63puGZZ4e5lWh1jip2118m6RbRvL7xPBlUcZVIKqutOlTi/aa9XlI8zuf5TYR8adtbyilulRULRzx1acItS+ZM8XB9TRrTz99fXtrSu5T8vQVeeKsaO3dUmuX376s635b4e/6tY/FVf2cjX6e0hw/q/VllrbwaJxHT1OpOzuqHldRpqTlTe5QqbXiW1T9pSXqn/obW9vbXTrWve3Tl4NFL2Y4c6k5PEacPe/8AfQ4jiK706nrel6pptzQrTXgVbh2zzipTqbG5YX30XzOx1XSrTWKNO1uZXEaUK3jwVvU2Nz2uPPk+meXL1JykllcnFyZ5Y5Y4+Y5ylrfGur762lWVvQtNzjCc409rxy/pa7y33wsGEuIeKdJrUo61Z050Kj5SpwhCUorq6VSk9mV2aOpg9L0u3t7SVza0KdtSjShCtWpRntj3Tecvq+XqaDiu90q60eUKF5a1q8byhOEKVWE5pNSjJ4j+kZlLdaTnjcMLn193TUqtOtRpXFKW6nUo+NSfROLhvi2v2nHWPGF06V47ujTuLtzoUdNtbWlKEq05blJzccvC5dOZvuHc/IOk5ef+CqJfBOaRzXBNvRnealdSinVt6NGlRbw9niyk5Sjn1wsE444yZb+zk5M887xzG629dS+/lIUJXHkqMKcVvdCnRtpSjFd6eXP9OT0WfF9hKwvLjUIKldWu2Lt6UmncuecOlu5rp7fb5zp84aa9Oafv9xwXkrWpxpUtpwi6CvK1y6bXsOUaXjJNds88Dj05+Z4HLjycNlwy3vt3e5alx/fRVxZ6fSt7aS3UoTp0VOUHzT+vvc/oSPvpHEl3WvfkvWKEaF3KThSmoeE3VXPw6sM45+jR0+e/X3nFcXxVHVdCuqfs1ZRoOTXLMqNylFv34eAxsz+mxfLjycEnJ1W/Lf8AEf3C1f8AJUv3sTycI8tEo/nV4/8AzGeviT7h6x+Sp/pqwPJwl9xKP5zefvGR/t1y/wDJn4R61qC4mWj4t1ZqTTapvxXi3VX7PPf3GPEVxxDTjdUrG0hU06enS85XcIOUN27xMSck+Sx96a+X9es/95L/ACh02qP+a9Z9+n3X6IF3WOU048evk4+Td8WuJ0K74oo2teGk2VK4t/MZqzqU6b21dkeWZTXpg7ewnfVLK0nf0407yVPNxTgkoxnufJYbXTHqaPgvHyXef3hL9xSOkI58t5a05fQ8dnHM938KQEOB9KKQEyCorIQGVIAEAgBAUAgMpkuoIuoBTdyfNmPIsnzZDvvJHIcgQytABAVAZGSAqQIMgxgARgrRk8OrahPTNPub+Furh0JUlKnKo6fsTltctyT6HtPnXo0bihXt68d9GvTnSqw7wksM01vu2UvT9Pl49H1KGr2FG+jBUpTnVp1Kak5+HOnJxabaz7z356e44OnR4l4Sr3DtreV/plWalLbCc08YSlJU/ajPHLKWD1fV1BrEdGuXV9Iuq3HPbEae4u4bu44cOaYzWfmMuPads7DTa81FV/MV6G7790HScpJvsn+06XSXUem6PKpnxHY2zm338NHHw07iDiq9oXmsUpWmm0eVOg4um3S3bvCoU292JffSaO6jtht2rEYpJRjySilhJIc+0mJ4Zcs8s9alcPwR9vcQfiUv31Q7d/Y1OX/Kq/4GfntKepcJatfTnZVLizucxUoqe2pS3ucHGpBNKS5ppr1Ou0bV3rFtfXLs6lrClOpRpxqOUpVF4O7csxXq8dDZzd23BlJj7d8uc4E6638LP/1DqNZpyraRrVGCbnOxrOKXVuH1zC+g5rgejcUnrXi0a1Ld5RLxqc6eWvEzjcjs3/vJOd1ntfp8beHpv8uC4W0jQ9UtLyV5QlVuaFyo5VWpBKlOClDlFpdcm/8AqT4X/A5/+Ir/APyNPc6ZrHDuoVdS0ejK4sayfi28YylKMHLd4c4R9rCfSS6ep9vq4p7dvyNdeP02qq9qfbHh7y71W7xrh4/b48enkx7xsJ8LcJwUfEtowz7UFUu6kXLD6xUp5f0Hm4u1a9saVlYWMpU617GUqlSDcanhqSpRpwkuay+rPDa2Gs8Q6rQ1fVrfy9lbOm6FCpHbvjTe+nThCXtbc85N9TYcWaTd6hStLuzjKdxZKcZ04L2505NTUod3F+gf6tZVdu+O3jx0xtODdHpU4u/8W8upLNaTqThSU+rUIxece9t9DycR6HoWn6VO5s7ONG4V1bU1NTqN7Z7tyxJtc8GdHjRU6cIXuk3ju4JRqeE3CNSSWN22pDKz69Twa1V4i1ix89Xs52mn21anG1s1CpK4rTq5Uq0o43YWPVLryHHr6pcqjk9r2rMce/4dPw79wdJ/Mqn7ahoOB/stb+Fp+2Zv+H4zp6FpcakZwnGzqKUZxamnmfJxfPJouCqVelLWfFo1qe7yqj4tOUMtOeUtyJt7ZOeS9fF+HY9jjIf17rfj1/8ALROzOOhTr/VvWq+DW8JyrvxHTn4eHbRSe/G0jjvlzepl3h+XYHGcafbugfi/+5gdlk5DjClXq3mheFRrVFGGJOnTnNRfmIyxJxQcP7letlvF2/hu+JH/ADHrH5Kl+9geThL7iUfzm8/eM9fESlPRdWhCMpSlSp7Ywi5SlirF8lHmeXhSFSno1GNSnUpy8xdvbUi4Sw6mU8S5m3/Tv5bGX9TPw1cv68r8eX+UR0uqfcvWP7vu/wDAc46dZ8beKqNbwd8vrvhz8P7VSzuxg6m4oq5trq3k8RuaFWg31S8SLWfm9Rzs3iPT424ck+bXPcFv+a7z+8JfuKR0pwem6hqHDUruyvNOrVac6iqJwcoreo7N1Oai4tSSX0HYabezv7K3u528rd1t7VKbk5RjGbim3JJ88Z6epPNO/V9nJ6HknROP7x7CFMcs4H0ZFyQEyZUgxkAFIwMkMdAABSDJMsArSpgIGVG7l1ZBLqyHfeS0AEA6CMMAqQIAZUCAArQyAgKkAAZUhzT5Zz3WcjLzn1IDHUM8888vrn/7JkECqXn6EbfLmwyAqRct9W38SMENtUnwFy+pCG2db8q231bICEq0ZfXPPv6jL65eQQ1pmMg3nm+f8Q22sNt/EEBcmgmX0y2uzbwGDeFagMv0bXwykQArXyc0Rtvn69/UZZA/grl4xnl85ADflWvgy+7/AP0gI2FpkUgIZcgAQFaGAyGOgEYBWgmRlgFaCFIZWlQC6gFSN3LqyFl1Zid95LQGGQDoIwDKAQAqQICAqRWQBmVIjAAKkCBkMVIMkBWgAhlaVkAYKkCAgGHcAhlSABAVIDsGQypAEAK0EAAhADK0MgIwVpX1ICGVIAEBQGGQxkACAqQIwwCtABDK0AEAquoCBl6buXVkYl1ZDvPJaCAGIRgPAKkCAAqQIAZUgyAcgVIEDxyIYg5DkQytABAUpAQFaVkDIBACGVIAEBUgQvIhlSBAAVIEAAhADK0EBOQK0rICGVIAEBQPnHIhjAAgKkCMrICpAAhlaACATkCAFaVdQF1ALbuXVmJZdWQ+g8kAEAwIwyAqRSAGVIE5AAqQI2GQxBkEMoAIBUgIC9KQEBSsgIYyABAVIDKGfcQFSBADKkCAgFSAGVoICZ9wKXJAQytABAUpMoEMYAgBUgMkz7iAqRWwQGVIAEAgyMkBWggBlKuoIuoBWm8l1ZiWXVkZ33kggAKQAMxgQAFwJll5mJipGH6kMqAAAoAAUEKYgo5kKQygBkBQTLKQyoEyUgKgQACEAMqBAAKZYBDLACAoGQyGIQpAUEywAVAhSGVABgCjZMlZAVAgBlBBzAKVAiAKjeS6sxLLqyH0HkggAGBAAXAgIYgBAVAAhjAAAuBARgQAhlABAUpGGQyoEABUCAAQgBlQICP0BQwCGUAEAgBAUAMhlKQj6gFQAIZUACMCMgAKgQMGUAnMAoIAZSrqCLqALeS6sxM3/AM77ybAhmAVpgRmYZlMCGZDGRhgGZAVIxIZv1ICtMGDNkMrTBgzAHT5gyAK0wDMgZemAZmRgdMCMzICpGJDMgKkYkM36kMqRiyGZAOmAMn1BlaYkMyArTAGQMdMCMzAL0wBmQx0wBmY9wVIxDMgY6YAyDBcjAhmyAdMfnIZgFaYEMgZWkQMl1Bm2//Z");
    #     background-size: cover;
    #     }
    #     </style>
    #     ''' 
    #     st.markdown(page_bg_img, unsafe_allow_html=True)
    # set_background()
    default_prompt = "" 
    default_question = "" 
    default_answer = ""

    if 'question' not in st.session_state:
        st.session_state['question'] = default_question
    if 'response' not in st.session_state:
        st.session_state['response'] = default_answer
    if 'context' not in st.session_state:
        st.session_state['context'] = ""
    if 'custom_prompt' not in st.session_state:
        st.session_state['custom_prompt'] = ""
    if 'custom_temperature' not in st.session_state:
        st.session_state['custom_temperature'] = float(os.getenv("OPENAI_TEMPERATURE", 0.7))

    if 'sources' not in st.session_state:
        st.session_state['sources'] = ""
    if 'followup_questions' not in st.session_state:
        st.session_state['followup_questions'] = []
    if 'input_message_key' not in st.session_state:
        st.session_state ['input_message_key'] = 1
    if 'askedquestion' not in st.session_state:
        st.session_state.askedquestion = default_question

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

    llm_helper = LLMHelper(custom_prompt=st.session_state.custom_prompt, temperature=st.session_state.custom_temperature)

    # Get available languages for translation
    available_languages = get_languages()

    # Custom prompt variables
    custom_prompt_placeholder = """{summaries}  
    Please reply to the question using only the text above.  
    Question: {question}  
    Answer:"""
    custom_prompt_help = """You can configure a custom prompt by adding the variables {summaries} and {question} to the prompt.  
    {summaries} will be replaced with the content of the documents retrieved from the VectorStore.  
    {question} will be replaced with the user's question.
        """
    st.text('OpenAI Queries')
    col1, col2 = st.columns([2,2])
    with col1:
        st.image(os.path.join('images','microsoft.png'))

    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        st.button("Check deployment", on_click=check_deployment)
    with col2:
        st.image(os.path.join('images','Settings.png'))
        with st.expander("Settings"):
            # model = st.selectbox(
            #     "OpenAI GPT-3 Model",
            #     [os.environ['OPENAI_ENGINE']]
            # )
            # st.tokens_response = st.slider("Tokens response length", 100, 500, 400)
            st.slider("Temperature", min_value=0.0, max_value=1.0, step=0.1, key='custom_temperature')
            st.text_area("Custom Prompt", key='custom_prompt', on_change=check_variables_in_prompt, placeholder= custom_prompt_placeholder,help=custom_prompt_help, height=150)
            st.selectbox("Language", [None] + list(available_languages.keys()), key='translation_language')


    question = st.text_input("Azure OpenAI Semantic Answer",placeholder="Type your question here", value=st.session_state['askedquestion'], key="input"+str(st.session_state ['input_message_key']), on_change=questionAsked)

    # Answer the question if any
    if st.session_state.askedquestion != '':
        st.session_state['question'] = st.session_state.askedquestion
        st.session_state.askedquestion = ""
        st.session_state['question'], \
        st.session_state['response'], \
        st.session_state['context'], \
        st.session_state['sources'] = llm_helper.get_semantic_answer_lang_chain(st.session_state['question'], [])
        st.session_state['response'], followup_questions_list = llm_helper.extract_followupquestions(st.session_state['response'])
        st.session_state['followup_questions'] = followup_questions_list

    sourceList = []

    # Display the sources and context - even if the page is reloaded
    if st.session_state['sources'] or st.session_state['context']:
        st.session_state['response'], sourceList, matchedSourcesList, linkList, filenameList = llm_helper.get_links_filenames(st.session_state['response'], st.session_state['sources'])
        st.write("<br>", unsafe_allow_html=True)
        st.markdown("Answer: " + st.session_state['response'])
 
    # Display proposed follow-up questions which can be clicked on to ask that question automatically
    if len(st.session_state['followup_questions']) > 0:
        st.write("<br>", unsafe_allow_html=True)
        st.markdown('**Proposed follow-up questions:**')
    with st.container():
        for questionId, followup_question in enumerate(st.session_state['followup_questions']):
            if followup_question:
                str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)
                st.button(str_followup_question, key=1000+questionId, on_click=ask_followup_question, args=(followup_question, ))

    if st.session_state['sources'] or st.session_state['context']:
        # Buttons to display the context used to answer
        st.write("<br>", unsafe_allow_html=True)
        st.markdown('**Document sources:**')
        for id in range(len(sourceList)):
            st.markdown(f"[{id+1}] {sourceList[id]}")

        # Details on the question and answer context
        st.write("<br><br>", unsafe_allow_html=True)
        with st.expander("Question and Answer Context"):
            if not st.session_state['context'] is None and st.session_state['context'] != []:
                for content_source in st.session_state['context'].keys():
                    st.markdown(f"#### {content_source}")
                    for context_text in st.session_state['context'][content_source]:
                        st.markdown(f"{context_text}")

            st.markdown(f"SOURCES: {st.session_state['sources']}") 

    for questionId, followup_question in enumerate(st.session_state['followup_questions']):
        if followup_question:
            str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)

    if st.session_state['translation_language'] and st.session_state['translation_language'] != '':
        st.write(f"Translation to other languages, 翻译成其他语言, النص باللغة العربية")
        st.write(f"{llm_helper.translator.translate(st.session_state['response'], available_languages[st.session_state['translation_language']])}")		
		
except Exception:
    st.error(traceback.format_exc())
