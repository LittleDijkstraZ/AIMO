import traceback 
try:
    from sympy import *
    
    from sympy import symbols, Eq, solve, sqrt
    
    def calculate_distance_sum():
        k, l = symbols('k l', real=True)
    
        # equation for the difference of the roots
        equation1 = Eq(sqrt((-2*k)**2 - 4*k*(l - 4))/k, 6)
    
        # solve for l in terms of k
        l_value = solve(equation1, l)[0]
    
        # substitute the value of l into the equation for the sum of the squares of the distances
        distance_sum = ((-2)**2 + 16 + (8)**2 + 16).subs(l, l_value)
    
        return distance_sum
    
    result = calculate_distance_sum()
    print(result)
    
except Exception as e:
    print(traceback.format_exc())
    print('FAIL')
