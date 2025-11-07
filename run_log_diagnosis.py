import sys
import os

# Add the necessary directories to the system path to import custom modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'Drain3')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'log_diagnosis')))

# Importing necessary modules for preprocessing, templatizing, and anomaly detection
from preprocessing.preprocessing import Preprocessing
from Drain3.run_drain.run_drain import Templatizer
from log_diagnosis.anomaly import Anomaly
from argparse import ArgumentParser, ArgumentTypeError


def validate_boolean(value):
    value = value.lower()
    if value not in ('true', 'false'):
        raise ArgumentTypeError(f"Invalid value for boolean argument: {value}. Please use 'True' or 'False'.")
    return value == 'true'

# Import pandarallel for parallel processing capabilities
from pandarallel import pandarallel

if __name__ == "__main__":
    """
    Main script to preprocess log files, generate templates using Drain3, and produce an anomaly report.

    This script performs three main tasks:
    1. Preprocess the log files to clean, format, and temporally sort the log data using the `Preprocessing` class.
    2. Use the Drain3 algorithm (via the `Templatizer` class) to generate log templates from the preprocessed data.
    3. Generate an anomaly report based on the processed log templates using the `Anomaly` class.

    The script accepts several command-line arguments for input files, time range, output directories, 
    and an optional XML file for further analysis.

    Steps:
        1. Parse command-line arguments using `argparse`.
        2. Preprocess the input files using the `Preprocessing` class.
        3. Generate log templates with the `Templatizer` class.
        4. Produce an anomaly report with the `Anomaly` class.

    Command-line Arguments:
        --input_files (list of str): Paths to the input log files to be processed.
        --time_range (str): Time range for which analysis is needed (e.g., all-data).
        --output_dir (str): Path to the directory where output files (reports) will be saved.

    Example usage:
        python run_log_diagnosis.py --input_files file1.txt:file2.txt \
                                    --time_range 'all-data' --output_dir '/path/to/output' \
                                    --debug_mode True
    """

    # Create an argument parser to handle command-line input
    arg_parser = ArgumentParser()
    arg_parser.add_argument('--input_files', nargs="+", type=str, help='Input Files for anomaly report generation')
    arg_parser.add_argument('--time_range', type=str, help='Time range for which analysis needs to be done', default='all-data')
    arg_parser.add_argument('--output_dir', type=str, help='Directory where output will be stored')
    arg_parser.add_argument('--debug_mode', type=str, help='Enable debug mode for saving debug files', default=True)
    arg_parser.add_argument('--process_log_files', type=validate_boolean, help='Flag to indicate if logs should be processed', default=True)
    arg_parser.add_argument('--process_txt_files', type=validate_boolean, help='Flag to indicate if text should be processed', default=False)
    
    # Parse the arguments provided by the user
    args = arg_parser.parse_args()
    print(args)

    # Step 1: Initialize and run the preprocessing on the input files
    preprocessing_obj = Preprocessing(args.debug_mode)
    preprocessing_obj.preprocess(args.input_files, 
                                 args.time_range, 
                                 args.output_dir,
                                 args.process_log_files,
                                 args.process_txt_files)

    # preprocessing_obj.df columns: "text", "preprocessed_text", "truncated_log", "epoch", "timestamps", "file_names"
    # Step 2: Initialize the Templatizer and create log templates
    drain_config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Drain3', 'run_drain', 'drain3.ini'))
    templatizer = Templatizer(debug_mode=args.debug_mode, config_path=drain_config_path)
    templatizer.miner(preprocessing_obj.df, 
                    args.output_dir, 
                    args.output_dir + "/test_templates/tm-test.templates.json")


    # templatizer.df columns: "text", "preprocessed_text", "truncated_log", "epoch", "timestamps", "file_names", "test_ids"
    # Step 3: Initialize the Anomaly detector and generate the anomaly report
    anomaly_obj = Anomaly(args.debug_mode)
    anomaly_obj.get_anomaly_report(templatizer.df, 
                                   args.output_dir + f"/log_diagnosis/", 
                                   args.output_dir + f"/developer_debug_files/", 
                                   )
