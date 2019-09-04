# pack5

python utility script to bundle multiple npz files into one hdf5

## Usage

This small script assumes that you have something like this:

``` shell
$ ls tests/*{json,npy}
tests/data_000000.npy  tests/data_000007.npy  tests/pars000004.json
tests/data_000001.npy  tests/data_000008.npy  tests/pars000005.json
tests/data_000002.npy  tests/data_000009.npy  tests/pars000006.json
tests/data_000003.npy  tests/pars000000.json  tests/pars000007.json
tests/data_000004.npy  tests/pars000001.json  tests/pars000008.json
tests/data_000005.npy  tests/pars000002.json  tests/pars000009.json
tests/data_000006.npy  tests/pars000003.json
```

The json files go as metadata with the `.npy` files. As mentioned it's the goal of this small script to pack the `.npy` files into a hdf5 compliant format. This can be done in 2 ways:

- by using a wildcard expression   
``` shell
$ python3 ./pack5.py --output cli.h5 --numpy-wc "./tests/data*.npy" --json-wc "./tests/pars*.json"
```
This will store are contents of the 10 `.npy` files inside `cli.h5` and attach the contents of the respective `pars*.json` as attributes (for more details, see [dataset attributes](http://docs.h5py.org/en/stable/high/attr.html).

- by providing a list of files  
``` shell
$ python3 ./pack5.py --output cli.h5 --numpy-list numpy.list --json-list json.list
```
which in turn contain the full paths.

The tool is written such that it can store only chunks of the data inside a series of hdf5 files:

``` shell
$ python3 ./pack5.py --output cli.h5 --numpy-wc "./tests/data*.npy" --json-wc "./tests/pars*.json" --files-per-chunk 2
Wrote 5/5 .h5 files from 10 inputs
```

This has created 5 .h5 files with 2 npy/json datasets inside each.
