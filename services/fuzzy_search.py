import re

from rapidfuzz import fuzz


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\u0600-\u06FF\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def acronym(name: str) -> str:
    """مخفف حروف اول هر کلمه؛ مثلا 'Red Dead Redemption' -> 'rdr'"""
    words = normalize(name).split()
    return "".join(w[0] for w in words if w)


def score_game(query: str, name: str) -> float:
    q = normalize(query)
    n = normalize(name)
    if not q or not n:
        return 0.0

    scores = [
        fuzz.WRatio(q, n),
        fuzz.token_sort_ratio(q, n),
        fuzz.partial_ratio(q, n),
    ]

    ac = acronym(name)
    if ac:
        # وقتی کاربر مخفف/غلط تایپی می‌زنه (مثلا rdd به‌جای rdr) این باعث میشه بازی توی نتایج بیاد
        scores.append(fuzz.ratio(q, ac))

    return max(scores)


def rank_games(
    query: str,
    games: list[tuple[int, str]],
    limit: int = 10,
    threshold: int = 45,
) -> list[tuple[int, str]]:
    """
    games: لیست (appid, name) کش‌شده از استیم.
    خروجی: لیست (appid, name) مرتب‌شده از بیشترین شباهت به کمترین.
    """
    scored = ((appid, name, score_game(query, name)) for appid, name in games)
    filtered = [g for g in scored if g[2] >= threshold]
    filtered.sort(key=lambda g: g[2], reverse=True)

    seen_names: set[str] = set()
    result: list[tuple[int, str]] = []
    for appid, name, _score in filtered:
        key = name.lower()
        if key in seen_names:
            continue
        seen_names.add(key)
        result.append((appid, name))
        if len(result) >= limit:
            break

    return result
