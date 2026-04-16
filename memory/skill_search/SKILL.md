# Skill Search — 105K Skill Retrieval

> Semantically search for the most matching skill among 105K+ skill cards. Zero dependencies, built-in default API address, ready to use out of the box.

## Simplest Invocation

```python
import sys; sys.path.append('../memory/skill_search')
from skill_search import search

results = search("python send email")  # ⚠️ MUST use English queries, Chinese matching is extremely poor
for r in results:
    s = r.skill
    print(f"[{r.final_score:.2f}] {s.name} — {s.one_line_summary}")
    print(f"  key: {s.key}  category: {s.category}  tags: {s.tags[:3]}")
```

## API Signature

```python
search(query, env=None, category=None, top_k=10) -> list[SearchResult]
#  env: Auto-detected, generally leave empty
#  category: Optional filter, e.g., "devops"
#  top_k: Number of returns, default 10
```

## Return Structure

```
SearchResult
  .final_score    float     Composite score (0~1)
  .relevance      float     Semantic relevance
  .quality        float     Quality score
  .match_reasons  list[str] Match reasons
  .warnings       list[str] Warnings
  .skill          SkillIndex ↓

SkillIndex (Common Fields)
  .key              str       Unique ID/Path
  .name             str       Name
  .one_line_summary str       One-line summary
  .description      str       Detailed description
  .category         str       Category
  .tags             list[str] Tags
  .form             str       Form (sop/script/...)
  .autonomous_safe  bool      Is it autonomous safe
```

## CLI

```bash
python -m skill_search "python testing"
python -m skill_search "docker deployment" --category devops --top 5
python -m skill_search "git" --json
python -m skill_search --stats
python -m skill_search --env
```

## Configuration

| Item | Default | Description |
|---|---|---|
| API Address | `http://www.fudankw.cn:58787` | Can be overridden via Env var `SKILL_SEARCH_API` |
| API Key | None (Optional) | Env var `SKILL_SEARCH_KEY` |