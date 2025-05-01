import streamlit as st
import streamlit.components.v1 as components
import os
from chatbot.chatbot import (
    load_extracted_text,
    embed_chunks,
    create_qdrant_index,
    retrieve_chunks,
    rerank_chunks,
    generate_answer,
    memory
)

# ===============
# Frontend Design
# ===============

st.set_page_config(layout="wide")

# Load the single self-contained HTML
html_path = os.path.join("frontend", "dist", "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

components.html(html_content, height=800, scrolling=True)

# ==========
# PDF Upload
# ==========
uploaded_file = st.file_uploader("Upload a Patent JSON", type=["json"])

if uploaded_file:

    # Perform pdf to json conversion

    
    # Save uploaded file temporarily
    temp_path = "temp_uploaded_patent.json"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("📄 Patent file uploaded and indexed!")

    # Preprocess and embed chunks
    full_text = load_extracted_text(temp_path)
    chunks, vectors = embed_chunks(full_text)
    create_qdrant_index(chunks, vectors)

    st.session_state['indexed'] = True
    st.session_state['chunks_ready'] = chunks

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Ask me anything about the uploaded patent 🤖"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if st.session_state.get('indexed'):
    if prompt := st.chat_input("Ask a question about the patent..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🔍 Thinking...")

            try:
                retrieved = retrieve_chunks(prompt)
                reranked = rerank_chunks(prompt, retrieved)
                context = "\n\n".join(reranked)
                response = generate_answer(prompt, context)
                memory.save_context({"query": prompt}, {"output": response})
            except Exception as e:
                response = f"❌ Error: {e}"

            message_placeholder.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("⬆️ Please upload a patent JSON to begin.")