from __future__ import annotations

import re
from pathlib import Path


def load_input(source: str) -> tuple[str, str]:
    if source.startswith("http://") or source.startswith("https://"):
        import httpx
        from bs4 import BeautifulSoup
        from markdownify import markdownify as html_to_markdown

        response = httpx.get(source, follow_redirects=True, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        text = html_to_markdown(str(soup.body or soup))
        return source, text

    path = Path(source)
    if path.exists():
        return str(path), path.read_text(encoding="utf-8")

    return "raw-text", source


def normalize_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.rstrip() for line in text.split("\n")]
    normalized = "\n".join(lines).strip()
    return normalized + "\n"


def extract_sections(markdown: str) -> list[tuple[int, str, str]]:
    sections: list[tuple[int, str, str]] = []
    current_level = 1
    current_title = "Introduction"
    buffer: list[str] = []

    for line in markdown.splitlines():
        if line.startswith("#"):
            if buffer:
                sections.append((current_level, current_title, "\n".join(buffer).strip()))
                buffer = []
            hashes, title = line.split(" ", 1) if " " in line else (line, line.lstrip("#"))
            current_level = len(hashes)
            current_title = title.strip() or "Untitled"
        else:
            buffer.append(line)

    if buffer:
        sections.append((current_level, current_title, "\n".join(buffer).strip()))

    return [section for section in sections if section[2]]
