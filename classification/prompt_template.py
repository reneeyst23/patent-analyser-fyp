from enum import Enum

class Prompt(Enum):
    RULE_CREATION = """
    You are an expert in patent classification and TRIZ principles. 
    CAPPED AROUND 200 WORDS
    Based on the following contexts, create a dynamic rule on 40 principles with this format (points, with dynamic definition, and dynamic short examples)
    DON'T MERGE OR COMBINE ANY TRIZ PRINCIPLE
    ONLY OUTPUT TRIZ PRINCIPLE YOU THINK CORRELATE WITH THIS DESCRIPTION.

    Relevant TRIZ background knowledge from previous analysis:
    {analysis}
    
    
    """
    PROBLEM_EXTRACTION = """
    You are a TRIZ expert, based on the instruction I give you, do this:
    Instruction: extract primary problem from patent claims related to eco-solutions, what's this patent trying to solve
        example: input: The invention involves a process for improving the energy efficiency of solar panels by reducing material waste during production
                 output: Improve the energy efficiency of solar panels by minimizing material waste during production.
    Output: descriptive points of primary and secondary problems, combination of different primary problems
    Patent Claims:
    {claims}
    """
    
    PROBLEM_ANALYSIS = """
    You are a TRIZ expert, based on the instruction I give you, do this:
    Break the problem statement down into specific sustainability aspect
    Focus on different dimension such as:
    Type of resources involved (object being manipulated)
    How it's manipulated (e.g reduction, optimization, shape changes, material changes)
    Problem points:
    {problems}
    
    reasoning in certain subjects: 
    {reasoning_trace}
    
    Output: points of different dimensions being used
    """
    FINAL_CLASSIFICATION = """
    You are a TRIZ expert. Based on the abstract and claims below, classify the invention using TRIZ 40 principles.
    Don't replicate the same principles, keep it as concise as possible.
    
    Dynamic Rule:
    {dynamic_rule}

    Patent Abstract:
    {abstract}

    Patent Claims:
    {claims}
    
    "Output ONLY a valid JSON. No explanation or comments."
    
    Output a JSON object with the following fields:
    - uuid: a unique identifier for this patent
    - principles: a list of TRIZ principles detected in the claims
    """