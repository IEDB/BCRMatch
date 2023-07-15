#!/usr/bin/env python

def create_tcrmatch_input(filename):
	name = filename.split(".fasta")[0]
	IFH1 = open(filename, 'r')
	OFH1 = open(name+"_tcrinput.txt", "w")
	#OFH2 = open(name+"_identical.txt", "w"
	lines = IFH1.readlines()
	seq_dict = {}
	final_seq_dict = {}
	for line in lines:
		line = line.strip("\n")
		if line[0] == ">":
			seq_id = line.split(">")[1]

			seq_dict[seq_id] = []
				
			
		else:
			aa_list = []
			amino_acids = line
			for aa in amino_acids:
				if aa != "-":
					aa_list.append(aa)
			aa_seq = ''.join(aa_list)

			seq_dict[seq_id] = aa_seq
			OFH1.write("%s\n"%(aa_seq))
	OFH1.close()
	return(seq_dict)

def get_key(seq_id_dict, seq_value):
	keys = [k for k,value in seq_id_dict.items() if value == seq_value]
	return keys

def create_tcroutput(tcroutput_file, seq_id_dict):
	IFH = open(tcroutput_file, "r")
	OFH = open(tcroutput_file+".csv", "w")
	lines2 = IFH.readlines()
	tcr_results = {}
	tcr_details = {}
	for line2 in lines2:
		line2 = line2.strip("\n")
		fields = line2.split("\t")
		seq1 = fields[0]
		seq2 = fields[1]
		score = fields[2]
		if seq1 not in tcr_details:
			tcr_details[seq1] = {}
			if seq2 not in tcr_details[seq1]:
				tcr_details[seq1][seq2] = score
		else:
			if seq2 not in tcr_details[seq1]:
				tcr_details[seq1][seq2] = score
	#print(tcr_details)

	for x in tcr_details.keys():
		for y in tcr_details[x].keys():
			seqid_1 = get_key(seq_id_dict, x)
			seqid_2 = get_key(seq_id_dict, y)

			for i in seqid_1:
				print(i)
				for j in seqid_2:
					print(j)

					if i not in tcr_results:
						tcr_results[i] = {}
						if j not in tcr_results[i]:
							tcr_results[i][j] = tcr_details[x][y]
					else:
						if j not in tcr_results[i]:
							tcr_results[i][j] = tcr_details[x][y]
	for p in tcr_results.keys():
		for q in tcr_results[p].keys():
			print(p,q,tcr_results[p][q])
			ab_pair = p+"_"+q
			OFH.write("%s,%s\n"%(ab_pair,tcr_results[p][q]))
	OFH.close()
