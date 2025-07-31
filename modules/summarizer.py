#summarizer.py

import google.generativeai as genai

def summarize_web_content(contents, model_name="models/gemini-1.5-pro"):
    prompt = f"""Berikut adalah hasil riset online terkait topik perusahaan:

{chr(10).join(contents)}

Buat ringkasan singkat, highlight penting, dan informasi yang relevan."""

    model = genai.GenerativeModel(model_name=model_name)
    response = model.generate_content(prompt)
    return response.text.strip()
