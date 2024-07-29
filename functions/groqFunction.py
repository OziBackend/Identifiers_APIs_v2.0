import os

os.environ["GROQ_API_KEY"] = (
    "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"  # Replace with your actual key
)
from groq import Groq
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def search_groq(prompt):
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(e)
        return []