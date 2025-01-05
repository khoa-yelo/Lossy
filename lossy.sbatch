#!/bin/bash
#SBATCH --job-name=lossy      # Job name
#SBATCH --partition=horence
#SBATCH --output=lossy_%j.out  # Output file name (%j is the job ID)
#SBATCH --error=lossy_%j.err   # Error file name
#SBATCH --ntasks=1                      # Number of tasks (single task)
#SBATCH --cpus-per-task=2               # Number of CPU cores to allocate for the task (adjust as needed)
#SBATCH --time=10:00:00                 # Time limit hrs:min:sec
#SBATCH --mem=64G                        # Memory limit (adjust as needed)
#SBATCH --array=0-1                     # Array range

export IMAGE="python-sequtils-blast-splash-pfam_latest.sif"
export REPO="/oak/stanford/groups/horence/khoa/scratch/scripts/Lossy"
export ENV="singularity run -B $REPO $IMAGE"

config_file=$1

# parse config file for input_dir, output_dir, encode_method, decode_method, dictionary, k
input_dir=$(jq -r ".input_dir" $config_file)
output_dir=$(jq -r ".output_dir" $config_file)
encode_method=$(jq -r ".encode_method" $config_file)
decode_method=$(jq -r ".decode_method" $config_file)
dictionary=$(jq -r ".dictionary" $config_file)
k=$(jq -r ".k" $config_file)

echo "input_dir: $input_dir"
echo "output_dir: $output_dir"
echo "encode_method: $encode_method"
echo "decode_method: $decode_method"
echo "dictionary: $dictionary"
echo "k: $k"

$ENV python $REPO/run_lossy.py $input_dir $output_dir $encode_method $decode_method $dictionary $k
