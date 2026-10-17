import os
import streamlit as st
from pypdf import PdfReader
import google.generativeai as genai

# Page Configuration
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for a ultra-modern, polished look
st.markdown(
    """
    <style>
    /* Main Theme & Background Accent */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Custom Headers */
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #6EE7B7, #3B82F6, #9333EA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.15rem;
        color: #9CA3AF;
        margin-bottom: 25px;
        font-weight: 400;
    }
    
    /* Card / Metric Styling */
    div.stMetric {
        background-color: #1F2937;
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid #374151;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div.stMetric label {
        color: #9CA3AF !important;
        font-weight: 600 !important;
    }
    div.stMetric [data-testid="stMetricValue"] {
        color: #F3F4F6 !important;
        font-weight: 700 !important;
    }

    /* Buttons & Inputs */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Sidebar Polish */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1F2937;
    }
    
    /* Chat bubbles & alerts */
    .stAlert {
        border-radius: 10px;
        border: 1px solid #374151;
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
  matching_lines = [line for line in lines if query_lower in line.lower()]
  if matching_lines:
    return (
        "**[Offline Fallback Mode - Keyword Match]**\n\nFound these relevant"
        f" lines:\n"
        + "\n".join([f"> {line}" for line in matching_lines[:5]])
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
st.sidebar.markdown("## ⚙️ Control Center")
st.sidebar.markdown("Configure your AI credentials and upload source files.")

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
    "📂 Upload Document", type=["pdf"], help="Select a PDF document to analyze"
)

# --- Main Application Header ---
st.markdown(
    '<p class="main-header">🧠 DocuMind AI</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Transform static study notes, research papers, and'
    " manuals into an interactive conversational intelligence platform.</p>",
    unsafe_allow_html=True,
)

# --- Core Logic ---
if uploaded_file is not None:
  with st.spinner("✨ Processing document structure & extracting text..."):
    pdf_text, total_pages = extract_pdf_text(uploaded_file)

  if pdf_text:
    word_count = len(pdf_text.split())

    # Modern Layout Tabs
    tab1, tab2, tab3 = st.tabs([
        "📊 Overview & Metrics",
        "📝 AI Summary & Takeaways",
        "💬 Interactive Q&A Chat",
    ])

    with tab1:
      st.markdown("### Document Telemetry")
      col1, col2, col3 = st.columns(3)
      col1.metric("📄 File Name", uploaded_file.name)
      col2.metric("📑 Total Pages", total_pages)
      col3.metric("📝 Word Count", f"{word_count:,}")

      st.markdown("<br>", unsafe_allow_html=True)
      with st.expander("🔍 Inspect Extracted Raw Text"):
        st.text_area("Raw Text Content", pdf_text, height=300)

    with tab2:
      st.markdown("### Executive Summary & Key Insights")
      st.markdown(
          "Generate an automated deep-dive summary and critical takeaway bullet"
          " points instantly."
      )

      if st.button("🚀 Generate AI Summary", type="primary"):
        if not api_key_input:
          st.warning(
              "⚠️ Please enter a Google Gemini API key in the sidebar to"
              " generate AI summaries."
          )
        else:
          with st.spinner("🤖 Synthesizing key insights..."):
            summary_prompt = (
                "Provide a comprehensive, beautifully structured executive"
                " summary of the following document, followed by 5 key"
                f" bullet-point takeaways:\n\n{pdf_text[:15000]}"
            )
            summary_result = generate_ai_response(summary_prompt, api_key_input)
            st.markdown(summary_result)
      else:
        st.info(
            "💡 Click the button above to synthesize document insights using"
            " Gemini AI."
        )

    with tab3:
      st.markdown("### Conversational Document Assistant")
      st.markdown(
          "Ask precise questions regarding concepts, tables, or sections within"
          " your document."
      )

      if "messages" not in st.session_state:
        st.session_state.messages = []

      for message in st.session_state.messages:
        with st.chat_message(message["role"]):
          st.markdown(message["content"])

      if user_query := st.chat_input("Ask anything about this document..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
          st.markdown(user_query)

        with st.chat_message("assistant"):
          with st.spinner("💭 Analyzing document context..."):
            if not api_key_input:
              response_text = fallback_search(user_query, pdf_text)
            else:
              qa_prompt = (
                  "You are DocuMind AI, an expert research assistant. Answer"
                  " the user's question strictly and accurately based on the"
                  " provided document text. If the answer cannot be found in"
                  " the text, state that clearly.\n\nDocument"
                  f" Text:\n{pdf_text[:15000]}\n\nUser Question: {user_query}"
              )
              response_text = generate_ai_response(qa_prompt, api_key_input)

            st.markdown(response_text)
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
else:
  # Sleek empty state container
  st.info(
      "👋 Welcome to **DocuMind AI**! Get started by uploading a PDF document"
      " using the sidebar on the left."
  )
