import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are a sustainability and packaging expert specializing in Life Cycle Assessment (LCA), ESG (Environmental, Social, Governance) reporting, "
    "and materiality analysis for packaging. Answer user questions as an industry authority, using up-to-date standards, real-world examples, and "
    "clear explanations tailored to packaging solutions."
    
)

def ask_groq(messages):
    """Send request to Groq API and return response."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    data = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"API Error {e.response.status_code}: {e.response.text}")
        else:
            st.error(f"Request failed: {e}")
        return None
    except KeyError as e:
        st.error(f"Unexpected API response format: {e}")
        return None

def main():
    st.set_page_config(
        page_title="Sustainability Packaging Chatbot",
        page_icon="🌱",
        layout="wide"
    )
    
    st.title("🌱 Sustainability Packaging Chatbot")
    st.markdown("Expert advice on LCA, ESG reporting, packaging sustainability, and materiality analysis")
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This chatbot specializes in:
        - Life Cycle Assessment (LCA)
        - ESG reporting
        - Packaging sustainability
        - Materiality analysis
        - Environmental standards
        """)
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Check API key
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY not found. Please add it to your .env file.")
        st.stop()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about sustainability, packaging, LCA, or ESG..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Prepare conversation for API
        conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
        conversation.extend(st.session_state.messages)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ask_groq(conversation)
                
                if response:
                    st.markdown(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.error("Failed to get response. Please try again.")

if __name__ == "__main__":
    main()
