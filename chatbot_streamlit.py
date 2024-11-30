import streamlit as st
from chat import get_response, bot_name

# Configuration de la page
st.set_page_config(
    page_title="Chatbot",
    page_icon="🤖",
    layout="centered",
)

# Initialisation des messages dans session_state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"sender": bot_name, "text": "Bonjour! Comment puis-je vous aider ?"}]
if "input_box" not in st.session_state:
    st.session_state["input_box"] = ""

# Fonction pour ajouter un message
def send_message():
    user_input = st.session_state.input_box
    if user_input:  # Si l'utilisateur a saisi quelque chose
        # Ajouter le message utilisateur
        st.session_state["messages"].append({"sender": "Vous", "text": user_input})

        # Obtenir la réponse du chatbot
        response = get_response(user_input)
        st.session_state["messages"].append({"sender": bot_name, "text": response})

        # Effacer le champ de saisie
        st.session_state.input_box = ""

# Titre de l'application
st.title("🤖 Bienvenue dans le Chatbot!")

# Afficher les messages existants
for message in st.session_state["messages"]:
    if message["sender"] == "Vous":
        st.markdown(f"**Vous**: {message['text']}")
    else:
        st.markdown(f"**{message['sender']}**: {message['text']}")

# Champ de saisie avec callback
st.text_input(
    "Écrivez votre message ici :",
    key="input_box",
    on_change=send_message,  # Appelle `send_message` lorsque l'utilisateur appuie sur Entrée
)

# Optionnel : bouton pour forcer une actualisation (au cas où)
if st.button("Actualiser"):
    st.experimental_rerun()
