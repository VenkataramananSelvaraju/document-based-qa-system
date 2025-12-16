import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="DocChat AI", layout="wide")

st.title("🤖 Document-Based QnA System")

# --- Initialize Session State for Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: File Upload ---
with st.sidebar:
    st.header("📂 Knowledge Base")
    uploaded_files = st.file_uploader("Upload PDF/DOCX", accept_multiple_files=True)
    
    if st.button("Update Knowledge Base"):
        if uploaded_files:
            files = [('files', (f.name, f.getvalue(), f.type)) for f in uploaded_files]
            with st.spinner("Indexing documents..."):
                try:
                    requests.post(f"{API_URL}/upload/", files=files)
                    st.success("✅ Knowledge Updated!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.markdown("---")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        if message.get("source"):
            src = message["source"]
            score_pct = src['score'] * 100
            
            # Dynamic Color for Confidence
            color = "green" if score_pct > 75 else "orange" if score_pct > 50 else "red"
            
            with st.expander(f"🔍 Top Source (Confidence: :{color}[{score_pct:.1f}%])"):
                st.caption(f"**File:** {src['source']}")
                st.markdown(f"**Excerpt:** _{src['content']}_")
                st.progress(src['score'])

# --- Handle New User Input ---
if prompt := st.chat_input("Ask a question about your documents..."):
    # 1. Display User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Add to History
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Get Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            try:
                res = requests.post(f"{API_URL}/query/", json={"question": prompt})
                
                if res.status_code == 200:
                    data = res.json()
                    answer_text = data["answer"]
                    
                    # Check if we have sources
                    top_source = data["sources"][0] if data["sources"] else None
                    
                    # Display Answer
                    st.markdown(answer_text)
                    
                    # Display Top Source Widget immediately
                    if top_source:
                        score_pct = top_source['score'] * 100
                        color = "green" if score_pct > 75 else "orange" if score_pct > 50 else "red"
                        
                        with st.expander(f"🔍 Top Source (Confidence: :{color}[{score_pct:.1f}%])"):
                            st.caption(f"**File:** {top_source['source']}")
                            st.markdown(f"**Excerpt:** _{top_source['content']}_")
                            st.progress(top_source['score'])

                    # Add to History
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer_text,
                        "source": top_source
                    })
                else:
                    st.error("Failed to get response from backend.")
            except Exception as e:
                st.error(f"Connection Error: {e}")