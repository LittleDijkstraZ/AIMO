import optuna
from optuna.storages import JournalStorage, JournalFileStorage

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

from utils import *

import time
import datetime


import gc

import torch
import transformers
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    AutoConfig,
    StoppingCriteria,
    set_seed
)

import pandas as pd

def objective(trial=None, 
              tuning_dir=None,
              config_dir=None,
              prompt_choices=None,
              config_choices=None,
              all_seeds=[42, 666]):
    

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    
    if trial is not None:
        trial_number = trial.number
    if tuning_dir is not None:
        os.makedirs(tuning_dir, exist_ok=True)
        config_dir = f'{tuning_dir}/config_{timestamp}.json'


    if config_dir == None and prompt_choices == None:
        code = \
"""
Below is a math problem you are to solve (natural number answer):
\"{}\"
To accomplish this, first list the problem's constraints, conditions and related knowledge, and thens solve the problem step by step. Be clear so even an idiot can follow your instructions. After solving the problem, output the final numerical answer within \\boxed{}.

Assistant:"""
        cot = \
"""
Below is a math problem you are to solve (natural number answer!):
\"{}\"
Analyze the problem and think step by step to come to a solution with programs. After solving the problem, output the final numerical answer within \\boxed{}.

Assistant:"""


        config_dir = f'{tuning_dir}/config_{timestamp}.json'
        config = {
            'temperature': trial.suggest_float('temperature', 0.5, 1.25),
            'top_p': trial.suggest_float('top_p', 0.75, 1.0),
            'top_k': trial.suggest_int('top_k', 16, 96, step=16),
            'temperature_coding': trial.suggest_float('temperature_coding', 0.5, 1.25),
            'top_p_coding': trial.suggest_float('top_p_coding', 0.75, 1.0),
            'top_k_coding': trial.suggest_int('top_k_coding', 16, 96, step=16),

            # 'n_repetitions': trial.suggest_int('n_repetitions', 8, 16),
            'n_repetitions': 12,
            # 'TOTAL_TOKENS': trial.suggest_int('TOTAL_TOKENS', 1024, 2048),
            'TOTAL_TOKENS': 1600,
            'REFLECTION': False,
            'starting_counts': trial.suggest_categorical('starting_counts', [0, 1, 2]),
            # 'starting_counts': (3,2),
            'prompt_options': [code, cot],

        }
        starting_counts_options = [(4,1), (3,3), (1,4)]
        config['starting_counts'] = starting_counts_options[config['starting_counts']]

        with open(config_dir, "w") as f:
            json.dump(config, f, indent=2)
    elif prompt_choices is not None and config_choices is not None:

        base_config_dir = trial.suggest_categorical('config_choices', config_choices)
        config_index = config_choices.index(base_config_dir)
        with open(base_config_dir, 'r') as f:
            config = json.load(f)

        code = trial.suggest_categorical('prompt_option', prompt_choices)
        prompt_index = prompt_choices.index(code)
        cot = code
        config['prompt_options'] = [code, cot]
        config['n_repetitions'] = 16
        config['TOTAL_TOKENS'] = 1600
        print(config)


        with open(config_dir, "w") as f:
            json.dump(config, f, indent=2)
    else:
        with open(config_dir, "r") as f:
            config = json.load(f)
        trial_number = None
            



    for _ in range(5): # clean the cache
        torch.cuda.empty_cache()
        gc.collect()
        time.sleep(0.2)


    torch.backends.cuda.enable_mem_efficient_sdp(False)


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
    REFLECTION = config.get('REFLECTION', False)
    # TOTAL_TOKENS = 512 # if PRIVATE else 512
    # test_df = pd.read_csv('./input/ai-mathematical-olympiad-prize/test.csv')
    # submission_df = pd.read_csv('./input/ai-mathematical-olympiad-prize/sample_submission.csv')
    test_df = pd.read_csv('./test.csv')
    submission_df = pd.read_csv('./sample_submission.csv')
    
    # TIME_LIMIT = 500 * len(submission_df)
    TIME_LIMIT = 31500

    MODEL_PATH = "./input/deepseek-math"#"/kaggle/input/gemma/transformers/7b-it/1"
    DEEP = True

    model_config = AutoConfig.from_pretrained(MODEL_PATH)
    model_config.gradient_checkpointing = True

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
            config=model_config,
        )
    else:  
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            device_map=device_map,
            torch_dtype="auto",
            trust_remote_code=True,
            #quantization_config=quantization_config,
            config=model_config
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
    total_model_score = 0
    for cur_seed in all_seeds:

        
        for _ in range(5): # clean the cache
            torch.cuda.empty_cache()
            gc.collect()
            time.sleep(0.2)
        set_seed(cur_seed)

        NOTEBOOK_START_TIME = time.time()

        # print(model.dtype, model.hf_device_map)


        
        prompt_options = config['prompt_options']


        torch.cuda.empty_cache()
        gc.collect()

        temperature = config['temperature']
        top_p = config['top_p']
        top_k = config['top_k']


        temperature_coding = config['temperature_coding'] # code need to be strict, but still should have some creativity to get through difficult problems
        top_p_coding = config['top_p_coding']
        top_k_coding = config['top_k_coding']

        starting_counts = config['starting_counts'] # 2:2, 2:3, 3:2, 2:4, 4:2 
        temperatures = '|'.join(map(lambda x: f'{x:.02f}', [temperature, top_p, temperature_coding, top_p_coding]))
        
        total_results = {}
        total_answers = {}
        best_stats = {}
        total_outputs = {}
        question_type_counts = {}

        all_captured = []
        all_self_reflections = []

        final_submission = pd.DataFrame(columns=submission_df.columns)
        model_score = 0
        TOTAL_REFLECTION_TIME = 0

        total_prompt_correct_count = [0 for _ in range(len(prompt_options))]
        for i in tqdm(range(len(test_df))):
            test, sample_submission = test_df.loc[i:i, :], submission_df.loc[i:i, :]
            # iterate through every problems in the environment
            # use a loop get the test row and the corresponding sample_submissions row

            total_answers_to_gen = 0
            valid_answers_generated = 0
            answers_matched = 0
            self_reflection_list = []
            prompt_correct_count = [0 for _ in range(len(prompt_options))]
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
                    print(f"\n\n\n## QUESTION {i} - {trial_j} \n- TIME_SPENT : {TIME_SPENT:.0f} secs\n")
                    
                    best, best_count = best_stats.get(i,(-1,-1))
                    # if best_count>np.sqrt(trial_j)+1:
                    #     print("SKIPPING CAUSE ALREADY FOUND BEST")
                    #     continue

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
                        counts = np.array([text_answers,code_answers])

                        draw_index = choice(range(len(prompt_options)), 1, p=counts/counts.sum())[0]
                        draw = [prompt_options[draw_index]]
                        # draw = choice(prompt_options, 1,
                        #             p=counts/counts.sum())
                        initail_message = draw[0].format(problem,"{}")            
                        prompt = f"User:\n{initail_message}"

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
                                                    top_k = top_k,
                                                    num_return_sequences=1,
                                                    stopping_criteria = stopping_criteria,
                                                    pad_token_id=tokenizer.eos_token_id) #

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
                                top_k_inner = top_k_coding
                                prompt = decoded_output
                            else:
                                temperature_inner=temperature
                                top_p_inner = top_p
                                top_k_inner = top_k
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

                                        if code_error_count>=2: # more allowance
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
                                                        top_k = top_k_inner,
                                                        num_return_sequences=1, 
                                                        stopping_criteria = stopping_criteria,
                                                        pad_token_id=tokenizer.eos_token_id) # for open ended gen


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

                    # self reflection: jason
                    REFLECTION_TIME_START = time.time()
                    self_reflection_text = 'None'
                    if result_output == -1 or result_output != test['answer'].values[0]:
                        if REFLECTION:
                            self_reflection = f"\n\nUser: Thanks for trying. In fact, the correct answer is {test['answer'].values[0]}. Can you briefly summarize what you did wrong and what will you do differently if you are to try again?\n\nAssistant:"
                            prompt = decoded_output + self_reflection
                            
                            model_inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
                            input_tokens_len = len(model_inputs['input_ids'][0])
                            old_values = generation_output.past_key_values
                            self_reflection_output = model.generate(**model_inputs, 
                                                            max_new_tokens=128, 
                                                            return_dict_in_generate=USE_PAST_KEY,
                                                            past_key_values=old_values,
                                                            do_sample = True,
                                                            temperature = 0.9,
                                                            top_p = 1,
                                                            num_return_sequences=1, 
                                                            stopping_criteria = stopping_criteria,
                                                            
                                                            pad_token_id=tokenizer.eos_token_id) # for open ended gen
                            new_content = self_reflection_output.sequences[0][input_tokens_len:]
                            self_reflection_text = tokenizer.decode(new_content, skip_special_tokens=True)
                    else:
                        prompt_correct_count[draw_index] += 1
                    self_reflection_text = f'\n### Question {i} {trial_j} reflection:\n' + self_reflection_text
                    self_reflection_list.append(self_reflection_text)
                    REFLECTION_TIME_END = time.time() - REFLECTION_TIME_START
                    TOTAL_REFLECTION_TIME += REFLECTION_TIME_END

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

                cur_score = best_matched * 100 + answers_matched/max(len(current_outputs),1) * 10 \
                    + valid_answers_generated/max(total_answers_to_gen,1) * 10


                if str(i)==tuning_dir[-1]: # expert development
                    model_score += cur_score * 2
                else:
                    model_score += cur_score
                # env.predict(sample_submission)
                final_submission = pd.concat([final_submission, sample_submission])

            cur_process = captured.stdout
            cur_process += '\nprompt correctness:'+ str(prompt_correct_count)
            cur_reflections = ''.join(self_reflection_list)
            all_self_reflections.append(cur_reflections)
            try:
                cur_process += '\n##Score: ' + str(cur_score)
            except:
                pass
            cur_process += '\n\n## Self-Reflections\n'+cur_reflections
            cur_process += '\n---\n'

            with open(f'outputs_{i}.txt', 'w') as fh:
                fh.write(cur_process)
            all_captured.append(cur_process)
            total_prompt_correct_count = np.array(total_prompt_correct_count) + np.array(prompt_correct_count)

        TIME_SPENT = time.time() - NOTEBOOK_START_TIME - TOTAL_REFLECTION_TIME
        model_score = model_score / len(test_df)
        prompt_correct = total_prompt_correct_count.tolist()

        print(json.dumps({'model_score': model_score,
                    'prompt_correct': prompt_correct,}))
        if trial is not None:
            trial_number = str(trial_number)
            trial_number = '0'*(4-len(trial_number)) + trial_number
            if prompt_choices==None:
                folder_name = f'{tuning_dir}/{timestamp}_trial={trial_number}_{model_score:.1f}_{prompt_correct}_T={int(TIME_SPENT)}_{n_repetitions}_{TOTAL_TOKENS}_{temperatures}'
            else:
                
                folder_name = f'{tuning_dir}/{timestamp}_trial={trial_number}_{model_score:.1f}_{sum(prompt_correct)}_T={int(TIME_SPENT)}_{prompt_index}_{config_index}_{cur_seed}'
            save_current_exp(folder_name, all_captured, final_submission, notebooks=[config_dir])
        else:
            temperatures = '|'.join(map(str, [temperature, top_p, temperature_coding, top_p_coding]))
            folder_name = f'outputs/all_captured_{timestamp}_T={int(TIME_SPENT)}_{n_repetitions}_{TOTAL_TOKENS}_{temperatures}_{model_score:.2f}'
            save_current_exp(folder_name, all_captured, final_submission, notebooks=['./tuning_script.py', './utils.py'])
        total_model_score += model_score

        for _ in range(5): # clean the cache
            torch.cuda.empty_cache()
            gc.collect()
            time.sleep(0.2)
    return total_model_score/len(all_seeds) 
    # save_current_exp(folder_name, all_captured)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', type=int, required=True)    
    gpu = parser.parse_args().gpu
    os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu) # create its own world
    tuning_name = "tuning_match"
    storage_str = f"sqlite:///{tuning_name}.db"
    try:
        study = optuna.load_study(study_name=f"{tuning_name}", storage=storage_str)
    except:
        study = optuna.create_study(
            direction="maximize",
            storage=storage_str,  # Specify the storage URL here.
            study_name=f"{tuning_name}",
            pruner=optuna.pruners.MedianPruner(),
            load_if_exists=True,
        )
    from functools import partial

    from prompt_pool import prompt_choices
    import glob
    config_choices = glob.glob('./specialized_configs/*.json')

    objective = partial(objective, 
                        tuning_dir=f"{tuning_name}",
                        prompt_choices=prompt_choices,
                        config_choices=config_choices)
    study.optimize(objective, n_trials=120)