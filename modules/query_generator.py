# query_generator.py

import google.generativeai as genai

def generate_queries_with_gemini(company_name, section_title, findings=None, model_name="models/gemini-1.5-pro"):
    if findings is None:
        findings = []

    prompt = f"""Tugasmu adalah membuat query pencarian untuk riset online.
Topik: "{section_title}" dari perusahaan "{company_name}"

Temuan sebelumnya:
{chr(10).join(f"- {item}" for item in findings)}

Buat 3–5 query pencarian spesifik untuk mendapatkan informasi relevan dan aktual."""

    model = genai.GenerativeModel(model_name=model_name)
    response = model.generate_content(prompt)
    return [line.strip("- ").strip() for line in response.text.strip().split("\n") if line.strip()]
