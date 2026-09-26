# ai_support.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an AI customer support analyst.

Analyze the customer's complaint and return ONLY valid JSON.

Return:
{
    "category": "",
    "urgency": "",
    "summary": "",
    "department": "",
    "suggested_action": "",
    "reply": ""
}

Categories:
Delivery, Billing, Technical, Product, Returns, Refund, Account, Other.

Urgency:
Low, Medium, High, Critical.

Departments:
Logistics, Billing, Technical Support, Product Support,
Returns & Refunds, Account Support, General Support.

The reply must be professional, polite, empathetic and concise.
"""

def analyze_complaint(complaint):
    response = client.chat.completions.create(
        model="gpt-5.6",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": complaint}
        ],
        temperature=0.2
    )

    return json.loads(response.choices[0].message.content)


if __name__ == "__main__":
    complaint = input("Enter customer complaint: ")

    result = analyze_complaint(complaint)

    print(json.dumps(result, indent=4))
