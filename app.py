import os
import streamlit as st
from pypdf import PdfReader
import google.generativeai as genai

# Page Configuration
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for polished UI
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 25px;
    }
    .stAlert {
        border-radius: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def extract_pdf_text(uploaded_file):
    """Extracts text page by page from an uploaded PDF file."""
    try:
        reader = PdfReader(uploaded_file)
        text_data = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                text_data.append(f"--- Page {idx + 1} ---\n{text}")
        return "\n\n".join(text_data), len(reader.pages)
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None, 0


def fallback_search(query, full_text):
    """Basic fallback search if no API key is supplied."""
    query_lower = query.lower()
    lines = full_text.split("\n")
    matching_lines = [
        line for line in lines if query_lower in line.lower()
    ]
    if matching_lines:
        return (
            "**[Offline Fallback Mode - Keyword Match]**\n\nFound these relevant"
            f" lines:\n"
            + "\n".join(
                [f"> {line}" for line in matching_lines[:5]]
            )
        )
    return (
        "**[Offline Fallback Mode]** No direct keyword matches found. Please"
        " configure a Google Gemini API key in the sidebar for intelligent AI"
        " Q&A."
    )


def generate_ai_response(prompt_text, api_key, system_instruction=""):
    """Generates response using Google Gemini API."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", system_instruction=system_instruction
        )
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        return f"API Error: {str(e)}"


# --- Sidebar Setup ---
st.sidebar.markdown("## ⚙️ Configuration & Upload")

default_api_key = os.environ.get("GEMINI_API_KEY", "")
if "GEMINI_API_KEY" in st.secrets:
    default_api_key = st.secrets["GEMINI_API_KEY"]

api_key_input = st.sidebar.text_input(
    "Google Gemini API Key",
    value=default_api_key,
    type="password",
    help=(
        "Get your free key from Google AI Studio. If left blank, offline"
        " fallback mode will be used."
    ),
)

st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader(
    "Upload your PDF Document", type=["pdf"]
)

# --- Main Application Header ---
st.markdown(
    '<p class="main-header">🤖 DocuMind AI</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Upload study notes, research papers, or manuals to'
    " instantly summarize and chat with your documents.</p>",
    unsafe_allow_html=True,
)

# --- Core Logic ---
if uploaded_file is not None:
    with st.spinner("Extracting text and analyzing document..."):
        pdf_text, total_pages = extract_pdf_text(uploaded_file)

    if pdf_text:
        word_count = len(pdf_text.split())

        tab1, tab2, tab3 = st.tabs(
            ["📊 Overview & Metrics", "📝 AI Summary", "💬 Ask Questions (Q&A)"]
        )

        with tab1:
            st.subheader("Document Overview")
            col1, col2, col3 = st.columns(3)
            col1.metric("File Name", uploaded_file.name)
            col2.metric("Total Pages", total_pages)
            col3.metric("Word Count", f"{word_count:,}")

            with st.expander("📄 View Extracted Raw Text"):
                st.text_area("Raw Text Content", pdf_text, height=300)

        with tab2:
            st.subheader("Automated Document Summary")
            if st.button("Generate Summary & Key Takeaways", type="primary"):
                if not api_key_input:
                    st.warning(
                        "Please enter a Google Gemini API key in the sidebar to generate"
                        " an AI summary."
                    )
                else:
                    with st.spinner("Analyzing text and generating insights..."):
                        summary_prompt = (
                            "Provide a comprehensive summary of the following document,"
                            " followed by 5 key bullet-point takeaways:\n\n"
                            f"{pdf_text[:15000]}"
                        )
                        summary_result = generate_ai_response(summary_prompt, api_key_input)
                        st.markdown(summary_result)
            else:
                st.info("Click the button above to generate automated key takeaways.")

        with tab3:
            st.subheader("Interactive Q&A Chat")
            st.markdown(
                "Ask any question about the contents of your uploaded document:"
            )

            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if user_query := st.chat_input(
                "What would you like to know from this document?"
            ):
                st.session_state.messages.append(
                    {"role": "user", "content": user_query}
                )
                with st.chat_message("user"):
                    st.markdown(user_query)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        if not api_key_input:
                            response_text = fallback_search(user_query, pdf_text)
                        else:
                            qa_prompt = (
                                "You are a helpful assistant. Answer the user's question"
                                " strictly based on the provided document text. If the"
                                " answer cannot be found in the text, state that clearly.\n\n"
                                f"Document Text:\n{pdf_text[:15000]}\n\n"
                                f"User Question: {user_query}"
                            )
                            response_text = generate_ai_response(qa_prompt, api_key_input)

                        st.markdown(response_text)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response_text}
                        )
else:
    st.info(
        "👈 Please upload a PDF file from the sidebar to begin your session."
    )
