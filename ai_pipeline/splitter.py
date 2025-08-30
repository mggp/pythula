import os
import json
import random

DIR_MAPPER = {
    "Data Processing": "data_processing",
    "Web/API Code": "web_api_code",
    "Algorithms/Logic": "algorithms_logic",
    "Machine Learning": "machine_learning"
}

def split_json_to_hf_dataset(
    input_json_path: str,
    output_dir: str,
    split_ratio: float = 0.8,
    seed: int = 42
):
    """
    Splits a JSON file into a folder hierarchy for Hugging Face datasets.

    Args:
        input_json_path (str): Path to the input JSON file.
        output_dir (str): Path to the output directory.
        split_ratio (float): Ratio of train data (e.g., 0.8 for 80% train, 20% test).
        seed (int): Random seed for reproducibility.

    Returns:
        None
    """
    # Load the JSON data
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Set the random seed for reproducibility
    random.seed(seed)

    # Shuffle the data
    random.shuffle(data)

    # Split the data into train and test sets
    split_index = int(len(data) * split_ratio)
    train_data = data[:split_index]
    test_data = data[split_index:]

    # Create the output directory structure
    for split_name, split_data in [("train", train_data), ("test", test_data)]:
        ouput_file = os.path.join(output_dir, split_name) + ".json"
        os.makedirs(os.path.dirname(ouput_file), exist_ok=True)
        
        with open(ouput_file, "w", encoding="utf-8") as snippet_file:
            snippet_file.write(json.dumps(split_data, indent=2))

    print(f"Dataset split and saved to {output_dir}")

# Example usage:
split_json_to_hf_dataset(
    input_json_path="code_dataset.json",
    output_dir="data",
    split_ratio=0.8,
    seed=42,
)