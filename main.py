connect streamlit

file=streamlit.get(file)
json=file.extract_json()

model= streamlit.get(model_choice)

model.classify_patent()
model.summarize()

model.initiate.chatbot() -> streamlit


