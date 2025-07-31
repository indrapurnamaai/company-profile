import tiktoken

def trim_prompt(prompt: str, max_tokens: int = 8000) -> str:
    if not prompt:
        return ""
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(prompt)
    if len(tokens) <= max_tokens:
        return prompt
    trimmed = encoding.decode(tokens[:max_tokens])
    return trimmed

def count_tokens(text: str, model: str = "cl100k_base") -> int:
    if not text:
        return 0
    try:
        encoding = tiktoken.get_encoding(model)
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
