# from path import Path
import pandas as pd
from anarci import run_anarci


def extract_cdr(sequence, region):
    # Region refers to L1,2,3 or H1,2,3
    CDR1_SEQUENCE_LIMIT = (27, 38)
    CDR2_SEQUENCE_LIMIT = (56, 65)
    CDR3_SEQUENCE_LIMIT = (105, 117)
    cdr_upper_limit = 0
    cdr_lower_limit = 0

    if region == 1:
        cdr_lower_limit = CDR1_SEQUENCE_LIMIT[0]
        cdr_upper_limit = CDR1_SEQUENCE_LIMIT[1] + 1
    
    if region == 2:
        cdr_lower_limit = CDR2_SEQUENCE_LIMIT[0]
        cdr_upper_limit = CDR2_SEQUENCE_LIMIT[1] + 1

    if region == 3:
        cdr_lower_limit = CDR3_SEQUENCE_LIMIT[0]
        cdr_upper_limit = CDR3_SEQUENCE_LIMIT[1] + 1

    output = run_anarci(sequence)
    cdr = ''.join([y for x,y in output[1][0][0][0] if (x[0] in range(cdr_lower_limit, cdr_upper_limit))&(y != '-')])
    return(cdr)



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
    heavy_chain_fasta_file = 'examples/heavy_chain_seq_input.fasta'
    heavy_seqs = read_fasta(heavy_chain_fasta_file)

    light_chain_fasta_file = 'examples/light_chain_seq_input.fasta'
    light_seqs = read_fasta(light_chain_fasta_file)
    # print(heavy_seqs)
    # print(light_seqs)
    # print(heavy_seqs.keys())
    # print(light_seqs.keys())

    REGION_LIMIT = 3

    # Create empty result DataFrame
    col_names = ['Seq_Name', 'CDRL1', 'CDRL2', 'CDRL3', 'CDRH1', 'CDRH2', 'CDRH3']
    result_df = pd.DataFrame(columns=col_names)

    # Assuming that the sequence ID for heavy and light chains are the same.
    seq_ids = list(heavy_seqs.keys())

    for id in seq_ids:
        heavy_sequence = heavy_seqs[id]
        light_sequence = light_seqs[id]

        row = []
        for i in range(REGION_LIMIT):
            region = i + 1
            cdrh_seq = extract_cdr(heavy_sequence, region=region)
            cdrl_seq = extract_cdr(light_sequence, region=region)
            row.append(cdrh_seq) # all CDRH sequences will be stored on even indices
            row.append(cdrl_seq) # all CDRL sequences will be stored on odd indices

        # Rearrange so CDRLs stay ahead of CDRHs
        cdrhs = row[0::2]
        cdrls = row[1::2]
        result_df.loc[len(result_df)] = [id] + cdrls + cdrhs

    print(result_df)
    

if __name__=='__main__':
    main()