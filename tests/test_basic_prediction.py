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
    # python_path = '/usr/bin/python3'
    python_path = sys.executable
    test_dir = f'{app_dir}/tests'
    example_dir = f'{test_dir}/examples-a'
    output_file_to_delete = ''  

    # def test_abpairs_abligity_1(self):
    #     today = datetime.date.today().strftime('%Y%m%d')
    #     training_version = f"9999{today}"
    #     output_file = f"{self.test_dir}/test_output.csv"
    #     dataset_name = 'abpairs_abligity_imgt_20240916_hk'
    #     dataset = f'{self.app_dir}/{dataset_name}.csv'
    #     ground_truth_file = f'{self.example_dir}/ground_truth_abpair_abligity.csv'
    #     self.output_file_to_delete = output_file

    #     # Training
    #     command = [
    #         self.python_path, 
    #         f"{self.app_dir}/run_bcrmatch.py", 
    #         "-tm", 
    #         "-tc", dataset, 
    #         # 9999 to indicate that it's a test
    #         "-tv", training_version,
    #         "-f",
    #     ]

    #     # print(command)

    #     # Call the program and capture output (stdout and stderr)
    #     result = subprocess.run(command, capture_output=True, text=True)

    #     # Check the result
    #     if result.returncode == 0:
    #         print("Program executed successfully")
    #         print("Output:", result.stdout)
    #     else:
    #         print("Error occurred")
    #         print("Error:", result.stderr)

    #     # Prediction
    #     command = [
    #         self.python_path,  # the Python executable
    #         f"{self.app_dir}/run_bcrmatch.py", 
    #         "-ch", f"{self.example_dir}/cdrh1_input.fasta", f"{self.example_dir}/cdrh2_input.fasta", f"{self.example_dir}/cdrh3_input.fasta",  # cdrh arguments
    #         "-cl", f"{self.example_dir}/cdrl1_input.fasta", f"{self.example_dir}/cdrl2_input.fasta", f"{self.example_dir}/cdrl3_input.fasta",  # cdrl arguments
    #         "-tn", dataset_name,  # training name
    #         "-tv", training_version,  # training version
    #         "-v",  # verbosity flag
    #         "-o", output_file,
    #     ]

    #     # print(command)

    #     result = subprocess.run(command, capture_output=True, text=True)
    #     # Check the result
    #     if result.returncode == 0:
    #         print("Program executed successfully")
    #     else:
    #         print("Error occurred")
    #         print("Error:", result.stderr)

    #     # Prediction Result
    #     df = pd.read_csv(output_file)
    #     row = df[df['Antibody pair'] == '24_764']

    #     # Precalculated Result (Ground Truth)
    #     gt_df = pd.read_csv(ground_truth_file)
    #     gt_row = gt_df[gt_df['Antibody pair'] == '24_764']

    #     # RF
    #     rf_score = row['RF Prediction'].values[0]
    #     gt_rf_score = gt_row['RF Prediction'].values[0]
    #     self.assertTrue(self.compare_values(rf_score, gt_rf_score))

    #     rf_score = row['RF Percentile Rank'].values[0]
    #     gt_rf_score = gt_row['RF Percentile Rank'].values[0]
    #     self.assertTrue(self.compare_values(rf_score, gt_rf_score))

    #     # LR
    #     lr_score = row['LR Prediction'].values[0]
    #     gt_lr_score = gt_row['LR Prediction'].values[0]
    #     self.assertTrue(self.compare_values(lr_score, gt_lr_score))
        
    #     lr_score = row['LR Percentile Rank'].values[0]
    #     gt_lr_score = gt_row['LR Percentile Rank'].values[0]
    #     self.assertTrue(self.compare_values(lr_score, gt_lr_score))
        
    #     # GNB
    #     gnb_score = row['GNB Prediction'].values[0]
    #     gt_gnb_score = gt_row['GNB Prediction'].values[0]
    #     self.assertTrue(self.compare_values(gnb_score, gt_gnb_score))
        
    #     gnb_score = row['GNB Percentile Rank'].values[0]
    #     gt_gnb_score = gt_row['GNB Percentile Rank'].values[0]
    #     self.assertTrue(self.compare_values(gnb_score, gt_gnb_score))
        
    #     # XGB
    #     xgb_score = row['XGB Prediction'].values[0]
    #     gt_xgb_score = gt_row['XGB Prediction'].values[0]
    #     self.assertTrue(self.compare_values(xgb_score, gt_xgb_score))
        
    #     xgb_score = row['XGB Percentile Rank'].values[0]
    #     gt_xgb_score = gt_row['XGB Percentile Rank'].values[0]
    #     self.assertTrue(self.compare_values(xgb_score, gt_xgb_score))

    #     # FFNN
    #     ffnn_score = row['FFNN Prediction'].values[0]
    #     gt_ffnn_score = gt_row['FFNN Prediction'].values[0]
    #     self.assertTrue(self.compare_values(ffnn_score, gt_ffnn_score))
        
    #     ffnn_score = row['FFNN Percentile Rank'].values[0]
    #     gt_ffnn_score = gt_row['FFNN Percentile Rank'].values[0]
    #     self.assertTrue(self.compare_values(ffnn_score, gt_ffnn_score))

    def test_abpairs_abligity_2(self):
        today = datetime.date.today().strftime('%Y%m%d')
        training_version = f"9999{today}"
        output_file = f"{self.test_dir}/test_output.csv"
        dataset_name = 'abpairs_abligity_imgt_20240916_hk'
        dataset = f'{self.app_dir}/{dataset_name}.csv'
        self.example_dir = f'{self.test_dir}/examples-b'
        ground_truth_file = f'{self.example_dir}/updated_examples_withpercentiles.csv'
        self.output_file_to_delete = output_file

        # Training
        command = [
            self.python_path, 
            f"{self.app_dir}/run_bcrmatch.py", 
            "-tm", 
            "-tc", dataset, 
            # 9999 to indicate that it's a test
            "-tv", training_version,
            "-f",
        ]

        # print(command)

        # Call the program and capture output (stdout and stderr)
        result = subprocess.run(command, capture_output=True, text=True)

        # Check the result
        if result.returncode == 0:
            print("Program executed successfully")
            print("Output:", result.stdout)
        else:
            print("Error occurred")
            print("Error:", result.stderr)

        # Prediction
        command = [
            self.python_path,  # the Python executable
            f"{self.app_dir}/run_bcrmatch.py", 
            "-ch", f"{self.example_dir}/cdrh1_seqs.fasta", f"{self.example_dir}/cdrh2_seqs.fasta", f"{self.example_dir}/cdrh3_seqs.fasta",  # cdrh arguments
            "-cl", f"{self.example_dir}/cdrl1_seqs.fasta", f"{self.example_dir}/cdrl2_seqs.fasta", f"{self.example_dir}/cdrl3_seqs.fasta",  # cdrl arguments
            "-tn", dataset_name,  # training name
            "-tv", training_version,  # training version
            "-v",  # verbosity flag
            "-o", output_file,
        ]

        # print(command)

        result = subprocess.run(command, capture_output=True, text=True)
        # Check the result
        if result.returncode == 0:
            print("Program executed successfully")
        else:
            print("Error occurred")
            print("Error:", result.stderr)

        # Prediction Result
        df = pd.read_csv(output_file)

        # Precalculated Result (Ground Truth)
        gt_df = pd.read_csv(ground_truth_file)

        predicted_pairs = df['Antibody pair'].to_list()

        for pair in predicted_pairs:
            print('comparing %s' %(pair))
            self.compare_scores_given_antibody_pair(df, gt_df, pair)

    def compare_scores_given_antibody_pair(self, df, gt_df, ab_pair):
        row = df[df['Antibody pair'] == ab_pair]
        gt_row = gt_df[gt_df['Antibody pair'] == ab_pair]

        # RF
        rf_score = row['RF Prediction'].values[0]
        gt_rf_score = gt_row['RF Prediction'].values[0]
        self.assertTrue(self.compare_values(rf_score, gt_rf_score))

        rf_score = row['RF Percentile Rank'].values[0]
        gt_rf_score = gt_row['RF Percentile Rank'].values[0]
        self.assertTrue(self.compare_values(rf_score, gt_rf_score))

        # LR
        lr_score = row['LR Prediction'].values[0]
        gt_lr_score = gt_row['LR Prediction'].values[0]
        self.assertTrue(self.compare_values(lr_score, gt_lr_score))
        
        lr_score = row['LR Percentile Rank'].values[0]
        gt_lr_score = gt_row['LR Percentile Rank'].values[0]
        self.assertTrue(self.compare_values(lr_score, gt_lr_score))
        
        # GNB
        gnb_score = row['GNB Prediction'].values[0]
        gt_gnb_score = gt_row['GNB Prediction'].values[0]
        self.assertTrue(self.compare_values(gnb_score, gt_gnb_score))
        
        gnb_score = row['GNB Percentile Rank'].values[0]
        gt_gnb_score = gt_row['GNB Percentile Rank'].values[0]
        self.assertTrue(self.compare_values(gnb_score, gt_gnb_score))
        
        # XGB
        xgb_score = row['XGB Prediction'].values[0]
        gt_xgb_score = gt_row['XGB Prediction'].values[0]
        self.assertTrue(self.compare_values(xgb_score, gt_xgb_score))
        
        xgb_score = row['XGB Percentile Rank'].values[0]
        gt_xgb_score = gt_row['XGB Percentile Rank'].values[0]
        self.assertTrue(self.compare_values(xgb_score, gt_xgb_score))

        # FFNN
        ffnn_score = row['FFNN Prediction'].values[0]
        gt_ffnn_score = gt_row['FFNN Prediction'].values[0]
        self.assertTrue(self.compare_values(ffnn_score, gt_ffnn_score))
        
        ffnn_score = row['FFNN Percentile Rank'].values[0]
        gt_ffnn_score = gt_row['FFNN Percentile Rank'].values[0]
        self.assertTrue(self.compare_values(ffnn_score, gt_ffnn_score))


    def compare_values(self, f1, f2):
        ff1 = self.format_values(f1)
        ff2 = self.format_values(f2)

        return ff1 == ff2
    
    def format_values(self, number):
        num = float(number)

        if number == 0.0: return 0.0

        if num < 0.1:
            # Format to scientific notation with 2 significant digits
            return "{:.2e}".format(num)
        else:
            # Calculate the number of significant digits after the decimal
            return round(num, 2 - int(math.floor(math.log10(abs(num)))) - 1)



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

def  main():
    tester = TestBasicPrediction()
    tester.test_abpairs_abligity_2()

if __name__=='__main__':
    unittest.main()
    # main()