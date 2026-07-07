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
langchain-groq
langchain-tavily
beautifulsoup4
requests
python-dotenv
pydantic
```

## Environment Variables

Create a `.env` file in the project root.

```env
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
```

## Gmail MCP Setup (Required)

This project uses the Gmail MCP server to send emails.

### Step 1: Install Node.js

Download and install Node.js from https://nodejs.org.

### Step 2: Create Google OAuth Credentials

- Create a Google Cloud project.
- Enable the **Gmail API**.
- Go to **APIs & Services → Credentials**.
- Create an **OAuth 2.0 Client ID** (Desktop App).
- Download the credentials file and rename it to:

```text
gcp-oauth.keys.json
```

### Step 3: Authenticate (One-Time Setup)

```bash
mkdir -p ~/.gmail-mcp
mv gcp-oauth.keys.json ~/.gmail-mcp/
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

Complete the Google sign-in in your browser. This only needs to be done once.

After authentication, simply run:

```bash
python main.py
```

The project will automatically connect to the Gmail MCP server and use your authenticated Gmail account to send emails.

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
