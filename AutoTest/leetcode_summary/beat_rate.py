import pandas as pd
import os


def calculate_beat_rate(df1, df2, metric):
    """
    Calculate the beat rate between two DataFrames for a given metric.

    Args:
        df1 (pd.DataFrame): DataFrame for the first model.
        df2 (pd.DataFrame): DataFrame for the second model.
        metric (str): Column name for comparison (e.g., 'Runtime' or 'Memory').

    Returns:
        str: The beat rate as # of beats/# of comparisons and the percentage.
    """
    # Filter valid comparisons where both values are >= 0
    valid_comparisons = (df1[metric] >= 0) & (df2[metric] >= 0)

    # Perform the comparison and count beats
    beats = (df1.loc[valid_comparisons, metric] < df2.loc[valid_comparisons, metric]).sum()
    total_comparisons = valid_comparisons.sum()

    # Calculate percentage
    beat_percentage = (beats / total_comparisons * 100) if total_comparisons > 0 else 0

    return f"{beats}/{total_comparisons} ({beat_percentage:.2f}%)"


def main():
    # Define file paths
    baseline_path = "3.5_complexity.csv"
    finetuned_path = "finetuned_complexity.csv"
    other_path = "4o_3.5_complexity.csv"

    # Check if files exist
    if not all(map(os.path.exists, [baseline_path, finetuned_path, other_path])):
        print("One or more input files are missing.")
        return

    # Load the data
    baseline_df = pd.read_csv(baseline_path)
    finetuned_df = pd.read_csv(finetuned_path)
    other_df = pd.read_csv(other_path)

    # Calculate beat rates for finetuned vs. baseline
    runtime_beat_rate_baseline = calculate_beat_rate(finetuned_df, baseline_df, "Runtime")
    memory_beat_rate_baseline = calculate_beat_rate(finetuned_df, baseline_df, "Memory")

    # Calculate beat rates for finetuned vs. 4o_3.5
    runtime_beat_rate_comparison = calculate_beat_rate(finetuned_df, other_df, "Runtime")
    memory_beat_rate_comparison = calculate_beat_rate(finetuned_df, other_df, "Memory")

    # Print results
    print("Beat Rate Results:")
    print("\nFinetuned vs 3.5:")
    print(f"Runtime: {runtime_beat_rate_baseline}")
    print(f"Memory: {memory_beat_rate_baseline}")

    print("\nFinetuned vs 4o_3.5:")
    print(f"Runtime: {runtime_beat_rate_comparison}")
    print(f"Memory: {memory_beat_rate_comparison}")


if __name__ == "__main__":
    main()
