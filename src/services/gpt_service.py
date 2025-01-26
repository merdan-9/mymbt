import streamlit as st
from openai import OpenAI

class GPTService:
    def __init__(self):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
    def get_stock_analysis(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a professional stock market analyst. 
                     Provide concise, factual analysis based on the given data.
                     Format your response using markdown with clear sections:
                     - Use ### for main headings
                     - Use bullet points for lists
                     - Use bold text for important numbers and metrics
                     - Separate sections with newlines for clarity
                     - Use emojis where appropriate to enhance readability"""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting GPT analysis: {str(e)}" 