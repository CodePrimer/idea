# -*- coding: utf-8 -*-
import os
from Landsat8.Landsat8Process import main

if __name__ == '__main__':
    rootDir = r'G:\landsat_2020'
    tempDir = r'G:\temp'
    outRootDir = r'G:\landsat_2020_output'

    for tarFile in os.listdir(rootDir):
        tarPath = os.path.join(rootDir, tarFile)
        outName = tarFile.split('.')[0] + '.tif'
        outPath = os.path.join(outRootDir, outName)
        main(tarPath, tempDir, outPath)