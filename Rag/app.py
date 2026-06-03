import os
import warnings

# Suppress harmless PyTorch and telemetry warnings
warnings.filterwarnings("ignore")
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

# Import custom modules
from utils.styling import apply_glassmorphism
from scraper import scrape_reddit
from embedder import process_product
from rag_pipeline import retrieve_complaints
from analyzer import analyze_complaints

# Configuration
st.set_page_config(page_title="Reddit Rage Analyzer", page_icon="😠", layout="wide")

def display_word_cloud(keywords):
    """Generates and displays a word cloud from keywords."""
    if not keywords:
        return
    text = " ".join(keywords)
    wordcloud = WordCloud(width=800, height=400, background_color="rgba(255, 255, 255, 0)", mode="RGBA", colormap="Blues").generate(text)
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    # Make matplotlib background transparent
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    st.pyplot(fig)

def create_download_link(data_dict, product_name):
    """Generates a downloadable CSV report."""
    df = pd.DataFrame([data_dict])
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download Full Report (CSV)",
        data=csv,
        file_name=f"{product_name}_rage_analysis.csv",
        mime="text/csv",
        use_container_width=True
    )

def main():
    # Apply custom UI styling
    apply_glassmorphism()
    
    st.title("Reddit Rage Analyzer")
    st.markdown("Uncover what users *really* hate about products using RAG and LLaMA 3.3 AI.")

    # Check for API keys
    from dotenv import load_dotenv
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        st.warning("⚠️ Warning: GROQ_API_KEY is missing. Please check your `.env` file.")
    
    # Sidebar
    with st.sidebar:
        st.header("Search Parameters")
        product_query = st.text_input("Enter Product Name:", placeholder="e.g. Instagram, ChatGPT...")
        analyze_btn = st.button("Analyze Sentiment", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### How it works")
        st.markdown("1. **Scrapes** Reddit (r/technology, r/apps, etc.)")
        st.markdown("2. **Cleans** and generates embeddings")
        st.markdown("3. **Retrieves** top complaints via semantic search")
        st.markdown("4. **Analyzes** insights using LLaMA 3.3")
    
    if analyze_btn and product_query:
        # State tracking
        product_name = product_query.strip()
        
        try:
            # Step 1: Scrape
            with st.spinner(f"Scraping Reddit for '{product_name}'..."):
                raw_data = scrape_reddit(product_name, limit_per_sub=5)
                if not raw_data:
                    st.error("No data found or scraping failed.")
                    return
            
            # Step 2: Embed and Store
            with st.spinner("Processing text and updating Vector DB..."):
                success = process_product(product_name)
                if not success:
                    st.error("Failed to process embeddings.")
                    return
            
            # Step 3: Retrieve relevant chunks
            with st.spinner("Retrieving semantic complaints via RAG..."):
                retrieved_docs = retrieve_complaints("major issues bugs hate worst features", product_name, k=15)
                if not retrieved_docs:
                    st.error("RAG retrieval failed.")
                    return
            
            # Step 4: Analyze with Gemini
            with st.spinner("Generating AI Analysis using LLaMA 3.3..."):
                analysis_result = analyze_complaints(product_name, retrieved_docs)
                if "error" in analysis_result:
                    st.error(f"Analysis failed: {analysis_result['error']}")
                    return
            
            # -----------------------------------------
            # DISPLAY DASHBOARD
            # -----------------------------------------
            st.success("Analysis Complete!")
            
            # Top row metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                with st.container(border=True):
                    st.metric("Overall Sentiment", analysis_result.get("overall_sentiment", "N/A"))
            with col2:
                with st.container(border=True):
                    st.metric("Emotional Intensity", analysis_result.get("emotional_intensity", "N/A"))
            with col3:
                with st.container(border=True):
                    st.metric("Total Complaints Analyzed", len(retrieved_docs))
                
            # Summary Section
            with st.container(border=True):
                st.subheader("📝 Executive Summary")
                st.write(analysis_result.get("summary_paragraph", ""))
            
            # Charts and Lists Row
            col_chart, col_lists = st.columns([1, 1])
            
            with col_chart:
                with st.container(border=True):
                    st.subheader("☁️ Top Complaint Keywords")
                    display_word_cloud(analysis_result.get("top_keywords", []))
                    
                    # Mock up a sentiment distribution for the pie chart based on the overall sentiment
                    sentiment = analysis_result.get("overall_sentiment", "Neutral").lower()
                    if "very negative" in sentiment:
                        vals = [80, 15, 5]
                    elif "negative" in sentiment:
                        vals = [60, 30, 10]
                    else:
                        vals = [40, 40, 20]
                        
                    fig = px.pie(
                        names=["Negative", "Neutral", "Positive"], 
                        values=vals, 
                        title="Estimated Sentiment Distribution",
                        color_discrete_sequence=["#ef4444", "#94a3b8", "#22c55e"]
                    )
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#111827"))
                    st.plotly_chart(fig, use_container_width=True)
                
            with col_lists:
                with st.container(border=True):
                    st.subheader("🔥 Most Hated Features")
                    for feature in analysis_result.get("most_hated_features", []):
                        st.markdown(f"- {feature}")
                    
                    st.subheader("🐛 Common Bug Patterns")
                    for bug in analysis_result.get("common_bug_patterns", []):
                        st.markdown(f"- {bug}")
                        
                    st.subheader("🔄 Key Recurring Complaints")
                    for complaint in analysis_result.get("key_recurring_complaints", []):
                        st.markdown(f"- {complaint}")
                
            # Raw Data Expander
            st.markdown("### Raw Retrieved Complaints")
            for i, doc in enumerate(retrieved_docs[:5]): # Show top 5
                with st.expander(f"Complaint #{i+1} (Upvotes: {doc.metadata.get('upvotes', 'N/A')})"):
                    st.write(doc.page_content)
                    st.caption(f"Subreddit: r/{doc.metadata.get('subreddit', 'N/A')}")
            
            # Download Button
            create_download_link(analysis_result, product_name)
            
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
