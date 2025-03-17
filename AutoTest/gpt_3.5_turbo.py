import argparse
from openai import OpenAI

# Initialize OpenAI client with your API key
client = OpenAI(
api_key="YOUR_API_KEY"
)

def generate_code_with_baseline(user_prompt, function_header):
    """
    Generates code using GPT-3.5 Turbo without prompt enhancement.

    Args:
        user_prompt (str): The user's input prompt.
        function_header (str): The function header to include in the prompt.

    Returns:
        str: The generated code.
    """
    # Combine user input and function header into the prompt
    combined_prompt = (
        f"{user_prompt}\n\n"
        f"Here is the function header you must use as the basis of your solution:\n\n"
        f"{function_header}\n\n"
        f"Please generate the complete solution for this problem. Please simply fill in the function header for me, no test cases or explanations, just Python3 code in your response."
    )

    # Send the prompt to GPT-3.5 Turbo
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": combined_prompt}],
        temperature=0,
        max_tokens=2048
    )

    # Extract the code from the response
    generated_code = response.choices[0].message.content
    return generated_code

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate baseline solutions using GPT-3.5 Turbo.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input file containing the problem description.")
    parser.add_argument("-f", "--function-header", required=True, help="Path to the file containing the function header.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output file for the generated solution.")
    args = parser.parse_args()

    # Read the user input
    with open(args.input, 'r', encoding='utf-8') as input_file:
        user_prompt = input_file.read().strip()

    # Read the function header
    with open(args.function_header, 'r', encoding='utf-8') as header_file:
        function_header = header_file.read().strip()

    # Generate the solution using the baseline approach
    generated_code = generate_code_with_baseline(user_prompt, function_header)
    print(f"Generated Code: {generated_code}")

    # Save the generated code to the output file
    with open(args.output, 'w', encoding='utf-8') as output_file:
        output_file.write(generated_code)

if __name__ == "__main__":
    main()
