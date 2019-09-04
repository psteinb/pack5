import h5py
import numpy as np
from pathlib import Path
import json
from argparse import ArgumentParser
import sys
from glob import glob

def main():

    parser = ArgumentParser(description='pack .npy and related .json files as h5 files (the each json file is used to as attributes to the hdf5 dataset created for each numpy file)')

    parser.add_argument('--numpy-wc', action='store', type=str,
                        default=None,
                        help='wildcard statement to use for finding input numpy files, e.g. "./data_*npy" to find all files that match in the current directory')
    parser.add_argument('--json-wc', action='store', type=str,
                        default=None,
                        help='wildcard statement to use for finding input json files, e.g. "./pars*json" to find all files that match in the current directory')

    parser.add_argument('--numpy-list', action='store', type=str,
                        default=None,
                        help='path to text file which lists all required numpy file paths (one per line)')

    parser.add_argument('--json-list', action='store', type=str,
                        default=None,
                        help='path to text file which lists all required json file paths (one per line)')

    parser.add_argument('--files-per-chunk', action='store', type=int,
                        default=-1,
                        help='use <files-per-chunk> files per output file')

    parser.add_argument('--output', action='store', type=str,
                        default="output.h5",
                        help='name of output file (please end with .h5)')

    args = parser.parse_args()
    if not args.numpy_list and not args.numpy_wc:
        parser.print_help()
        sys.exit(1)

    npf = []
    if args.numpy_list:
        if Path(args.numpy_list).exists():
            npf = [ Path(name) for name in open(args.numpy_list).readlines() ]
        else:
            print(f"Error: {args.numpy_list} does not appear to exist")
            sys.exit(1)
    else:
        try:
            gfiles = glob(args.numpy_wc)
        except Exception as ex:
            print(f"Error: wildcard statement {args.numpy_wc} is not understood by glob",ex)
            raise
        npf = [ Path(name) for name in gfiles ]

    jsonf = []
    if args.json_list:
        if Path(args.json_list).exists():
            jsonf = [ Path(name) for name in open(args.json_list).readlines() ]
        else:
            print(f"Error: {args.json_list} does not appear to exist")
            sys.exit(1)
    else:
        try:
            gfiles = glob(args.json_wc)
        except Exception as ex:
            print(f"Error: wildcard statement {args.json_wc} is not understood by glob",ex)
            raise
        jsonf = [ Path(name) for name in gfiles ]

    if len(jsonf) != len(npf):
        print(f"Error: Number of json files {len(jsonf)} does not match number of numpy files {len(npf)}")
        sys.exit(1)

    arrays = [ np.load(f) for f in npf ]
    jattr  = [ json.load(open(j)) for j in jsonf ]

    if args.files_per_chunk > len(npf):
        print(f"Error: files per chunk {args.files_per_chunk} larger than numpy files found {len(npf)}")
        sys.exit(1)

    expected_nchunks = 1 if args.files_per_chunk < 2 else len(arrays)//args.files_per_chunk
    current_chunk = 0
    max_chunk_digits = len(str(expected_nchunks))
    suffix_template = "_{0:0"+str(max_chunk_digits)+"d}.h5"
    output = Path(args.output)
    if expected_nchunks != 1:
        output = Path(args.output.replace(".h5",suffix_template.format( current_chunk )))

    h5o = h5py.File(str(output))

    for fi,ar,js in zip(npf,arrays,jattr):
        ds = h5o.create_dataset(str(fi),
                                data=ar,
                                compression="lzf")
        for k,v in js.items():
            if isinstance(v,type(str())):
                ds.attrs.create(k,v, None, dtype=f"<S{len(v)}")
            else:
                ds.attrs.create(k,v)

        if expected_nchunks > 1:
            index = npf.index(fi)
            if index % args.files_per_chunk == 0:
                h5o.close()
                del h5o
                output = Path(args.output.replace(".h5",suffix_template.format( current_chunk )))
                h5o = h5py.File(str(output))
                current_chunk += 1

    if expected_nchunks == 1:
        current_chunk += 1

    print(f"Wrote {current_chunk}/{expected_nchunks} .h5 files from {len(npf)} inputs")



if __name__ == '__main__':
    main()
