# CodingPromptRefinement

This project is to explore the possibility of helping amateur developers to achieve high-quality solutions in coding challenges by enhancing their input prompts
to GPT through a fine-tuned GPT-4o model.

## Usage

### Requirements

Make sure you have these libraries installed for code generation and initiate automation:
- Python 3.9 or higher installed
- OPENAI API KEY 
- Required libraries:
    - undetected_chromedriver
    - openai
    - webdriver-manager
    - selenium
    - pandas
    - requests

### Features
- Cookie Management: leetcode_login.py is used to generate LeetCode cookies and CSRF token and put them in ./leetcode_cookies_csrftoken.json
- Question ID Mapping: leetcode_id_mapper.py is used to extract question id from Leetcode webpage for automation purpose
- Solution Generation: leetcode_automation.py is used to trigger finetuned and baseline model to generate solutions for questions in ./test.csv
- Solution Verification: verify_leetcode.py is used to evaluated generated solutions by sending requests to corresponding questions on Leetcode plaform and collect results
- Result Processing: ./leetcode_summary/beat_rate.py is used to process the final result and generate statistics. 

### Command Line Arguments

you can run leetcode_automation.py with the following command line args:
```
`-t`,   `--test-file`: The question descriptions input to the GPT models for prompt engineering (default: ./test.csv)
`-a`,   `--finetuned-model-path`: The path to the finetuned GPT model script (default: ./finetuned_gpt_4o+3.5_turbo.py)
`-b`,   `--baseline-model-path`: The path to the baseline GPT model script (default: ./gpt_3.5_turbo.py)
`-o`,   `--other-model-path`: The path to the other comparison model script (default: ./gpt_4o+3.5_turbo.py)
`-s`,   `--solutions-path`: The path to the model generated solutions (default: ./leetcode_solutions)
`-v`,   `--verify-path`: Directory where verification results will be saved (default: ./leetcode_verify)
`-sum`, `--summary-path`: Directory where statistical summaries will be saved (default: ./leetcode_summary)
`-sve`, `--skip-verify-exist`: If provided, skips verifying solutions that already have verification results (default: store_false)
```

## Output

The tool will generate the following files:
- leetcode_solutions/4o_3.5/*.py (generated solutions using GPT-3.5 based on the enhanced prompt using baseline GPT-4o model)
- leetcode_solutions/finetuned/*.py (generated solutions using GPT-3.5 based on the enhanced prompt using finetuned GPT-4o model)
- leetcode_solutions/4o_3.5_score_readable.json (test results for each question using baseline model enhanced prompts)
- leetcode_summary/4o_3.5_score_summary_readable.json (summary of the test results using baseline model enhanced prompts)
- leetcode_solutions/finetuned_score_readable.json (test results for each question using finetuned model enhanced prompts)
- leetcode_summary/finetuned_score_summary_readable.json (summary of the test results using finetuned model enhanced prompts)
