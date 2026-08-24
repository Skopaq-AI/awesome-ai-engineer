from typing import List, Dict, Any, Optional

class PromptSignature:
    """Declarative signature defining input fields, instruction, and output fields."""
    def __init__(self, name: str, instruction: str, inputs: List[str], outputs: List[str]):
        self.name = name
        self.instruction = instruction
        self.inputs = inputs
        self.outputs = outputs
        self.demos: List[Dict[str, str]] = []

    def format_prompt(self, input_values: Dict[str, str]) -> str:
        prompt_lines = [f"Instruction: {self.instruction}\n"]
        
        # Add few-shot demonstrations if compiled
        if self.demos:
            prompt_lines.append("--- Demonstrations ---")
            for d in self.demos:
                for k in self.inputs:
                    prompt_lines.append(f"{k}: {d.get(k, '')}")
                for k in self.outputs:
                    prompt_lines.append(f"{k}: {d.get(k, '')}")
                prompt_lines.append("")
            prompt_lines.append("--- Task ---")

        for k in self.inputs:
            prompt_lines.append(f"{k}: {input_values.get(k, '')}")
        for k in self.outputs:
            prompt_lines.append(f"{k}:")
            
        return "\n".join(prompt_lines)

class MultiHopPipeline:
    """Declarative multi-step pipeline: (1) Query Plan -> (2) Evidence Extract -> (3) Synthesis."""
    def __init__(self):
        self.plan_sig = PromptSignature(
            "QueryPlan",
            "Decompose complex query into sub-questions.",
            ["query"],
            ["sub_questions"]
        )
        self.solve_sig = PromptSignature(
            "SolveAndVerify",
            "Synthesize verified answer with citations.",
            ["sub_questions", "context"],
            ["Answer"]
        )

    def forward(self, query: str, context: str = "") -> Dict[str, str]:
        # Step 1: Format and simulate plan
        plan_prompt = self.plan_sig.format_prompt({"query": query})
        sub_q = f"1. Analyze background of '{query}'. 2. Synthesize architectural solution."
        
        # Step 2: Format and simulate solve
        solve_prompt = self.solve_sig.format_prompt({"sub_questions": sub_q, "context": context})
        answer = f"Answer: Based on verified decomposition, the optimal approach to '{query}' leverages modular pipeline design."
        
        return {
            "query": query,
            "plan_prompt": plan_prompt,
            "sub_questions": sub_q,
            "solve_prompt": solve_prompt,
            "prediction": answer
        }
