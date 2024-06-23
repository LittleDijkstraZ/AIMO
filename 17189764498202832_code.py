import traceback 
try:
    from sympy import *
    
    # try:
    #     sum_of_squares = distance**2 + (sqrt(k*solutions[0]**2 - 2*k*solutions[0] + l)**2 + (sqrt(k*solutions[1]**2 - 2*k*solutions[1] + l)**2)
    # except Exception as e:
    #     print(e)
    print(a)
except Exception as e:
    print(traceback.format_exc())
    print('FAIL')
