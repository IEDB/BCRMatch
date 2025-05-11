import os
import sys
import pickle
import tempfile
import pandas as pd
import numpy as np
import math
from statsmodels.distributions.empirical_distribution import ECDF
from bcrmatch_argparser import BCRMatchArgumentParser
from bcrmatch import bcrmatch_functions, classify_abs
from subprocess import Popen, PIPE
from pathlib import Path
from statistics import harmonic_mean

# Absolute path to the TCRMatch program
TCRMATCH_PATH = os.getenv('TCRMATCH_PATH', '/src/bcrmatch')
BASE_DIR = str(Path(__file__).parent.absolute())
MODEL_DIR = 'models/models'

import tensorflow as tf
tf.random.set_seed(42)

def output_result(result_df, output_location, is_verbose):
	default_columns_to_display = [
		'Antibody pair',
		'LR Prediction',
		'LR Percentile Rank',
		'GNB Prediction',
		'GNB Percentile Rank',
		# 'XGB Percentile Rank',
		# 'FFNN Percentile Rank',
		# 'RF Percentile Rank',
		'Mean Percentile Rank',
		# 'Overall Mean Percentile Rank',
	]

	if not is_verbose:
		result_df = result_df[default_columns_to_display].copy()

	# Round the entire dataframe to 2 sigfigs
	result_df.loc[:, result_df.columns[1:]] = result_df.iloc[:, 1:].applymap(format_values)

	# Display result to terminal
	if not output_location:
		print(result_df)
		sys.exit()

	# Write out to a file
	result_df.to_csv(output_location, index=False)
	print("Completed!")

def add_mean_percentile_ranks(df):
	headers = df.columns.tolist()
	lr_gnb_mean_col_list = []
	overall_mean_col_list = []
	lr_idx = headers.index('LR Percentile Rank')+1
	gnb_idx = headers.index('GNB Percentile Rank')+1
	xgb_idx = headers.index('XGB Percentile Rank')+1
	ffnn_idx = headers.index('FFNN Percentile Rank')+1
	rf_idx = headers.index('RF Percentile Rank')+1

	# Adding LR+GNB mean percentile rank + Overall mean percentile rank
	for row in df.itertuples(): 
		# LR+GNB mean percentile rank
		lr_pr = getattr(row, f'_{lr_idx}')
		gnb_pr = getattr(row, f'_{gnb_idx}')
		mean = harmonic_mean([lr_pr, gnb_pr])
		lr_gnb_mean_col_list.append(mean)


		# Overall mean percentile rank
		xgb_pr = getattr(row, f'_{xgb_idx}')
		ffnn_pr = getattr(row, f'_{ffnn_idx}')
		rf_pr = getattr(row, f'_{rf_idx}')
		mean = harmonic_mean([lr_pr, gnb_pr, xgb_pr, ffnn_pr, rf_pr])
		overall_mean_col_list.append(mean)

	df['Mean Percentile Rank'] = lr_gnb_mean_col_list
	df['Overall Mean Percentile Rank'] = overall_mean_col_list

	return df

def load_percentile_rank_dataset(classifier):
	#TODO: This is technically score distribution and not percentile rank.
	pkl_path = f'{BASE_DIR}/pickles/score_distributions/{classifier}.pkl'

	with open(pkl_path, 'rb') as f:
		pr_dataset = pickle.load(f)
	
	return pr_dataset

def calculate_percentile_rank(classifier, score):
	'''
	This function utilizes scipy to caculate percentile rank
	of the predicted score from the 'percentile_rank_dataset.csv'.
	'''
	pr_dataset = load_percentile_rank_dataset(classifier)

	ecdf = ECDF(pr_dataset.values)

	# NOTE: High score should equal lower ranks
	return (1 - ecdf(score)) * 100

def predict(complete_score_dict, classifiers, scaler):
	result = []

	# Set column names
	result_header = [
		"Antibody pair", 
		"RF Prediction", 
		"RF Percentile Rank",
		"LR Prediction",
		"LR Percentile Rank",
		"GNB Prediction", 
		"GNB Percentile Rank",
		"XGB Prediction", 
		"XGB Percentile Rank",
		"FFNN Prediction",
		"FFNN Percentile Rank",
		# "Mean LR and GNB Percentile Ranks"
		]
	
	# NOTE: It needs to be specifically in this order
	ordered_classifiers = {
		'rf': classifiers['rf'],
		'log_reg': classifiers['log_reg'],
		'gnb': classifiers['gnb'],
		'xgb': classifiers['xgb'],
		'ffnn': classifiers['ffnn'],
	}
	
	
	for ab_pair in complete_score_dict.keys():
		rowline = []
		rowline.append(ab_pair)

		input_data = classify_abs.preprocess_input_data(
			complete_score_dict[ab_pair], scaler)
		
		for classifier_name, classifier_obj in ordered_classifiers.items():
			if classifier_name == 'ffnn':
				output = classifier_obj.predict(input_data)
				score = output[0][0]
			else:
				output = classifier_obj.predict_proba(input_data)[:, 1]
				score = output[0]
			
			# calculate percentile rank
			percentile_rank = calculate_percentile_rank(classifier_name, score)
					
			rowline.append(score)
			rowline.append(percentile_rank)
			
		result.append(rowline)

	return pd.DataFrame(result, columns=result_header)

def format_values(number):
	num = float(number)

	if number == 0.0: return 0.0

	if num < 0.1:
		# Format to scientific notation with 2 significant digits
		return "{:.2e}".format(num)
	else:
		# Calculate the number of significant digits after the decimal
		return round(num, 2 - int(math.floor(math.log10(abs(num)))) - 1)

def get_classifiers(dataset_name, version, db):
	df = pd.read_csv(db, sep='\t')
	
	# NOTE: dataset_version column is saved as int type.
	filtered_df = df[(df['dataset_name']==dataset_name) & (df['dataset_version']==version)]	
	classifiers = {}

	for i, row in filtered_df.iterrows():
		pkl_path = '%s/%s' %(MODEL_DIR, row['pickle_file'])
		classifier = row['model']

		try:
			with open(pkl_path, 'rb') as f:
				classifiers[classifier] = pickle.load(f)
		except:
			sys.tracebacklimit = 0
			raise Exception('Please check if the %s (%s) has been saved in a pickle file.' %(row['model'], row['dataset_version']))

	return classifiers

def get_models_dir_path(dataset, version):
	# return '%s/%s/%s/%s' %(BASE_DIR, MODEL_DIR, dataset, version)
	return f'{MODEL_DIR}/{dataset}/{version}'

def save_scaler(dataset, version, scaler):
	print("Pickling scaler object...")
	base_path = get_models_dir_path(dataset, version)
	pkl_file_path = f'{base_path}/scaler.pkl'

	with open(pkl_file_path, 'wb') as f:
		pickle.dump(scaler, f)


def save_classifiers(dataset, version, classifiers):
	# Saves classifers into pickle files
	print("Pickling classifiers...")

	for classifier_name, classifier_obj in classifiers.items():
		# Create directories recursively even if they don't exists
		base_path = get_models_dir_path(dataset, version)
		path = Path(base_path)
		path.mkdir(parents=True, exist_ok=True)

		pkl_file_name = '%s_%s.pkl' %(classifier_name, dataset)
		pkl_file_path = '%s/%s' %(base_path, pkl_file_name)
		
		print(pkl_file_path)
		with open(pkl_file_path, 'wb') as f:
			pickle.dump(classifier_obj, f)


def train_classifiers(x_train, y_train):
	# Trains data, then saves the model as pickle file.
	rf = classify_abs.RF(x_train, y_train)
	gnb = classify_abs.GNB(x_train, y_train)
	log_reg = classify_abs.LR(x_train, y_train)
	xgb = classify_abs.XGB(x_train, y_train)
	ffnn = classify_abs.FFNN(x_train, y_train)

	classifiers = {
		'rf': rf,
		'gnb': gnb,
		'log_reg': log_reg,
		'xgb': xgb,
		'ffnn': ffnn
	}

	return classifiers


def train_models(dataset_file):
	x_train, y_train = classify_abs.preprocess_ml_dataset(dataset_file)
	
	# Train classifiers
	return train_classifiers(x_train, y_train)
	

def compile_scores(file_name):
	score_dict = {}
	IFH1 = open(file_name, "r")
	lines1 = IFH1.readlines()

	for line1 in lines1:
		line1 = line1.strip("\n")
		line1 = line1.split(",")
		pair_id = line1[0]
		score = line1[1]
		if pair_id not in score_dict:
			score_dict[pair_id] = score

	return (score_dict)


def get_scoring_dict_from_csv(file_names):
	"""
	file_name: text file that contains all the input csv file names.
		* dict_1 = compile_scores("test_cdrh3_iedb_seq_tcroutput.csv")
		* dict_2 = compile_scores("test_cdrh2_iedb_seq_tcroutput.csv")
		* dict_3 = compile_scores("test_cdrh1_iedb_seq_tcroutput.csv")
		* dict_4 = compile_scores("test_cdrl3_iedb_seq_tcroutput.csv")
		* dict_5 = compile_scores("test_cdrl2_iedb_seq_tcroutput.csv")
		* dict_6 = compile_scores("test_cdrl1_iedb_seq_tcroutput.csv")
	"""
	all_score_dict = {}
	dict_1 = None
	dict_2 = None
	dict_3 = None
	dict_4 = None
	dict_5 = None
	dict_6 = None

	for each_file in file_names:
		if 'cdrh1' in each_file:
			dict_1 = compile_scores(each_file)

		if 'cdrh2' in each_file:
			dict_2 = compile_scores(each_file)
		
		if 'cdrh3' in each_file:
			dict_3 = compile_scores(each_file)

		if 'cdrl1' in each_file:
			dict_4 = compile_scores(each_file)

		if 'cdrl2' in each_file:
			dict_5 = compile_scores(each_file)

		if 'cdrl3' in each_file:
			dict_6 = compile_scores(each_file)


	for pair in dict_1.keys():
		if pair not in all_score_dict.keys():
			all_score_dict[pair] = []
			all_score_dict[pair].append(dict_1[pair])
			all_score_dict[pair].append(dict_2[pair])
			all_score_dict[pair].append(dict_3[pair])
			all_score_dict[pair].append(dict_4[pair])
			all_score_dict[pair].append(dict_5[pair])
			all_score_dict[pair].append(dict_6[pair])
		else:
			all_score_dict[pair].append(dict_1[pair])
			all_score_dict[pair].append(dict_2[pair])
			all_score_dict[pair].append(dict_3[pair])
			all_score_dict[pair].append(dict_4[pair])
			all_score_dict[pair].append(dict_5[pair])
			all_score_dict[pair].append(dict_6[pair])

	return all_score_dict


def get_tcr_output_files(tsv_content) :
	tcrout_filenames = []
	sequence_name_key = list(tsv_content.keys())[0]
	sequence_names = tsv_content[sequence_name_key]

	for k, v in tsv_content.items():
		# Skip sequence names
		if k == sequence_name_key :
			continue
		
		seq_dict = {}
		for i in range(len(sequence_names)):
			seq_dict[str(sequence_names[i])] = v[i]

		# Create temporary file containing 'seq_dict' to be used as input for TCRMatch
		with tempfile.NamedTemporaryFile(mode='w', prefix=f'{k.lower()}_', suffix='_tcrinput', delete=False) as tmp:
			tmp.write('\n'.join(list(seq_dict.values())))

		# Run TCRMatch
		cmd = ['%s/tcrmatch' % (TCRMATCH_PATH), '-i', '%s' %
								(tmp.name), '-t', '10', '-s', '0', '-d', '%s' % (tmp.name)]

		process = Popen(cmd, stdout=PIPE)
		stdoutdata, stderrdata_ignored = process.communicate()
		stdoutdata = stdoutdata.decode().strip()

		# Format the results into a file
		tcr_output_result = bcrmatch_functions.create_tcroutput(stdoutdata, seq_dict)

		with tempfile.NamedTemporaryFile(mode='w', prefix=f'{k.lower()}_', suffix='_tcroutput', delete=False) as tmp:
			tmp.write(tcr_output_result)
			tcrout_filenames.append(tmp.name)
			
		# TODO: Clean up the input temporary files

	return tcrout_filenames


def update_db_content(parser, name, dataset, version):
	dataset_db_header = [
		'dataset_name',
		'model',
		'dataset',
		'pickle_file',
		'dataset_version',
	]

	# Create 5 dataset entry for all 5 models
	data = []
	for model in parser.MODELS:
		pickle_file_path = '%s/%s/%s_%s.pkl' %(name, version, model, name)
		data.append(
			[name, model, dataset, pickle_file_path, version])
	
	return pd.DataFrame(data, columns=dataset_db_header)


def start_training_mode(parser):
	# For training mode, user must provide the following:
	#   * training-dataset-csv
	#   * training-dataset-name
	#   * training-dataset-version
	training_dataset_file = parser.training_dataset
	training_dataset_name = parser.training_dataset_name
	training_dataset_version = parser.training_dataset_version
	force_retrain = parser.force_retrain_flag
	database_db = parser.database
	
	# Check existence of dataset db
	if Path(database_db).is_file():
		# Check if the user provided entry already exists in the database
		df = pd.read_csv(database_db, sep='\t')

		# Only need to check dataset name and dataset version to check for existence
		filtered_df = df[(df['dataset_name']==training_dataset_name) & (df['dataset_version']==training_dataset_version)]
		residue_df = df[(df['dataset_name']!=training_dataset_name) | (df['dataset_version']!=training_dataset_version)]
		
		if 0 < len(filtered_df):
			# If force flag is set, retrain
			if force_retrain:
				print('Force Retraining -- call train_model()')
				df = residue_df

			else:
				# Do not print tracebacks
				sys.tracebacklimit = 0
				raise Exception('All models have already been train under the %s (%s) dataset.' %(training_dataset_name, training_dataset_version))

		# entry doesn't exists, thus add to db		
		df2 = update_db_content(parser, training_dataset_name,
		                        training_dataset_file, training_dataset_version)

		# Append the data to the existing db
		df = pd.concat([df, df2])
		
	else:
		df = update_db_content(parser, training_dataset_name,
		                       training_dataset_file, training_dataset_version)
	
	df.sort_values(['dataset_name', 'dataset_version'], ascending=[True, True], inplace=True)

	# create dataset db
	df.to_csv(database_db, sep='\t', index=False)
	
	# Train classifiers and fit scaler to the datset + save
	classifiers = train_models(training_dataset_file)
	scaler = classify_abs.get_standard_scaler()
	save_classifiers(training_dataset_name, training_dataset_version, classifiers)
	save_scaler(training_dataset_name, training_dataset_version, scaler)


def get_available_datasets(db):
	df = pd.read_csv(db, sep='\t')

	sub_df = df.groupby(['dataset_name', 'dataset_version'])

	return pd.DataFrame(sub_df.size().reset_index(name='count')).drop(columns=['count'])


def get_csv_file_path(dataset_name, version, db):
	df = pd.read_csv(db, sep='\t')
	filtered_df = df[(df['dataset_name']==dataset_name) & (df['dataset_version']==version)]	
	
	return filtered_df['dataset'].iloc[0]
	

def get_standard_scaler(dataset, version):
	# Create directories recursively
	base_path = get_models_dir_path(dataset, version)
	path = Path(base_path)
	if not os.path.isdir(path):
		raise NotADirectoryError(f'Directory Not Found: {base_path}')
	path.mkdir(parents=True, exist_ok=True)

	pkl_file_name = 'scaler.pkl'
	pkl_file_path = '%s/%s' %(base_path, pkl_file_name)

	scaler = None
	try:
		with open(pkl_file_path, 'rb') as f:
			scaler = pickle.load(f)
	except:
		raise FileExistsError(f'No such file or directory: \'{pkl_file_path}\'')
	
	return scaler


def main():
	print("Starting program...")
	bcrmatch_parser = BCRMatchArgumentParser()
	args, parser = bcrmatch_parser.parse_args(sys.argv[1:])

	# Basic validation and prep on all the params(flags)
	bcrmatch_parser.validate(args)

	# Set BASE_DIR (config step)
	global BASE_DIR
	BASE_DIR = bcrmatch_parser.root_dir

	global MODEL_DIR
	MODEL_DIR = bcrmatch_parser.models_dir

	print('-----------------------------')
	print(f'BASE MODEL: {BASE_DIR}')
	print(f'MODEL DIR: {MODEL_DIR}')
	print('-----------------------------')

	dataset_db = bcrmatch_parser.database

	if bcrmatch_parser.list_datasets_flag:
		dataset_df = get_available_datasets(dataset_db)
		print(dataset_df.to_string(index=False))
		sys.exit(0)
	

	# Check training mode
	if bcrmatch_parser.training_mode:
		print('Training mode on..')

		start_training_mode(bcrmatch_parser)

		print("Finished training the models...")
		sys.exit(0)


	# Get all the sequences into a dictionary
	sequence_info_dict = bcrmatch_parser.get_sequences(args, parser)
	dataset_name = bcrmatch_parser.training_dataset_name
	dataset_ver = bcrmatch_parser.training_dataset_version
	output_location = bcrmatch_parser.output_location
	verbose = bcrmatch_parser.verbose

	# Get scaler that was pre-fitted to the training dataset through dataset_name
	scaler = get_standard_scaler(dataset_name, dataset_ver)
	
	print("Retrieving all files containing the TCRMatch result...")
	tcrout_files = get_tcr_output_files(sequence_info_dict)

	print("Retrieve scores...")
	score_dict = get_scoring_dict_from_csv(tcrout_files)
	# test_df = pd.DataFrame(score_dict)
	# test_df.to_csv('score_dict_data.csv', index=False)
	
	classifiers = get_classifiers(dataset_name, dataset_ver, db=dataset_db)

	result_df = predict(score_dict, classifiers, scaler)

	result_df = add_mean_percentile_ranks(result_df)

	output_result(result_df, output_location, is_verbose=verbose)


if __name__ == "__main__":
    main()	
