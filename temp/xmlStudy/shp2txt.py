# -- coding: utf-8 -- 
import arcpy
import os
import sys

reload(sys)
sys.setdefaultencoding( "utf-8" )

'''福建行政区划入库txt'''

compFolder = r'C:\Users\wangbin\Desktop\CompShp'

insertTxt = r'C:\Users\wangbin\Desktop\INSERT.txt'

fieldList = ["PCODE","ID","level","PNAME","NAME","XCENTER","YCENTER","XMIN","XMAX","YMIN","YMAX"]
attribute = arcpy.da.SearchCursor(os.path.join(compFolder, 'AreaProvince.shp'), fieldList)
for a in attribute:
    insert_str = 'INSERT INTO `htht_fujian`.`htht_uus_region_info` (`regionid`, `t_m_regionid`, `regionlevel`, `fullname`, `districtname`, `enable`, `longitude_center`, `latitude_center`, `longitude_min`, `longitude_max`, `latitude_min`, `latitude_max`) VALUES ('
    insert_str += "'" + a[0] +"'" + ', '
    insert_str += "'" + a[1] +"'" + ', '
    insert_str += "'" + a[2] +"'" + ', '
    insert_str += "'" + a[3] +"'" + ', '
    insert_str += "'" + a[4] +"'" + ', '
    insert_str += "NULL" + ', '
    insert_str += "'" + unicode(a[5]) +"'" + ', '
    insert_str += "'" + unicode(a[6]) +"'" + ', '
    insert_str += "'" + unicode(a[7]) +"'" + ', '
    insert_str += "'" + unicode(a[8]) +"'" + ', '
    insert_str += "'" + unicode(a[9]) +"'" + ', '
    insert_str += "'" + unicode(a[10]) +"'" 
    insert_str += ");"
    with open(insertTxt, 'a') as f:
        f.write(insert_str + "\n")


fieldList = ["ACODE","PCODE","level","ANAME","NAME","XCENTER","YCENTER","XMIN","XMAX","YMIN","YMAX"]
attribute = arcpy.da.SearchCursor(os.path.join(compFolder, 'AreaCity.shp'), fieldList)
for a in attribute:
    insert_str = 'INSERT INTO `htht_fujian`.`htht_uus_region_info` (`regionid`, `t_m_regionid`, `regionlevel`, `fullname`, `districtname`, `enable`, `longitude_center`, `latitude_center`, `longitude_min`, `longitude_max`, `latitude_min`, `latitude_max`) VALUES ('
    insert_str += "'" + a[0] +"'" + ', '
    insert_str += "'" + a[1] +"'" + ', '
    insert_str += "'" + a[2] +"'" + ', '
    insert_str += "'" + a[3] +"'" + ', '
    insert_str += "'" + a[4] +"'" + ', '
    insert_str += "NULL" + ', '
    insert_str += "'" + unicode(a[5]) +"'" + ', '
    insert_str += "'" + unicode(a[6]) +"'" + ', '
    insert_str += "'" + unicode(a[7]) +"'" + ', '
    insert_str += "'" + unicode(a[8]) +"'" + ', '
    insert_str += "'" + unicode(a[9]) +"'" + ', '
    insert_str += "'" + unicode(a[10]) +"'" 
    insert_str += ");"
    with open(insertTxt, 'a') as f:
        f.write(insert_str + "\n")


fieldList = ["CCODE","ACODE","level","CNAME","NAME","XCENTER","YCENTER","XMIN","XMAX","YMIN","YMAX"]
attribute = arcpy.da.SearchCursor(os.path.join(compFolder, 'AreaCounty.shp'), fieldList)
for a in attribute:
    insert_str = 'INSERT INTO `htht_fujian`.`htht_uus_region_info` (`regionid`, `t_m_regionid`, `regionlevel`, `fullname`, `districtname`, `enable`, `longitude_center`, `latitude_center`, `longitude_min`, `longitude_max`, `latitude_min`, `latitude_max`) VALUES ('
    insert_str += "'" + a[0] +"'" + ', '
    insert_str += "'" + a[1] +"'" + ', '
    insert_str += "'" + a[2] +"'" + ', '
    insert_str += "'" + a[3] +"'" + ', '
    insert_str += "'" + a[4] +"'" + ', '
    insert_str += "NULL" + ', '
    insert_str += "'" + unicode(a[5]) +"'" + ', '
    insert_str += "'" + unicode(a[6]) +"'" + ', '
    insert_str += "'" + unicode(a[7]) +"'" + ', '
    insert_str += "'" + unicode(a[8]) +"'" + ', '
    insert_str += "'" + unicode(a[9]) +"'" + ', '
    insert_str += "'" + unicode(a[10]) +"'" 
    insert_str += ");"
    with open(insertTxt, 'a') as f:
        f.write(insert_str + "\n")


fieldList = ["TCODE","CCODE","level","TNAME","NAME","XCENTER","YCENTER","XMIN","XMAX","YMIN","YMAX"]
attribute = arcpy.da.SearchCursor(os.path.join(compFolder, 'AreaXiang.shp'), fieldList)
for a in attribute:
    insert_str = 'INSERT INTO `htht_fujian`.`htht_uus_region_info` (`regionid`, `t_m_regionid`, `regionlevel`, `fullname`, `districtname`, `enable`, `longitude_center`, `latitude_center`, `longitude_min`, `longitude_max`, `latitude_min`, `latitude_max`) VALUES ('
    insert_str += "'" + a[0] +"'" + ', '
    insert_str += "'" + a[1] +"'" + ', '
    insert_str += "'" + a[2] +"'" + ', '
    insert_str += "'" + a[3] +"'" + ', '
    insert_str += "'" + a[4] +"'" + ', '
    insert_str += "NULL" + ', '
    insert_str += "'" + unicode(a[5]) +"'" + ', '
    insert_str += "'" + unicode(a[6]) +"'" + ', '
    insert_str += "'" + unicode(a[7]) +"'" + ', '
    insert_str += "'" + unicode(a[8]) +"'" + ', '
    insert_str += "'" + unicode(a[9]) +"'" + ', '
    insert_str += "'" + unicode(a[10]) +"'" 
    insert_str += ");"
    with open(insertTxt, 'a') as f:
        f.write(insert_str + "\n")

# INSERT INTO `htht_fujian`.`htht_uus_region_info` (`regionid`, `t_m_regionid`, `regionlevel`, `fullname`, `districtname`, `enable`, `longitude_center`, `latitude_center`, `longitude_min`, `longitude_max`, `latitude_min`, `latitude_max`) VALUES ('140000000000', '140000000000', '0', '山西省', '山西省', NULL, '110.950996400000000', '34.793701200000000', '110.211998000000000', '111.691001900000000', '34.587398500000000', '35.000099200000000');