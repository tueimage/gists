import pydicom.filereader as pydicom_freader
from functools import cmp_to_key
import os.path as osp
import os
import sys
import getopt


def slice_cmp(firstSlice, secondSlice):
    if firstSlice.AcquisitionNumber == secondSlice.AcquisitionNumber:
        if firstSlice.SliceLocation == secondSlice.SliceLocation:
            if firstSlice.InstanceNumber > secondSlice.InstanceNumber:
                return -1
            else:
                return 1
        else:
            if float(firstSlice.SliceLocation) > float(secondSlice.SliceLocation):
                return -1
            else:
                return 1
    else:
        if float(firstSlice.AcquisitionNumber) > float(secondSlice.AcquisitionNumber):
            return -1
        else:
            return 1


def split_series(dicom_dir, slices_per_series):
    print('Processing series from', dicom_dir)
    dicom_files = os.listdir(dicom_dir)
    dicom_images = [pydicom_freader.read_file(osp.join(dicom_dir, dfile)) for dfile in dicom_files]
    
    sorted_slices = sorted(dicom_images, key=cmp_to_key(slice_cmp))
    
    amount_images = len(sorted_slices) // slices_per_series
    
    series = [None] * amount_images
    
    for idx, img_slice in enumerate(sorted_slices):
        image_idx = idx % amount_images
        if series[image_idx] is None:
            series[image_idx] = []
        series[image_idx].append(img_slice)
    
    print('Split series into', amount_images, 'images')
    return series


def save_split_series(series, out_dir):
    for i, img_series in enumerate(series):
        print('Saving series #{}'.format(i))
        
        series_dir = 'series{}'.format(i)
        
        os.makedirs(osp.join(out_dir, series_dir), exist_ok=True)
        
        for slice_idx, img_slice in enumerate(img_series):
            img_slice.save_as(osp.join(out_dir, series_dir, str(slice_idx)))


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hi:n:o:",["inputDir=","slicesPerSeries=", "outDir="])
    except getopt.GetoptError:
        print('dicom_split.py -i <inputDir> -n <slicesPerSeries> -o <outputDir>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print('dicom_split.py -i <inputDir> -n <slicesPerSeries> -o <outputDir>')
            return
        if opt in ('-i', '--inputDir'):
            dicom_dir = arg
        elif opt in ('-n', '--slicesPerSeries'):
            slices_per_series = int(arg)
        elif opt in ('-o', '--outDir'):
            out_dir = arg
    
    all_series = split_series(dicom_dir, slices_per_series)
    save_split_series(all_series, out_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
