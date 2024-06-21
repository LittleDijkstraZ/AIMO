import os
import re
import sys
import subprocess
import time

def naive_parse(answer):
    '''
    get the first consecutive numbers
    '''
    out = []
    start = False
    end = False
    answer = answer.split('answer')[-1] # limit the number to be obtained
    if len(answer)>20: 
        return ''
    for l in reversed(list(answer)):
        if l in '0123456789' and not end:
            start = True
            out.append(l)
        else:
            if start:
                end = True
        
    out = reversed(out)
    return ''.join(out)

def return_last_print(output, n=-1, grab_error=False):
    lines = output.strip().split('\n')
    if lines:
        if not grab_error:
            return lines[n]
        else: # jason
            error_locations = output.split(', line ')
            if error_locations:
                error_text = 'Traceback: line ' + error_locations[-1]
            return error_text
    else:
        return ""

def process_code(code, return_shell_output=False):
    
    def repl(match):
        if "real" not in match.group():
            return "{}{}".format(match.group()[:-1], ', real=True)')
        else:
            return "{}{}".format(match.group()[:-1], ')')
    code = re.sub(r"symbols\([^)]+\)", repl, code)

    if return_shell_output:
        code = code.replace('\n', '\n    ')
            # Add a try...except block
        # code = "\ntry:\n    from sympy import *\n{}\nexcept Exception as e:\n    print(e)\n    print('FAIL')\n".format(code)
        code = \
"""import traceback 
try:
    from sympy import *
    {}
except Exception as e:
    print(traceback.format_exc())
    print('FAIL')
""".format(code)
    
    if not return_shell_output:
        print(code)

    timestamp = str(time.time()).replace('.', '')
    code_file = f'{timestamp}_code.py'
    with open(code_file, 'w') as fout:
        fout.write(code)
    
    batcmd = 'timeout 7 ' + sys.executable + f' {code_file}'
    try:
        shell_output = subprocess.check_output(batcmd, shell=True).decode('utf8')
        return_value = return_last_print(shell_output, -1)
        print(shell_output)
        if return_shell_output:
            if return_value=='FAIL':
                CODE_STATUS = False
                return_value = return_last_print(shell_output, grab_error=True)
                if "not defined" in return_value:
                    return_value+='\nTry checking the formatting and imports'
            else:
                CODE_STATUS = True
            os.remove(code_file)
            return return_value, CODE_STATUS  
        code_output = round(float(eval(return_value))) % 1000
    except Exception as e:
        print(e,'shell_output')
        code_output = -1
    
    if return_shell_output:
        if code_output==-1:
            CODE_STATUS = False
        else:
            CODE_STATUS = True
        os.remove(code_file)
        return code_output, CODE_STATUS  
    
    os.remove(code_file)
    return code_output


def process_text_output(output):
    result = output    
    try:
        result_output = re.findall(r'\\boxed\{(\d+)\}', result)

        print('BOXED', result_output)
        if not len(result_output):
            result_output = naive_parse(result)
        else:
            result_output = result_output[-1]

        print('BOXED FINAL', result_output)
        if not len(result_output):
            result_output = -1
        else:
            result_output = round(float(eval(result_output))) % 1000
    
    except Exception as e:
        print(e)
        print('ERROR PARSING TEXT')
        result_output = -1
    
    return result_output

from IPython import display
from IPython.display import Javascript
import shutil
def save_and_copy_notebook(source_path, destination_path):
    # Save the notebook first
    try:
        display(Javascript('IPython.notebook.save_checkpoint();'))
        
        # Ensure the notebook is saved before copying
    except:
        pass
    import time
    time.sleep(3)  # Wait for a few seconds before copying

    # Copy the notebook
    shutil.copy2(source_path, destination_path)
    print(f"Notebook copied to {destination_path}")

def save_current_exp(folder_name, all_captured, final_submission, 
                     all_self_reflections = None,
                     notebooks=[]):

    os.makedirs(folder_name, exist_ok=True)
    for i, captured in enumerate(all_captured):
        with open(f'{folder_name}/output_{i}.txt', 'w') as fh:
            fh.write(captured)
        # change to md
        os.rename(f'{folder_name}/output_{i}.txt', f'{folder_name}/output_{i}.md')
        # if all_self_reflections:
        #     with open(f'{folder_name}/output_{i}_reflection.txt', 'w') as fh:
        #         fh.write(all_self_reflections)
        # os.rename(f'{folder_name}/output_{i}_reflection.txt', f'{folder_name}/output_{i}_reflection.md')
            

    all_captured_txt = '\n'.join(all_captured)
    with open(f'{folder_name}/all_outputs.txt', 'w') as fh:
        fh.write(all_captured_txt)
    
    
    final_submission = final_submission.reset_index(drop=True)
    final_submission.to_csv(f'{folder_name}/submission.csv', index=False)

    for notebook in notebooks:
        notebook_name = notebook.split('/')[-1]
        save_and_copy_notebook(notebook, f'{folder_name}/{notebook_name}')