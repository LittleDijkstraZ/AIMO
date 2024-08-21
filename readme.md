This Repo contains my attempts to the Kaggle Competition:

The original pipeline is adapted from:
- https://kaggle.com/code/xiaoz259/pure-rng/notebook
- https://www.kaggle.com/code/olyatsimboy/aimo-openmath-mistral-baseline
- https://www.kaggle.com/code/aatiffraz/prompt-prediction-w-mixtral-mistral7b-gemma-llama
- https://www.kaggle.com/code/thedrcat/aimo-mixtral-baseline

Quite some changes have been made to the original pipeline, resulting in [this notebook](./test_pipeline_4.ipynb) and [this script](./tuning_6_pool_script.py).

Few things I have tried:
- RAG on similar problems with answers [notebook](./test_pipeline_RAG.ipynb)
- Tuning via Optuna [script](./tuning_6_pool_script.py)
    - Prompt Strategies
    - Temperature