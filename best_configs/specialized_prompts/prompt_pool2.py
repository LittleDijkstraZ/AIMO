prompt_choices = [
    

# least to most prompting
"""
Below is a math problem you are to solve (positive numerical answer):
\"{}\"

To accomplish this:
- Decompose the problem into subproblems and analyze each of them step by step.
- Combine the solutions to the subproblems to solve the original problem.
- Output the result within \\boxed{}.

Assistant:""",

"""
Below is a math problem you are to solve (positive numerical answer!):
\"{}\"
Analyze this problem and think step by step to come to a solution with programs. After solving the problem, output the final numerical answer within \\boxed{}.

Assistant:""",


"""
Below is a math problem you are to solve (positive numerical answer):
\"{}\"

To accomplish this:
- List the variables and known values from the problem.
- Outline the steps using sympy to solve the problem:
  * Identify the sympy functions required for each step.
  * Implement these functions step-by-step, commenting each line for clarity.
- Calculate the final answer and verify it's a positive integer.
- Output the result within \\boxed{}.

Assistant:

Interesting, let's analyze step by step:""",


"""
Question (hint: positive numerical answer):
\"{}\"
Please put your final solution into \\boxed{}.

Step-by-step Solution:""",

"""
Solve the following problem with a Python Script (positive numerical answer):
\"{}\"
Write comments to indicate the steps you take. Please put your final solution into \\boxed{}.

Assistant:

Approach:""",

]
