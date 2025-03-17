import glob
import math
import os
import logging
import time
import argparse
import json
import pandas as pd
from datetime import datetime

id_map_table = {}


def ensure_cookies_exist():
    """Checks if the cookies file exists, if not, runs the login script."""
    cookies_path = "leetcode_cookies_csrftoken.json"
    if not os.path.exists(cookies_path):
        logging.info(f"{cookies_path} not found. Running login script.")
        os.system("python3 ./leetcode_login.py")
        if not os.path.exists(cookies_path):
            logging.error(f"Failed to generate {cookies_path}. Ensure login script runs correctly.")
            exit(1)
    else:
        logging.info(f"Cookies file {cookies_path} found.")


def generate_solution(user_input, function_header, model_path, solution_path):
    """
    Generate a solution using a specified model.

    Args:
        user_input (str): The user input prompt.
        function_header (str): The function header for the problem.
        model_path (str): Path to the model script (fine-tuned or baseline).
        solution_path (str): Path to save the generated solution.
    """
    temp_input_file = "temp_input.txt"
    temp_header_file = "temp_header.txt"

    # Save user input and function header to temporary files
    with open(temp_input_file, 'w', encoding='utf-8') as f:
        f.write(user_input)
    with open(temp_header_file, 'w', encoding='utf-8') as f:
        f.write(function_header)

    # Run the model script
    os.system(f"python3 \"{model_path}\" -i \"{temp_input_file}\" -f \"{temp_header_file}\" -o \"{solution_path}\"")

    # Remove temporary files
    os.remove(temp_input_file)
    os.remove(temp_header_file)


def generate_solutions(finetuned_model_path, baseline_model_path, other_model_path, test_file, solutions_path):
    """
    Generate solutions for problems listed in test.csv.

    Args:
        finetuned_model_path (str): Path to the fine-tuned model script.
        baseline_model_path (str): Path to the baseline model script.
        test_file (str): Path to the test.csv file.
        solutions_path (str): Directory to save the solutions.
    """
    logging.info("Generating solutions using models...")

    # Read the test.csv file
    df = pd.read_csv(test_file, header=None)
    df.columns = ['C1', 'C2', 'C3', 'C4']  # Assign appropriate column names

    # Create solution directories if they don't exist
    finetuned_solution_path = os.path.join(solutions_path, "finetuned")
    baseline_solution_path = os.path.join(solutions_path, "3.5")
    other_solution_path = os.path.join(solutions_path, "4o_3.5")
    os.makedirs(finetuned_solution_path, exist_ok=True)
    os.makedirs(baseline_solution_path, exist_ok=True)
    os.makedirs(other_solution_path, exist_ok=True)

    # Iterate over each row in the DataFrame
    for _, row in df.iterrows():
        question_id = row['C1']
        user_input = row['C3']
        function_header = row['C4']

        # Generate solutions for both models
        finetuned_output_path = os.path.join(finetuned_solution_path, f"{question_id}.py")
        baseline_output_path = os.path.join(baseline_solution_path, f"{question_id}.py")
        other_output_path = os.path.join(other_solution_path, f"{question_id}.py")

        generate_solution(user_input, function_header, finetuned_model_path, finetuned_output_path)
        generate_solution(user_input, function_header, baseline_model_path, baseline_output_path)
        generate_solution(user_input, function_header, other_model_path, other_output_path)

    logging.info("All solutions generated successfully.")


def verify_solutions(solutions_path, model_type, verify_path, skip_verify_exist):
    with open("leetcode_cookies_csrftoken.json", 'r', encoding='utf-8') as fi:
        cookies_csrftoken = json.loads(fi.read())
        logging.info(cookies_csrftoken)

    cookies = cookies_csrftoken['cookies']
    csrf_token = cookies_csrftoken['csrf_token']
    sol_path = ""
    model_verify_path = ""

    if model_type == "finetuned":
        sol_path = solutions_path + "/finetuned"
        model_verify_path = verify_path + "/finetuned"
    elif model_type == "baseline":
        sol_path = solutions_path + "/3.5"
        model_verify_path = verify_path + "/3.5"
    elif model_type == "other":
        sol_path = solutions_path + "/4o_3.5"
        model_verify_path = verify_path + "/4o_3.5"
    else:
        logging.warning("No such model type exists")
        return -1

    # Ensure the model_verify_path exists
    os.makedirs(model_verify_path, exist_ok=True)

    sol_list = []
    for file_path in glob.iglob(sol_path + '/**', recursive=True):
        if os.path.isfile(file_path) and ".py" in file_path:
            sol_list.append(file_path)

    if len(sol_list) == 0:
        logging.warning("No solutions to verify. Exiting.")
        return -1

    for sol_file_path in sol_list:
        question_id = os.path.basename(sol_file_path).replace(".py", "")
        logging.info(f"Checking question_id={question_id}")

        if skip_verify_exist and os.path.exists(model_verify_path + "/" + str(id) + ".py"):
            logging.info("id:" + str(id) + " verify result exist, skip")
            continue

        if int(question_id) not in id_map_table:
            logging.warning(f"Question ID {question_id} not found in id_map_table. Skipping.")
            continue

        slug = id_map_table[int(question_id)]["slug"]
        frontend_question_id = id_map_table[int(question_id)]["question_id"]

        url = f"https://leetcode.com/problems/{slug}/"
        output_path = os.path.join(model_verify_path, f"{question_id}.json")
        cmd = f"python3 ./verify_leetcode.py -u \"{url}\" -i \"{sol_file_path}\" -o \"{output_path}\"" \
              f" -q \"{frontend_question_id}\" -t \"{csrf_token}\" -c \"{cookies}\""
        # logging.info(f"Executing command: {cmd}")
        os.system(cmd)
        logging.info(f"Verification for question ID {question_id} done.")

        if not os.path.exists(output_path):
            logging.warning(f"Verification for question ID {question_id} failed.")
            time.sleep(3)
            continue
        time.sleep(10)


def read_question_id_slug():
    with open("leetcode_question_id_slug_mapping.json", 'r', encoding='utf-8') as f:
        question_id_slug_mapping = json.loads(f.read())
    for r in question_id_slug_mapping["question_id_mapping"]:
        id_map_table[r['frontend_question_id']] = {"question_id": r['question_id'], "slug": r['slug']}
    return 0

def stat_solutions(model_type, verify_path, summary_path, test_file):
    """Generates statistics for solutions based on the model type."""
    # Initialize scores
    score_summary = {"success": 0, "failed": 0, "success_rate": 0.0, "failed_rate": 0.0, "score": 0.0, "difficulty":{}, "detail": {}}
    final_score = {"total": 0, "success": 0, "failed": 0, "success_rate": 0.0, "failed_rate": 0.0, "detail": {}}

    # Set paths based on model type
    if model_type == "finetuned":
        verify_path = os.path.join(verify_path, "finetuned")
        readable_file_name = "finetuned_score_readable.json"
        summary_file_name = "finetuned_score_summary_readable.json"
    elif model_type == "baseline":
        verify_path = os.path.join(verify_path, "3.5")
        readable_file_name = "3.5_score_readable.json"
        summary_file_name = "3.5_score_summary_readable.json"
    elif model_type == "other":
        verify_path = os.path.join(verify_path, "4o_3.5")
        readable_file_name = "4o_3.5_score_readable.json"
        summary_file_name = "4o_3.5_score_summary_readable.json"
    else:
        logging.warning("Invalid model type provided: " + model_type)
        return -1

    # Read the test.csv file
    df = pd.read_csv(test_file, header=None)
    df.columns = ['C1', 'C2', 'C3', 'C4']  # Assign appropriate column names

    complexity = []

    # Process results
    for file_path in glob.glob(os.path.join(verify_path, "*.json")):
        if os.path.isfile(file_path):
            title_id = os.path.basename(file_path).replace(".json", "")
            with open(file_path, 'r', encoding='utf-8') as fi:
                verify_result = json.loads(fi.read())
                final_score["detail"][title_id] = verify_result

                if verify_result.get("status_msg") == "Accepted":
                    final_score["success"] += 1
                else:
                    final_score["failed"] += 1

                difficulty = df.loc[df['C1'] == int(title_id), 'C2'].iloc[0]

                if verify_result.get("status_msg") == "Accepted":
                    if difficulty not in score_summary["difficulty"]:
                        score_summary["difficulty"][difficulty] = 1
                    else:
                        score_summary["difficulty"][difficulty] += 1
                    if difficulty == "Easy":
                        score_summary["score"] += 1
                    if difficulty == "Medium":
                        score_summary["score"] += 2
                    if difficulty == "Hard":
                        score_summary["score"] += 3
                elif verify_result.get("status_msg") == "Wrong Answer":
                    result = verify_result.get("compare_result")
                    correct_ratio = result.count('1') / len(result)
                    if difficulty == "Easy":
                        score_summary["score"] += 1 * correct_ratio
                    if difficulty == "Medium":
                        score_summary["score"] += 2 * correct_ratio
                    if difficulty == "Hard":
                        score_summary["score"] += 3 * correct_ratio

                temp={}
                temp["Runtime"] = int(verify_result.get("status_runtime").replace(" ms", "").strip()) if verify_result.get("status_runtime") != "N/A" else -1
                temp["Memory"] = verify_result.get("memory") if verify_result.get("status_runtime") != "N/A" else -1

                complexity.append(temp)



                # Update status group details
                status_msg = verify_result.get("status_msg", "Unknown")
                if status_msg not in score_summary["detail"]:
                    score_summary["detail"][status_msg] = 1
                else:
                    score_summary["detail"][status_msg] += 1


    complexity = pd.DataFrame(complexity)
    if model_type == 'other':
        file_path = f'leetcode_summary/4o_3.5_complexity.csv'
    if model_type == 'baseline':
        file_path = f'leetcode_summary/3.5_complexity.csv'
    else:
        file_path = f'./leetcode_summary/{model_type}_complexity.csv'
    complexity.to_csv(file_path, index=False)

    # Calculate total and rate
    final_score["total"] = final_score["success"] + final_score["failed"]
    if final_score["total"] > 0:
        final_score["success_rate"] = final_score["success"] / final_score["total"]
        final_score["failed_rate"] = final_score["failed"] / final_score["total"]

    score_summary["success"] = final_score["success"]
    score_summary["failed"] = final_score["failed"]
    score_summary["success_rate"] = final_score["success_rate"]
    score_summary["failed_rate"] = final_score["failed_rate"]

    # Save the results
    os.makedirs(summary_path, exist_ok=True)
    with open(os.path.join(summary_path, readable_file_name), 'w', encoding='utf-8') as fo:
        json.dump(final_score, fo, indent=4)
    with open(os.path.join(summary_path, summary_file_name), 'w', encoding='utf-8') as fo:
        json.dump(score_summary, fo, indent=4)

    logging.info(f"Statistics for {model_type} model saved.")
    return 0


if __name__ == "__main__":
    now = datetime.now()

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-t", "--test-file", dest="test_file",
                        default="./test.csv",
                        help="Path to the test.csv file.")
    parser.add_argument("-a", "--finetuned-model-path", dest="finetuned_model_path", default="./finetuned_gpt_4o+3.5_turbo.py",
                        help="Path to the fine-tuned model script.")
    parser.add_argument("-b", "--baseline-model-path", dest="baseline_model_path", default="./gpt_3.5_turbo.py",
                        help="Path to the baseline model script.")
    parser.add_argument("-o", "--other-model-path", dest="other_model_path", default="./gpt_4o+3.5_turbo.py",
                        help="Path to the other comparison model script.")
    parser.add_argument("-s", "--solutions-path", dest="solutions_path", default="./leetcode_solutions",
                        help="Directory to save the generated solutions.")
    parser.add_argument("-v", "--verify-path", dest="verify_path", default="./leetcode_verify",
                        help="Directory to save verification results.")
    parser.add_argument("-sum", "--summary-path", dest="summary_path", default="./leetcode_summary",
                        help="Directory to save summary results.")
    parser.add_argument("-sve", "--skip-verify-exist", dest="skip_verify_exist", action='store_false',
                        help="Skip already verified solutions.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    ensure_cookies_exist()


    id_map_table = {}
    # Load the question ID to slug mapping
    read_question_id_slug()
    logging.info("Read index_url done.")


    # logging.info("generate_solutions start")
    # # Generate solutions
    # # Commented out the step to skip solution generation
    # generate_solutions(args.finetuned_model_path, args.baseline_model_path, args.other_model_path, args.test_file, args.solutions_path)
    # logging.info("generate_solutions done")

    # Verify solutions
    # verify_solutions(args.solutions_path, "finetuned", args.verify_path, args.skip_verify_exist)
    # verify_solutions(args.solutions_path, "baseline", args.verify_path, args.skip_verify_exist)
    # verify_solutions(args.solutions_path, "other", args.verify_path, args.skip_verify_exist)

    # Generate statistics
    # stat_solutions("finetuned", args.verify_path, args.summary_path, args.test_file)
    stat_solutions("baseline", args.verify_path, args.summary_path, args.test_file)
    stat_solutions("other", args.verify_path, args.summary_path, args.test_file)
    logging.info("stat_solutions done")

    logging.info(f"Total execution time: {datetime.now() - now}")

