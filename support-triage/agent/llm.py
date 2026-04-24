import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    base_url="https://api.minimax.io/anthropic"
)

def classify_with_ai(subject: str, body: str) -> dict:
    response = client.messages.create(
        model="MiniMax-M2.7",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [{"type": "text", "text": f"Classify this ticket: {subject} {body}"}]
        }]
    )
    # Handle both TextBlock and ThinkingBlock (MiniMax may return thinking blocks)
    result = ""
    for block in response.content:
        if block.type == "text":
            result = block.text
            break
    return {"intent": result, "confidence": 0.85}