import streamlit as st
import time
import random

st.set_page_config(layout="wide")
st.components.v1.iframe("http://localhost:56871", height=800, scrolling=True)

# === BOTTOM: Chatbot ===
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask something about a patent..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Existing responses
        assistant_response = random.choice([
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ])

        # Responses with model
        # +++++++++++++++++++++++++++++++++++++++++++++
        # """
        # from triz_engine import (
        #     summarize_patent, format_triz_output, classify_triz_with_llm,
        #     hybrid_retrieve, rerank_chunks, generate_structured_answer,
        #     load_extracted_text, build_retrieval_index, memory
        # )
        # from langchain_text_splitters import RecursiveCharacterTextSplitter
        # # Load patent only once
        # if "loaded" not in st.session_state:
        #     sections = load_extracted_text("extracted_text.json")
        #     full_text = "\n\n".join(sections.values())
        #     st.session_state.summary = summarize_patent(full_text)
        #     st.session_state.chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_text(full_text)
        #     st.session_state.index, st.session_state.embeddings = build_retrieval_index(st.session_state.chunks)
        #     triz_results = classify_triz_with_llm(sections)
        #     st.session_state.triz_output = format_triz_output(triz_results)
        #     st.session_state.loaded = True

        # # Actual assistant response
        # query = prompt
        # context = "\n\n".join(rerank_chunks(query, hybrid_retrieve(query, st.session_state.chunks, st.session_state.index, st.session_state.embeddings)))
        # history = memory.load_memory_variables({}).get("history", "")
        # assistant_response = generate_structured_answer(
        #     st.session_state.summary,
        #     query,
        #     st.session_state.triz_output,
        #     context,
        #     history
        # )
        # memory.save_context({"input": query}, {"output": assistant_response})
        # """
        # +++++++++++++++++++++++++++++++++++++++++++++

        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
