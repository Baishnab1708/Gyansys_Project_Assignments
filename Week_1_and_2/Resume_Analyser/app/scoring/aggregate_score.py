from app.config import settings
from app.schemas import ScoringSignals


def compute_aggregate_score(
    semantic_score: float,
    skill_match_score: float,
    experience_score: float,
    project_relevance_score: float
) -> float:

    weighted_sum = (
        settings.scoring.semantic_weight * semantic_score +
        settings.scoring.skill_weight * skill_match_score +
        settings.scoring.experience_weight * experience_score +
        settings.scoring.project_weight * project_relevance_score
    )
    
    return round(weighted_sum * 100, 2)


def create_scoring_signals(
    semantic: float,
    skill: float,
    experience: float,
    project: float
) -> ScoringSignals:
    return ScoringSignals(
        semantic_score=round(semantic, 3),
        skill_match_score=round(skill, 3),
        experience_score=round(experience, 3),
        project_relevance_score=round(project, 3)
    )
