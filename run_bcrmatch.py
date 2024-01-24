import os
import sys
import csv
import pickle
import tempfile
import ast
import pandas as pd
from scipy import stats
from bcrmatch_argparser import BCRMatchArgumentParser
from bcrmatch import bcrmatch_functions, classify_abs
from subprocess import Popen, PIPE
from pathlib import Path

# Absolute path to the TCRMatch program
TCRMATCH_PATH = os.getenv('TCRMATCH_PATH', '/src/bcrmatch')
BASE_DIR = Path(__file__).parent.absolute()



def load_percentile_rank_dataset(classifier):
	pkl_path = f'./pickles/percentile_ranks/{classifier}.pkl'
	with open(pkl_path, 'rb') as f:
		pr_dataset = pickle.load(f)
	
	return pr_dataset

def calculate_percentile_rank(classifier, score):
	'''
	This function utilizes scipy to caculate percentile rank
	of the predicted score from the 'percentile_rank_dataset.csv'.
	'''
	pr_dataset = load_percentile_rank_dataset(classifier)

	# return the percentile rank
	return stats.percentileofscore(pr_dataset, score)


def predict(complete_score_dict, classifiers, scaler):
	# convert scaler string back to StandardScaler obj.
	scaler = ast.literal_eval(scaler)
	scaler = pickle.loads(scaler)

	with open("output.csv", "w", newline='') as csvfile:
		outfile_writer = csv.writer(csvfile, delimiter=',')

		# Set column names
		outfile_writer.writerow([
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
			])

		for ab_pair in complete_score_dict.keys():
			rowline = []
			rowline.append(ab_pair)

			# input_data = classify_abs.preprocess_input_data([0.98,1,1,1,1,0.98])
			input_data = classify_abs.preprocess_input_data(
				complete_score_dict[ab_pair], scaler)

			for classifier_name, classifier_obj in classifiers.items():
				if classifier_name == 'ffnn':
					output = classifier_obj.predict(input_data)
					score = output[0][0]
				else:
					output = classifier_obj.predict_proba(input_data)[:, 1]
					score = output[0]
				
				# calculate percentile rank
				percentile_rank = calculate_percentile_rank(classifier_name, score)

				# add score and percentile rank
				rowline.append(score)
				rowline.append(percentile_rank)
	
			outfile_writer.writerow(rowline)


def get_classifiers(dataset_name, version, db):
	df = pd.read_csv(db, sep='\t')
	filtered_df = df[(df['dataset_name']==dataset_name) & (df['dataset_version']==version)]	
	classifiers = {}

	for i, row in filtered_df.iterrows():
		pkl_path = '%s/pickles/%s' %(BASE_DIR, row['pickle_file'])
		classifier = row['model']

		try:
			with open(pkl_path, 'rb') as f:
				classifiers[classifier] = pickle.load(f)
		except:
			sys.tracebacklimit = 0
			raise Exception('Please check if the %s (%s) has been saved in a pickle file.' %(row['model'], row['dataset_version']))

	return classifiers

def save_scaler(dataset, version, scaler):
	print("Pickling scaler object...")
	base_path = '%s/pickles/%s/%s' %(BASE_DIR, dataset, version)
	path = Path(base_path)
	pkl_file_path = '%s/scaler.pkl' %(base_path)

	with open(pkl_file_path, 'wb') as f:
		pickle.dump(scaler, f)


def save_classifiers(dataset, version, classifiers):
	# Saves classifers into pickle files
	print("Pickling classifiers...")

	for classifier_name, classifier_obj in classifiers.items():
		# Create directories recursively even if they don't exists
		base_path = '%s/pickles/%s/%s' %(BASE_DIR, dataset, version)
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

	dict_1 = compile_scores(file_names[0])
	dict_2 = compile_scores(file_names[1])
	dict_3 = compile_scores(file_names[2])
	dict_4 = compile_scores(file_names[3])
	dict_5 = compile_scores(file_names[4])
	dict_6 = compile_scores(file_names[5])

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
	# [['Seq_Name', 'CDRL1', 'CDRL2', 'CDRL3', 'CDRH1', 'CDRH2', 'CDRH3'], ['1', 'NNIGSKS', 'DDS', 'WDSSSDHA', 'GFTFDDY', 'SWNTGT', 'RSYVVAAEYYFH'], ['2', 'SQDISNY', 'YTS', 'DFTLPF', 'GYTFTNY', 'YPGNGD', 'GGSYRYDGGFD'], ['3', 'ASGNIHN', 'YYT', 'HFWSTPR', 'GFSLTGY', 'WGDGN', 'RDYRLD'], ['4', 'SESVDNYGISF', 'AAS', 'SKEVPL', 'GYTFTSS', 'HPNSGN', 'RYGSPYYFD'], ['5', 'ASQDISN', 'YFT', 'QYSTVPW', 'GYDFTHY', 'NTYTGE', 'PYYYGTSHWYFD']]
	# for entry in tsv_content :

	# Seq_Name
	# [1, 2, 3, 4, 5]
	# CDRL1
	# ['NNIGSKS', 'SQDISNY', 'ASGNIHN', 'SESVDNYGISF', 'ASQDISN']
	# CDRL2
	# ['DDS', 'YTS', 'YYT', 'AAS', 'YFT']
	# CDRL3
	# ['WDSSSDHA', 'DFTLPF', 'HFWSTPR', 'SKEVPL', 'QYSTVPW']
	# CDRH1
	# ['GFTFDDY', 'GYTFTNY', 'GFSLTGY', 'GYTFTSS', 'GYDFTHY']
	# CDRH2
	# ['SWNTGT', 'YPGNGD', 'WGDGN', 'HPNSGN', 'NTYTGE']
	# CDRH3
	# ['RSYVVAAEYYFH', 'GGSYRYDGGFD', 'RDYRLD', 'RYGSPYYFD', 'PYYYGTSHWYFD']
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
		with tempfile.NamedTemporaryFile(mode='w', prefix='tcr_', suffix='_input', delete=False) as tmp:
			tmp.write('\n'.join(list(seq_dict.values())))

		# Run TCRMatch
		cmd = ['%s/tcrmatch' % (TCRMATCH_PATH), '-i', '%s' %
								(tmp.name), '-t', '10', '-s', '0', '-d', '%s' % (tmp.name)]

		process = Popen(cmd, stdout=PIPE)
		stdoutdata, stderrdata_ignored = process.communicate()
		stdoutdata = stdoutdata.decode().strip()

		# Format the results into a file
		tcr_output_result = bcrmatch_functions.create_tcroutput(stdoutdata, seq_dict)

		with tempfile.NamedTemporaryFile(mode='w', prefix='tcr_', suffix='_output', delete=False) as tmp:
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
		# 'scaler'
	]

	# pickle standard scaler
	# pickled_scaler = pickle.dumps(scaler)

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
	training_dataset_file = parser.get_training_dataset()
	training_dataset_name = parser.get_training_dataset_name()
	training_dataset_version = parser.get_training_dataset_version()
	force_retrain = parser.get_force_retrain_flag()
	database_db = parser.get_database()
	

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
		                       training_dataset_file, training_dataset_version, scaler)
	
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
	

def get_standard_scaler(dataset_name, version, db):
	df = pd.read_csv(db, sep='\t')
	filtered_df = df[(df['dataset_name'] == dataset_name)
                  & (df['dataset_version'] == version)]

	# returns a string format of the standard scaler
	return filtered_df['scaler'].iloc[0]

def main():
	print("Starting program...")
	bcrmatch_parser = BCRMatchArgumentParser()
	args, parser = bcrmatch_parser.parse_args(sys.argv[1:])

	# Basic validation and prep on all the params(flags)
	bcrmatch_parser.validate(args)

	dataset_db = bcrmatch_parser.get_database()

	if bcrmatch_parser.get_list_datasets_flag():
		dataset_df = get_available_datasets(dataset_db)
		print(dataset_df.to_string(index=False))
		sys.exit(0)
	

	# Check training mode
	if bcrmatch_parser.get_training_mode():
		print('Training mode on..')

		start_training_mode(bcrmatch_parser)

		print("Finished training the models...")
		sys.exit(0)


	# Get all the sequences into a dictionary
	sequence_info_dict = bcrmatch_parser.get_sequences(args, parser)
	# print(sequence_info_dict)
	# dataset_file = bcrmatch_parser.get_training_dataset()
	dataset_name = bcrmatch_parser.get_training_dataset_name()
	dataset_ver = bcrmatch_parser.get_training_dataset_version()

	# Get scaler that was pre-fitted to the training dataset through dataset_name
	scaler = get_standard_scaler(dataset_name, dataset_ver, db=dataset_db)


	print("Retrieving all files containing the TCRMatch result...")
	tcrout_files = get_tcr_output_files(sequence_info_dict)

	print("Retrieve scores as dictionary...")
	score_dict = get_scoring_dict_from_csv(tcrout_files)

	classifiers = get_classifiers(dataset_name, dataset_ver, db=dataset_db)

	print("Writing the final output to CSV...")
	predict(score_dict, classifiers, scaler)

	print("Completed!")

if __name__ == "__main__":
    main()	