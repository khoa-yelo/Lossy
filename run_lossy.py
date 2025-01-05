import subprocess
import os
from os.path import join
import argparse

# input directory containing the input files
# output directory to store the output files

SLURM_ARRAY_TASK_ID = int(os.getenv("SLURM_ARRAY_TASK_ID", -1))
SLURM_ARRAY_TASK_COUNT = int(os.getenv("SLURM_ARRAY_TASK_COUNT", -1))


def run_lossy(input_dir, output_dir, encode_method, decode_method, dictionary, k):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        print(f"Creating output directory {output_dir}")
        os.makedirs(output_dir)
    
    # Get the list of input files
    input_files = os.listdir(input_dir)
    for i, file in enumerate(input_files):
        print(f"Processing file {file}")
        print(f"SLURM_ARRAY_TASK_ID: {SLURM_ARRAY_TASK_ID}, SLURM_ARRAY_TASK_COUNT: {SLURM_ARRAY_TASK_COUNT}")
        if i % SLURM_ARRAY_TASK_COUNT != SLURM_ARRAY_TASK_ID:
            continue
        # Get the file name
        file_name = file.rsplit('.', 1)[0]
        
        # Set the input and output file paths
        input_file = join(input_dir, file)
        encoded_output_file = join(output_dir, f"{file_name}.encoded.fasta")
        decoded_output_file = join(output_dir, f"{file_name}.decoded.fasta")
        encoded_split_output_file = join(output_dir, f"{file_name}.encoded.split.fasta")

        # Encode the input file
        encode_command = f"python /oak/stanford/groups/horence/khoa/scratch/scripts/Lossy/lossy.py encode {input_file} {encoded_output_file} {encode_method}"
        print(encode_command)
        subprocess.run(encode_command, shell=True, check=True)
        # Split encoded file
        split_command = f"python /oak/stanford/groups/horence/khoa/scratch/scripts/Lossy/lossy.py split {encoded_output_file} {encoded_split_output_file} {k}"
        subprocess.run(split_command, shell=True, check=True)
        # Decode the output file
        decode_command = f"python /oak/stanford/groups/horence/khoa/scratch/scripts/Lossy/lossy.py decode {encoded_split_output_file} {decoded_output_file} {decode_method} {dictionary}"
        subprocess.run(decode_command, shell=True, check=True)
    
def parse_args():
    parser = argparse.ArgumentParser(description='Lossy compression of DNA sequences')
    parser.add_argument('input_dir', type=str, help='Path to the input directory')
    parser.add_argument('output_dir', type=str, help='Path to the output directory')
    parser.add_argument('encode_method', type=str, help='Encoding method')
    parser.add_argument('decode_method', type=str, help='Decoding method')
    parser.add_argument('dictionary', type=str, help='Dictionary for decoding')
    parser.add_argument('k', type=int, help='Length of the k-mers')
    return parser.parse_args()

def main():
    args = parse_args()
    print(args)
    run_lossy(args.input_dir, args.output_dir, args.encode_method, args.decode_method, args.dictionary, args.k)
    print("Done")
if __name__ == '__main__':
    main()