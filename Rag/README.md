# 🤬 Reddit Rage Analyzer

A powerful Retrieval-Augmented Generation (RAG) AI application that scrapes Reddit to discover what users *really* hate about products. It uses **LangChain**, **ChromaDB**, and **Gemini 1.5 Pro** to analyze complaints and display insights on a modern **Streamlit** dashboard.

## 🌟 Features
- **Live Reddit Scraping**: Automatically fetches complaints across popular subreddits (r/technology, r/apps, etc.) using `praw`.
- **RAG Pipeline**: Generates text embeddings using `sentence-transformers/all-MiniLM-L6-v2` and performs semantic search via local **ChromaDB**.
- **Gemini AI Analysis**: Extracts the "most hated features", bug patterns, emotional intensity, and overall sentiment.
- **Glassmorphism UI**: Beautiful, dark-themed Streamlit dashboard with custom CSS, Plotly charts, and word clouds.
- **Downloadable Reports**: Export AI insights directly to CSV.

## 🏗 Architecture
1. **Scraping**: `scraper.py`
2. **Preprocessing & Embedding**: `utils/clean_text.py` -> `embedder.py`
3. **Retrieval**: `rag_pipeline.py`
4. **Generation/Analysis**: `analyzer.py`
5. **UI**: `app.py` & `utils/styling.py`

## 🚀 Setup Instructions

### 1. Clone & Install Dependencies
Ensure you have Python 3.9+ installed.
```bash
# Clone the repository (if applicable)
cd RedditRageAnalyzer

# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Keys
Rename `.env.template` (or create a `.env` file) in the root directory and add your credentials:
```env
# Create an app at https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=RedditRageAnalyzer/1.0

# Get this from Google AI Studio: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run the App
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

## 📸 Screenshots
*(Add screenshots of your Glassmorphism dashboard here)*

## 🔮 Future Improvements
- **Competitor Comparison**: Compare the rage score between two products side-by-side.
- **Historical Trends**: Plot complaint volume over time.
- **Automated Alerts**: Email summaries when a new "severe" bug pattern emerges.

## 📝 License
MIT License
