#!/usr/bin/env python
import sys,argparse
import numpy
import os
import h5py
import scipy.misc
import configobj

def get_dims(f_name):
    with h5py.File(f_name,"r") as f:
        s = numpy.shape(f["mean"])
    list(s).pop(0)
    return tuple(s)

def get_threshold_mask(f_names, ds_name, threshold):
    d = []
    for fn in f_names:
        with h5py.File(fn, "r") as f:
            d.append(numpy.array(f[ds_name]))
    return (numpy.mean(d,axis=0) < threshold)

def get_limit_mask(f_names, ds_name, threshold):
    d = []
    for fn in f_names:
        with h5py.File(fn, "r") as f:
            d.append(numpy.array(f[ds_name]))
    return (numpy.mean(d,axis=0) > threshold)

def get_badpixelmask(f_name):
    if f_name[-3:] == ".h5":
        with h5py.File(f_name, "r"):
            m = numpy.array(f["/data/data"])
    elif f_name[-4:] == ".png":
        m = scipy.misc.imread(f_name,flatten=True) / 255.
    return m


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Hummingbird mask tool. Creates mask from stack files in current directory and given configuration file.')
    parser.add_argument('config', type=str,
                        help="configuration file")
    if(len(sys.argv) == 1):
        parser.print_help()
    args = parser.parse_args()

    C = configobj.ConfigObj(args.config)
    
    files = os.listdir(".")
    files = [f for f in files if len(f) > 3]
    files = [f for f in files if f[-3:] == ".h5"]

    if len(files) == 0:
        sys.exit(0)

    s = get_dims(files[0])
    mask = numpy.ones(shape=s, dtype="bool")

    if C["mean_threshold"].lower() != 'none':
        mask *= get_threshold_mask(files, "mean", float(C["mean_threshold"]))

    if C["std_threshold"].lower() != 'none':
        mask *= get_threshold_mask(files, "std", float(C["std_threshold"]))

    if C["median_threshold"].lower() != 'none':
        mask *= get_threshold_mask(files, "median", float(C["median_threshold"]))

    if C["mean_limit"].lower() != 'none':
        mask *= get_limit_mask(files, "mean", float(C["mean_limit"]))

    if C["std_limit"].lower() != 'none':
        mask *= get_limit_mask(files, "std", float(C["std_limit"]))

    if C["median_limit"].lower() != 'none':
        mask *= get_limit_mask(files, "median", float(C["median_limit"]))

    if C["badpixelmask"].lower() != 'none':
        mask *= get_badpixelmask(C["badpixelmask"])

    if bool(C["output_png"].lower()):
        import matplotlib.pyplot as pypl
        pypl.imsave("mask.png", mask, cmap="binary_r", vmin=0, vmax=1)

    with h5py.File("mask.h5", "w") as f:
        f["data/data"] = mask