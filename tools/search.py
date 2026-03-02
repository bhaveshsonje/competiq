import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        _client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    return _client


def web_search(query: str, max_results: int = 6) -> dict:
    """
    Search the web using Tavily and return results with metadata.
    Returns findings, sources, and a raw confidence score.
    """
    try:
        client = get_client()
        response = client.search(
            query=query,
            max_results=max_results,
            include_answer=True,
            search_depth="advanced"
        )

        results = []
        sources = []

        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "score": r.get("score", 0)
            })
            sources.append({
                "title": r.get("title", ""),
                "url": r.get("url", "")
            })

        # Confidence based on result quality scores
        avg_score = sum(r["score"] for r in results) / len(results) if results else 0
        confidence = min(10, round(avg_score * 10))

        return {
            "results": results,
            "sources": sources,
            "confidence": confidence,
            "answer": response.get("answer", "")
        }

    except Exception as e:
        print(f"   ⚠️ Search error: {e}")
        return {"results": [], "sources": [], "confidence": 0, "answer": ""}


def format_results(search_data: dict) -> str:
    """Format search results into readable context for the LLM."""
    results = search_data.get("results", [])
    answer = search_data.get("answer", "")

    if not results:
        return "No search results found."

    formatted = ""
    if answer:
        formatted += f"Quick Answer: {answer}\n\n"

    formatted += "Detailed Sources:\n"
    for i, r in enumerate(results, 1):
        formatted += f"\n[{i}] {r['title']}\n"
        formatted += f"    URL: {r['url']}\n"
        formatted += f"    {r['content'][:500]}\n"

    return formatted
