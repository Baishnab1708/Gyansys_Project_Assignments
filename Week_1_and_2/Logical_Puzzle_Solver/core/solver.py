from core.chains import create_chain

class PuzzleSolver:
    def __init__(self, llm):
        self.chain = create_chain(llm, "solver.txt")
    
    def solve(self, puzzle: str, strategy: str, feedback: str = "") -> dict:
        return self.chain.invoke({
            "puzzle": puzzle, 
            "strategy": strategy,
            "feedback": feedback or "None"
        })
