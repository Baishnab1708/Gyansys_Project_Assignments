from typing import List, Set

def normalize_skill(skill: str) -> str:
    return skill.lower().strip().replace("-", " ").replace("_", " ")


def get_skill_variants(skill: str) -> Set[str]:
    """Get common variants of a skill name."""
    base = normalize_skill(skill)
    variants = {base}
    
    # Common aliases
    aliases = {
        "javascript": {"js", "ecmascript"},
        "typescript": {"ts"},
        "python": {"py"},
        "postgresql": {"postgres", "psql"},
        "mongodb": {"mongo"},
        "kubernetes": {"k8s"},
        "react": {"reactjs", "react.js"},
        "node": {"nodejs", "node.js"},
        "fastapi": {"fast api"},
        "machine learning": {"ml"},
        "artificial intelligence": {"ai"},
        "amazon web services": {"aws"},
        "google cloud platform": {"gcp"},
        "microsoft azure": {"azure"},
    }
    
    for key, vals in aliases.items():
        if base == key or base in vals:
            variants.add(key)
            variants.update(vals)
    
    return variants


def compute_skill_match_score(
    must_have_skills: List[str],
    nice_to_have_skills: List[str],
    candidate_skills: List[str],
    must_have_weight: float = 0.7,
    nice_to_have_weight: float = 0.3
) -> float:
    
    if not must_have_skills and not nice_to_have_skills:
        return 1.0  # No requirements = perfect match
    
    # Normalize candidate skills with variants
    candidate_variants = set()
    for skill in candidate_skills:
        candidate_variants.update(get_skill_variants(skill))
    
    # Count must-have matches
    must_have_matches = 0
    for skill in must_have_skills:
        skill_variants = get_skill_variants(skill)
        if skill_variants & candidate_variants:
            must_have_matches += 1
    
    must_have_score = must_have_matches / len(must_have_skills) if must_have_skills else 1.0
    
    # Count nice-to-have matches
    nice_matches = 0
    for skill in nice_to_have_skills:
        skill_variants = get_skill_variants(skill)
        if skill_variants & candidate_variants:
            nice_matches += 1
    
    nice_score = nice_matches / len(nice_to_have_skills) if nice_to_have_skills else 1.0
    
    # Weighted combination
    if must_have_skills and nice_to_have_skills:
        return (must_have_weight * must_have_score) + (nice_to_have_weight * nice_score)
    elif must_have_skills:
        return must_have_score
    else:
        return nice_score
