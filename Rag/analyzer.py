import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# We'll use LLaMA 3.3 70B via Groq which is blazing fast and excellent at JSON
MODEL_NAME = 'llama-3.3-70b-versatile'

def analyze_complaints(product_name: str, retrieved_docs: list) -> dict:
    """
    Analyzes the retrieved Reddit complaints using Groq API and returns a structured JSON result.
    """
    if not retrieved_docs:
        return {"error": "No documents provided for analysis."}
        
    if not os.getenv("GROQ_API_KEY"):
        return {"error": "GROQ_API_KEY is not set in .env."}

    # Compile documents into a single text block
    context = ""
    for i, doc in enumerate(retrieved_docs):
        context += f"--- Complaint {i+1} ---\n"
        context += f"{doc.page_content}\n\n"

    # Define the prompt for Groq
    prompt = f"""
    You are an expert AI product analyst. Your task is to analyze the following Reddit complaints about the product '{product_name}'.
    
    Based ONLY on the complaints provided below, generate a comprehensive analysis and return the result as a strictly formatted JSON object. 
    Do NOT include Markdown formatting like ```json or ``` in the response, just return the raw JSON.
    
    The JSON structure MUST be exactly as follows:
    {{
        "most_hated_features": ["feature 1", "feature 2", "feature 3"],
        "common_bug_patterns": ["bug 1", "bug 2"],
        "emotional_intensity": "High/Medium/Low",
        "overall_sentiment": "Positive/Neutral/Negative/Very Negative",
        "key_recurring_complaints": ["complaint 1", "complaint 2"],
        "summary_paragraph": "A professional 3-4 sentence summary of the general consensus and main issues.",
        "top_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
    }}
    
    --- COMPLAINTS DATA ---
    {context}
    """

    try:
        # Initialize Groq client
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that only outputs strictly valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=MODEL_NAME,
            temperature=0.2,
        )
        
        # Clean the response text to extract JSON (in case it still wraps it in markdown)
        result_text = chat_completion.choices[0].message.content.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        result_json = json.loads(result_text.strip())
        return result_json

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from Groq response: {e}")
        return {"error": "Failed to parse AI response into JSON format."}
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return {"error": str(e)}
