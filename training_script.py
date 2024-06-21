import re
from collections import defaultdict
from collections import Counter

import json
import time

import shutil
import os
from IPython.display import display, Javascript

from numpy.random import choice
import numpy as np
from IPython.utils import io
from tqdm.auto import tqdm

import argparse

from .utils import save_current_exp

import time
import torch

import gc
'''
accelerate execution a bit
'''

from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    AutoConfig,
    StoppingCriteria,
    set_seed
)

import transformers

import pandas as pd


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--trial_number', type=int, required=True)
    parser.add_argument('--config_dir', type=str, required=True)
    parser.add_argument('--gpu', type=int, required=True)
    

    trial_number = parser.parse_args().trial_number
    config_dir = parser.parse_args().config_dir
    gpu = parser.parse_args().gpu
    with open(config_dir) as f:
        config = json.load(f) 


    torch.backends.cuda.enable_mem_efficient_sdp(False)
    print(f"Transformers Version: {transformers.__version__}")
    set_seed(42)

    NOTEBOOK_START_TIME = time.time()


    DEBUG = False

    QUANT = False

    if QUANT:
        from transformers import BitsAndBytesConfig
        quantization_config = BitsAndBytesConfig(
            load_in_4bit = True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )

    USE_PAST_KEY = True

    NOTEBOOK_START_TIME = time.time()



    n_repetitions = config['n_repetitions'] # Original notebook had 22 but times out :(

    TOTAL_TOKENS = config['TOTAL_TOKENS'] # if PRIVATE else 512
    # TOTAL_TOKENS = 512 # if PRIVATE else 512
    test_df = pd.read_csv('./input/ai-mathematical-olympiad-prize/test.csv')
    submission_df = pd.read_csv('./input/ai-mathematical-olympiad-prize/sample_submission.csv')
    TIME_LIMIT = 500 * len(submission_df)


    MODEL_PATH = "./input/deepseek-math"#"/kaggle/input/gemma/transformers/7b-it/1"
    DEEP = True

    config = AutoConfig.from_pretrained(MODEL_PATH)
    config.gradient_checkpointing = True

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    
    device_i = 'cuda:0' # get first visible gpu

    device_map = [('model.embed_tokens', device_i),
                 ('model.layers.0', device_i),
                 ('model.layers.1', device_i),
                 ('model.layers.2', device_i),
                 ('model.layers.3', device_i),
                 ('model.layers.4', device_i),
                 ('model.layers.5', device_i),
                 ('model.layers.6', device_i),
                 ('model.layers.7', device_i),
                 ('model.layers.8', device_i),
                 ('model.layers.9', device_i),
                 ('model.layers.10', device_i),
                 ('model.layers.11', device_i),
                 ('model.layers.12', device_i),
                 ('model.layers.13', device_i),
                 ('model.layers.14', device_i),
                 ('model.layers.15', device_i),
                 ('model.layers.16', device_i),
                 ('model.layers.17', device_i),
                 ('model.layers.18', device_i),
                 ('model.layers.19', device_i),
                 ('model.layers.20', device_i),
                 ('model.layers.21', device_i),
                 ('model.layers.22', device_i),
                 ('model.layers.23', device_i),
                 ('model.layers.24', device_i),
                 ('model.layers.25', device_i),
                 ('model.layers.26', device_i),
                 ('model.layers.27', device_i),
                 ('model.layers.28', device_i),
                 ('model.layers.29', device_i),
                 ('model.norm', device_i),
                 ('lm_head', device_i)]

    device_map = {ii:jj for (ii,jj) in device_map}

    if QUANT:
        from transformers import BitsAndBytesConfig
        quantization_config = BitsAndBytesConfig(
            load_in_4bit = True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            device_map="sequential",
            torch_dtype="auto",
            trust_remote_code=True, 
            quantization_config=quantization_config,
            config=config
        )
    else:  
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            device_map=device_map,
            torch_dtype="auto",
            trust_remote_code=True,
            #quantization_config=quantization_config,
            config=config
        )
    
    pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype='auto',
    device_map=device_map,
    )
    
    from transformers import StoppingCriteriaList

    class StoppingCriteriaSub(StoppingCriteria):
        def __init__(self, stops = [], encounters=1):
            super().__init__()
            self.stops = [stop.to("cuda") for stop in stops]

        def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor):
            for stop in self.stops:
                last_token = input_ids[0][-len(stop):]
                if torch.all(torch.eq(stop,last_token)):
                    return True
            return False


    stop_words = ["```output", "```python", "```\nOutput" , ")\n```" , "``````output"] #,  
    stop_words_ids = [tokenizer(stop_word, return_tensors='pt', add_special_tokens=False)['input_ids'].squeeze() for stop_word in stop_words]
    stopping_criteria = StoppingCriteriaList([StoppingCriteriaSub(stops=stop_words_ids)])
    
    print(model.dtype, model.hf_device_map)


    code = \
    """Below is a math problem you are to solve (positive numerical answer):
    \"{}\"
    To accomplish this, first determine a sympy-based approach for solving the problem by listing each step to take and what functions need to be called in each step. Be clear so even an idiot can follow your instructions, and remember, your final answer should be positive integer, not an algebraic expression!
    Write the entire script covering all the steps (use comments and document it well) and print the result. After solving the problem, output the final numerical answer within \\boxed{}.

    Approach:"""


    # cot = \
    # """Below is a math problem you are to solve (positive numerical answer!):
    # \"{}\"
    # Analyze this problem and think step by step to come to a solution with programs. After solving the problem, output the final numerical answer within \\boxed{}.\n\n"""

    cot = \
    """Below is a math problem you are to solve (positive numerical answer!):
    \"{}\"
    Analyze this problem and think step by step to come to a solution. You may use python to assist with solving it. Output the final numerical answer within \\boxed{}.\n\n"""


    #     code = \
    # """
    # 假设你是IMO数学竞赛指导老师，以下是一个数学问题：
    # \"{}\"
    # \n
    # 1. 请先把这个问题翻译成中文。
    # 2. 接着，确定一个基于sympy，numpy，或者scipy的解题方法，列出每一步的操作。
    # 3. 请编对应的python脚本，并打印结果。
    # 4. 你的最终答案应该是正整数，而不是代数表达式！
    # 5. 解决问题后，在\\boxed{}中输出最终的数值答案。

    # 解：
    # """
    #     cot = \
    # """
    # 假设你是IMO数学竞赛指导老师，以下是一个数学问题：
    # \"{}\"
    # \n
    # 1. 请先把这个问题翻译成中文。
    # 2. 分析这个问题，明确问题的要求与条件，并确定解题思路。
    # 3. 尝试一步步解决这个问题，在必要的地方列式计算。 
    # 4. 必要时，可以通过python脚本来辅助计算。
    # 5. 解决问题后，在\\boxed{}中输出最终的数值答案。

    # 解：
    # """

    torch.cuda.empty_cache()
    gc.collect()

    prompt_options = [code,cot]
    temperature = config['temperature']
    top_p = config['top_p']

    temperature_coding = config['temperature_coding'] # code need to be strict, but still should have some creativity to get through difficult problems
    top_p_coding = config['top_p_coding']

    
    total_results = {}
    total_answers = {}
    best_stats = {}
    total_outputs = {}
    question_type_counts = {}
    starting_counts = config['starting_counts'] # 2:2, 2:3, 3:2, 2:4, 4:2 



    all_captured = []

    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    all_answers = {}



    final_submission = pd.DataFrame(columns=submission_df.columns)

    model_score = 0

    for i in range(len(test_df)):
        test, sample_submission = test_df.loc[i:i, :], submission_df.loc[i:i, :]
        # iterate through every problems in the environment
        # use a loop get the test row and the corresponding sample_submissions row

        total_answers_to_gen = 0
        valid_answers_generated = 0
        answers_matched = 0
        with io.capture_output() as captured: # i capture the printouts

            print(f"Solving problem {i} ...")
            TIME_SPENT = time.time() - NOTEBOOK_START_TIME

            if TIME_SPENT>TIME_LIMIT: # submit the prediction if no time is left
                sample_submission['answer'] = 0
                # env.predict(sample_submission)
                final_submission = pd.concat([final_submission, sample_submission])
                break
                
            for trial_j in tqdm(range(n_repetitions)):   

                problem = test['problem'].values[0]
                print(f"\n\n\nQUESTION {i} - {trial_j} - TIME_SPENT : {TIME_SPENT:.0f} secs")
                
                best, best_count = best_stats.get(i,(-1,-1))
                if best_count>np.sqrt(trial_j)+1:
                    print("SKIPPING CAUSE ALREADY FOUND BEST")
                    continue

                total_answers_to_gen += 1
                    
                outputs = total_outputs.get(i,[])
                text_answers, code_answers = question_type_counts.get(i,starting_counts)
                results = total_results.get(i,[])
                answers = total_answers.get(i,[])
                
                for _ in range(5): # clean the cache
                    torch.cuda.empty_cache()
                    gc.collect()
                    time.sleep(0.2)

                try:
                    ALREADY_GEN = 0
                    code_error = None
                    code_error_count = 0
                    code_output = -1
                    #initail_message = problem  + tool_instruction 
                    counts = np.array([text_answers,code_answers])

                    draw = choice(prompt_options, 1,
                                p=counts/counts.sum())

                    initail_message = draw[0].format(problem,"{}")            
                    prompt = f"User: {initail_message}"

                    current_printed = len(prompt)
                    print(f"{trial_j}_{prompt}\n")

                    model_inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
                    input_len = len(model_inputs['input_ids'][0])

                    generation_output = model.generate(**model_inputs, 
                                                    max_new_tokens=TOTAL_TOKENS-ALREADY_GEN,
                                                    return_dict_in_generate=USE_PAST_KEY,
                                                    do_sample = True,
                                                    temperature = temperature,
                                                    top_p = top_p,
                                                    num_return_sequences=1,
                                                    stopping_criteria = stopping_criteria)

                    if USE_PAST_KEY:
                        output_ids = generation_output.sequences[0]
                    else:
                        output_ids = generation_output[0]
                    decoded_output = tokenizer.decode(output_ids, skip_special_tokens=True)
                    print(f"{decoded_output[current_printed:]}\n")
                    current_printed += len(decoded_output[current_printed:])
                    cummulative_code = ""
                    
                    
                    stop_word_cond = False
                    for stop_word in stop_words:
                        stop_word_cond = stop_word_cond or (decoded_output[-len(stop_word):]==stop_word)
                        
                    
                    while (stop_word_cond) and (ALREADY_GEN<(TOTAL_TOKENS)):

                        if (decoded_output[-len("```python"):]=="```python"):
                            temperature_inner=temperature_coding
                            top_p_inner = top_p_coding
                            prompt = decoded_output
                        else:
                            temperature_inner=temperature
                            top_p_inner = top_p
                            try:
                                if (decoded_output[-len("``````output"):]=="``````output"):
                                    code_text = decoded_output.split('```python')[-1].split("``````")[0]
                                else:
                                    code_text = decoded_output.split('```python')[-1].split("```")[0]
                                

                                cummulative_code+=code_text
                                code_output, CODE_STATUS = process_code(cummulative_code, return_shell_output=True)
                                print('CODE RESULTS', code_output)
                                
                                # TODO: try to add the following prompt:
                                # Senario: CODE RESULTS 888.888888888889
                                # The result is not a positive integer, so we must have made a mistake somewhere. Let's go back and check our work.


                                if code_error==code_output:
                                    code_error_count+=1
                                else:
                                    code_error=code_output
                                    code_error_count = 0

                                if not CODE_STATUS:
                                    cummulative_code = cummulative_code[:-len(code_text)]

                                    if code_error_count>=1:
                                        print("REPEATED ERRORS")
                                        break

                            except Exception as e:
                                print(e)
                                print('ERROR PARSING CODE')
                                code_output = -1

                        
                            if code_output!=-1:
                                self_correcting_prompt = ''
                            
                                if (decoded_output[-len(")\n```"):]==")\n```"):
                                    prompt = decoded_output+'```output\n'+str(code_output)+'\n```\n'+self_correcting_prompt
                                else:
                                    prompt = decoded_output+'\n'+str(code_output)+'\n```\n' +self_correcting_prompt
                            else:
                                self_correcting_prompt = "Let's analyze and fix the error in our code, and then continue to solve the math problem."

                                prompt = decoded_output
                                cummulative_code=""



                        model_inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
                        ALREADY_GEN =  len(model_inputs['input_ids'][0])-input_len

                        if USE_PAST_KEY:
                            old_values = generation_output.past_key_values
                        else:
                            old_values = None

                        generation_output = model.generate(**model_inputs, 
                                                        max_new_tokens=TOTAL_TOKENS-ALREADY_GEN, 
                                                        return_dict_in_generate=USE_PAST_KEY,
                                                        past_key_values=old_values,
                                                        do_sample = True,
                                                        temperature = temperature_inner,
                                                        top_p = top_p_inner,
                                                        num_return_sequences=1, 
                                                        stopping_criteria = stopping_criteria)

                        if USE_PAST_KEY:
                            output_ids = generation_output.sequences[0]
                        else:
                            output_ids = generation_output[0]
                        decoded_output = tokenizer.decode(output_ids, skip_special_tokens=True)
                        print(f"\nINTERMEDIATE OUT :\n{decoded_output[current_printed:]}\n")
                        current_printed+=len(decoded_output[current_printed:])
                        
                        stop_word_cond = False
                        for stop_word in stop_words:
                            stop_word_cond = stop_word_cond or (decoded_output[-len(stop_word):]==stop_word)

                    if USE_PAST_KEY:
                        output_ids = generation_output.sequences[0]
                    else:
                        output_ids = generation_output[0]

                    raw_output = tokenizer.decode(output_ids[input_len:], skip_special_tokens=True)
                    #print(f"\n\nOutput :\n{raw_output}\n")                            
                    result_output = process_text_output(raw_output)
                    
                    try:
                        code_output = round(float(eval(code_output))) % 1000
                    except Exception as e:
                        print(e,'final_eval')
                        code_output = -1

                except Exception as e:
                    print(e,"5")
                    result_output, code_output = -1, -1

                valid_answer_obtained = False
                if code_output!=-1:
                    outputs.append(code_output)
                    code_answers+=1
                    valid_answer_obtained = True

                if result_output!=-1:
                    outputs.append(result_output)
                    text_answers+=1
                    valid_answer_obtained = True

                valid_answers_generated += int(valid_answer_obtained)

                if len(outputs) > 0:
                    occurances = Counter(outputs).most_common()
                    print(occurances)
                    if occurances[0][1] > best_count:
                        print("GOOD ANSWER UPDATED!")
                        best = occurances[0][0]
                        best_count = occurances[0][1]
                        # in case the following break happens while the best changes
                        # get the best in advance
                        best_stats[i] = (best, best_count) 
                    if occurances[0][1] > 3: # originally 5
                        print("ANSWER FOUND!")
                        break

                results.append(result_output)
                answers.append(code_output)
                
                best_stats[i] = (best, best_count) 
                question_type_counts[i] = (text_answers, code_answers)
                total_outputs[i] = outputs
                
                total_results[i] = results
                total_answers[i] = answers

                print("code_answers",code_answers-starting_counts[1],"text_answers",text_answers-starting_counts[0])
                if DEBUG:
                    break
                    
            print(f"Predicted best answer: {best_stats}")
            sample_submission['answer'] = best_stats[i][0]
            correct_answer = test['answer'].values[0]
            current_outputs = total_outputs.get(i, [])
            answers_matched = Counter(current_outputs).get(correct_answer, 0)
            best_matched = best_stats[i][0] == correct_answer # True when most common is correct

            model_score += best_matched * 100 + answers_matched/len(current_outputs) * 10 \
                + valid_answers_generated/total_answers_to_gen * 10

            # env.predict(sample_submission)
            final_submission = pd.concat([final_submission, sample_submission])

        cur_process = captured.stdout
        cur_process += '\n==sep==\n'
        with open(f'outputs_{i}.txt', 'w') as fh:
            fh.write(cur_process)
        all_captured.append(cur_process)

    model_score = model_score / len(test_df)


    print(json.dumps({'model_score': model_score}))

    temperatures = '|'.join(map(str, [temperature, top_p, temperature_coding, top_p_coding]))
    trial_number = str(trial_number)
    trial_number = '0'*(4-len(trial_number)) + trial_number
    folder_name = f'trial={trial_number}_T={int(TIME_SPENT)}_{n_repetitions}_{TOTAL_TOKENS}_{temperatures}'

    save_current_exp(folder_name, all_captured)
