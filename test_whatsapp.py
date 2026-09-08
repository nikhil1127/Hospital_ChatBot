import requests

# The URL of our local server
URL = "http://localhost:8000/whatsapp"

# A dummy payload that looks exactly like what Twilio sends
payload = {
    "From": "whatsapp:+1234567890",
    "Body": "Hi! I'm feeling a bit dizzy and I think I need to see a doctor. Can you help me?"
}

print("Sending simulated WhatsApp message...")
try:
    response = requests.post(URL, data=payload)
    print(f"Status Code: {response.status_code}")
    print("Bot Response:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
