
try:
    from sympy import *

    from sympy import symbols, Eq, solve
    
    def find_x_coordinates():
        x, k, l = symbols('x k l', real=True)
        equation = Eq(4, k*x**2 - 2*k*x + l)
        solutions = solve(equation, x)
        return solutions
    
    result = find_x_coordinates()
    print(result)
    
    from sympy import symbols, sqrt, solve
    
    def find_l_in_terms_of_k():
        k = symbols('k', real=True)
        x1 = (k - sqrt(k*(k - 4)))/k
        x2 = (k + sqrt(k*(k - 4)))/k
        distance = 6
    
        # Substitute x1 and x2 into the formula for the distance
        equation = 2*sqrt((x1 + x2)**2 - 4*x1*x2) - distance
    
        # Solve for l
        l = solve(equation, k)[0]
        return l
    
    l = find_l_in_terms_of_k()
    print(l)
    
except Exception as e:
    print(e)
    print('FAIL')
