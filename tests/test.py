from twilio.rest import Client
import streamlit as st

account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

symbol = 'BTC-USD'
price = 409173

message = client.messages.create(
  from_=f'whatsapp:{st.secrets["TWILIO_WHATSAPP_NUMBER"]}',
  content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
  content_variables=f'{{"1":"{symbol}","2":"{price}"}}',
  to=f'whatsapp:{st.secrets["TO_WHATSAPP_NUMBER"]}'
)

print(message.sid)