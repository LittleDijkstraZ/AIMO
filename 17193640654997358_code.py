import traceback 
try:
    from sympy import *
    
    from sympy import symbols, solve, diff, N, Abs
    
    def solve_math_problem():
        u, v = symbols('u v', real=True)
    
        # Define the function f(u, v)
        f = 5*u**2 + 5*v**2
    
        # Define the constraint equation
        constraint = Abs(u + 1.6*v) + Abs(v - 0.8*u) - 40
    
        # Solve the constraint equation for v in terms of u
        solution = solve(constraint, v)
    
        # Substitute the solutions into f(u, v)
        f_substituted = [f.subs(v, sol) for sol in solution]
    
        # Find the minimum value of f(u, v) in the region defined by the constraint
        min_value = min([N(f.subs({u: u0, v: v0})) for u0 in range(-100, 100) for v0 in solution if constraint.subs({u: u0, v: v0}) < 0.1])
    
        return min_value
    
    result = solve_math_problem()
    print(result)
    
except Exception as e:
    print(traceback.format_exc())
    print('FAIL')
