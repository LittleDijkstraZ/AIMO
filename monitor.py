import optuna
import time
while True:
    study = optuna.create_study(study_name='tuning_6_fewshot', storage='sqlite:///tuning_6_fewshot.db', load_if_exists=True)
    try:
        print(study.best_value, study.best_trial.number, len(study.get_trials()))
        print(study.best_params)
    except:
        print('waiting for the first trial')
    time.sleep(120)