import re


def clean_text(text: str) -> str:

    if not text:
        return ""
    
    text = text.replace("\x00", "")
    
    text = re.sub(r"[ \t]+", " ", text)
    
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    
    return text.strip()


def truncate_text(text: str, max_chars: int = 8000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."
