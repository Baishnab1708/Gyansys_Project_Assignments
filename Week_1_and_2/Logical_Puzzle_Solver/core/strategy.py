from core.chains import create_chain

class StrategySelector:
    def __init__(self, llm):
        self.chain = create_chain(llm, "strategy_selector.txt")
    
    def select(self, puzzle: str, classification: dict, feedback: str = "") -> dict:
        return self.chain.invoke({
            "puzzle": puzzle,
            "puzzle_type": classification.get("puzzle_type", "deduction"),
            "difficulty": classification.get("difficulty", "medium"),
            "feedback": feedback or "None"
        })
