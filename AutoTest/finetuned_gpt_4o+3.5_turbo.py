import os
import argparse
import logging
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(
    api_key="YOUR_API_KEY"
)

def refine_prompt(user_prompt):
    """
    Refines the user-provided prompt using the fine-tuned GPT model.

    Args:
        user_prompt (str): The initial prompt describing the coding task.

    Returns:
        str: The refined prompt.
    """
    response = client.chat.completions.create(
        model="FineTuneGPT-model-name",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that enhances user prompts for better coding problem-solving. "
                           "Your task is to take a user's incomplete or vague description of a problem and return a "
                           "well-structured, detailed prompt, using technical terms, Chain-of-Thought reasoning, and "
                           "Meta Prompting. Include descriptions, examples, constraints, and optimization focus "
                           "(runtime and memory) without providing actual code."
            },
            {"role": "user", "content": user_prompt}
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message.content

def generate_code(refined_prompt, function_header):
    """
    Generates code based on the refined prompt and function header using GPT-3.5 Turbo.

    Args:
        refined_prompt (str): The refined prompt.
        function_header (str): The function header for the coding problem.

    Returns:
        str: The generated code.
    """
    combined_prompt = (
        f"{refined_prompt}\n\n"
        f"Here is the function header you must use as the basis of your solution:\n\n"
        f"{function_header}\n\n"
        f"Please generate the complete solution for this problem.  Please simply fill in the function header for me, no test cases or explanations, just Python3 code in your response"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": combined_prompt}],
        temperature=0,
        max_tokens=2048
    )
    return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description="Generate solutions using fine-tuned GPT model.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input file containing the user prompt.")
    parser.add_argument("-f", "--function-header", required=True, help="Path to the file containing the function header.")
    parser.add_argument("-o", "--output", required=True, help="Path to save the generated solution.")
    args = parser.parse_args()

    # Read input and function header
    with open(args.input, 'r', encoding='utf-8') as input_file:
        user_prompt = input_file.read().strip()

    with open(args.function_header, 'r', encoding='utf-8') as header_file:
        function_header = header_file.read().strip()

    # Step 1: Refine the user prompt
    refined_prompt = refine_prompt(user_prompt)

    # Step 2: Generate the code
    generated_code = generate_code(refined_prompt, function_header)

    # Step 3: Save the generated code
    with open(args.output, 'w', encoding='utf-8') as output_file:
        output_file.write(generated_code)

if __name__ == "__main__":
    main()
