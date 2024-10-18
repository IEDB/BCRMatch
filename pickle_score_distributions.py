import pandas as pd
import pickle
from pathlib import Path


def main():
    # Modify these three variables appropriately
    # TODO: Create argument parser for this
    # filename = 'percentile_rank_dataset.csv'
    # outfile_dir = './pickles/percentile_ranks'
    # pr_df = pd.read_csv(f'./datasets/{filename}')
    # filename = 'output_filrered_newtrain.csv'

    # Set file paths
    curr_file = Path(__file__).parent
    outfile_dir = curr_file / 'pickles' / 'score_distributions'
    
    # Create directory path if it does not exist
    if not outfile_dir.is_dir(): 
        outfile_dir.mkdir(parents=True, exist_ok=True)

    # Read Mahita's first and second data, and combine them
    df1 = pd.read_csv('output_filrered_newtrain.csv') 
    df2 = pd.read_csv('output_filtered_scv2_newtrain.csv')
    pr_df = pd.concat([df1, df2], axis=0)

    col_names = [col_name for col_name in list(pr_df.columns) if 'Prediction' in col_name]

    for col_name in col_names :
        # retrieve only the classifier name
        file_name = col_name.strip().split(' ')[0].lower()
        
        if file_name == 'lr' :
            file_name = 'log_reg'

        series = pr_df[col_name]

        pickle_file_loc = f"{outfile_dir}/{file_name}.pkl"

        with open(pickle_file_loc, 'wb') as f:
            pickle.dump(series, f)

    print('done')

if __name__ == '__main__':
    main()