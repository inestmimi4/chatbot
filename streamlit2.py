import streamlit as st
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import random
import json
import shelve

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Ines"

def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])

    return "Je ne comprends pas..."

def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("discussions", [])

def save_chat_history(discussions):
    with shelve.open("chat_history") as db:
        db["discussions"] = discussions

if "discussions" not in st.session_state:
    st.session_state.discussions = load_chat_history()

if "current_discussion" not in st.session_state:
    st.session_state.current_discussion = []

def new_discussion():
    if st.session_state.current_discussion:
        st.session_state.discussions.append(st.session_state.current_discussion)
        save_chat_history(st.session_state.discussions)
    st.session_state.current_discussion = []

with st.sidebar:


    if st.button("➕ Nouvelle discussion"):
        new_discussion()
    st.subheader("🕘 Historique des discussions")

    history_container = st.empty()



    if st.button(" Réinitialiser l'historique"):
        st.session_state.discussions = []
        st.session_state.current_discussion = []
        save_chat_history([])

        model = st.selectbox('What model would you like to use?',('gpt-3.5-turbo', 'gpt-4'))


with history_container.container():
    if st.session_state.discussions:
        for i, discussion in enumerate(st.session_state.discussions):
            with st.expander(f"Discussion {i + 1}"):
                for message in discussion:
                    role = "👤" if message["role"] == "user" else "🤖"
                    st.write(f"{role} {message['content']}")

st.title("🤖 Hello Ines How are You?")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

for message in st.session_state.current_discussion:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Comment puis-je vous aider ?"):

    st.session_state.current_discussion.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    response = get_response(prompt)
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        st.markdown(response)

    st.session_state.current_discussion.append({"role": "assistant", "content": response})

save_chat_history(st.session_state.discussions + [st.session_state.current_discussion])