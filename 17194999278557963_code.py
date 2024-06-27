import traceback 
try:
    from sympy import *
    
    from sympy import symbols, Eq, solve, simplify, sqrt
    
    def calculate_distance_sum():
        k, l = symbols('k l', real=True)
    
        # Equation (1): kx^2 - 2kx + l - 4 = 0
        equation1 = Eq(k**2 - 2*k*sqrt(l - 4) + l - 4, 0)
    
        # Equation (2): k^2 - k(l - 4) = 9
        equation2 = Eq(k**2 - k*(l - 4), 9)
    
        # Solve the system of equations
        solution = solve((equation1, equation2), (k, l))
    
        # Get the values of k and l from the solution
        k_value = solution[0][0]
        l_value = solution[0][1]
    
        # Calculate the coordinates of points A and B
        x1, y1 = sqrt(l_value - 4), 4
        x2, y2 = -sqrt(l_value - 4), 4
    
        # Calculate the sum of the squares of the distances from A and B to the origin
        distance_sum = simplify((x1**2 + y1**2) + (x2**2 + y2**2))
    
        return distance_sum
    
    result = calculate_distance_sum()
    print(result)
    
except Exception as e:
    print(traceback.format_exc())
    print('FAIL')
