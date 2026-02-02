from core.chains import create_chain

class PuzzleClassifier:
    def __init__(self, llm):
        self.chain = create_chain(llm, "classifier.txt")
    
    def classify(self, puzzle: str, feedback: str = "") -> dict:
        return self.chain.invoke({"puzzle": puzzle, "feedback": feedback or "None"})
