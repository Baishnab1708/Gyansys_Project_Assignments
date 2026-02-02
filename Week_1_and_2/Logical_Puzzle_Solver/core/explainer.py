from core.chains import create_chain

class ExplanationBuilder:
    def __init__(self, llm):
        self.chain = create_chain(llm, "explainer.txt")
    
    def build(self, puzzle: str, solution: dict, verification: dict) -> dict:
        constraints_str = "\n".join(f"- {c}" for c in solution.get("constraints", []))
        return self.chain.invoke({
            "puzzle": puzzle,
            "answer": solution.get("answer", ""),
            "constraints": constraints_str,
            "verification_summary": verification.get("verification_summary", "Verified")
        })
