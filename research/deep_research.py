import google.generativeai as genai
from datetime import datetime
from typing import List, Optional
from research.prompts import get_system_prompt
from research.model_utils import trim_prompt
from dotenv import load_dotenv
import os

load_dotenv()

def generate_feedback(query: str, num_questions: int = 3, model_name: str = "models/gemini-1.5-pro", api_key: Optional[str] = None) -> List[str]:
    genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
    system_prompt = get_system_prompt()
    full_prompt = f"""{system_prompt}

Given the following query from the user, ask some follow-up questions to clarify the research direction.
Return a maximum of {num_questions} questions, but feel free to return less if the original query is clear:

<query>{query}</query>
"""
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(full_prompt)
    return [line.strip("-• ").strip() for line in response.text.strip().split("\n") if line.strip()][:num_questions]

def deep_research(query, company_name='Unknown', depth=2, breadth=3, learnings=None, visited_urls=None, model_name="models/gemini-1.5-pro", api_key: Optional[str] = None):
    genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
    if learnings is None:
        learnings = []
    if visited_urls is None:
        visited_urls = []

    from modules.query_generator import generate_queries_with_gemini
    from modules.firecrawl_client import fetch_firecrawl_results
    from modules.summarizer import summarize_web_content

    queries = generate_queries_with_gemini(
        company_name=company_name,
        section_title=query,
        findings=learnings,
        model_name=model_name
    )[:breadth]

    all_learnings = learnings[:]
    all_urls = visited_urls[:]

    for serp_query in queries:
        try:
            results = fetch_firecrawl_results(serp_query, api_key=api_key)
            urls = [item["url"] for item in results if "url" in item]
            contents = [item["description"] for item in results if "description" in item]
            all_urls.extend(urls)

            print("🔥 SERP Query:", serp_query)
            print("📎 URL Ditemukan:", urls)
            print("📄 Jumlah konten:", len(contents))


            summary = summarize_web_content(contents, model_name=model_name)
            all_learnings.append(summary)

            if depth > 1:
                deeper = deep_research(
                    query=serp_query + "\n" + summary,
                    company_name=company_name,
                    depth=depth - 1,
                    breadth=max(1, breadth // 2),
                    learnings=all_learnings,
                    visited_urls=all_urls,
                    model_name=model_name,
                    api_key=api_key
                )
                all_learnings.extend(deeper["learnings"])
                all_urls.extend(deeper["visited_urls"])

        except Exception as e:
            all_learnings.append(f"[Error: {str(e)}]")

    return {
        "learnings": list(set(all_learnings)),
        "visited_urls": list(set(all_urls))
    }

def write_final_report(prompt: str, learnings: List[str], visited_urls: List[str], model_name: str = "models/gemini-1.5-pro", api_key: Optional[str] = None) -> str:
    genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
    context = "\n".join(f"<learning>\n{item}\n</learning>" for item in learnings)
    sources = "\n".join(f"- {url}" for url in visited_urls)

    full_prompt = f"""{get_system_prompt()}

You are an expert researcher.

Given the following prompt from the user, write a detailed section or report based on the learnings gathered below.

<prompt>{prompt}</prompt>

<learnings>
{context}
</learnings>
"""

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(trim_prompt(full_prompt))
    markdown = response.text.strip()
    return markdown + "\n\nSumber Referensi:\n" + sources

def write_final_answer(prompt: str, learnings: List[str], model_name: str = "models/gemini-1.5-pro", api_key: Optional[str] = None) -> str:
    genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
    context = "\n".join(f"<learning>\n{item}\n</learning>" for item in learnings)

    full_prompt = f"""{get_system_prompt()}

Given the following prompt, write a short and exact answer using the research learnings.

<prompt>{prompt}</prompt>

<learnings>
{context}
</learnings>
"""

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(trim_prompt(full_prompt))
    return response.text.strip()
