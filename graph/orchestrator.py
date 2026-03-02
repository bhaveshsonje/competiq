from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional, Any
from agents import news_agent, product_agent, pricing_agent, sentiment_agent, market_agent
from agents import synthesizer, critic_agent


class IntelState(TypedDict):
    # Input
    company: str
    competitors: List[str]

    # Agent findings
    news_findings: Optional[str]
    news_confidence: Optional[int]
    news_sources: Optional[List[dict]]

    product_findings: Optional[str]
    product_confidence: Optional[int]
    product_sources: Optional[List[dict]]

    pricing_findings: Optional[str]
    pricing_confidence: Optional[int]
    pricing_sources: Optional[List[dict]]

    sentiment_findings: Optional[str]
    sentiment_confidence: Optional[int]
    sentiment_sources: Optional[List[dict]]
    sentiment_scores: Optional[dict]

    market_findings: Optional[str]
    market_confidence: Optional[int]
    market_sources: Optional[List[dict]]

    # Synthesis
    draft_report: Optional[str]
    overall_confidence: Optional[int]
    all_sources: Optional[List[dict]]

    # Critique
    critique: Optional[dict]
    final_report: Optional[str]
    needs_revision: Optional[bool]

    # Metadata
    revision_count: Optional[int]


def should_revise(state: IntelState) -> str:
    """Conditional edge: revise or finalize based on critique score."""
    revision_count = state.get("revision_count", 0)
    if state.get("needs_revision") and revision_count < 2:
        return "revise"
    return "finalize"


def revision_node(state: IntelState) -> IntelState:
    """Re-runs synthesis with critic feedback to improve the report."""
    print(f"🔄  Revising report based on critic feedback...")
    from groq import Groq
    import os

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    critique = state.get("critique", {})

    prompt = f"""Improve this competitive intelligence report based on critic feedback.

Original Report:
{state.get("draft_report", "")}

Critic Feedback:
- Score: {critique.get("overall_score", 7)}/10
- Weak sections: {critique.get("weak_sections", [])}
- Feedback: {critique.get("feedback", "")}

Rewrite the report addressing all weaknesses. Be more specific with data points
and make recommendations more actionable."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=3000
    )

    return {
        **state,
        "draft_report": response.choices[0].message.content.strip(),
        "revision_count": state.get("revision_count", 0) + 1,
        "needs_revision": False
    }


def finalize_node(state: IntelState) -> IntelState:
    """Marks the report as final."""
    return {**state, "final_report": state.get("draft_report", "")}


def build_graph():
    graph = StateGraph(IntelState)

    # Add all agent nodes
    graph.add_node("news_agent", news_agent.run)
    graph.add_node("product_agent", product_agent.run)
    graph.add_node("pricing_agent", pricing_agent.run)
    graph.add_node("sentiment_agent", sentiment_agent.run)
    graph.add_node("market_agent", market_agent.run)
    graph.add_node("synthesizer", synthesizer.run)
    graph.add_node("critic", critic_agent.run)
    graph.add_node("revise", revision_node)
    graph.add_node("finalize", finalize_node)

    # Fan-out: all 5 agents start in parallel from entry
    graph.set_entry_point("news_agent")
    graph.add_edge("news_agent", "synthesizer")

    # Parallel branches
    for agent in ["product_agent", "pricing_agent", "sentiment_agent", "market_agent"]:
        graph.add_node(agent, eval(f"{agent.replace('_agent', '_agent')}.run"))

    # NOTE: LangGraph executes nodes sequentially by default.
    # For true parallelism we run agents via asyncio in main.py.
    # The graph here defines the logical flow.
    graph.add_edge("synthesizer", "critic")
    graph.add_conditional_edges("critic", should_revise, {
        "revise": "revise",
        "finalize": "finalize"
    })
    graph.add_edge("revise", "critic")
    graph.add_edge("finalize", END)

    return graph.compile()


# Async parallel runner (used by FastAPI)
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_parallel_agents(company: str, competitors: List[str], progress_callback=None) -> IntelState:
    """
    Runs all 5 research agents in parallel using ThreadPoolExecutor,
    then passes combined state through synthesizer → critic → finalize.
    """
    initial_state = {
        "company": company,
        "competitors": competitors,
        "revision_count": 0
    }

    loop = asyncio.get_event_loop()

    if progress_callback:
        await progress_callback("agent_start", "All 5 agents starting in parallel...")

    # Run agents in parallel threads
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            "news": loop.run_in_executor(executor, news_agent.run, initial_state.copy()),
            "product": loop.run_in_executor(executor, product_agent.run, initial_state.copy()),
            "pricing": loop.run_in_executor(executor, pricing_agent.run, initial_state.copy()),
            "sentiment": loop.run_in_executor(executor, sentiment_agent.run, initial_state.copy()),
            "market": loop.run_in_executor(executor, market_agent.run, initial_state.copy()),
        }

        results = {}
        for name, future in futures.items():
            results[name] = await future
            if progress_callback:
                await progress_callback("agent_done", f"{name.title()} agent completed")

    # Merge all agent results into one state
    merged_state = {**initial_state}
    for result in results.values():
        merged_state.update({k: v for k, v in result.items() if k not in initial_state})

    if progress_callback:
        await progress_callback("synthesizing", "Synthesizing findings into report...")

    # Run synthesizer
    merged_state = synthesizer.run(merged_state)

    if progress_callback:
        await progress_callback("critiquing", "Critic agent evaluating report quality...")

    # Run critic loop (max 2 revisions)
    for _ in range(2):
        merged_state = critic_agent.run(merged_state)
        if not merged_state.get("needs_revision"):
            break
        if progress_callback:
            await progress_callback("revising", "Revising report based on critic feedback...")
        merged_state = revision_node(merged_state)

    merged_state["final_report"] = merged_state.get("draft_report", "")

    if progress_callback:
        await progress_callback("complete", "Analysis complete!")

    return merged_state
