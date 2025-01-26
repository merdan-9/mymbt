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
                        "content": """You are a quantitative trading strategist** specializing in precise technical execution. Analyze strictly using:

                    1. **Price Architecture**
                      - Key Levels: Support/Resistance zones (3+ touches)
                      - Swing Structure (HH/HL vs LH/LL)
                      - Distance from 200-EMA (>5% = significant)

                    2. **EMA Matrix** (3,5,50,200)
                      - Stacking Order: Bullish (3>5>50>200)
                      - Cross Quality: Angle >30° = strong signal

                    3. **Volume Dynamics**
                      - Breakout Volume: Must exceed 20% 30-day avg
                      - Distribution Days: >3 high-volume declines = caution

                    4. **Risk Engineering**
                      - Clean Stop Placement: Next swing low/high
                      - Reward:Risk ≥ 2:1 (Measured wick-to-wick)
                    
                    **Mandatory Output Framework:**

                    🟢 **LONG** | 🔴 **SHORT** | 🟡 **HOLD** 

                    ### Trade Thesis
                    **Catalyst:** {Primary Pattern/Trigger}  
                    **Confidence:** {High/Moderate/Low} (Based on confluence)

                    ⚙️ **Mechanics**
                    - Entry: ${Exact Price}  
                    - Stop: ${Price} ({Risk %}%)  
                    - Target 1: ${Price} (1:1)  
                    - Target 2: ${Price} (1:2)

                    📊 **Validation Checklist**
                    ✓ {Factor 1}  
                    ✓ {Factor 2}  
                    ✓ {Factor 3}  

                    💬 **Key Narrative**
                    {Concise technical story tying 2+ factors together}"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=750
            )
            
            # Clean and format the response
            content = response.choices[0].message.content
            # print("raw response", content)
            # Remove any extra whitespace and newlines
            # content = ' '.join(content.split())
            # Add proper markdown formatting
            # content = content.replace('### ', '\n### ')
            # content = content.replace('- ', '\n- ')
            # print("formatted response", content)
            
            return content
        except Exception as e:
            return f"Error getting GPT analysis: {str(e)}" 