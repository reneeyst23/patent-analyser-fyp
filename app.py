import openai as OpenAI
import streamlit as st
import streamlit.components.v1 as components
import os
import time
import random
import development.classification.rag_system as model

# st.set_page_config(layout="wide")

# # Building path for frontend
# build_path = os.path.join(os.path.dirname(__file__), "frontend")

# components.html(
#     open(os.path.join(build_path, "index.html")).read(),
#     height = 800,
#     scrolling = True
# )

st.set_page_config(layout="wide")
components.iframe("http://localhost:8000", height=800, scrolling=True)

# === BOTTOM: Chatbot ===
# Upload patent pdf
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

# Initialisation
# sections = model.load_extracted_text("extracted_text.json")
# full_text = "\n\n".join(sections.values())
# summary = model.modelsummarize_patent(full_text)
# chunks = model.RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_text(full_text)
# index, embeddings = model.build_retrieval_index(chunks)
# triz_results = model.classify_triz_with_llm(sections)
# triz_output = model.format_triz_output(triz_results)
# memory = model.memory

client= OpenAI(api_key="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")

# -------
# ChatBot
# -------
# if prompt: 
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------
# File Upload
# -----------
"""
import fitz (pip install pymupdf)
def extract()
def preprocess()
then output text result
"""
if uploaded_file:
    # Display upload as user message
    with st.chat_message("user"):
        st.markdown(f"Uploaded **{uploaded_file.name}**")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = "Processing PDF..."
        message_placeholder.markdown(full_response + " ▌")

        # Text extraction & preprocessing
        raw_text = extract_text_from_pdf(uploaded_file)
        processed_text = preprocess_text(raw_text) # json / html output

        time.sleep(1)
        full_response = f"**Preprocessed Output:**\n\n{processed_text[:500]}..."  # show preview
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "user", "content": f"Uploaded {uploaded_file.name}"})
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Accept user input
# if prompt := st.chat_input("Ask something about a patent..."):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         message_placeholder.markdown("🔍 Thinking...")

#         # Hybrid retrieval + rerank
#         context = "\n\n".join(model.rerank_chunks(prompt, model.hybrid_retrieve(prompt, chunks, index, embeddings)))
#         history = memory.load_memory_variables({}).get("history", "")

#         # Generate model response
#         response = model.generate_structured_answer(summary, prompt, triz_output, context, history)

#         message_placeholder.markdown(response)

#         memory.save_context({"input": prompt}, {"output": response})
#     st.session_state.messages.append({"role": "assistant", "content": response})

response_obj = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a TRIZ patent analysis expert."},
        {"role": "user", "content": f"{prompt}\n\nContext:\n{context}\n\nPrior Summary:\n{summary}\n\nTRIZ:\n{triz_output}\n\nConversation:\n{history}"}
    ],
    temperature=0.7
)
response = response_obj.choices[0].message.content.strip()
