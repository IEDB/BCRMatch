import csv
import pickle
from bcrmatch import classify_abs
from bcrmatch_argparser import BCRMatchArgumentParser


#user_provided:datset to choose for training, sequences for calculating CDR Kmer
#create another python object to calculate cdr kmer

# def parse_arguments():
#     parser = argparse.ArgumentParser(
#         prog='run_classify.py',
#         usage='%(prog)s [options]'
#     )
#     parser.add_argument("-i", "--inputFile", help="Text file containing list of cdrh/cdrl FASTA file names.", required=True)

#     return parser.parse_args()

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

def get_scoring_dict_from_csv(file_name):
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
	IFH2 = open(file_name, "r")
	csv_list = []
	for csv_file in IFH2.readlines():
		csv_file = csv_file.strip("\n")
		csv_list.append(csv_file)

	dict_1 = compile_scores(csv_list[0])
	dict_2 = compile_scores(csv_list[1])
	dict_3 = compile_scores(csv_list[2])
	dict_4 = compile_scores(csv_list[3])
	dict_5 = compile_scores(csv_list[4])
	dict_6 = compile_scores(csv_list[5])


	for pair in dict_1.keys():
		if pair not in all_score_dict.keys():
			all_score_dict[pair] = []
			all_score_dict[pair].append(dict_1[pair])
			all_score_dict[pair].append(dict_2[pair])
			all_score_dict[pair].append(dict_3[pair])
			all_score_dict[pair].append(dict_4[pair])
			all_score_dict[pair].append(dict_5[pair])
			all_score_dict[pair].append(dict_6[pair])
		# else:
		# 	all_score_dict[pair].append(dict1[pair])
		# 	all_score_dict[pair].append(dict2[pair])
		# 	all_score_dict[pair].append(dict3[pair])
		# 	all_score_dict[pair].append(dict4[pair])
		# 	all_score_dict[pair].append(dict5[pair])
		# 	all_score_dict[pair].append(dict6[pair])

	#print(all_score_dict)
	return all_score_dict


def get_training_data(file_name):
	# X_train, y_train = classify_abs.preprocess_ml_dataset("test_subset_iedb_ml_dataset_filtered.csv")
	X_train, y_train = classify_abs.preprocess_ml_dataset(file_name)
	return X_train, y_train

def train_classifiers(x_train, y_train):
	# Trains data, then saves the model as pickle file.
	rf_classifier = classify_abs.RF(x_train, y_train)
	gnb_classifier = classify_abs.GNB(x_train, y_train)

	with open("rf_classifier.pkl", "wb") as f:
		pickle.dump(rf_classifier, f)
	
	with open("gnb_classifier.pkl", "wb") as f:
		pickle.dump(gnb_classifier, f)

def get_classifiers(rf_pkl, gnb_pkl):
	with open("rf_classifier.pkl", "rb") as f:
		rf_classifier = pickle.load(f)
	
	with open("gnb_classifier.pkl", "rb") as f:
		gnb_classifier = pickle.load(f)
	
	return rf_classifier, gnb_classifier


# def _get_classifiers(x_train, y_train):
# 	# Trains data, then saves the model as pickle file.
# 	rf_classifier = classify_abs.RF(x_train, y_train)
# 	gnb_classifier = classify_abs.GNB(x_train, y_train)
	
# 	return rf_classifier, gnb_classifier

def get_results(complete_score_dict, rf_classifier, gnb_classifier):
	with open("output.csv", "w", newline='') as csvfile:
		outfile_writer = csv.writer(csvfile, delimiter=',')
		outfile_writer.writerow(["Antibody pair","RF Prediction", "GNB Prediction"])
		for ab_pair in complete_score_dict.keys():
			rowline = []
			rowline.append(ab_pair)
			#input_data = classify_abs.preprocess_input_data([0.98,1,1,1,1,0.98])
			input_data = classify_abs.preprocess_input_data(complete_score_dict[ab_pair])
			#print(input_data)

			output_rf = rf_classifier.predict(input_data)
			output_gnb = gnb_classifier.predict(input_data)

			#print(output_rf)
			#print(output_gnb)

			if output_rf == 0:
				if output_gnb == 0:
					#print("Doesn't bind to same epitope as given antibody\n")
					rowline.append(output_rf)
					rowline.append(output_gnb)
					rowline.append("0")
				elif output_gnb == 1:
					#print("Binds to same epitope as given antibody\n")
					rowline.append(output_rf)
					rowline.append(output_gnb)
					rowline.append("1")
			elif output_rf == 1:
				#print("Binds to same epitope as given antibody\n")
				rowline.append(output_rf)
				rowline.append(output_gnb)
				rowline.append("1")
			outfile_writer.writerow(rowline)


def main():
	score_dict = get_scoring_dict_from_csv("list_csv_files")
	x_train, y_train = get_training_data("test_subset_iedb_ml_dataset_filtered.csv")

	# Saves as pickle file
	train_classifiers(x_train, y_train)

	# Read from pickle file
	rf_classifier, gnb_classifier = get_classifiers(x_train, y_train)

	# Writes out to file
	get_results(score_dict, rf_classifier, gnb_classifier)



if __name__ == '__main__':
	main()