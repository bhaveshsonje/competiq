import os
from groq import Groq
from dotenv import load_dotenv
from tools.search import web_search, format_results

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def run(state: dict) -> dict:
    company = state["company"]
    competitors = state["competitors"]
    all_names = [company] + competitors

    print(f"💰  Pricing Agent: Analyzing pricing models...")

    all_findings = []
    all_sources = []
    total_confidence = 0

    for name in all_names:
        query = f"{name} pricing plans cost tiers subscription 2024 2025"
        data = web_search(query, max_results=4)
        context = format_results(data)
        all_sources.extend(data["sources"])
        total_confidence += data["confidence"]

        prompt = f"""Analyze the pricing strategy of {name}.

Search Results:
{context}

Summarize in 2-3 sentences: pricing tiers, cost structure, free tier availability, enterprise pricing approach.
Include specific numbers where available."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        all_findings.append(f"**{name}:** {response.choices[0].message.content.strip()}")

    avg_confidence = round(total_confidence / len(all_names))

    return {
        **state,
        "pricing_findings": "\n\n".join(all_findings),
        "pricing_confidence": avg_confidence,
        "pricing_sources": all_sources[:8]
    }
