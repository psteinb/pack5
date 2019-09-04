import h5py
import numpy as np
from pathlib import Path
import json

def test_unpack_again():

    files = [ Path("data_{0:06d}.npy".format(i)) for i in range(10) ]
    assert all([f.exists() for f in files])

    arrays = [ np.load(f) for f in files ]

    output = Path("test.h5")
    h5o = h5py.File(str(output))
    for fi,ar in zip(files[3:5],arrays[3:5]):
        h5o.create_dataset(str(fi),
                           data=ar,
                           compression="lzf")

    h5o.close()
    assert output.exists()
    assert output.stat().st_size > 0
    assert output.stat().st_size < sum([ f.stat().st_size for f in files[3:5]])
    print(output.stat().st_size, sum([ f.stat().st_size for f in files[3:5]]))
    output.unlink()

def test_reloaded():

    files = [ Path("data_{0:06d}.npy".format(i)) for i in range(10) ]
    assert all([f.exists() for f in files])

    arrays = [ np.load(f) for f in files ]

    output = Path("test.h5")
    h5o = h5py.File(str(output))
    for fi,ar in zip(files[3:5],arrays[3:5]):
        h5o.create_dataset(str(fi),
                           data=ar,
                           compression="lzf")

    h5o.close()
    del h5o

    reh5 = h5py.File(str(output))
    assert str(files[3]) in reh5
    arr3 = reh5[str(files[3])]

    assert np.array_equal(arr3,arrays[3])
    output.unlink()

def test_read_jsons():

    jsons = [ Path("pars{0:06d}.json".format(i)) for i in range(10) ]
    assert all([f.exists() for f in jsons])

    dicts = [ json.load(open(j)) for j in jsons ]
    assert len(dicts) == len(jsons)

    assert dicts[0]['shape'] == "cylinder"


def test_attributes_from_json():

    files = [ Path("data_{0:06d}.npy".format(i)) for i in range(10) ]
    assert all([f.exists() for f in files])


    arrays = [ np.load(f) for f in files ]

    jsonsf = [ Path("pars{0:06d}.json".format(i)) for i in range(10) ]
    dicts = [ json.load(open(j)) for j in jsonsf ]

    output = Path("test.h5")
    h5o = h5py.File(str(output))
    for fi,ar,js in zip(files[3:5],arrays[3:5],dicts[3:5]):
        ds = h5o.create_dataset(str(fi),
                                data=ar,
                                compression="lzf")
        for k,v in js.items():
            if isinstance(v,type(str())):
                ds.attrs.create(k,v, None, dtype=f"<S{len(v)}")
            else:
                ds.attrs.create(k,v)

    h5o.close()
    del h5o

    reh5 = h5py.File(str(output))
    assert str(files[3]) in reh5
    arr3 = reh5[str(files[3])]

    assert np.array_equal(arr3,arrays[3])
    assert arr3.attrs.get("shape") == str.encode(dicts[3]["shape"])
    assert arr3.attrs.get("distance_factor") == dicts[3]["distance_factor"]
    assert arr3.attrs.get("alpha_i") == dicts[3]["alpha_i"]

    output.unlink()
