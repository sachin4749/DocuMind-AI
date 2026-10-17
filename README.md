# 🤖 DocuMind AI

A feature-rich, sleek Streamlit web application that allows users to upload PDF documents, analyze metadata, generate automated summaries, and interactively query document contents using Google Gemini AI.

## 🚀 Key Features
- **Instant PDF Parsing:** Extracts clean text layout page-by-page from any standard PDF.
- **Document Metrics:** Displays real-time file statistics including total pages and word counts.
- **AI-Powered Summaries:** Generates concise executive summaries and key bullet-point takeaways.
- **Interactive Chat Interface:** Natural language Q&A assistant trained specifically on the text of your uploaded document.
- **Fallback Mode:** Includes basic keyword search capability if no API key is active.

## 🛠️ Local Installation & Running Guide

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/documind-ai.git
   cd documind-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

## ☁️ Deployment on Streamlit Community Cloud
1. Push your repository files (`app.py`, `requirements.txt`, `README.md`) to GitHub.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app** and connect your GitHub repository, branch (`main`), and main file path (`app.py`).
4. Click **Deploy!**
