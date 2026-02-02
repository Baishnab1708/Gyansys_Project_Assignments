"""
Experience Score - curve-based scoring for experience fit.
"""
import math


def compute_experience_score(
    candidate_years: float,
    min_required: float,
    max_required: float = None,
    tolerance: float = 2.0
) -> float:
    """
    Compute experience fit score with penalties for under/over-qualification.
    
    Uses a bell curve centered on the ideal range.
    
    Args:
        candidate_years: Candidate's years of experience
        min_required: Minimum required years
        max_required: Maximum preferred years (if None, uses min + 5)
        tolerance: Years of tolerance outside range (default 2)
        
    Returns:
        Experience score (0-1)
    """
    if max_required is None:
        max_required = min_required + 5  # Default range
    
    # Perfect fit within range
    if min_required <= candidate_years <= max_required:
        return 1.0
    
    # Under-qualified penalty (steeper)
    if candidate_years < min_required:
        gap = min_required - candidate_years
        # Exponential decay - more severe penalty for larger gaps
        return max(0.0, math.exp(-0.5 * (gap / tolerance) ** 2))
    
    # Over-qualified penalty (gentler)
    if candidate_years > max_required:
        gap = candidate_years - max_required
        # Gentler decay - being overqualified is less of an issue
        return max(0.3, math.exp(-0.3 * (gap / tolerance) ** 2))
    
    return 0.5  # Fallback
