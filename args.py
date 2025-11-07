from argparse import ArgumentParser
import json
import os
import time

from jinja2 import Environment, FileSystemLoader
import patoolib
from patoolib.util import PatoolError

def is_archive_file(file_paths):
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    
    return all(patoolib.is_archive(filepath) for filepath in file_paths)

def compute_cmdcheck_metrics(output_dir, time):
    with open(os.path.join(output_dir, "metrics", "cmdline_args_check.json"), 'w') as writer:
        json.dump({
            'cmdline_args_check_time_ms': time,
        }, writer)

def custom_exit(output_dir, start_time, err_code):
    compute_cmdcheck_metrics(output_dir, (time.time() - start_time) * 1000)
    exit(err_code)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input_files', type=str, nargs='+', help='List of input files for preprocessing')
    parser.add_argument('--output_dir', required=True)
    args = parser.parse_args()
    print(args)
    
    start = time.time()

    env = Environment(loader=FileSystemLoader('log_diagnosis/templates/'))
    html_template = env.get_template('error_message.html')
    error_flag = False

    if is_archive_file(args.input_files):
        error_message = (
                "AnalyzeSWSupport does not support archive files.<br><br>"
                "Best Practices for using AnalyzeSWSupport:<br>"
                "1. Unpack compressed files first before running the tool.<br>"
                "2. Do not launch the tool on the whole case directory.<br>"
                "3. After launching tool, select one or more files or folders from the browse button.<br>"
                "4. Select the proper TimeRange for the best processing time.<br><br>"
                     )
        error_flag = True
    else:
        error_message = ""  # Default error message when no conditions are met

    parent_dir = os.path.dirname(args.output_dir)
    err_code = 0

    if error_flag:
        rendered_html = html_template.render(error_message=error_message)
        output_file_path = os.path.join(args.output_dir, 'summary.html')
        with open(output_file_path, "w") as file:
            file.write(rendered_html)

        print(f"Rendered HTML saved to {output_file_path}")

        err_code = 102
        
    custom_exit(parent_dir, start, err_code)
