import traceback 
try:
    from sympy import *
    # print('done')
    print('done')
    
except Exception as e:
    print(traceback.format_exc())
    print('FAIL')
