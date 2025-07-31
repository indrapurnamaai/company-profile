import os
import google.generativeai as genai
from dotenv import load_dotenv
from modules.query_generator import generate_queries_with_gemini
from modules.firecrawl_client import fetch_firecrawl_results
from modules.summarizer import summarize_web_content
from research.model_utils import count_tokens

load_dotenv()

def get_google_api_key():
    try:
        import streamlit as st
        return st.secrets.get("GOOGLE_API_KEY")
    except:
        return os.getenv("GOOGLE_API_KEY")

def fetch_section_content(company_name, section_title, temperature=0.7, model_name="models/gemini-1.5-pro", depth=1, breadth=3):
    api_key = get_google_api_key()
    genai.configure(api_key=api_key)
    all_insights = []
    all_urls = []
    tokens_in = 0
    tokens_out = 0

    for _ in range(depth):
        try:
            queries = generate_queries_with_gemini(
                company_name=company_name,
                section_title=section_title,
                findings=all_insights,
                model_name=model_name
            )[:breadth]

            tokens_in += sum(count_tokens(q, model="cl100k_base") for q in queries)

            web_contents = []
            for query in queries:
                search_results = fetch_firecrawl_results(query, api_key=api_key)
                urls = [item.get("url", "") for item in search_results if "url" in item]
                texts = [item.get("description", "") for item in search_results if "description" in item]

                web_contents.extend(texts)
                all_urls.extend(urls)

            if web_contents:
                summary = summarize_web_content(web_contents[:3], model_name=model_name)
                all_insights.append(summary)
                tokens_out += count_tokens(summary, model="gpt-3.5-turbo")

        except Exception as e:
            all_insights.append(f"[Riset gagal: {e}]")

    research_context = "\n".join(f"- {insight}" for insight in all_insights)
    prompt = f"""
Kamu adalah seorang profesional senior management consultant yang ahli dalam membuat profil perusahaan.
Tulis bagian "{section_title}" untuk profil perusahaan "{company_name}".
Gunakan bahasa formal dan komprehensif.

Berikut hasil riset online yang relevan untuk digunakan sebagai referensi tambahan:
{research_context}

Tambahkan daftar sumber referensi aktual jika memungkinkan.
"""

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt.strip())
        final_text = response.text.strip()
        tokens_in += count_tokens(prompt, model="gpt-3.5-turbo")
        tokens_out += count_tokens(final_text, model="gpt-3.5-turbo")
        return final_text, list(set(all_urls)), tokens_in, tokens_out
    except Exception as e:
        return f"[GAGAL MENGAMBIL KONTEN: {e}]", [], tokens_in, tokens_out
