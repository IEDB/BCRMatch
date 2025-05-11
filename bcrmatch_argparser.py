import os
import sys
import argparse
import pandas as pd
import textwrap
from pathlib import Path

def is_running_in_anarci_docker():
    try:
        if os.path.exists('/.dockerenv') and os.getenv('CONTAINER_TYPE') == 'anarci':
            return True
    except:
        pass
    return False

# Only import get_cdr_table if running in anarci Docker
if is_running_in_anarci_docker():
    from anarci_input_converter import get_cdr_table


class BCRMatchArgumentParser:
    parser = argparse.ArgumentParser(
                    usage = '%(prog)s [-i] <input_tsv> [-tc] <training_dataset_csv>',
                    description = 'This is a command-line tool interface for BCRMatch.',
                    formatter_class=argparse.RawTextHelpFormatter)	
    
    MODELS = ['rf', 'gnb', 'log_reg', 'xgb', 'ffnn']

    def __init__(self):
        self._root_dir = self.find_root_dir()
        self._training_mode = ''
        self._training_dataset = ''
        self._training_dataset_name = ''
        self._training_dataset_version = ''
        self._dataset_db = ''
        self._models_dir = ''
        self._force_retrain_flag = False
        self._list_datasets_flag = False
        self._output_location = ''
        self._verbose = False

    def parse_args(self, args):
        # Optional Arguments (Flags)
        # we need a parameter to define whether we should run training or prediction
        # prediction should be the default
        self.parser.add_argument('--input-tsv', '-i', dest = 'input_tsv', required = False,
                            nargs = '?', 
                            type = argparse.FileType('r'),
                            default = argparse.SUPPRESS,
                            help = textwrap.dedent('''\
                                TSV file containing information about CDRLs and CDRHs.
                                ex)
                                    Seq_Name    CDRL1    CDRL2    CDRL3    CDRH1    CDRH2    CDRH3
                                    1   NNIGSKS     DDS    WDSSSDHA    GFTFDDY    SWNTGT    RSYVVAAEYYFH
                                    2   SQDISNY     YTS    DFTLPF    GYTFTNY    YPGNGD    GGSYRYDGGFD
                                    3   ASGNIHN     YYT    HFWSTPR    GFSLTGY    WGDGN    RDYRLD
                                    4   SESVDNYGISF     AAS    SKEVPL    GYTFTSS    HPNSGN    RYGSPYYFD
                                    5   ASQDISN     YFT    QYSTVPW    GYDFTHY    NTYTGE    PYYYGTSHWYFD
                            '''
                            ))
        self.parser.add_argument('--input-cdrh', '-ch', 
                            dest = 'cdrh_fasta', 
                            required = False,
                            nargs = '*', 
                            type = argparse.FileType('r'),
                            default = argparse.SUPPRESS,
                            help = 'FASTA file containing 3 CDRHs.')
        self.parser.add_argument('--input-cdrl', '-cl', 
                            dest = 'cdrl_fasta', 
                            required = False,
                            nargs = '*', 
                            type = argparse.FileType('r'),
                            default = argparse.SUPPRESS,
                            help = 'FASTA file containing 3 CDRLs.')
        
        # Only add full chain FASTA arguments if running in anarci Docker
        if is_running_in_anarci_docker():
            self.parser.add_argument('--full-heavy-chain-fasta', '-fh', 
                                dest = 'full_heavy_fasta', 
                                required = False,
                                nargs = 1, 
                                type = argparse.FileType('r'),
                                default = argparse.SUPPRESS,
                                help = 'Full length heavy sequences in FASTA format.')
            self.parser.add_argument('--full-light-chain-fasta', '-fl', 
                                dest = 'full_light_fasta', 
                                required = False,
                                nargs = 1, 
                                type = argparse.FileType('r'),
                                default = argparse.SUPPRESS,
                                help = 'Full length light sequences in FASTA format.')
        self.parser.add_argument('--database', '-db', 
                            dest = 'database', 
                            required = False,
                            type = str,
                            default = 'models/dataset-db',
                            help = textwrap.dedent('''\
                            Path to the database/json created or modified in the training.
                            (The 'dataset-db' in the code directory will be used as the default database.)
                            '''))
        self.parser.add_argument('--models-dir', '-md', 
                            dest = 'models_dir', 
                            required = False,
                            type = str,
                            default = 'models/models/',
                            help = textwrap.dedent('''\
                            Path to the directory that contains all the pickled models.
                            '''))
        self.parser.add_argument('--training-dataset-csv', '-tc',
                            dest = 'training_dataset_csv',
                            required = False,
                            help = 'Path to the CSV file that will be used for training.')
        self.parser.add_argument('--training-dataset-name', '-tn', 
                            dest = 'training_dataset_name', 
                            required = False, 
                            type = str,
                            default = argparse.SUPPRESS,
                            help = textwrap.dedent('''\
                            Rename the training dataset CSV to be stored in the database.
                            This will be used to lookup dataset in the database during prediction.
                            '''))
        self.parser.add_argument('--verbose', '-v', 
                    dest = 'verbose', 
                    required = False, 
                    # type = bool,
                    action='store_true',
                    default = argparse.SUPPRESS,
                    help = textwrap.dedent('''\
                    Display the complete result data to the user.
                    '''))
        # TODO: This needs to be str type, as users can provide their custom versions.
        self.parser.add_argument('--training_dataset-version', '-tv',
                            dest = 'training_dataset_version',
                            required = False,
                            type = int,
                            default = '20240916',
                            help = 'A version number of the dataset.')
        self.parser.add_argument('--training-mode', '-tm',
                            dest = 'training_mode',
                            required = False,
                            action='store_true',
                            help = 'Train the classifiers on the provided dataset.')
        self.parser.add_argument('--force-training', '-f',
                            dest = 'retrain_dataset',
                            required = False,
                            action='store_true',
                            help = 'Force training if the same dataset name and version exist.')
        self.parser.add_argument('--list-datasets', '-l',
                            dest = 'list_datasets',
                            required = False,
                            action='store_true',
                            help = 'Displays all unique dataset/version.')
        self.parser.add_argument('--output', '-o', 
                            dest = 'output', 
                            required = False,
                            nargs = '?', 
                            type = str,
                            action='store',
                            default = argparse.SUPPRESS,
                            help = textwrap.dedent('''\
                            Path to the output file.
                            (The default output file is 'output.csv'.)
                            '''))

        # Positional Arguments (User input parameters)
        self.parser.add_argument('inline_seqs', type = str,
                            nargs = '?',
                            help = 'Space separated peptide sequences.')


        return self.parser.parse_args(), self.parser
    

    def find_root_dir(self, start_dir=None, anchor_files=None):
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

    def get_anarci_input_to_tsv(self, args):
        ''' DESCRIPTION:
            Takes two FASTA files: one full heavy sequences FASTA and one full light sequences FASTA file. 
            This then uses ANARCI to pull out the CDRL and CDRH sequences and creates a table.
        '''
        if not is_running_in_anarci_docker():
            raise NotImplementedError("ANARCI functionality is only available when running in the anarci Docker container")
            
        full_heavy_file = getattr(args, 'full_heavy_fasta')[0]
        full_light_file = getattr(args, 'full_light_fasta')[0]
        df = get_cdr_table(full_heavy_file.name, full_light_file.name)
        return df
    
    def get_input_tsv_content(self, args) :
        ''' DESCRIPTION:
            This will open the TSV file and return its content.

            Return Value: List of lists
            It returns list containing each row in a list format.   
        '''
        file_name = getattr(args, 'input_tsv').name
        
        return pd.read_table(file_name).to_dict('list')
    
    def get_sequences(self, args, parser) :
        ''' DESCRIPTION:
            Reads either TSV file or list of 6 FASTA files (3 CDRLs, 3 CDRHs), and turns
            them into a dictionary in the following format:
            {
                'Seq_Name': [1, 2, 3, 4, 5], 
                'CDRL1': ['NNIGSKS', 'SQDISNY', 'ASGNIHN', 'SESVDNYGISF', 'ASQDISN'], 
                'CDRL2': ['DDS', 'YTS', 'YYT', 'AAS', 'YFT'], 
                'CDRL3': ['WDSSSDHA', 'DFTLPF', 'HFWSTPR', 'SKEVPL', 'QYSTVPW'], 
                'CDRH1': ['GFTFDDY', 'GYTFTNY', 'GFSLTGY', 'GYTFTSS', 'GYDFTHY'], 
                'CDRH2': ['SWNTGT', 'YPGNGD', 'WGDGN', 'HPNSGN', 'NTYTGE'], 
                'CDRH3': ['RSYVVAAEYYFH', 'GGSYRYDGGFD', 'RDYRLD', 'RYGSPYYFD', 'PYYYGTSHWYFD']
            }
        '''
        _NUM_FASTA_FILES = 3

        # CASE 1: User provides TSV file
        if 'input_tsv' in args:
            return self.get_input_tsv_content(args)

        # CASE 2: User provides full heavy and light fasta files (total 2 files)
        if is_running_in_anarci_docker():
            if 'full_heavy_fasta' in args and 'full_light_fasta' not in args:
                raise parser.error('missing full light file')

            if 'full_light_fasta' in args and 'full_heavy_fasta' not in args:
                raise parser.error('missing full heavy file')

            if 'full_light_fasta' in args and 'full_heavy_fasta' in args:
                return self.get_anarci_input_to_tsv(args)
        else:
            if 'full_heavy_fasta' in args or 'full_light_fasta' in args:
                raise parser.error('Full chain FASTA input is only available when running in the anarci Docker container')
        
        # CASE 3: User provides 3 CDRL FASTA files and 3 CDRH FASTA files
        # Check if cdrh/cdrl flags are specified.
        if 'cdrh_fasta' not in args:
            raise parser.error('Please provide FASTA files containing CDRH sequences.')
        
        if 'cdrl_fasta' not in args:
            raise parser.error('Please provide FASTA files containing CDRL sequences.')
        
        # Check if 3 fasta files are provided for each cdrh and cdrl flags.
        if len(getattr(args, 'cdrh_fasta')) != _NUM_FASTA_FILES :
            raise parser.error('Please provide 3 CDRH fasta files.')

        if len(getattr(args, 'cdrl_fasta')) != _NUM_FASTA_FILES :
            raise parser.error('Please provide 3 CDRL fasta files.')

        if 'cdrh_fasta' in args and 'cdrl_fasta' in args :
            # NOTE: Is it safe to assume that the user will provide exact number of sequences for all?
            cdrh_files = getattr(args, 'cdrh_fasta')
            cdrl_files = getattr(args, 'cdrl_fasta')
            sequence_names = []
            sequence_series = []

            for i in range(_NUM_FASTA_FILES):
                _INDEX = i + 1
                cdrh_file = cdrh_files[i].name
                cdrl_file = cdrl_files[i].name

                with open(cdrh_file, 'r') as f:
                    cdrh_fcontent = [_.strip().replace('>','') for _ in f.readlines()]
                
                with open(cdrl_file, 'r') as f:
                    cdrl_fcontent = [_.strip().replace('>','') for _ in f.readlines()]

                # Retrieve sequence names (only have to perform once)
                if not sequence_names:
                    for i in range(len(cdrl_fcontent)):
                        if i%2 == 0 :
                            sequence_names.append(cdrl_fcontent[i])
                
                    sequence_series.append( pd.DataFrame({'Seq_Name': sequence_names}) )

                # Collect sequences into Series
                cdrl_col = []
                cdrh_col = []
                for i in range(len(cdrl_fcontent)):
                    if i%2:
                        cdrl_col.append(cdrl_fcontent[i])
                        cdrh_col.append(cdrh_fcontent[i])
                
                sequence_series.append( pd.DataFrame({'CDRL%s' %(_INDEX): cdrl_col}) )
                sequence_series.append( pd.DataFrame({'CDRH%s' %(_INDEX): cdrh_col}) )


            seq_df = pd.concat(sequence_series, axis=1)

            return seq_df.to_dict('list')

        return {} 


    # Properties for training mode
    @property
    def training_mode(self):
        return self._training_mode

    @training_mode.setter
    def training_mode(self, args):
        self._training_mode = getattr(args, 'training_mode')

    # Properties for training dataset
    @property
    def training_dataset(self):
        return self._training_dataset

    @training_dataset.setter
    def training_dataset(self, args):
        self._training_dataset = getattr(args, 'training_dataset_csv')

    # Properties for training dataset name
    @property
    def training_dataset_name(self):
        return self._training_dataset_name

    @training_dataset_name.setter
    def training_dataset_name(self, args):
        try:
            self._training_dataset_name = getattr(args, 'training_dataset_name')
        except:
            # Set the CSV file name as the default for the training_dataset_name
            training_dataset_file = self.training_dataset
            training_dataset_name = os.path.basename(training_dataset_file)
            self._training_dataset_name = os.path.splitext(training_dataset_name)[0]

    # Properties for training dataset version
    @property
    def training_dataset_version(self):
        return self._training_dataset_version

    @training_dataset_version.setter
    def training_dataset_version(self, args):
        self._training_dataset_version = getattr(args, 'training_dataset_version')

    # Properties for force retrain flag
    @property
    def force_retrain_flag(self):
        return self._force_retrain_flag

    @force_retrain_flag.setter
    def force_retrain_flag(self, args):
        self._force_retrain_flag = getattr(args, 'retrain_dataset')

    # Properties for list datasets flag
    @property
    def list_datasets_flag(self):
        return self._list_datasets_flag

    @list_datasets_flag.setter
    def list_datasets_flag(self, args):
        self._list_datasets_flag = getattr(args, 'list_datasets')

    # Properties for database
    @property
    def database(self):
        return self._dataset_db

    @database.setter
    def database(self, args):
        db_path = getattr(args, 'database')
        self._dataset_db = f'{self._root_dir}/{db_path}'

    # Properties for models directory
    @property
    def models_dir(self):
        return self._models_dir

    @models_dir.setter
    def models_dir(self, args):
        models_dir = getattr(args, 'models_dir')
        # Make sure the path has no trailing '/'
        if models_dir.endswith(os.sep):
            models_dir = models_dir[:-1]
        self._models_dir = f'{self._root_dir}/{models_dir}'

    # Properties for output location
    @property
    def output_location(self):
        return self._output_location

    @output_location.setter
    def output_location(self, args):
        output_loc = getattr(args, 'output')
        output_dir = Path(output_loc).parent.absolute()
        if not output_dir.is_dir():
            raise IsADirectoryError(f'{output_dir} folder does not exist. Please check your path.')
        self._output_location = output_loc

    # Properties for verbose flag
    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, args):
        self._verbose = getattr(args, 'verbose')

    # Properties for root directory
    @property
    def root_dir(self):
        return self._root_dir

    def validate(self, args):
        # Check list_datasets first before checking others
        # as this should take priority.
        if hasattr(args, 'list_datasets'):
            self.list_datasets_flag = args
            
            # terminate early only if 'list_datasets' is set to 'True'
            if getattr(args, 'list_datasets'):
                self.database = args
                return
            
        if hasattr(args, 'training_dataset_csv'):
            self.training_dataset = args

        self.training_dataset_name = args

        if hasattr(args, 'training_dataset_version'):
            self.training_dataset_version = args

        if hasattr(args, 'training_mode'):
            self.training_mode = args

        if hasattr(args, 'retrain_dataset'):
            self.force_retrain_flag = args

        if hasattr(args, 'database'):
            self.database = args
        
        if hasattr(args, 'models_dir'):
            self.models_dir = args
        
        if hasattr(args, 'output'):
            self.output_location = args
        
        if hasattr(args, 'verbose'):
            self.verbose = args
