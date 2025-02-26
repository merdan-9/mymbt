import streamlit as st
from openai import OpenAI

class GPTService:
    def __init__(self):
        # self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self.client = OpenAI(api_key=st.secrets["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
        
    def get_stock_analysis(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                # model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a quantitative trading strategist** specializing in precise technical execution"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=750
            )

            content = response.choices[0].message.content
            
            return content
        except Exception as e:
            return f"Error getting GPT analysis: {str(e)}" 