import traceback 
try:
    from sympy import *
    
    def calculate_f_of_100():
        n = 100
        while True:
            # Apply the second condition of the function f
            n = 2 * n + 1
            # Check if n equals 199 (the value that will allow us to use the first condition of the function f)
            if n == 199:
                # Apply the first condition of the function f to find f(100)
                f_of_100 = 8 * 100 - 7
                break
        return f_of_100
    
    result = calculate_f_of_100()
    print(result)
    
except Exception as e:
    print(traceback.format_exc())
    print('FAIL')
