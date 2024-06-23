prompt_choices = [

"""
Below is a math problem you are to solve (positive numerical answer):
\"{}\"
To accomplish this, first determine a sympy-based approach for solving the problem by listing each step to take and what functions need to be called in each step. Be clear so even an idiot can follow your instructions, and remember, your final answer should be positive integer, not an algebraic expression!
Write the entire script covering all the steps (use comments and document it well) and print the result. After solving the problem, output the final numerical answer within \\boxed{}.

Assistant: 

Interesting, let's analyze step by step:""",

"""
Below is a math problem you are to solve (positive numerical answer!):
\"{}\"
Analyze this problem and think step by step to come to a solution with programs. After solving the problem, output the final numerical answer within \\boxed{}.

Assistant:""",

"""
Below is a math problem you are to solve (positive numerical answer!):
\"{}\"
Analyze this problem and think step by step to come to a solution with programs. After solving the problem, output the final numerical answer within \\boxed{}.

Assistant:

Here's the step by step solution:""",


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
Below is a math problem you are to solve (natural number answer):
\"{}\"
To accomplish this, first list the problem's constraints, conditions and related knowledge, and thens solve the problem step by step. Be clear so even an idiot can follow your instructions. After solving the problem, output the final numerical answer within \\boxed{}.

Assistant:""",


"""
Can you help me to solve the math problem below (natural number answer)?
\"{}\"
Analyze the problem and derive an algebraic expression for the solution. Implement this expression in a program, commenting your code for clarity. Verify the solution's correctness. Output the final numerical answer within \\boxed{}.

Assistant:

Certainly! let's derive the algebraic expression step by step:""",

"""
I have a math problem that I need help solving using Python and the sympy library. The problem is:

\"{}\"

To solve this, I need a step-by-step approach using sympy functions. Each step should be clearly documented with comments in the script so that anyone, regardless of their expertise level, can understand the solution process. Here's what I need:

1. Identify the type of problem and the mathematical principles involved.
2. List the sympy functions that will be used at each step.
3. Write a Python script with clear comments explaining each part of the solution.
4. Ensure the final output is a positive integer, and present it within a LaTeX formatted box, like so: \\boxed{}.

Assistant:

Great, let's break down the problem step-by-step:""",

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
