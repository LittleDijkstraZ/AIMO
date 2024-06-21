
from sympy import symbols, Eq, solve

def solve_function():
    n = symbols('n')
    f = symbols('f')

    # Define the given equations
    eq1 = Eq(f.subs(n, f.subs(n, f)), 8*n - 7)
    eq2 = Eq(f.subs(n, 2*n), 2*f + 1)

    # Solve the first equation for f(f(f(n)))
    eq1_solution = solve(eq1, f)[0]

    # Substitute f(n) in the second equation
    eq2 = eq2.subs(f, eq1_solution)

    # Solve the second equation for f(n)
    eq2_solution = solve(eq2, f)[0]

    # Substitute n = 100 in the solution for f(n)
    f_100 = eq2_solution.subs(n, 100)

    return f_100

result = solve_function()
print(result)
