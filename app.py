import streamlit as st
import json
import os
from rag_chain import ask

CHAT_FILE="chat_history.json"
DATA_DIR="data"

st.set_page_config(layout="wide")
st.title("📄 Offline Research Paper Assistant")

def load_chat():
    try:
        return json.load(open(CHAT_FILE))
    except:
        return []

def save_chat(m):
    json.dump(m, open(CHAT_FILE,"w"), indent=2)

if "messages" not in st.session_state:
    st.session_state.messages = load_chat()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ask your papers")

if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    ans = ask(prompt)

    with st.chat_message("assistant"):
        st.markdown(ans)

    st.session_state.messages.append({"role":"assistant","content":ans})
    save_chat(st.session_state.messages)

with st.sidebar:
    st.header("📥 Upload PDFs (max 5)")
    files = st.file_uploader("",type=["pdf"],accept_multiple_files=True)

    if files:
        if len(files)>5:
            st.error("Max 5 PDFs allowed")
        else:
            for f in files:
                with open(os.path.join(DATA_DIR,f.name),"wb") as out:
                    out.write(f.read())
            st.success("Uploaded. Now run ingest.py")

    st.info("After uploading PDFs → run python ingest.py")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages=[]
        save_chat([])
        st.rerun()
