# Document-Based Question Answering System

A high-performance, web-based QA application designed to process technical documentation (PDF, TXT, DOCX) and provide evidence-based answers using Semantic Search.

## 🚀 Features
- **Multi-Format Support:** Upload and parse PDF, Word, and Text files.
- **Semantic Retrieval:** Uses the `all-MiniLM-L6-v2` transformer model for high-accuracy matching.
- **Transparency:** Displays confidence scores and provides the exact source paragraph for verification.
- **Hybrid Input:** Support for both file uploads and direct text copy-pasting.

## 🛠️ Installation & Setup

1. **Clone or Extract the Project Folder:**
    cd qa_system

2. ***Create a Virtual Environment (Optional but Recommended):***
    python -m venv venv
    source venv/bin/activate

3. ***Install Dependencies:***
    pip install -r requirements.txt

4. ***Run the Application:***
    streamlit run app.py

## 📖 How to Use
***Load Knowledge:*** Use the sidebar to upload your technical manuals or paste text directly.

***Analyze:*** Once the "Processed successfully" message appears, enter your question in the main text field.

***Review:*** Examine the extracted answer, check the confidence score, and expand the "Source Context" to see the surrounding sentences.

## 🏗️ System Architecture
The system follows a standard Retrieval pipeline:

***Parsing:*** Documents are converted into clean text strings.

***Chunking:*** Text is split into meaningful sentence-level segments.

***Embedding:*** Segments are converted into high-dimensional vectors.

***Scoring:*** The user's query is compared against document vectors using Cosine Similarity.
