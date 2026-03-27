import re


class KeywordExtractor:
    """Extract normalized keywords from text for retrieval and ranking."""

    STOPWORDS = {
        "the",
        "and",
        "with",
        "for",
        "from",
        "that",
        "this",
        "have",
        "has",
        "are",
        "you",
    }

    @staticmethod
    def extract(text: str, limit: int = 15) -> list[str]:
        words = re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{1,}", text.lower())
        filtered = [w for w in words if w not in KeywordExtractor.STOPWORDS]
        unique: list[str] = []
        for token in filtered:
            if token not in unique:
                unique.append(token)
            if len(unique) >= limit:
                break
        return unique
