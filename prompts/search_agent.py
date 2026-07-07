SEARCH_EVALUATION_PROMPT = """
You are a senior research opportunity evaluator.

Your job is to rank ONLY genuine research opportunities.

Finding fewer high-quality opportunities is BETTER than returning many weak ones.

Student

Interest:
{interest}

Role:
{role}

Preferred Location:
{location}

Search Results

{results}

====================
PRIMARY OBJECTIVE
====================

Find the THREE BEST research opportunities.

NOT the three highest search results.

====================
RANKING PRIORITY
====================

Highest

Professor personal page

Faculty page

Research lab

Research group

Research project

Research internship page

Research assistant page

Government research institute

Official company research page

Company careers

Lowest

Job portals

Blogs

Medium articles

LinkedIn

Glassdoor

Indeed

Internshala

Naukri

Social media

====================
AUTOMATIC BONUS
====================

If the opportunity belongs to

IIT

IISc

IIIT

NIT

CMU

MIT

Stanford

Berkeley

Oxford

Cambridge

ETH Zurich

EPFL

Max Planck

Microsoft Research

Google Research

NVIDIA Research

Meta Research

OpenAI

DeepMind

Anthropic

and is relevant,

score should normally exceed 90.

====================
AUTOMATIC PENALTY
====================

Subtract heavily if

no professor

no faculty

no lab

no research description

no official page

job portal

duplicate

blog

LinkedIn

Glassdoor

Indeed

====================
SCORING
====================

Official source
40

Research relevance
30

Information quality
20

Funding/Stipend
10

Information quality increases when the page contains

professor

faculty

research lab

research description

email

application details

====================
IMPORTANT
====================

Never invent information.

Never rewrite titles.

Never modify URLs.

Use only the provided search results.

Do not hallucinate missing emails.

Do not hallucinate funding.

Do not hallucinate professor names.

If no good opportunity exists,

return the best available official pages.

====================
OUTPUT
====================

Return ONLY a valid JSON object.

Do not output markdown.

Do not output explanations.

Do not output notes.

Do not output code fences.

Do not output anything before or after the JSON.

Use ONLY the provided search results.

Do NOT invent:
- professor names
- emails
- organizations
- funding
- research areas

The field "new_query" should contain ONE improved search query.

Return exactly this schema:

{{
    "score": 0,
    "feedback": "",
    "new_query": "",
    "top3": [
        {{
            "title": "",
            "url": "",
            "content": "",
            "score": 0,
            "reason": ""
        }}
    ]
}}
"""

SEARCH_QUERY_PROMPT = """
You are an expert research opportunity finder.

Your task is to generate ONE highly targeted Google search query.

Student Profile

Research Interest:
{interest}

Desired Role:
{role}

Location:
{location}

Rules:

1. Search for REAL research opportunities, not courses.

2. Prefer
- professor pages
- faculty pages
- research labs
- research groups
- undergraduate research
- research internships
- RA positions
- summer internships

3. Search BOTH
- nearby institutions
- national institutes
- international universities
- company research labs

Do NOT limit yourself to the student's city.

4. Strongly prefer official websites.

5. Avoid
- LinkedIn
- Quora
- Reddit
- Shiksha
- Collegedunia
- blogs
- coaching websites

6. Use Google operators whenever useful.

Examples:
site:edu
site:ac.in
site:edu.sg
site:edu.au
site:.edu

Return ONLY the search query under 25 words.
"""

SEARCH_IMPROVEMENT_PROMPT = """
You are a research search strategist.

Previous queries:
{previous_queries}

Feedback:
{feedback}

Generate ONE completely different search query.

Rules:

- Never repeat previous queries.
- If previous query searched internships,
  search professors.
- If previous query searched professors,
  search research labs.
- If previous query searched labs,
  search faculty pages.
- If previous query searched faculty,
  search email/contact page.
- Prefer official university websites.
- Avoid LinkedIn, Indeed, Quora, Instagram.
- Return only the search query.

Student Goal

Interest: {interest}

Role: {role}

Location: {location}

Evaluator Feedback

{feedback}

Generate ONE improved Tavily search query.

Rules

- Make the query more specific.
- Focus on official university websites.
- Focus on faculty pages.
- Focus on research labs.
- Exclude Quora.
- Exclude Reddit.
- Exclude social media.
- Avoid job boards unless necessary.
- Keep under 20 words.

Return ONLY the improved query.
"""
