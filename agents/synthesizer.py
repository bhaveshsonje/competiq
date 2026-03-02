import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def run(state: dict) -> dict:
    company = state["company"]
    competitors = state["competitors"]

    print(f"📝  Synthesizer: Writing competitive intelligence report...")

    avg_confidence = round((
        state.get("news_confidence", 5) +
        state.get("product_confidence", 5) +
        state.get("pricing_confidence", 5) +
        state.get("sentiment_confidence", 5) +
        state.get("market_confidence", 5)
    ) / 5)

    prompt = f"""You are a senior competitive intelligence analyst. Write a comprehensive report for:

Company Being Analyzed: {company}
Competitors: {', '.join(competitors)}

--- RESEARCH FINDINGS ---

📰 RECENT NEWS & DEVELOPMENTS:
{state.get("news_findings", "No data")}

🛠️ PRODUCT & FEATURES:
{state.get("product_findings", "No data")}

💰 PRICING & BUSINESS MODEL:
{state.get("pricing_findings", "No data")}

💬 CUSTOMER SENTIMENT:
{state.get("sentiment_findings", "No data")}

📊 MARKET POSITION:
{state.get("market_findings", "No data")}

---

Write a structured competitive intelligence report with these sections:
1. **Executive Summary** (3-4 sentences, key takeaways)
2. **Competitive Landscape Overview**
3. **Product Comparison** (compare {company} vs each competitor)
4. **Pricing Analysis**
5. **Market Positioning & Sentiment**
6. **Strategic Opportunities for {company}** (concrete recommendations)
7. **Key Risks & Threats**
8. **SWOT Analysis for {company}**

Use clear headers, be specific with data points, and write in professional analyst style."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=3000
    )

    report = response.choices[0].message.content.strip()

    all_sources = (
        state.get("news_sources", []) +
        state.get("product_sources", []) +
        state.get("pricing_sources", []) +
        state.get("sentiment_sources", []) +
        state.get("market_sources", [])
    )
    seen = set()
    unique_sources = []
    for s in all_sources:
        if s["url"] not in seen:
            seen.add(s["url"])
            unique_sources.append(s)

    return {
        **state,
        "draft_report": report,
        "overall_confidence": avg_confidence,
        "all_sources": unique_sources[:20]
    }
