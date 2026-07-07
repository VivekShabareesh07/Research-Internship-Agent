from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langchain_core.runnables.graph import MermaidDrawMethod
from dotenv import load_dotenv
from typing import TypedDict
import json
from prompts.writer_agent import EMAIL_DRAFT_PROMPT,EMAIL_REVIEW_PROMPT,EMAIL_IMPROVEMENT_PROMPT

import time
from google.genai.errors import ServerError

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

class EmailState(TypedDict):

    student_name: str
    university: str
    year: str

    skills: str
    projects: str
    achievements: str
    attached: bool

    professor_name: str
    professor_email: str
    organization_name: str
    personalization: str
    generic_mode: bool
    lab_name: str
    research_area: str
    opportunity_description: str
    opportunity_url:str

    subject: str
    body: str

    feedback: str
    score: int

    attempts: int

def draft_node(state: EmailState):

    prompt = EMAIL_DRAFT_PROMPT.format(
        student_name=state["student_name"],
        university=state["university"],
        year=state["year"],
        skills=state["skills"],
        projects=state["projects"],
        achievements=state["achievements"],
        attached = state["attached"],
        professor_name=state["professor_name"],
        organization_name=state["organization_name"],
        personalization=state["personalization"],
        generic_mode=state["generic_mode"],
        lab_name=state["lab_name"],
        research_area=state["research_area"],
        opportunity_description=state["opportunity_description"],
        opportunity_url=state["opportunity_url"]
    )

    response = safe_invoke(prompt)

    text = response.content
    if isinstance(text, list):
        text = text[0]["text"]

    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON found in LLM output")

    text = text[start:end+1]

    data = json.loads(text)

    print("\nEmail Draft Generated")

    return {
        "subject": data["subject"],
        "body": data["body"]
    }

def review_node(state: EmailState):

    prompt = EMAIL_REVIEW_PROMPT.format(
        subject=state["subject"],
        body=state["body"],
        professor_name=state["professor_name"],
        research_area=state["research_area"]
    )

    response = safe_invoke(prompt)

    text = response.content

    if isinstance(text, list):
        text = text[0]["text"]

    text = text.replace("```json", "").replace("```", "").strip()
    # start = text.find("{")
    # end = text.rfind("}")

    # if start != -1 and end != -1:
    #     text = text[start:end+1]

    data = json.loads(text)

    print(f"\nEmail Score : {data['score']}")
    print(f"Feedback : {data['feedback']}")

    return {
        "score": data["score"],
        "feedback": data["feedback"]
    }

def improve_node(state: EmailState):

    prompt = EMAIL_IMPROVEMENT_PROMPT.format(
        subject=state["subject"],
        body=state["body"],
        feedback=state["feedback"],
        professor_name=state["professor_name"],
        research_area=state["research_area"]
    )

    response = safe_invoke(prompt)

    text = response.content

    if isinstance(text, list):
        text = text[0]["text"]

    text = text.replace("```json", "").replace("```", "").strip()

    data = json.loads(text)

    print("\nImproved Email Generated")

    return {
        "subject": data["subject"],
        "body": data["body"],
        "attempts": state["attempts"] + 1
    }

def router(state: EmailState):

    if state["score"] >= 87:
        print("Email approved.")
        return "end"

    if state["attempts"] >= 1:
        print("Maximum improvements reached.")
        return "end"

    print("Improving email...")
    return "improve"

workflow = StateGraph(EmailState)

workflow.add_node("draft", draft_node)
workflow.add_node("review", review_node)
workflow.add_node("improve", improve_node)

workflow.set_entry_point("draft")
workflow.add_edge("draft", "review")

workflow.add_conditional_edges(
    "review",
    router,
    {
        "improve": "improve",
        "end": END
    }
)

workflow.add_edge("improve", "review")

app = workflow.compile()

def run_writer_agent(state):
    return app.invoke(state)

if __name__ == "__main__":
    png = app.get_graph().draw_mermaid_png(
        draw_method=MermaidDrawMethod.API
    )

    with open("writer_agent_graph.png", "wb") as f:
        f.write(png)

    initial_state = {
        "student_name": "Vivek",
        "university": "IIT Bombay",
        "year": "Second Year",
        "skills": "Python, ROS2, Machine Learning",
        "projects": "Built a robotics simulator using ROS2 and Gazebo.",
        "achievements": "CPI 9.34",
        "attached":False,

        "professor_name": "Dr. XYZ",
        "professor_email": "xyz@iitb.ac.in",
        "lab_name": "Autonomous Systems Lab",
        "research_area": "Robotics and Motion Planning",
        "opportunity_description": "Research on Autonoums Vechicles",

        "subject": "",
        "body": "",
        "feedback": "",
        "score": 0,
        "attempts": 1,
    }

    result = app.invoke(initial_state)

    print("subject:", result["subject"])
    print("body:", result["body"])