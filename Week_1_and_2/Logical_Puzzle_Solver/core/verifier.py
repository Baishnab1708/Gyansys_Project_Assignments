from core.chains import create_chain

class SolutionVerifier:
    def __init__(self, llm):
        self.chain = create_chain(llm, "verifier.txt")
    
    def verify(self, puzzle: str, classification: dict, strategy: str, 
               solution: dict, previous_feedback: str = "") -> dict:
        constraints_str = "\n".join(f"- {c}" for c in solution.get("constraints", []))
        return self.chain.invoke({
            "puzzle": puzzle,
            "puzzle_type": classification.get("puzzle_type", "unknown"),
            "difficulty": classification.get("difficulty", "unknown"),
            "strategy": strategy,
            "answer": solution.get("answer", ""),
            "constraints": constraints_str,
            "previous_feedback": previous_feedback or "None"
        })
