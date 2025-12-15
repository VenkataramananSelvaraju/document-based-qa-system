import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from sentence_transformers import SentenceTransformer, util

# --- Page Config ---
st.set_page_config(page_title="Document-Based Question Answering System", layout="wide")

# --- Initialize Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] 

@st.cache_resource
def load_model():
    # Efficient model for semantic similarity
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# --- Parsing Logic ---
def extract_text(files):
    combined_text = []
    for file in files:
        if file.name.endswith('.pdf'):
            pdf = PdfReader(file)
            for page in pdf.pages:
                text = page.extract_text()
                if text: combined_text.append(text)
        elif file.name.endswith('.docx'):
            doc = Document(file)
            for para in doc.paragraphs:
                if para.text.strip(): combined_text.append(para.text)
        elif file.name.endswith('.txt'):
            combined_text.append(file.read().decode("utf-8"))
    return " ".join(combined_text)

# --- QA Logic ---
def get_answer(query, corpus):
    # Split corpus into sentences
    sentences = [s.strip() for s in corpus.split('.') if len(s.strip()) > 15]
    if not sentences:
        return "No relevant content found.", "N/A", 0.0
    
    # Compute embeddings
    query_emb = model.encode(query, convert_to_tensor=True)
    corpus_emb = model.encode(sentences, convert_to_tensor=True)
    
    # Find the top relevant sentence
    hits = util.semantic_search(query_emb, corpus_emb, top_k=1)
    best_hit = hits[0][0]
    
    score = best_hit['score']
    source_sentence = sentences[best_hit['corpus_id']]
    
    return source_sentence, source_sentence, score

# --- Sidebar ---
with st.sidebar:
    st.header("📂 Knowledge Base")
    input_type = st.radio("Source:", ["Upload Documents", "Manual Text Entry"])
    
    full_corpus = ""
    if input_type == "Upload Documents":
        uploaded_files = st.file_uploader("Upload (PDF, DOCX, TXT)", accept_multiple_files=True)
        if uploaded_files:
            full_corpus = extract_text(uploaded_files)
            st.success(f"Indexed {len(uploaded_files)} files.")
    else:
        full_corpus = st.text_area("Paste documentation here...", height=250)

    if st.button("🗑️ Clear History"):
        st.session_state.chat_history = []
        st.rerun()

# --- Main UI ---
st.title("🤖 Document-Based Question Answering System")
st.caption("Ask multiple questions and see the exact source sentences from your documents.")

if full_corpus:
    # Multiple Question Input
    with st.form(key="qa_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1], vertical_alignment="bottom")
        with col1:
            user_query = st.text_input("Enter your question:", placeholder="e.g., What are the safety protocols?")
        with col2:
            st.write(" ") # Padding
            submit = st.form_submit_button("Ask Question")

    if submit and user_query:
        with st.spinner("Analyzing document content..."):
            ans, source, conf = get_answer(user_query, full_corpus)
            # Store in history
            st.session_state.chat_history.insert(0, {
                "q": user_query,
                "a": ans,
                "s": source,
                "c": conf
            })

    # Display History
    for chat in st.session_state.chat_history:
        with st.container():
            st.markdown(f"### ❓ {chat['q']}")
            
            # Answer Box
            st.markdown(f"""
                <div style="background-color:#eef2f6; padding:15px; border-radius:10px; border-left: 5px solid #007bff;">
                    <strong>Answer:</strong> {chat['a']}
                </div>
            """, unsafe_allow_html=True)
            
            # Source Sentence and Score
            st.markdown(f"**📍 Source Sentence:** *\"{chat['s']}\"*")
            st.progress(chat['c'], text=f"Confidence Score: {chat['c']:.2f}")
            st.divider()

else:
    st.warning("Please upload a document or enter text in the sidebar to begin.")
