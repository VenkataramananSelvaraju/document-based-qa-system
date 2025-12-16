import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate

# Load Env Variables
load_dotenv()

# Verify API Key
if not os.getenv("GOOGLE_API_KEY"):
    print("CRITICAL ERROR: GOOGLE_API_KEY not found in .env file")

app = FastAPI(title="Document-Based QnA Backend")

# --- Configuration ---
VECTOR_DB_DIR = "chroma_db_free"

# 1. Use Local Embeddings (Runs on CPU, No API Cost)
# "all-MiniLM-L6-v2" is a small, fast model perfect for local use.
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = None

# Initialize Vector Store if exists
if os.path.exists(VECTOR_DB_DIR):
    vectorstore = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)

# --- Data Models ---
class QueryRequest(BaseModel):
    question: str

class SourceData(BaseModel):
    content: str
    source: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceData]

# --- Load Documents / Texts ---
def load_and_split_document(file_path: str, filename: str):
    if filename.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif filename.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        loader = TextLoader(file_path)
    return loader.load()

# --- API Endpoints ---
@app.post("/upload/")
async def upload_documents(files: List[UploadFile] = File(...)):
    global vectorstore
    
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    all_docs = []

    for file in files:
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        docs = load_and_split_document(file_path, file.filename)
        all_docs.extend(docs)

    # Split Text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)

    # Create/Update Vector Store (Local ChromaDB)
    if vectorstore is None:
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=embeddings, 
            persist_directory=VECTOR_DB_DIR
        )
    else:
        vectorstore.add_documents(splits)
    
    return {"message": f"Processed {len(files)} documents successfully."}

@app.post("/query/", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    global vectorstore
    if not vectorstore:
        raise HTTPException(status_code=400, detail="Knowledge base is empty.")

    # 1. Get Top Matches (Fetch 3-4 to ensure we get a good pool)
    docs_and_scores = vectorstore.similarity_search_with_relevance_scores(request.question, k=3)
    
    if not docs_and_scores:
        return QueryResponse(answer="I couldn't find any relevant info.", sources=[])

    # 2. Filter: Get strictly the SINGLE best source
    sorted_docs = sorted(docs_and_scores, key=lambda x: x[1], reverse=True)
    top_doc, top_score = sorted_docs[0]

    # 3. Generate Answer
    context_text = "\n\n".join([d[0].page_content for d in sorted_docs])
    
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.3)
    prompt = f"""You are a helpful assistant. Answer the question based ONLY on the following context.
    If the answer is not in the context, say "I cannot find the answer in the documents."
    
    Context:
    {context_text}
    
    Question: {request.question}
    Answer:"""
    response = llm.invoke(prompt)

    # 4. Format ONLY the Top Source for the return
    top_source_data = SourceData(
        content=top_doc.page_content[:300] + "...", 
        source=top_doc.metadata.get("source", "Unknown"),
        score=float(top_score)
    )

    return QueryResponse(answer=response.content, sources=[top_source_data])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)