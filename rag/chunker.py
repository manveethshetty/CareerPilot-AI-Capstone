"""
Chunking logic for RAG.
Resumes are short documents, so we chunk by logical section (heuristic on
blank-line/heading boundaries) rather than fixed token windows, then fall
back to a sliding window for any oversized section.
"""
import re

SECTION_HEADINGS = [
    "education", "experience", "work experience", "projects", "skills",
    "technical skills", "certifications", "achievements", "extracurricular",
    "summary", "objective", "publications", "internships", "leadership",
]


def chunk_resume(text: str, max_words: int = 120, overlap: int = 20) -> list[dict]:
    """
    Returns a list of {"id": str, "text": str, "section": str} chunks.
    Tries to split on likely section headings first; falls back to a
    sliding window over the whole text if no headings are detected.
    """
    lines = text.split("\n")
    sections = []
    current_section = "general"
    current_lines = []

    def is_heading(line: str) -> bool:
        clean = line.strip().lower().strip(":")
        return clean in SECTION_HEADINGS or (
            len(clean.split()) <= 3 and clean in SECTION_HEADINGS
        )

    for line in lines:
        if is_heading(line):
            if current_lines:
                sections.append((current_section, "\n".join(current_lines)))
            current_section = line.strip().strip(":").lower()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_section, "\n".join(current_lines)))

    # Fallback: no headings detected at all
    if len(sections) <= 1:
        sections = [("general", text)]

    chunks = []
    chunk_id = 0
    for section_name, section_text in sections:
        words = section_text.split()
        if not words:
            continue
        if len(words) <= max_words:
            chunks.append({
                "id": f"chunk_{chunk_id}",
                "text": section_text.strip(),
                "section": section_name,
            })
            chunk_id += 1
        else:
            start = 0
            while start < len(words):
                window = words[start:start + max_words]
                chunks.append({
                    "id": f"chunk_{chunk_id}",
                    "text": " ".join(window).strip(),
                    "section": section_name,
                })
                chunk_id += 1
                start += max_words - overlap

    return chunks
