# AI Research Opportunity Finder

An Agentic AI application built using LangGraph and LangChain that automatically finds research opportunities, extracts contact information, and generates personalized cold emails.

## Features

- Multi-agent workflow using LangGraph
- Intelligent search query generation
- Search refinement and ranking
- Contact information extraction
- Personalized cold email generation
- Email review and improvement loop

## Installation

Clone the repository

```bash
git clone https://github.com/VivekShabareesh07/Research-Internship-Agent.git
cd Research-Internship-Agent 
```

Create a virtual environment (optional)

```bash
python -m venv .venv
```

Activate it

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

## Required Packages

```text
langchain
langgraph
langchain-google-genai
langchain-groq
langchain-tavily
langchain-ollama
beautifulsoup4
requests
python-dotenv
pydantic
```

## Environment Variables

Create a `.env` file in the project root.

```env
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
```

## Run

```bash
python main.py
```

Follow the prompts to enter your profile. The agent will:

- Search for relevant research opportunities
- Rank the best opportunities
- Extract contact information
- Generate and refine a personalized cold email

## Tech Stack

- Python
- LangGraph
- LangChain
- Google Gemini
- Groq
- Tavily Search
- BeautifulSoup
- Requests
