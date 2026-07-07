import json

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from supervisor import run_supervisor
import asyncio
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

def ask(prompt):

    while True:

        value = input(prompt).strip()

        if value:
            return value

        print("\nInput cannot be empty. Please try again.\n")


PROFILE_PROMPT = """
You are given information about a student.

Convert it into the following JSON.

Return ONLY valid JSON with these keys:

student_name
university
year
skills
projects
achievements
interest
role
location
attached
search_state
search_result
search_attempts
selected_opportunity
best_opportunity
professor_email
writer_state
writer_result
approved
sent

Rules:

- Infer the location from the university.
- Infer the student's year if possible. Otherwise use "Unknown".
- Extract concise skills from the project description.
- Keep projects exactly as provided.
- Keep achievements exactly as provided.
- Interest should be the research field.
- Role should be the desired opportunity.
- attached should always be false.
- Do not hallucinate facts.
- Return ONLY JSON.
Output ONLY a valid JSON object. Do not include explanations, notes, 
markdown, code fences, comments, or any text before or after the JSON. 
The first character of the response must be {{ and the last character must be }}.

Student Information

Name:
{name}

University:
{university}

Research Interest:
{interest}

Desired Role:
{role}

Achievements:
{achievements}

Projects:
{projects}
"""


async def main():

    print("=" * 60)
    print("Research Internship Agent")
    print("=" * 60)

    name = ask("Name : ")

    university = ask("College / University : ")

    interest = ask(
        "Research Interest (Be specific): "
    )

    role = ask(
        "Desired Role (Research Internship / RA / etc): "
    )

    achievements = ask(
        "\nAchievements (CGPA, awards, competitions etc):\n"
    )

    projects = ask(
        "\nRelevant Projects (minimum one paragraph):\n"
    )

    prompt = PROFILE_PROMPT.format(
        name=name,
        university=university,
        interest=interest,
        role=role,
        achievements=achievements,
        projects=projects
    )

    response = safe_invoke(prompt)

    text = response.content

    if isinstance(text, list):
        text = text[0]["text"]

    text = text.replace("```json", "").replace("```", "").strip()

    print("\n========== RAW LLM OUTPUT ==========\n")
    print(repr(text))
    print("\n==================================\n")
    state = json.loads(text)
    state["attached"] = False

    state["search_state"] = {}
    state["search_result"] = {}
    state["search_attempts"] = 0

    state["selected_opportunity"] = {}
    state["best_opportunity"] = {}

    state["professor_email"] = ""

    state["writer_state"] = {}
    state["writer_result"] = {}

    state["approved"] = False
    state["sent"] = False

    state["professor_name"] = ""
    state["organization_name"] = ""
    state["research_area"] = ""


    print("\nProfile prepared successfully.\n")
    print(f"Searching for {state['interest']} opportunities...\n")

    await run_supervisor(state)


if __name__ == "__main__":
    asyncio.run(main())