#firecrawl_client.py

import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()  

def get_firecrawl_api_key():
    try:
        import streamlit as st
        return st.secrets.get("FIRECRAWL_API_KEY")
    except:
        return os.getenv("FIRECRAWL_API_KEY")

def fetch_firecrawl_results(query, api_key=None, max_results=5):
    api_key = api_key or get_firecrawl_api_key()
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY tidak ditemukan di environment, .env, atau secrets.")

    # Debug log
    print(f"🔥 FIRECRAWL: Menjalankan query → {query}")
    print(f"🔑 Menggunakan API key: {api_key[:6]}...")

    try:
        app = FirecrawlApp(api_key=api_key)
        search_result = app.search(query, limit=max_results)

        results = []
        for result in search_result.data:
            title = result.get("title", "Tanpa Judul")
            url = result.get("url", "")
            desc = result.get("description", "") or result.get("content", "")
            results.append({
                "title": title,
                "url": url,
                "description": desc
            })

            print(f"✅ {title} | {url}")

        print(f"📎 Total hasil: {len(results)}")
        return results

    except Exception as e:
        print(f"❌ FIRECRAWL Error saat query: {query}")
        print(e)
        return []
