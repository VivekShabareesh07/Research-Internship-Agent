from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from langchain_core.runnables.graph import MermaidDrawMethod
from typing import TypedDict
import json
from prompts.search_agent import SEARCH_EVALUATION_PROMPT,SEARCH_QUERY_PROMPT,SEARCH_IMPROVEMENT_PROMPT
import time

def safe_invoke(prompt, retries=5):
    for i in range(retries):
        try:
            return llm.invoke(prompt)
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                wait = 2 ** i
                print(f"Gemini busy. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Gemini unavailable after retries.")

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
)

search = TavilySearch(max_results=3)

class SearchState(TypedDict):
    interest: str
    role: str
    location: str

    query: str

    results: list
    best_results: list
    previous_queries: list

    top3: list

    score: int

    feedback: str

    attempts: int

def generate_query_node(state):

    prompt = SEARCH_QUERY_PROMPT.format(
        interest=state["interest"],
        role=state["role"],
        location=state["location"]
    )

    response = safe_invoke(prompt)

    query = response.content

    if isinstance(query, list):
        query = query[0]["text"]

    new_query = query.strip()
    return {
        "query": new_query,
        "attempts": state["attempts"] + 1,
        "previous_queries": state["previous_queries"] + [new_query]
    }

def search_node(state: SearchState):
    print(f"\nSearching: {state['query']}\n")
    results = search.invoke(state["query"])
    print(f"Found {len(results)} search results.")

    return {
        "results": results
    }

def evaluate_node(state: SearchState):

    prompt = SEARCH_EVALUATION_PROMPT.format(
        interest=state["interest"],
        role=state["role"],
        location=state["location"],
        results=state["results"]
    )

    response = safe_invoke(prompt)

    text = response.content

    if isinstance(text, list):
        text = text[0]["text"]

    text = text.replace("```json", "").replace("```", "").strip()

    start = text.find("{")
    end = text.rfind("}")
    
    if start == -1 or end == -1:
        print("\nNo JSON object found.")
        return {
            "feedback": "No JSON found.",
            "top3": state["best_results"]
    }
    else:
        text = text[start:end+1]

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print("\nInvalid JSON:\n")
        print(text)

        return {
            "score": state["score"],
            "feedback": "Failed to parse LLM output.",
            "top3": state["best_results"]
        }

    for i, item in enumerate(data["top3"], 1):
        print(f"{i}. {item['title']} ({item['score']})")
    print(f"Feedback: {data['feedback']}")
    return {
        "score": data["score"],
        "feedback": data["feedback"],
        "top3": data["top3"]
    }

def keep_results_node(state):

    current = state["best_results"].copy()

    # Add new opportunities
    for r in state["top3"]:

        if r["url"] not in [x["url"] for x in current]:
            current.append(r)

    # Highest score first
    current.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # Keep only best 3
    best3 = current[:3]

    # If no result exists
    if not best3:
        return {
            "best_results": [],
            "score": 0
        }

    # Average score of selected opportunities
    avg_score = round(
        sum(x["score"] for x in best3) / len(best3)
    )

    return {
        "best_results": best3,
        "score": avg_score
    }

def improve_query_node(state: SearchState):

    prompt = SEARCH_IMPROVEMENT_PROMPT.format(
        interest=state["interest"],
        role=state["role"],
        location=state["location"],
        query=state["query"],
        feedback=state["feedback"],
        previous_queries=state["previous_queries"]
    )

    response = safe_invoke(prompt)

    query = response.content

    if isinstance(query, list):
        query = query[0]["text"]

    print("\nImproved Query:")
    new_query=query.strip()
    print(new_query)
    return {
        "query": new_query,
        "previous_queries": state["previous_queries"] + [new_query],
        "attempts": state["attempts"] + 1
    }

def router(state: SearchState):

    if state["score"] >= 85:
        print("Search quality acceptable.")
        return "end"

    if state["attempts"] >= 3:
        print("Maximum attempts reached.")
        return "end"

    return "improve"

workflow = StateGraph(SearchState)

workflow.add_node("generateQuery", generate_query_node)
workflow.add_node("search", search_node)
workflow.add_node("evaluate", evaluate_node)
workflow.add_node("keep", keep_results_node)
workflow.add_node("improve", improve_query_node)

workflow.set_entry_point("generateQuery")

workflow.add_edge("generateQuery", "search")
workflow.add_edge("search", "evaluate")
workflow.add_edge("evaluate", "keep")

workflow.add_conditional_edges(
    "keep",
    router,
    {
        "improve": "improve",
        "end": END
    }
)

workflow.add_edge("improve", "search")

app = workflow.compile()

def run_search_agent(state):
    result = app.invoke(state)
    print("\n========== FINAL SEARCH STATE ==========")
    print(result)
    print("========================================")

    return result

if __name__ == "__main__":
    png = app.get_graph().draw_mermaid_png(
        draw_method=MermaidDrawMethod.API
    )

    with open("search_agent_graph.png", "wb") as f:
        f.write(png)

    print("Graph saved as search_agent_graph.png")

    initial_state = {
        "interest": "Robotics",
        "role": "Research Internship",
        "location": "India",

        "query": "",

        "results": [],
        "best_results":[],

        "score": 0,
        "feedback": "",
        "top3": [],

        "attempts": 1
    }

    result = app.invoke(initial_state)

    print("\nFinal Score:", result["score"])
    print("\nTop 3 Opportunities:\n")

    for i, r in enumerate(result["best_results"], 1):
        print(f"{i}. {r}")


