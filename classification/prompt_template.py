from enum import Enum

class Prompt(Enum):
    topic_prompt="""
    Through this abstract:
    - extract main scientific topic this talked about
    choices to select:
    ['Medicinal Chemistry', 'Nanotechnology', 'Electrochemistry', 'Chemical Engineering', 'Biochemistry', 'Physical Chemistry', 'Analytical Chemistry', 'Thermodynamics', 'Inorganic Chemistry', 'Organic Chemistry', 'Astrochemistry', 'Quantum Chemistry', 'Materials Science', 'Polymer Chemistry', 'Industrial Chemistry', 'Green Chemistry', 'Surface Chemistry', 'Solid State Chemistry', 'Supramolecular Chemistry', 'Photochemistry', 'Computational Chemistry', 'Environmental Chemistry', 'Theoretical Chemistry', 'Radiochemistry', 'electrical engineering]
    RETURN IN A LIST OF STRING FORMAT(Python)
    ANSWER CAN BE MAX 4 TOPICS
    {abstract}
    """
    RULE_CREATION = """
    You are an expert in patent classification and TRIZ principles.

    Your task:

    1. Step-by-step, reason which TRIZ principles best match the following analysis dimensions.
    2. Select the most appropriate TRIZ principle(s) without merging or combining different principles.
    3. Write your reasoning and selected principle(s) in clear points.

    Instructions:
    - Limit your full response to around 200 words.
    - For each selected TRIZ principle, include:
    - A dynamic definition based on the analysis.
    - A dynamic short example relevant to the context.
    - Only output TRIZ principles you find directly correlated to the provided description.
    - Do NOT invent new principles or combine multiple TRIZ rules into one.
    - output in example output
    
    Relevant TRIZ background knowledge from previous analysis:
    {analysis}
    """
    PROBLEM_EXTRACTION = """
    You are a TRIZ expert specializing in eco-solutions. Your task is:

    1. Extract the **primary problem** that the patent claims are trying to solve.
    2. Extract **secondary problems** if mentioned.
    3. Identify any **combinations** of primary problems.

    📝 Expected Output:
    - Format: A Python dictionary with keys: "primary", "secondary", "combination", each containing a list of strings.
    - Example:

    Input Patent Claims:
    {claims}
    
    Output format in Python dtype:
    Dict[List[str]]
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

    Patent Claims:
    {claims}
    
    "Output ONLY a valid JSON. No explanation or comments."
    
    Output a JSON object with the following fields:
    - uuid: a unique identifier for this patent
    - principles: a list of TRIZ principles detected in the claims
    """