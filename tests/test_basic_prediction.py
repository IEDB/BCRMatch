import datetime
import unittest
import tensorflow as tf
tf.random.set_seed(42)

import math
import os
import pandas as pd
import shutil
import subprocess
import sys
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_directory)
from io import StringIO


def find_root_dir(start_dir=None, anchor_files=None):
    """Find the app root directory by looking for known anchor files."""
    if start_dir is None:
        start_dir = os.getcwd()  # Default to the current working directory
    
    if anchor_files is None:
        anchor_files = ['LICENSE']
    
    # Normalize to absolute path
    current_dir = os.path.abspath(start_dir)
    
    # Traverse up the directory tree until an anchor file is found or root is reached
    while current_dir != os.path.dirname(current_dir):
        # Check for anchor files in the current directory
        for anchor in anchor_files:
            if os.path.isfile(os.path.join(current_dir, anchor)) or os.path.isdir(os.path.join(current_dir, anchor)):
                return current_dir  # Return the directory where the anchor file is found

        # Check for anchor files in child directories
        for root, dirs, files in os.walk(current_dir):
            for anchor in anchor_files:
                if anchor in dirs or anchor in files:
                    return root  # Return the child directory where the anchor file is found

        current_dir = os.path.dirname(current_dir)  # Move up one level
    
    # If no anchor file is found, return None or raise an error
    return None


def delete_folders_with_prefix(root_dir, prefix="9999"):
    """Recursively delete folders that start with the specified prefix."""
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):  # topdown=False ensures we remove subfolders first
        for dirname in dirnames:
            if dirname.startswith(prefix):  # Check if the folder starts with the prefix
                folder_to_remove = os.path.join(dirpath, dirname)
                print(f"Deleting folder: {folder_to_remove}")
                shutil.rmtree(folder_to_remove)  # Remove the folder and its contents


class TestBasicPrediction(unittest.TestCase):
    app_dir = find_root_dir()
    python_path = sys.executable
    test_dir = f'{app_dir}/tests'
    example_dir = f'{test_dir}/examples-a'
    output_file_to_delete = ''  

    def test_tsv_prediction_output(self):
        """Test prediction using TSV input and compare output with reference file."""
        output_file = f"{self.test_dir}/bcrout-test.csv"
        reference_file = f"{self.test_dir}/bcrout.csv"
        self.output_file_to_delete = output_file

        # Run prediction with TSV input
        command = [
            self.python_path,
            f"{self.app_dir}/run_bcrmatch.py",
            "-i", f"{self.app_dir}/examples/set-a/example.tsv",
            "-tn", "abpairs_abligity",
            "-o", output_file
        ]

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print("Error occurred during prediction")
            print("Error:", result.stderr)
            self.fail("Prediction failed")

        # Read both CSV files
        output_df = pd.read_csv(output_file)
        reference_df = pd.read_csv(reference_file)

        # Compare the dataframes with tolerance for numerical differences
        pd.testing.assert_frame_equal(
            output_df,
            reference_df,
            check_exact=False,
            rtol=1e-3,  # relative tolerance
            atol=1e-5   # absolute tolerance
        )

    def tearDown(self):
        # Example usage
        if self.app_dir:
            print(f"App root directory is: {self.app_dir}")
        else:
            print("Root directory not found.")

        # Delete all the models folder that has been created
        delete_folders_with_prefix(f'{self.app_dir}/models', prefix='9999')

        # Delete the output file that was created
        if os.path.isfile(self.output_file_to_delete):
            os.remove(self.output_file_to_delete)
            print(f'File {self.output_file_to_delete} is removed')

def main():
    unittest.main()

if __name__=='__main__':
    main()