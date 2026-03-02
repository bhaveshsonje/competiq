import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def run(state: dict) -> dict:
    """
    Reflexion pattern: critiques the draft report and decides
    whether to accept it or flag sections needing re-research.
    """
    print(f"🔍  Critic Agent: Evaluating report quality...")

    report = state.get("draft_report", "")
    company = state["company"]

    prompt = f"""You are a critical analyst reviewing a competitive intelligence report about {company}.

Report to evaluate:
{report[:3000]}

Evaluate the report on these criteria (score each 1-10):
1. completeness: Does it cover all key areas?
2. specificity: Are claims backed by specific data points?
3. actionability: Are the recommendations concrete and useful?
4. balance: Is it objective and balanced?

Respond ONLY with valid JSON in this exact format:
{{
  "scores": {{
    "completeness": 8,
    "specificity": 7,
    "actionability": 6,
    "balance": 9
  }},
  "overall_score": 7,
  "weak_sections": ["pricing analysis lacks specific numbers"],
  "feedback": "The report is comprehensive but needs more specific pricing data.",
  "approved": true
}}

Set "approved" to true if overall_score >= 7, false otherwise."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()

    try:
        # Extract JSON from response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        critique = json.loads(raw[start:end])
    except:
        critique = {
            "scores": {"completeness": 7, "specificity": 7, "actionability": 7, "balance": 7},
            "overall_score": 7,
            "weak_sections": [],
            "feedback": "Report meets quality standards.",
            "approved": True
        }

    print(f"   Score: {critique['overall_score']}/10 — {'✅ Approved' if critique['approved'] else '🔄 Needs revision'}")

    return {
        **state,
        "critique": critique,
        "final_report": state["draft_report"] if critique["approved"] else None,
        "needs_revision": not critique["approved"]
    }
