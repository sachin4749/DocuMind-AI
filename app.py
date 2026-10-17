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

# Custom CSS styling for an ultra-modern, polished look
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
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
        font-size: 1.125rem;
        color: #9CA3AF;
        margin-bottom: 25px;
        font-weight: 400;
    }
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
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1F2937;
    }
    .stAlert {
        border-radius: 10px;
        border: 1px solid #374151;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def get_backend_api_key():
  """Backend se secure tarike se API key fetch karne ke liye."""
  if "GEMINI_API_KEY" in st.secrets:
    return st.secrets["GEMINI_API_KEY"]
  return os.environ.get("GEMINI_API_KEY", "")


def extract_pdf_text(uploaded_file):
  """Uploaded PDF file se text extract karne ke liye."""
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


def generate_ai_response(prompt_text, api_key, temperature=0.3):
  """Google Gemini API se response generate karne ke liye."""
  try:
    genai.configure(api_key=api_key)
    generation_config = {"temperature": temperature}
    # Latest stable Gemini 2.0 Flash model
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash", generation_config=generation_config
    )
    response = model.generate_content(prompt_text)
    return response.text
  except Exception as e:
    return f"API Error: {str(e)}"


# Backend API key fetch karna
api_key = get_backend_api_key()

# --- Sidebar Setup ---
st.sidebar.markdown("## ⚙️ Control Center")
st.sidebar.markdown("Upload your PDF document to start exploring.")

# Upload option
uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Document", type=["pdf"], help="Select a PDF file to analyze"
)

st.sidebar.markdown("---")

# AI Settings Slider
temperature = st.sidebar.slider(
    "🎛️ AI Creativity (Temperature)",
    min_value=0.0,
    max_value=1.0,
    value=0.3,
    step=0.1,
    help="Lower = precise/factual, Higher = creative responses.",
)

st.sidebar.markdown("---")

# Reset chat history button
if st.sidebar.button("🗑️ Reset Chat History"):
  if "messages" in st.session_state:
    st.session_state.messages = []
  st.sidebar.success("Chat history cleared!")

# --- Main Application Header ---
st.markdown(
    '<p class="main-header">🧠 DocuMind AI</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Transform static notes, research papers, and books'
    " into an interactive conversational intelligence platform.</p>",
    unsafe_allow_html=True,
)

# --- Core Logic ---
if uploaded_file is not None:
  with st.spinner("✨ Processing document structure & extracting text..."):
    pdf_text, total_pages = extract_pdf_text(uploaded_file)

  if pdf_text:
    word_count = len(pdf_text.split())
    est_reading_time = max(1, word_count // 200)

    # Tabs Layout
    tab1, tab2, tab3 = st.tabs([
        "📊 Overview & Telemetry",
        "📝 AI Summary & Takeaways",
        "💬 Interactive Q&A Chat",
    ])

    with tab1:
      st.markdown("### 📈 Document Telemetry")
      col1, col2, col3, col4 = st.columns(4)
      col1.metric("📄 File Name", uploaded_file.name[:18] + "...")
      col2.metric("📑 Total Pages", total_pages)
      col3.metric("📝 Word Count", f"{word_count:,}")
      col4.metric("⏱️ Est. Read Time", f"{est_reading_time} mins")

      st.markdown("<br>", unsafe_allow_html=True)
      with st.expander("🔍 Inspect Extracted Raw Text"):
        st.text_area("Raw Text Content", pdf_text, height=300)
        st.download_button(
            label="📥 Download Raw Text (.txt)",
            data=pdf_text,
            file_name=f"{uploaded_file.name}_extracted.txt",
            mime="text/plain",
        )

    with tab2:
      st.markdown("### 📑 Executive Summary & Key Insights")
      st.markdown(
          "Generate an automated deep-dive summary and critical takeaway bullet"
          " points instantly."
      )

      if st.button("🚀 Generate AI Summary", type="primary"):
        if not api_key:
          st.error(
              "❌ Backend API Key missing! Please set GEMINI_API_KEY in"
              " Streamlit secrets."
          )
        else:
          with st.spinner("🤖 Synthesizing key insights..."):
            summary_prompt = f"""Provide a comprehensive, beautifully structured executive summary of the following document, followed by 5 key bullet-point takeaways:

Document Text:
{pdf_text[:15000]}"""

            summary_result = generate_ai_response(
                summary_prompt, api_key, temperature
            )
            st.markdown(summary_result)

            st.download_button(
                label="📥 Download Summary (.txt)",
                data=summary_result,
                file_name=f"{uploaded_file.name}_summary.txt",
                mime="text/plain",
            )
      else:
        st.info("💡 Click the button above to synthesize insights.")

    with tab3:
      st.markdown("### 💬 Conversational Document Assistant")
      st.markdown(
          "Ask precise questions regarding concepts, tables, or sections within"
          " your document."
      )

      # Quick Suggestions
      st.markdown("**⚡ Quick Suggestions:**")
      col_q1, col_q2, col_q3 = st.columns(3)
      quick_prompt = None

      if col_q1.button("📌 Main Objective?"):
        quick_prompt = (
            "What is the main objective or core topic of this document?"
        )
      if col_q2.button("🔑 Key Takeaways"):
        quick_prompt = "List 5 most critical takeaways from this document."
      if col_q3.button("❓ Target Audience?"):
        quick_prompt = "Who is the intended target audience for this document?"

      if "messages" not in st.session_state:
        st.session_state.messages = []

      if quick_prompt:
        st.session_state.messages.append({"role": "user", "content": quick_prompt})

      for message in st.session_state.messages:
        with st.chat_message(message["role"]):
          st.markdown(message["content"])

      user_query = st.chat_input("Ask anything about this document...")

      if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
          st.markdown(user_query)

        with st.chat_message("assistant"):
          with st.spinner("💭 Analyzing document context..."):
            if not api_key:
              response_text = (
                  "❌ **Backend Configuration Issue:** API Key is not set in"
                  " secrets."
              )
            else:
              qa_prompt = f"""You are DocuMind AI, an expert research assistant. Answer the user's question strictly and accurately based on the provided document text. If the answer cannot be found in the text, state that clearly.

Document Text:
{pdf_text[:15000]}

User Question: {user_query}"""

              response_text = generate_ai_response(
                  qa_prompt, api_key, temperature
              )

            st.markdown(response_text)
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
else:
  st.info(
      "👋 Welcome to **DocuMind AI**! Get started by uploading a PDF document"
      " using the sidebar on the left."
  )
