import argparse
import os
import csv
import pickle
import tempfile
from pathlib import Path
from bcrmatch import bcrmatch_functions, classify_abs
from subprocess import Popen, PIPE


# Absolute path to the TCRMatch program
TCRMATCH_PATH = os.getenv('TCRMATCH_PATH', '/src/bcrmatch')


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='user_input.py',
        usage='%(prog)s [options]'
    )
    parser.add_argument("-i", "--inputFile", help="Text file containing list of cdrh/cdrl FASTA file names.", required=True)

    return parser.parse_args()


def get_results(complete_score_dict, rf_classifier, gnb_classifier, log_reg_classifier, xgb_classifier, ffnn_classifier):
	with open("output_hk.csv", "w", newline='') as csvfile:
		outfile_writer = csv.writer(csvfile, delimiter=',')
		outfile_writer.writerow(["Antibody pair","RF Prediction","LR Prediction","GNB Prediction", "XGB Prediction", "FFNN Prediction"])
		for ab_pair in complete_score_dict.keys():
			rowline = []
			rowline.append(ab_pair)
			#input_data = classify_abs.preprocess_input_data([0.98,1,1,1,1,0.98])
			input_data = classify_abs.preprocess_input_data(complete_score_dict[ab_pair])
			#print(input_data)

			# output_rf = rf_classifier.predict(input_data)
			# output_gnb = gnb_classifier.predict(input_data)

			output_rf = rf_classifier.predict_proba(input_data)[:,1]
			output_lr = log_reg_classifier.predict_proba(input_data)[:,1]
			output_gnb = gnb_classifier.predict_proba(input_data)[:,1]
			output_xgb = xgb_classifier.predict_proba(input_data)[:,1]
			output_ffnn = ffnn_classifier.predict(input_data)

			rowline.append(output_rf)
			rowline.append(output_lr)
			rowline.append(output_gnb)
			rowline.append(output_xgb)
			rowline.append(output_ffnn)

			#print(output_rf)
			#print(output_gnb)

			# if output_rf == 0:
			# 	if output_gnb == 0:
			# 		#print("Doesn't bind to same epitope as given antibody\n")
			# 		rowline.append(output_rf)
			# 		rowline.append(output_gnb)
			# 		rowline.append("0")
			# 	elif output_gnb == 1:
			# 		#print("Binds to same epitope as given antibody\n")
			# 		rowline.append(output_rf)
			# 		rowline.append(output_gnb)
			# 		rowline.append("1")
			# elif output_rf == 1:
			# 	#print("Binds to same epitope as given antibody\n")
			# 	rowline.append(output_rf)
			# 	rowline.append(output_gnb)
			# 	rowline.append("1")

			outfile_writer.writerow(rowline)

def train_classifiers(x_train, y_train):
	# Trains data, then saves the model as pickle file.
	rf_classifier = classify_abs.RF(x_train, y_train)
	gnb_classifier = classify_abs.GNB(x_train, y_train)
	log_reg_classifer = classify_abs.LR(x_train, y_train)
	xgb_classifier = classify_abs.XGB(x_train, y_train)
	ffnn_classifier = classify_abs.FFNN(x_train, y_train)
	#ffnn_classfier.save('ffnn_abligity.h5')

	with open("rf_classifier.pkl", "wb") as f:
		pickle.dump(rf_classifier, f)
	
	with open("gnb_classifier.pkl", "wb") as f:
		pickle.dump(gnb_classifier, f)

	with open("log_reg_classifer", "wb") as f:
		pickle.dump(log_reg_classifer, f)
	
	with open("xgb_classifier", "wb") as f:
		pickle.dump(xgb_classifier, f)

	with open("ffnn_classifier", "wb") as f:
		pickle.dump(ffnn_classifier, f)


def get_classifiers(rf_pkl, gnb_pkl):
	with open("rf_classifier.pkl", "rb") as f:
		rf_classifier = pickle.load(f)
	
	with open("gnb_classifier.pkl", "rb") as f:
		gnb_classifier = pickle.load(f)
	
	with open("xgb_classifier.pkl", "rb") as f:
		xgb_classifier = pickle.load(f)
	
	with open("log_reg_classifier.pkl", "rb") as f:
		log_reg_classifier = pickle.load(f)
	
	with open("ffnn_classifier.pkl", "rb") as f:
		ffnn_classifier = pickle.load(f)
	
	return rf_classifier, gnb_classifier, xgb_classifier, log_reg_classifier, ffnn_classifier

def get_training_data(file_name):
	# X_train, y_train = classify_abs.preprocess_ml_dataset("test_subset_iedb_ml_dataset_filtered.csv")
	X_train, y_train = classify_abs.preprocess_ml_dataset(file_name)
	return X_train, y_train

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
                        
	return(score_dict)

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

	#print(all_score_dict)
	return all_score_dict


def get_tcr_output_files(ifh1, input_files_path) :
    tcrout_filenames = []
    for input_file_name in ifh1 :
        # Get full path to individual example input FASTA file
        input_file_name = input_files_path + '/' + input_file_name
                
        seq_dict = bcrmatch_functions.create_tcrmatch_input_hk(input_file_name)
        
        # Create temporary file containing 'seq_dict' to be used as input for TCRMatch
        with tempfile.NamedTemporaryFile(mode = 'w', prefix='tcr_', suffix='_input', delete=False) as tmp :
            tmp.write('\n'.join(list(seq_dict.values())))

        # Run TCRMatch
        cmd = ['%s/TCRMatch-0.1.1/tcrmatch' %(TCRMATCH_PATH), '-i', '%s' %(tmp.name), '-t', '10', '-s', '0', '-d','%s' %(tmp.name)]
        process = Popen(cmd,stdout=PIPE)
        stdoutdata, stderrdata_ignored = process.communicate()
        stdoutdata = stdoutdata.decode().strip()
        
        # Format the results into a file
        tcr_output_result = bcrmatch_functions.create_tcroutput_hk(stdoutdata, seq_dict)

        with tempfile.NamedTemporaryFile(mode = 'w', prefix='tcr_', suffix='_output', delete=False) as tmp :
            tmp.write(tcr_output_result)
            tcrout_filenames.append(tmp.name)

        # TODO: Clean up the input temporary files

    return tcrout_filenames


def main():
    print("Starting program...")
    args = parse_arguments()
    print("Done parsing arguments...")
    bcr_input_filenames = []
    pdir = str(Path(args.inputFile).parent.absolute())
    with open(args.inputFile, "r") as f :
        bcr_input_filenames = [_.strip() for _ in f.readlines()]

    print("Retrieving all files containing the TCRMatch result...")
    tcrout_files = get_tcr_output_files(bcr_input_filenames, pdir)
    
    print("Retrieve scores as dictionary...")
    score_dict = get_scoring_dict_from_csv(tcrout_files)
    x_train, y_train = get_training_data("./datasets/test_subset_iedb_ml_dataset_filtered.csv")
    # x_train, y_train = get_training_data("abpairs_abligity.csv")

    print("Pickling classifiers...")
	# Saves classifers into pickle files
    train_classifiers(x_train, y_train)

	# Read from pickle file
    rf_classifier, gnb_classifier, xgb_classifier, log_reg_classifier, ffnn_classifier = get_classifiers(x_train, y_train)

    print("Writing the final output to CSV...")
	# Writes out to file
    get_results(score_dict, rf_classifier, gnb_classifier, log_reg_classifier, xgb_classifier, ffnn_classifier)

    print("Completed!")

if __name__ == "__main__":
    main()	