# -*-- coding: UTF-8 -*-
import os
import sys
import arcpy
import pickle


def createFileGDB(gdbPath):
    """创建GDB文件"""
    gdbDir = os.path.dirname(gdbPath)
    gdbName = os.path.basename(gdbPath)
    if not arcpy.Exists(gdbPath):
        arcpy.CreateFileGDB_management(gdbDir, gdbName)


def createMosaicDataset(gdbPath, mdName, prjFile):
    """
    1.创建镶嵌数据集
    3.开启自动跟踪功能    会自动添加四个属性字段
    """
    gdbname = gdbPath
    mdname = mdName
    prjfile = prjFile
    noband = "1"
    pixtype = "32_BIT_FLOAT"

    # 1.创建镶嵌数据集
    mdpath = gdbPath + "/" + mdName
    if not arcpy.Exists(mdpath):
        arcpy.CreateMosaicDataset_management(gdbname, mdname, prjfile, noband, pixtype)

    # 2.并添加四个属性字段
    # if arcpy.Exists(mdpath):
    #     arcpy.AddField_management(mdpath, 'createpreson', 'TEXT', 18, 11)
    #     arcpy.AddField_management(mdpath, 'createtime', 'DATE')
    #     arcpy.AddField_management(mdpath, 'updateepreson', 'TEXT', 18, 11)
    #     arcpy.AddField_management(mdpath, 'updatetime', 'DATE')

    # 3.开启自动跟踪功能
    desc = arcpy.Describe(mdpath)
    if not desc.editorTrackingEnabled:
        arcpy.EnableEditorTracking_management(mdpath, "createperson", "createtime", "updateperson", "updatetime",
                                              "ADD_FIELDS", "UTC")


def addRastersToMosaicDataset(gdbPath, pluginName, prjFile, tiffFileName):
    """镶嵌数据集信息存储"""

    try:
        createFileGDB(gdbPath)
        createMosaicDataset(gdbPath, pluginName, prjFile)
        mdname = gdbPath + "/" + pluginName
        rastype = "Raster Dataset"
        inpath = tiffFileName
        updatecs = "UPDATE_CELL_SIZES"
        updatebnd = "UPDATE_BOUNDARY"
        updateovr = "NO_OVERVIEWS"
        maxlevel = "#"
        maxcs = "0"
        maxdim = "1500"
        spatialref = "#"
        inputdatafilter = ""
        subfolder = "SUBFOLDERS"
        duplicate = "ALLOW_DUPLICATES"
        buildpy = "NO_PYRAMIDS"
        calcstats = "NO_STATISTICS"
        buildthumb = "NO_THUMBNAILS"
        comments = "#"
        forcesr = "#"

        # 添加栅格到镶嵌数据集
        arcpy.AddRastersToMosaicDataset_management(
            mdname, rastype, inpath, updatecs, updatebnd, updateovr,
            maxlevel, maxcs, maxdim, spatialref, inputdatafilter,
            subfolder, duplicate, buildpy, calcstats,
            buildthumb, comments, forcesr)
    except:
        return


def main(args):
    # 读取pkl变量
    fr = open(args[1], 'rb')
    param = pickle.load(fr)
    fr.close()
    gdbPath = param['gdbPath']
    mosaicDatasetName = param['mosaicDatasetName']
    prjFile = param['prjFile']
    tifPath = param['tifPath']
    addRastersToMosaicDataset(gdbPath, mosaicDatasetName, prjFile, tifPath)
    print('Add Rasters To MosaicDataset Success.')


if __name__ == '__main__':
    # gdb_path = r'C:\Users\wangbin\Desktop\qinghaiData\gdb\cdfq.gdb'
    # mosaic_dataset = 'cdfq'
    # prj_file = r'C:\Users\wangbin\Desktop\qinghai2\code\depend\prj\GCS_WGS_1984.prj'
    # tif_path = r'C:\Users\wangbin\Desktop\qinghaiData\demo\ABC_DEF_RCUR_202003030000_SOUR.tif'
    # addRastersToMosaicDataset(gdb_path, mosaic_dataset, prj_file, tif_path)
    # args = ['test', r'C:\Users\wangbin\Desktop\qinghaiData\tempdir\158935490735\addMosaicDataset_158935491641.pkl']
    # main(args)

    main(sys.argv)
