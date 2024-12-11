# from path import Path
import pandas as pd
from anarci import run_anarci

    
def extract_cdr1(sequence):
    # These limits are constant variables for both heavy and light chains
    CDR1_SEQUENCE_LIMIT = (27, 38)
    output = run_anarci(sequence)
    cdr1 = ''.join([y for x,y in output[1][0][0][0] if (x[0] in range(CDR1_SEQUENCE_LIMIT[0], CDR1_SEQUENCE_LIMIT[1]+1))&(y != '-')])
    return(cdr1)

def extract_cdr2(sequence):
    # These limits are constant variables for both heavy and light chains
    CDR2_SEQUENCE_LIMIT = (56, 65)
    output = run_anarci(sequence)
    cdr2 = ''.join([y for x,y in output[1][0][0][0] if (x[0] in range(CDR2_SEQUENCE_LIMIT[0], CDR2_SEQUENCE_LIMIT[1]+1))&(y != '-')])
    return(cdr2)

def extract_cdr3(sequence):
    # These limits are constant variables for both heavy and light chains
    CDR3_SEQUENCE_LIMIT = (105, 117)
    output = run_anarci(sequence)
    cdr3 = ''.join([y for x,y in output[1][0][0][0] if (x[0] in range(CDR3_SEQUENCE_LIMIT[0], CDR3_SEQUENCE_LIMIT[1]+1))&(y != '-')])
    return(cdr3)


def read_fasta(file_path):
    with open(file_path, 'r') as file:
        sequence_id = None
        sequence = ''
        sequences = {}

        for line in file:
            line = line.strip()
            if line.startswith('>'):
                if sequence_id:  # Save the previous sequence
                    sequences[sequence_id] = sequence
                sequence_id = line[1:]  # Get the sequence ID (remove '>')
                sequence = ''
            else:
                sequence += line  # Append sequence data

        if sequence_id:  # Save the last sequence
            sequences[sequence_id] = sequence

    return sequences


def main():
    heavy_chain_fasta_file = '/mnt/c/Users/USER/NG-IEDB/cli-tools/BCRMatch/examples/heavy_chain_seq_input.fasta'
    heavy_seqs = read_fasta(heavy_chain_fasta_file)

    light_chain_fasta_file = '/mnt/c/Users/USER/NG-IEDB/cli-tools/BCRMatch/examples/light_chain_seq_input.fasta'
    light_seqs = read_fasta(light_chain_fasta_file)
    # print(heavy_seqs)
    # print(light_seqs)
    # print(heavy_seqs.keys())
    # print(light_seqs.keys())

    col_names = ['Seq_Name', 'CDRL1', 'CDRL2', 'CDRL3', 'CDRH1', 'CDRH2', 'CDRH3']
    result_df = pd.DataFrame(columns=col_names)

    # Assuming that the sequence ID for heavy and light chains are the same.
    seq_ids = list(heavy_seqs.keys())

    for id in seq_ids:
        heavy_sequence = heavy_seqs[id]
        light_sequence = light_seqs[id]

        cdrh1_seq = extract_cdr1(heavy_sequence)
        cdrh2_seq = extract_cdr2(heavy_sequence)
        cdrh3_seq = extract_cdr3(heavy_sequence)

        cdrl1_seq = extract_cdr1(light_sequence)
        cdrl2_seq = extract_cdr2(light_sequence)
        cdrl3_seq = extract_cdr3(light_sequence)

        result_df.loc[len(result_df)] = [
            id,
            cdrl1_seq,
            cdrl2_seq,
            cdrl3_seq,
            cdrh1_seq,
            cdrh2_seq,
            cdrh3_seq
        ]

    print(result_df)
        

    



if __name__=='__main__':
    main()