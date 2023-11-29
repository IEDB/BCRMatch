import os
import sys
import csv
import pickle
import tempfile
import pandas as pd
from bcrmatch_argparser import BCRMatchArgumentParser
from bcrmatch import bcrmatch_functions, classify_abs
from subprocess import Popen, PIPE
from pathlib import Path


# Absolute path to the TCRMatch program
TCRMATCH_PATH = os.getenv('TCRMATCH_PATH', '/src/bcrmatch')
BASE_DIR = Path(__file__).parent.absolute()


def predict(complete_score_dict, classifiers):
	with open("output.csv", "w", newline='') as csvfile:
		outfile_writer = csv.writer(csvfile, delimiter=',')
		outfile_writer.writerow(["Antibody pair", "RF Prediction", "LR Prediction",
		                        "GNB Prediction", "XGB Prediction", "FFNN Prediction"])
		for ab_pair in complete_score_dict.keys():
			rowline = []
			rowline.append(ab_pair)

			# input_data = classify_abs.preprocess_input_data([0.98,1,1,1,1,0.98])
			input_data = classify_abs.preprocess_input_data(complete_score_dict[ab_pair])


			for classifier_name, classifier_obj in classifiers.items():
				if classifier_name == 'ffnn':
					output = classifier_obj.predict(input_data)
					rowline.append(output[0][0])
				else:
					output = classifier_obj.predict_proba(input_data)[:, 1]
					rowline.append(output[0])
				
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
		'dataset_version'
	]

	# Create 5 dataset entry for all 5 models
	data = []
	for model in parser.MODELS:
		pickle_file_path = '%s/%s/%s_%s.pkl' %(name, version, model, name)
		data.append([name, model, dataset, pickle_file_path, version])
	
	return pd.DataFrame(data, columns=dataset_db_header)


def start_training_mode(parser):
	# For training mode, user must provide the following:
	#   * training-dataset-csv
	#   * training-dataset-name
	#   * training-dataset-version
	training_dataset_file = parser.get_training_dataset()
	training_dataset_name = os.path.basename(training_dataset_file)
	training_dataset_name = os.path.splitext(training_dataset_name)[0]
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
				classifiers = train_models(training_dataset_file)
				save_classifiers(training_dataset_name, training_dataset_version, classifiers)
				df = residue_df

			else:
				# Do not print tracebacks
				sys.tracebacklimit = 0
				raise Exception('All models have already been train under the %s (%s) dataset.' %(training_dataset_name, training_dataset_version))
		
		classifiers = train_models(training_dataset_file)
		save_classifiers(training_dataset_name, training_dataset_version, classifiers)
		# entry doesn't exists, thus add to db		
		df2 = update_db_content(parser, training_dataset_name, training_dataset_file, training_dataset_version)

		# Append the data to the existing db
		df = pd.concat([df, df2])
		
	else:
		classifiers = train_models(training_dataset_file)
		save_classifiers(training_dataset_name, training_dataset_version, classifiers)
		df = update_db_content(parser, training_dataset_name, training_dataset_file, training_dataset_version)
	
	df.sort_values(['dataset_name', 'dataset_version'], ascending=[True, True], inplace=True)

	# create dataset db
	df.to_csv(database_db, sep='\t', index=False)


def get_available_datasets(db):
	df = pd.read_csv(db, sep='\t')

	sub_df = df.groupby(['dataset_name', 'dataset_version'])

	return pd.DataFrame(sub_df.size().reset_index(name='count')).drop(columns=['count'])


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
	training_dataset_file = bcrmatch_parser.get_training_dataset()
	training_dataset_name = os.path.basename(training_dataset_file)
	training_dataset_name = os.path.splitext(training_dataset_name)[0]
	dataset_ver = bcrmatch_parser.get_training_dataset_version()

	# get training data
	x_train, y_train = classify_abs.preprocess_ml_dataset(training_dataset_file)
	# x_train, y_train = get_training_data(training_dataset_file)

	print("Retrieving all files containing the TCRMatch result...")
	tcrout_files = get_tcr_output_files(sequence_info_dict)

	print("Retrieve scores as dictionary...")
	score_dict = get_scoring_dict_from_csv(tcrout_files)
	
	classifiers = get_classifiers(training_dataset_name, dataset_ver, db=dataset_db)

	print("Writing the final output to CSV...")
	predict(score_dict, classifiers)

	print("Completed!")

if __name__ == "__main__":
    main()	