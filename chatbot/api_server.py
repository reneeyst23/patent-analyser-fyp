# from fastapi import FastAPI, UploadFile, File, HTTPException, Body
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from chatbot import (
#     load_extracted_text,
#     embed_chunks,
#     create_qdrant_index,
#     retrieve_chunks,
#     rerank_chunks,
#     generate_answer,
#     memory,
# )
# from typing import List
# import tempfile

# import os

# app = FastAPI(title="Patent Chatbot API")

# # Allow CORS so React can access this API
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Replace with your frontend URL in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # # ========== /upload ==========
# # @app.post("/upload")
# # async def upload_patent(file: UploadFile = File(...)):
# #     contents = await file.read()
# #     temp_path = "temp_uploaded_patent.json"

# #     with open(temp_path, "wb") as f:
# #         f.write(contents)

# #     try:
# #         full_text = load_extracted_text(temp_path)
# #         chunks, vectors = embed_chunks(full_text)
# #         create_qdrant_index(chunks, vectors)

# #         return {
# #             "status": "indexed",
# #             "chunks_ready": len(chunks)
# #         }
# #     except Exception as e:
# #         return {
# #             "status": "error",
# #             "detail": str(e)
# #         }

# # # ========== /chat ==========
# # class ChatRequest(BaseModel):
# #     message: str
# # 
# @app.post("/chat")
# async def chat_endpoint(req: ChatRequest):
#     try:
#         query = req.message
#         retrieved = retrieve_chunks(query)
#         reranked = rerank_chunks(query, retrieved)
#         context = "\n\n".join(reranked)
#         answer = generate_answer(query, context)
#         memory.save_context({"query": query}, {"output": answer})
#         return {"reply": answer}
#     except Exception as e:
#         return {"reply": f"❌ Error: {e}"}

# # Models
# # class ChatRequest(BaseModel):
# #     message: str

# # class ChatResponse(BaseModel):
# #     reply: str

# # class SuggestedQuestionsResponse(BaseModel):
# #     questions: List[str]

# # class StatusResponse(BaseModel):
# #     status: str
# #     message: str

# # Global variables
# document_loaded = False
# document_summary = ""

# def extract_text_from_pdf(pdf_file: UploadFile) -> str:
#     with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#         temp_file.write(pdf_file.file.read())
#         temp_path = temp_file.name

#     text = ""
#     try:
#         with open(temp_path, 'rb') as file:
#             pdf_reader = PyPDF2.PdfReader(file)
#             for page in pdf_reader.pages:
#                 text += page.extract_text() + "\n\n"
#     finally:
#         os.unlink(temp_path)
    
#     return text

# @app.post("/upload-pdf", response_model=StatusResponse)
# async def upload_pdf(file: UploadFile = File(...)):
#     global document_loaded, document_summary
    
#     if not file.filename.endswith('.pdf'):
#         raise HTTPException(status_code=400, detail="File must be a PDF")
    
#     try:
#         # Extract text from PDF
#         full_text = extract_text_from_pdf(file)
        
#         # Process the text
#         chunks, vectors = embed_chunks(full_text)
#         create_qdrant_index(chunks, vectors)
        
#         # Extract summary for suggested questions
#         document_summary = full_text[:2000]  # Use first 2000 chars as summary
#         document_loaded = True
        
#         return StatusResponse(
#             status="success", 
#             message="PDF processed successfully"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

# @app.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest = Body(...)):
#     if not document_loaded:
#         raise HTTPException(status_code=400, detail="No document loaded. Please upload a PDF first.")
    
#     try:
#         query = request.message
#         retrieved = retrieve_chunks(query)
#         reranked = rerank_chunks(query, retrieved)
#         context = "\n\n".join(reranked)
#         answer = generate_answer(query, context)
        
#         memory.save_context({"query": query}, {"output": answer})
        
#         return ChatResponse(reply=answer)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

# # @app.get("/suggested-questions", response_model=SuggestedQuestionsResponse)
# # async def get_suggested_questions():
# #     if not document_loaded:
# #         raise HTTPException(status_code=400, detail="No document loaded. Please upload a PDF first.")
    
# #     try:
# #         questions = generate_suggested_questions(document_summary)
# #         return SuggestedQuestionsResponse(questions=questions)
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

# @app.get("/status", response_model=StatusResponse)
# async def get_status():
#     return StatusResponse(
#         status="online" if document_loaded else "ready",
#         message="Document loaded and ready" if document_loaded else "Server is running, but no document is loaded"
#     )

# # @app.on_event("shutdown")
# # def shutdown_event():
# #     clean_up_index()

# # if __name__ == "__main__":
# #     uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from chatbot import (
    generate_answer,
    retrieve_chunks,
    create_qdrant_index, 
    embed_chunks, 
    load_extracted_text, 
    rerank_chunks
)
import shutil

app = FastAPI()

# Allow requests from frontend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, use ["http://192.168.1.14:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.post("/chat")
# async def chat(request: Request):
#     data = await request.json()
#     user_message = data.get("message", "")
#     print(f"🔍 Received message from frontend: {user_message}")  # Debug log
#     response = generate_answer(user_message)
#     return {"reply": response}

# State variable to check if document is indexed
indexed = False
chunks_ready = []

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload and process a JSON patent file.
    """
    try:
        # Save uploaded file temporarily
        temp_path = "temp_uploaded_patent.json"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load, chunk, embed, and index
        full_text = load_extracted_text(temp_path)
        chunks, vectors = embed_chunks(full_text)
        create_qdrant_index(chunks, vectors)

        # Mark as indexed and store chunks
        global indexed, chunks_ready
        indexed = True
        chunks_ready = chunks

        return {"status": "success", "message": f"{file.filename} uploaded and indexed."}

    except Exception as e:
        return {"status": "error", "message": f"Failed to upload file: {e}"}

@app.post("/chat")
async def chat(request: Request):
    global indexed, chunks_ready
    data = await request.json()
    user_message = data.get("message", "")
    print(f"🔍 Received message: {user_message}")

    try:
        if indexed:
            # Use Qdrant context if patent is indexed
            retrieved = retrieve_chunks(user_message)
            reranked = rerank_chunks(user_message, retrieved)
            context = "\n\n".join(reranked)
            response = generate_answer(user_message, context)
        else:
            # General chatbot fallback (no document context)
            response = generate_answer(user_message, context="")  # or skip context param

    except Exception as e:
        response = f"❌ Error: {e}"

    return {"reply": response}

