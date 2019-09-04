import numpy as np
from pathlib import Path

def test_files_exist():
    first = Path("data_000000.npy")
    assert first.exists()

def test_npy_opens():

    first = Path("data_000000.npy")

    npyref = np.load(first)
    assert type(npyref) != type(None)
    assert isinstance(npyref,type(np.ones(1)))
    assert npyref.dtype == np.float64

def test_npy_shapes():

    first = Path("data_000000.npy")

    npyref = np.load(first)
    assert len(npyref.shape) == 2

def test_search_all_files():

    files = [ Path("data_{0:06d}.npy".format(i)) for i in range(10) ]

    assert all([f.exists() for f in files])

def test_all_in_one_npz():

    files = [ Path("data_{0:06d}.npy".format(i)) for i in range(10) ]
    assert all([f.exists() for f in files])

    arrays = [ np.load(f) for f in files ]

    np.savez_compressed("test.npz",arrays[:3],files[:3])

    output = Path("test.npz")
    assert output.exists()
    assert output.stat().st_size > 0
    assert output.stat().st_size < sum([ f.stat().st_size for f in files[:3] ])
    output.unlink()

def test_unpack_again():

    files = [ Path("data_{0:06d}.npy".format(i)) for i in range(10) ]
    assert all([f.exists() for f in files])

    arrays = [ np.load(f) for f in files ]

    np.savez_compressed("test.npz",*dict(zip(files[-3:],arrays[-3:])))

    output = Path("test.npz")

    reloaded = np.load(output)

    assert len(reloaded.files) == 3
    assert not str(files[-1]) in reloaded.keys()
    output.unlink()
