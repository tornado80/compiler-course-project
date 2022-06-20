import os


def get_output_file_path(input_file_path: str, output_path: str):
    input_file_name = os.path.basename(input_file_path)
    return f"{output_path}/{input_file_name}"
