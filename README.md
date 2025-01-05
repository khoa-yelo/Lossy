# Lossy

## Overview 

SPLASH is currently engineered to operate on DNA sequences. However, SPLASH is a general framework that can be adapted to other alphabets. This repo provides a way to process DNA fasta files into encoded alphabets that are compatible with current SPLASH inputs. 

Repo files and folders

- codon_table.json: one-to-one mapping between amino acid and codon 
- config.json: input config (the only input needed)
- lossy.py: main script to encode and decode DNA to alternative alphabets
- run_lossy.py: all 3 steps in lossy.py is put togethered here (encode, split, decode)
- lossy.sbatch: sbatch script to be submitted to SLURM to run the code in parallel (adjust `--array` as needed)
- test_data: folder containing test inputs and outputs

## Method


An input DNA fasta file will go through 3 steps process

1. Encode (check `class SeqEncoder` in `lossy.py`)

DNA sequence is encode into different alphabets, currently support "translation" into protein sequence

2. Split 

Encoded sequence is splitted into kmers length `k` specified in config file. This ensures SPLASH does not process out of frame alphabets

3. Decode (check `class SeqDecoder` in `lossy.py`)

Splitted/Encoded sequences are mapped back to DNA alphabets to be compatible with SPLASH input. Currently support "direct mapping" with provided dictionary

Input config 

- "input_dir": dir contain input fastas
- "output_dir": dir contain output fastas
- "encode_method": encoding method, currentlu support  "translation",
- "decode_method": decoding method, currently support "direct_mapping" - map one to one from encoded alphabets back to DNA alphabets using dictionary,
- "dictionary": dictionary used in decoding step,
- "k": extender length in encoded (protein) alphabets


## Outputs

Each input fasta will result in 3 output corresponding to each step

```
*.encoded.fasta: encoded sequence, in example below encoded to protein sequence
*.encoded.split.fasta: encoded sequence is splitted into kmers length determined by `k` param in config
*.decoded.fasta: encoded sequence (protein sequence) mapped one-to-one back to DNA alphabets (hence lossy)

```

*.decoded.fasta should be used as input to SPLASH 

## Usage

### 1. Set up

Download Singularity image

```
singularity pull docker://scr.svc.stanford.edu/khoang99/contai
ners/python-sequtils-blast-splash-pfam
```

Modify REPO env argument corresponding to path to code repo in `lossy.sh`
```
export REPO="/oak/stanford/groups/horence/khoa/scratch/scripts/Lossy"
```

### 2. Run each step separately

Encode
```
python lossy.py encode {input_file} {encoded_output_file} {encode_method}
```

Split 
```
python lossy.py split {encoded_output_file} {encoded_split_output_file} {k}
```

Decode
```
python /lossy.py decode {encoded_split_output_file} {decoded_output_file} {decode_method} {dictionary}
```

### 3. Run 3 steps at once

```
python $REPO/run_lossy.py $input_dir $output_dir $encode_method $decode_method $dictionary $k
```

OR use SLURM if need to run multiple files in parallel

```
./lossy.sbatch config.json
```

Note: Adjust `--array` param in `lossy.sbatch` appropriately to process multiple files in parallel


## Example

Config  file 

```
{
    "input_dir": "/oak/stanford/groups/horence/khoa/scratch/scripts/Lossy/test_data/test_seqs",
    "output_dir": "/oak/stanford/groups/horence/khoa/scratch/scripts/Lossy/test_data/test_seqs_lossy",
    "encode_method": "translation",
    "decode_method": "direct_mapping",
    "dictionary": "/oak/stanford/groups/horence/khoa/scratch/scripts/Lossy/codon_table.json",
    "k": 18
}
```
1. Encode DNA fasta file to protein alphabets and decode back to DNA alphabets

```
./lossy.sbatch config.json
```

Output sequences at `test_data/test_seqs_lossy`

2. Construct `sample_sheet` for test sequences (DNA vs Protein samples) - `test_data/sample_sheet*.txt`

3. Run SPLASH on fasta DNA sequence before and after encoded to protein alphabets

```
/scratch/users/khoang99/build/splash2.6.1/splash '/oak/stanford/groups/horence/khoa/scratch/scripts/Lossy/test_data/sample_sheet_dna.txt'

/scratch/users/khoang99/build/splash2.6.1/splash '/oak/stanford/groups/horence/khoa/scratch/scripts/Lossy/test_data/sample_sheet_protein.txt'
```

Output at

```
/oak/stanford/groups/horence/khoa/scratch/scripts/Lossy/test_data/splash_out_dna
/oak/stanford/groups/horence/khoa/scratch/scripts/Lossy/test_data/splash_out_protein
```

It can be observed from the output results that the protein encoded SPLASH input allows detection of significant anchors while that is not the case for raw DNA input
```
/oak/stanford/groups/horence/khoa/scratch/scripts/Lossy/test_data/splash_out_dnaresult.after_correction.scores.top_effect_size_bin.tsv

/oak/stanford/groups/horence/khoa/scratch/scripts/Lossy/test_data/splash_out_protein/result.after_correction.scores.top_effect_size_bin.tsv
```

More info on processing a real dataset here

https://docs.google.com/document/d/11n-pascBntB66ieJpEEXOLjKFANWTZ5VFYYdiuaoHrU/edit?tab=t.0
