# -*- coding: utf-8 -*-

import os

from Sentinel2Process import Sentinel2

if __name__ == '__main__':
    dataDir = r'D:\share\Sentinel2Process\01data'
    outDir = r'D:\share\Sentinel2Process\02output'
    tempDir = r'D:\share\Sentinel2Process\03temp'
    for zipFile in os.listdir(dataDir):
        zipFilePath = os.path.join(dataDir, zipFile)
        print('Start Process: %s' % zipFile)
        Sentinel2.main(zipFilePath, outDir, tempDir)