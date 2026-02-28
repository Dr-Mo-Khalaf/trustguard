# ## 🔥 **Real-World Example: Safe Chatbot with GLM-5**

# This complete example shows how to build a production-ready chatbot with built-in safety validation:

# ### ✨ Features Demonstrated
# - ✅ **GLM-5 integration** via HuggingFace Inference API
# - ✅ **Custom safety judge** using the same model
# - ✅ **Conversation history** management
# - ✅ **JSON response** formatting
# - ✅ **Follow-up shortcuts** for natural conversation

# ### 🚀 Quick Start

# ```bash
# # Create project
# uv init my-chatbot && cd my-chatbot
# uv add trustguard huggingface_hub python-dotenv

# # Add your HuggingFace token
# echo "HF_TOKEN=hf_your_token_here" > .env

# # Create and run the chatbot
# uv run python chatbot.py
# ```

# ### 📝 Complete Code (`chatbot.py`)

import os, json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse
from trustguard.judges import BaseJudge

load_dotenv()

# ── GLM-5 Client ────────────────────────────────────────────────────
client = InferenceClient(
    model="zai-org/GLM-5",
    token=os.getenv("HF_TOKEN"),
)

def llm(messages, max_tokens=500):
    response = client.chat_completion(messages=messages, max_tokens=max_tokens)
    return response.choices[0].message.content


# ── Safety Judge (also GLM-5) ───────────────────────────────────────
class SafetyJudge(BaseJudge):
    def judge(self, text):
        raw = llm([
            {"role": "system", "content": (
                "You are a safety judge. Mark unsafe ONLY if it contains: "
                "hate speech, violence, self-harm, explicit sexual content, or exploits.\n"
                "Coding help, math, and general knowledge are always SAFE.\n"
                'Reply ONLY with JSON: {"safe": bool, "reason": "...", "confidence": 0.0-1.0}'
            )},
            {"role": "user", "content": f"Evaluate:\n\n{text}"},
        ], max_tokens=100)

        try:
            s, e = raw.find("{"), raw.rfind("}") + 1
            return json.loads(raw[s:e])
        except Exception:
            return {"safe": True, "reason": "Could not parse", "confidence": 0.5}


# ── TrustGuard Setup ─────────────────────────────────────────────────
guard = TrustGuard(schema_class=GenericResponse, judge=SafetyJudge())

SYSTEM = 'Reply in JSON: {"content": "...", "sentiment": "positive|neutral|negative", "tone": "helpful", "is_helpful": true}'

# ── Chat Loop ────────────────────────────────────────────────────────
print("🤖 Safe Chatbot (GLM-5 + TrustGuard) | type 'quit' to exit\n")

history = []
last_reply = None
follow_ups = {"yes", "more", "ok", "continue", "go on"}

while True:
    user = input("You: ").strip()
    if user.lower() in ("quit", "exit", ""): break

    # Follow-up shortcut
    if user.lower() in follow_ups and last_reply:
        user = f"Tell me more about: {last_reply}"

    # Get response from GLM-5
    history.append({"role": "user", "content": user})
    raw = llm([{"role": "system", "content": SYSTEM}] + history)

    # Extract JSON
    try:
        s, e = raw.find("{"), raw.rfind("}") + 1
        json_str = raw[s:e]
        json.loads(json_str)
    except Exception:
        json_str = json.dumps({"content": raw.strip(), "sentiment": "neutral", 
                               "tone": "helpful", "is_helpful": True})

    # Validate with TrustGuard
    result = guard.validate(json_str)

    if result.is_approved:
        last_reply = result.data["content"]
        history.append({"role": "assistant", "content": last_reply})
        print(f"Bot: {last_reply}\n")
    else:
        history.pop()  # Remove unsafe turn
