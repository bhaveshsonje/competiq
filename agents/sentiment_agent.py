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

    print(f"💬  Sentiment Agent: Analyzing customer sentiment...")

    all_findings = []
    all_sources = []
    total_confidence = 0
    sentiment_scores = {}

    for name in all_names:
        query = f"{name} reviews customer feedback complaints praise Reddit G2 2024 2025"
        data = web_search(query, max_results=4)
        context = format_results(data)
        all_sources.extend(data["sources"])
        total_confidence += data["confidence"]

        prompt = f"""Analyze customer sentiment and reviews for {name}.

Search Results:
{context}

Provide:
1. Overall sentiment (Positive/Mixed/Negative) with a score out of 10
2. Top 2 praised aspects
3. Top 2 common complaints
Keep it to 3-4 sentences total."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        summary = response.choices[0].message.content.strip()
        all_findings.append(f"**{name}:** {summary}")

        # Extract numeric sentiment score for charts
        score_prompt = f"Based on this sentiment analysis, give ONLY a number from 1-10 for overall sentiment. Just the number:\n{summary}"
        score_resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": score_prompt}],
            temperature=0
        )
        try:
            score = int(score_resp.choices[0].message.content.strip().split()[0])
            sentiment_scores[name] = min(10, max(1, score))
        except:
            sentiment_scores[name] = 5

    avg_confidence = round(total_confidence / len(all_names))

    return {
        **state,
        "sentiment_findings": "\n\n".join(all_findings),
        "sentiment_confidence": avg_confidence,
        "sentiment_sources": all_sources[:8],
        "sentiment_scores": sentiment_scores
    }
