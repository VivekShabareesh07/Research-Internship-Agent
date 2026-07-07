from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_mcp_adapters.client import MultiServerMCPClient
from bs4 import BeautifulSoup

from searcher import run_search_agent
from writer import run_writer_agent

import requests
import re


mcp_client = None
send_tool = None


class SupervisorState(TypedDict):

    student_name: str
    university: str
    year: str

    skills: str
    projects: str
    achievements: str

    interest: str
    role: str
    location: str

    attached: bool

    search_state: dict
    search_result: dict

    search_attempts: int

    selected_opportunity: dict
    best_opportunity: dict

    professor_email: str
    professor_name: str

    research_area: str

    writer_state: dict
    writer_result: dict

    approved: bool
    sent:bool

def generate_search_state(state: SupervisorState):

    print("\nPreparing Search Agent...\n")

    return {

        "search_state": {

            "interest": state["interest"],

            "role": state["role"],

            "location": state["location"],

            "query": "",

            "results": [],

            "best_results": [],
            "previous_queries": [],

            "score": 0,

            "feedback": "",

            "attempts": 0

        }

    }

def search_node(state: SupervisorState):

    print("\nRunning Search Agent...\n")

    result = run_search_agent(

        state["search_state"]

    )
    best = {}

    if result["best_results"]:
        best = result["best_results"][0]

    return {
    "search_result": result,
    "best_opportunity": best,
    "search_attempts": (state.get("search_attempts") or 0) + 1
    }

def extract_contact_info(url):

    pages = ["","/people","/faculty","/team","/members","/contact","/contacts","/about","/join-us","/directory" ]

    for page in pages:

        try:

            html = requests.get(
                url + page,
                timeout=5,
                headers={
                    "User-Agent":"Mozilla/5.0"
                }
            ).text

            soup = BeautifulSoup(html,"html.parser")

            text = soup.get_text("\n")

            emails = re.findall(
                r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                text
            )
            BAD_DOMAINS = [
                "example.com",
                "test.com",
                "sample.com",
            ]

            BAD_EMAILS = [
                "contact@example.com",
                "admin@example.com",
                "example@example.com",
            ]

            if not emails:
                continue
            emails = sorted(emails,
                            key=lambda e: (
                            not any(x in e.lower() for x in [
                                "prof","faculty","cs","cse","ee","ece","iit",
                                "iiit","lab"
                            ]),
                            any(x in e.lower() for x in [
                                "info","contact","office","admin","support",
                                "admission","help","webmaster"
                            ])
                        )
                    )

            email=""
            for email in emails:
                if (email in BAD_EMAILS or any(email.endswith(domain) for domain in BAD_DOMAINS)):
                    email = ""
                else:
                    break
            if not email:
                continue

            for t in soup(["script", "style"]):
                t.extract()

            context = soup.get_text("\n")

            idx = context.find(email)

            if idx != -1:
                context = context[max(0, idx-600): idx+600]

            professor=""

            names = re.findall(
                r"(Professor\s+[A-Z][a-zA-Z.-]+\s+[A-Z][a-zA-Z.-]+|Dr\.?\s+[A-Z][a-zA-Z.-]+\s+[A-Z][a-zA-Z.-]+|[A-Z][a-zA-Z.-]+\s+[A-Z][a-zA-Z.-]+)",
                context
            )

            if names:
                professor = names[-1]

            BAD_WORDS = {
                "LAB", "TEAM", "FOLLOW", "HOME", "CONTACT",
                "RESEARCH", "GROUP", "MEMBER", "STAFF"
            }

            if any(word.upper() in professor.upper() for word in BAD_WORDS):
                professor = ""

            BAD_NAMES = ["Copyright","IIT","University","Institute","Research Office","Office","Administration","Admissions","Chair","Professorship","Department","Faculty","School","Campus","Home","Contact","Email","Privacy","Terms",]
            if any(x.lower() in professor.lower() for x in BAD_NAMES):
                professor = ""
        
            research=""

            lines=context.split("\n")

            keywords=[]

            for line in lines:

                if any(k in line.lower() for k in ["research","machine","vision","robot","ai","learning","language","graph","optimization","medical","nlp"]):
                    keywords.append(line.strip())

            research=" ".join(keywords[-3:])

            return {

                "email":email,

                "professor_name":professor,

                "research_area":research

            }

        except Exception:
            continue

    return None

def select_opportunity_node(state: SupervisorState):

    print("\nSelecting Opportunity...\n")
    opportunities = state["search_result"]["best_results"]

    for opportunity in opportunities:
        info = extract_contact_info(
            opportunity["url"]
        )
        if info:
            print(f"Info extracted: {info}")
            return {
            "selected_opportunity": opportunity,
            "professor_email": info["email"],
            "professor_name": info["professor_name"],
            "research_area": info["research_area"]
            }

    print("\nNo Email Found.")

    return {
        "selected_opportunity": {}
    }

def search_router(state: SupervisorState):

    if state.get("selected_opportunity"):
        return "writer"

    if state["search_attempts"] >= 2:
        print("\nNo public email found after two searches.")
        return "writer"

    return "search"

def generate_writer_state(state: SupervisorState):

    print("\nPreparing Writer Agent...\n")

    if state["selected_opportunity"]:
        opportunity = state["selected_opportunity"]
    else:
        opportunity = state["best_opportunity"]

    if not opportunity:
        raise ValueError("No opportunity available to generate email.")

    writer_state = {

        "student_name": state["student_name"],
        "university": state["university"],
        "year": state["year"],
        "skills": state["skills"],
        "projects": state["projects"],
        "achievements": state["achievements"],
        "professor_name":state["professor_name"],
        "organization_name": opportunity.get("organization_name", ""),
        "lab_name": opportunity.get("lab_name", ""),
        "research_area":state["research_area"],
        "personalization": opportunity.get("personalization", ""),
        "generic_mode": (
            opportunity.get("professor_name","") == "" and
            opportunity.get("organization_name","") == ""
        ),
        "opportunity_description": opportunity["content"],
        "opportunity_url": opportunity["url"],
        "attached": state["attached"],

        "subject": "",
        "body": "",
        "feedback": "",
        "score": 0,
        "attempts": 0

    }

    return {

        "writer_state": writer_state

    }

def writer_node(state: SupervisorState):

    print("\nRunning Writer Agent...\n")

    result = run_writer_agent(state["writer_state"])

    return {"writer_result": result}

def human_review_node(state: SupervisorState):
    email = state["writer_result"]
    print("\n" + "="*60)
    print("TO :")
    if state["professor_email"]:
        print(state["professor_email"])
    else:
        print("No public email found.")
    print()
    print("SUBJECT :")
    print(email["subject"])
    print()
    print("BODY :\n")
    print(email["body"])
    print("\n" + "="*60)
    if state["professor_email"]:
        choice = input("\nSend this email? (y/n): ")
    else:
        print("\nSorry, no public email was found.")
        print("I recommend checking this opportunity manually:\n")
        print(state["best_opportunity"]["title"])
        print(state["best_opportunity"]["url"])
        choice = "n"

    return {

        "approved":

        choice.lower() == "y"

    }

def review_router(state: SupervisorState):

    if state["approved"] and state["professor_email"]:
        return "send"

    return "cancel"

async def initialize_mcp():

    global mcp_client
    global send_tool

    mcp_client = MultiServerMCPClient(
        {
            "gmail": {
                "command": "npx",
                "args": [
                    "@gongrzhe/server-gmail-autoauth-mcp"
                ],
                "transport": "stdio",
            }
        }
    )

    tools = await mcp_client.get_tools()

    send_tool = next(
        t for t in tools
        if t.name == "send_email"
    )


async def send_node(state):

    print("\nSending Email...\n")

    try:

        result = await send_tool.ainvoke(
            {
                "to": [state["professor_email"]],
                "subject": state["writer_result"]["subject"],
                "body": state["writer_result"]["body"]
            }
        )

        print(result)

        return {
            "sent": True
        }

    except Exception as e:

        print("\nEmail sending failed.")
        print(e)

        return {
            "sent": False
        }

def cancel_node(state: SupervisorState):

    print("\nEmail Cancelled.")

    return {}

workflow = StateGraph(SupervisorState)

workflow.add_node(
    "generate_search_state",
    generate_search_state
)

workflow.add_node(
    "search",
    search_node
)

workflow.add_node(
    "find_email",
    select_opportunity_node
)

workflow.add_node(
    "generate_writer_state",
    generate_writer_state
)

workflow.add_node(
    "writer",
    writer_node
)

workflow.add_node(
    "review",
    human_review_node
)

workflow.add_node(
    "send",
    send_node
)

workflow.add_node(
    "cancel",
    cancel_node
)

workflow.set_entry_point(
    "generate_search_state"
)

workflow.add_edge(
    "generate_search_state",
    "search"
)

workflow.add_edge(
    "search",
    "find_email"
)

workflow.add_conditional_edges(

    "find_email",

    search_router,

    {

        "search":"search",

        "writer":"generate_writer_state"

    }

)

workflow.add_edge(

    "generate_writer_state",

    "writer"

)

workflow.add_edge(

    "writer",

    "review"

)

workflow.add_conditional_edges(

    "review",

    review_router,

    {

        "send":"send",

        "cancel":"cancel"

    }

)

workflow.add_edge(

    "send",

    END

)

workflow.add_edge(

    "cancel",

    END

)

app = workflow.compile()

async def run_supervisor(state):
    await initialize_mcp()
    return await app.ainvoke(state)

if __name__ == "__main__":

    png = app.get_graph().draw_mermaid_png(

        draw_method=MermaidDrawMethod.API

    )

    with open(

        "supervisor_graph.png",

        "wb"

    ) as f:

        f.write(png)

    print("Graph Saved.")