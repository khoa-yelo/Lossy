"""
Module for Lossy compression of DNA sequences
Author: Khoa Hoang
Date: 10/23/2024
"""
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt

import Bio
from Bio import SeqIO
from Bio.Seq import Seq


def split_kmers(fasta_file, k, output_file):
    """
    Split sequences from a FASTA file into k-mers and write them to a new FASTA file.

    :param fasta_file: Path to the input FASTA file.
    :param k: Length of the k-mers.
    :param output_file: Path to the output FASTA file.
    """
    with open(output_file, 'w') as out_fasta:
        for record in SeqIO.parse(fasta_file, "fasta"):
            seq = str(record.seq)
            seq_id = record.id

            # Generate k-mers from the sequence
            for i in range(len(seq) - k + 1):
                kmer = seq[i:i + k]
                kmer_id = f"{seq_id}_{i}"
                
                # Write to output FASTA file
                out_fasta.write(f">{kmer_id}\n{kmer}\n")


class SeqEncoder:

    def __init__(self, method):
        self.method = method

    def encode(self, seq):
        if self.method == "translation":
            return self.translate(seq)

    def translate(self, seq):
        seq = Seq(seq)
        try:
            translated_seq = seq.translate()
        # if error encounter during translation, replace with 'N'
        except:
            print('Error encountered during translation')
            translated_seq = 'N'
        return str(translated_seq)


class SeqDecoder:

    def __init__(self, dictionary, method = "direct_mapping"):
        self.dictionary = dictionary
        self.method = method

    def decode(self, seq):
        if self.method == "direct_mapping":
            return self.direct_mapping(seq)
   
    def direct_mapping(self, seq):
        return "".join([self.dictionary[ele] for ele in seq])

class SeqFileEncoder:

    def __init__(self, method):
        self.method = method
        self.seq_ids = []
        self.seqs = []
        self.encoded_seqs = []
        self.encoder_method = None

    def encode(self, input_file, output_file):
        # Read file
        self.read_file(input_file)

        # Encode
        self.encoder_method = SeqEncoder(self.method)
        for seq in self.seqs:
            self.encoded_seqs.append(self.encoder_method.encode(seq))

        # Write output
        self.write_encoded_fasta(output_file)

    def read_file(self, file):
        print('Reading file...')
        file_format = file.split('.')[-1]
        assert file_format in ['fasta', 'fastq'], 'File format must be fasta or fastq'
        ids, seqs = [], []
        with open(file, 'r') as f:
            for record in SeqIO.parse(f, file_format):
                ids.append(record.id)
                seqs.append(str(record.seq))
        self.seq_ids = ids
        self.seqs = seqs
        print('File read successfully')

    def set_method(self, method):
        self.method = method
    
    def get_method(self):
        return self.method
    
    def write_encoded_fasta(self, output):
        assert output.endswith('.fasta'), 'Output file must be a fasta file'
        with open(output, 'w') as f:
            for i in range(len(self.seq_ids)):
                f.write('>' + self.seq_ids[i] + '\n')
                f.write(str(self.encoded_seqs[i]) + '\n')


class SeqFileDecoder:
    def __init__(self, dictionary, method):
        self.dictionary = dictionary
        self.method = method
        self.seq_ids = []
        self.seqs = []
        self.decoded_seqs = []
        self.decoder_method = None

    def decode(self, input_file, output_file):
        # Read file
        self.read_file(input_file)

        # Encode
        self.decoder_method = SeqDecoder(self.dictionary, self.method)
        for seq in self.seqs:
            self.decoded_seqs.append(self.decoder_method.decode(seq))
        # Write output
        self.write_decoded_fasta(output_file)

    def read_file(self, file):
        print('Reading file...')
        file_format = file.split('.')[-1]
        assert file_format in ['fasta', 'fastq'], 'File format must be fasta or fastq'
        ids, seqs = [], []
        with open(file, 'r') as f:
            for record in SeqIO.parse(f, file_format):
                ids.append(record.id)
                seqs.append(str(record.seq))
        self.seq_ids = ids
        self.seqs = seqs
        print('File read successfully')

    def set_method(self, method):
        self.method = method
    
    def get_method(self):
        return self.method
    
    def write_decoded_fasta(self, output):
        assert output.endswith('.fasta'), 'Output file must be a fasta file'
        with open(output, 'w') as f:
            for i in range(len(self.seq_ids)):
                f.write('>' + self.seq_ids[i] + '\n')
                f.write(str(self.decoded_seqs[i]) + '\n')


def parse_args():
    parser = argparse.ArgumentParser(description='Lossy compression of DNA sequences')
    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')

    # Sub-parser for splitting k-mers
    parser_split = subparsers.add_parser('split', help='Split sequences into k-mers')
    parser_split.add_argument('fasta_file', type=str, help='Path to the input FASTA file')
    parser_split.add_argument('output_file', type=str, help='Path to the output FASTA file')
    parser_split.add_argument('k', type=int, help='Length of the k-mers')

    # Sub-parser for encoding sequences
    parser_encode = subparsers.add_parser('encode', help='Encode sequences')
    parser_encode.add_argument('input_file', type=str, help='Path to the input FASTA file')
    parser_encode.add_argument('output_file', type=str, help='Path to the output FASTA file')
    parser_encode.add_argument('method', type=str, help='Encoding method')

    # Sub-parser for decoding sequences
    parser_decode = subparsers.add_parser('decode', help='Decode sequences')
    parser_decode.add_argument('input_file', type=str, help='Path to the input FASTA file')
    parser_decode.add_argument('output_file', type=str, help='Path to the output FASTA file')
    parser_decode.add_argument('method', type=str, help='Decoding method')
    parser_decode.add_argument('dictionary', type=str, help='Dictionary for decoding')


    return parser.parse_args()

def main():
    args = parse_args()

    if args.command == 'split':
        split_kmers(args.fasta_file, args.k, args.output_file)

    if args.command == 'encode':
        encoder = SeqFileEncoder(args.method)
        encoder.encode(args.input_file, args.output_file)

    if args.command == 'decode':
        with open(args.dictionary, 'r') as f:
            dictionary = json.load(f)
        decoder = SeqFileDecoder(dictionary, args.method)
        decoder.decode(args.input_file, args.output_file)


if __name__ == '__main__':
    main()