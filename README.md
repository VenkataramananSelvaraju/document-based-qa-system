# 📄 Document-Based Question Answering System

A robust, Retrieval-Augmented Generation (RAG) application that allows users to chat with their documents (PDF, DOCX, TXT). 

Built with **FastAPI** (Backend) and **Streamlit** (Frontend), this system leverages **Google Gemini Flash** for reasoning and **HuggingFace Local Embeddings** for vector search and embeddings.

---

## 🚀 Features

* **Multi-Document Support:** Upload and index multiple PDF, DOCX, or TXT files simultaneously.
* **Tech Stack:**
    * **LLM:** Google Gemini Flash (via Google AI Studio).
    * **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (Running locally on CPU).
* **Interactive Chat UI:** Streamlit-based chat interface supporting follow-up questions.
* **Real-Time Confidence Scoring:** displays the "Confidence Score" (vector similarity) for the top source.
* **Source Citation:** Accurate referencing of the exact document source and excerpt used to generate the answer.
* **Decoupled Architecture:** Separate Frontend (Streamlit) and Backend (FastAPI) for scalability.

---

## 🛠️ Tech Stack

* **Backend:** FastAPI, Uvicorn
* **Frontend:** Streamlit
* **Orchestration:** LangChain
* **Vector Database:** ChromaDB (Persistent Local Storage)
* **AI Models:** * *Generation:* Google Gemini Flash
    * *Embedding:* Sentence-Transformers (HuggingFace)

---

## 📂 Project Structure

```text
doc_qa_app/
├── backend.py           # FastAPI server (Logic & API endpoints)
├── frontend.py          # Streamlit UI (Chat interface)
├── requirements.txt     # Python dependencies
├── .env                 # API Keys (Not committed to repo)
├── chroma_db_free/      # Local Vector Store (Auto-generated)
└── uploads/             # Temp storage for uploaded files

## ⚙️ Installation & Setup

**Prerequisites**
* Python 3.9 or higher
* A Google Account (to get the free API key)

1. **Clone or Extract the Project Folder:**
    ```bash
    cd document-based-qa-system
    ```

2. **Create a Virtual Environment (Optional but Recommended):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. Set Up Environment Variables
* Create a file named .env in the root directory and add your Google Gemini API Key.
* Get a key from Google AI Studio.
* Add it to .env:

5. **Run the Application:**
**Terminal 1: Start the Backend API**
    ```bash
    python backend.py
    ```
**Terminal 2: Start the Frontend UI**
    ```bash
    streamlit run frontend.py
    ```

## 📖 Usage Guide

1. Build Knowledge Base:
    * Open the sidebar on the left.
    * Click "Browse files" to select PDF or DOCX documents.
    * Click "Update Knowledge Base".
    * Wait for the success message (this builds the vector index locally).

2. Ask Questions:
    * Type your question in the chat input box (e.g., "What are the safety protocols?").
    * The AI will answer based only on your documents.

3. View Sources:
    * Expand the "🔍 Top Source" box below the answer to see the exact text chunk and the confidence score (Green/Orange/Red based on relevance).