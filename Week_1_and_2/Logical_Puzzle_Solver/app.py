import json
from config import Config
from models.llm_client import get_llm
from core.classifier import PuzzleClassifier
from core.strategy import StrategySelector
from core.solver import PuzzleSolver
from core.verifier import SolutionVerifier
from core.explainer import ExplanationBuilder


class PuzzlePipeline:
    
    def __init__(self):
        llm = get_llm()
        self.classifier = PuzzleClassifier(llm)
        self.strategy_selector = StrategySelector(llm)
        self.solver = PuzzleSolver(llm)
        self.verifier = SolutionVerifier(llm)
        self.explainer = ExplanationBuilder(llm)
        self.max_retries = Config.MAX_RETRIES
    
    def solve(self, puzzle: str, verbose: bool = False) -> dict:
        feedback = ""
        classification = None
        strategy = None
        solution = None
        verification = None
        
        for attempt in range(self.max_retries):
            if verbose: print(f"\n--- Attempt {attempt + 1}/{self.max_retries} ---\n")
            
            # Step 1: Classify (with feedback if reclassifying)
            classifier_feedback = feedback if verification and verification.get("issue_source") == "classifier" else ""
            if verbose: print("[1/6] Classifying...")
            classification = self.classifier.classify(puzzle, classifier_feedback)
            if verbose: print(f"      Type: {classification['puzzle_type']}, Difficulty: {classification['difficulty']}")
            
            # Step 2: Select strategy (with feedback if reselecting)
            strategy_feedback = feedback if verification and verification.get("issue_source") == "strategy" else ""
            if verbose: print("[2/6] Selecting strategy...")
            strategy_result = self.strategy_selector.select(puzzle, classification, strategy_feedback)
            strategy = strategy_result["strategy"]
            if verbose: print(f"      Strategy: {strategy}")
            
            # Step 3: Solve (with feedback if retrying)
            solver_feedback = feedback if verification and verification.get("issue_source") == "solver" else ""
            if verbose: print("[3/6] Solving...")
            solution = self.solver.solve(puzzle, strategy, solver_feedback)
            if verbose: print(f"      Answer: {solution['answer']}")
            
            # Step 4: Verify
            if verbose: print("[4/6] Verifying...")
            verification = self.verifier.verify(puzzle, classification, strategy, solution, feedback)
            
            if verification.get("is_valid", False):
                if verbose: print("      PASSED")
                break
            else:
                issue_source = verification.get("issue_source", "solver")
                feedback = f"Issue in {issue_source}: {verification.get('issue_details', '')}. Suggestion: {verification.get('suggestion', '')}"
                if verbose: 
                    print(f"      FAILED - Issue source: {issue_source}")
                    print(f"      Feedback: {feedback}")
        
        # Step 5: Explain
        if verbose: print("[5/6] Building explanation...")
        explanation = self.explainer.build(puzzle, solution, verification)
        
        # Step 6: Done
        if verbose: print("[6/6] Done")
        return {
            "puzzle_type": classification["puzzle_type"],
            "difficulty": classification["difficulty"],
            "strategy": strategy,
            "answer": explanation.get("final_answer", solution["answer"]),
            "explanation": {
                "assumptions": explanation.get("assumptions", []),
                "deductions": explanation.get("deductions", []),
                "verification": explanation.get("verification", "")
            }
        }


def main():
    puzzle = """
    Five people live in five different colored houses (Red, Blue, Green, Yellow, White).
    Each person has a different nationality (British, Swedish, Danish, Norwegian, German).
    Each person drinks a different beverage (Tea, Coffee, Milk, Beer, Water).
    Each person owns a different pet (Dog, Bird, Cat, Horse, Fish).
    
    Clues:
    1. The British person lives in the Red house.
    2. The Swedish person owns a Dog.
    3. The Danish person drinks Tea.
    4. The Green house is immediately to the left of the White house.
    5. The owner of the Green house drinks Coffee.
    6. The person who owns a Bird lives in the Yellow house.
    7. The owner of the middle house drinks Milk.
    8. The Norwegian lives in the first house.
    9. The German drinks Beer.
    10. The Norwegian lives next to the Blue house.
    11. The person who owns a Horse lives next to the one who owns a Cat.
    12. The person who drinks Water lives next to the one who owns a Bird.
    
    Question: Who owns the Fish?
    """
    
    print("=" * 50)
    print("Logical Puzzle Solver")
    print("=" * 50)
    print("\nPuzzle:", puzzle.strip()[:100] + "...")
    
    pipeline = PuzzlePipeline()
    result = pipeline.solve(puzzle, verbose=True)
    
    print("\n" + "=" * 50)
    print("RESULT")
    print("=" * 50)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
