from BaseUtil import BaseUtil
from GeoTiffFile import GeoTiffFile
import xml.dom.minidom, gdal, time, sys, os


def cal_sixs(year, month, day, hour, minute, lon, lat, wave):
    igeom = '7\n'
    time_lonlat = str(month) + '\t' + str(day) + '\t' + str(hour) + '.' + str(minute) + '\t' + str(lon) + '\t' + str(lat) + '\n'
    if month > 4 and month < 9:
        idatm = '2\n'
    else:
        idatm = '3\n'
    iaer = '1\n'
    v = '0\n'
    taer55 = '0.2\n'
    xps = '0.05\n'
    xpp = '-1000\n'
    iwave = '0\n'
    w = str(wave[0]) + '\t' + str(wave[1])
    inhomo = '0\n'
    idirect = '0\n'
    igroun = '1\n'
    rapp = '-0.4\n'
    file_content = [
     igeom, time_lonlat, idatm, iaer, v, taer55, xps, xpp, iwave, w, inhomo, idirect, idirect, igroun, rapp]
    in_txt = os.path.join(BaseUtil.filePathInfo(__file__)[0], 'in.txt')
    with open(in_txt, 'w') as (f):
        f.writelines(file_content)
    out_txt = os.path.join(BaseUtil.filePathInfo(__file__)[0], 'out.txt')
    exe_path = os.path.join(BaseUtil.filePathInfo(__file__)[0], '6S_IDL_NOBRDF', 'main.exe')
    in_txt = in_txt.replace('\\', '/')
    out_txt = out_txt.replace('\\', '/')
    exe_path = exe_path.replace('\\', '/')
    cmd_str = exe_path + '<' + in_txt + '>' + out_txt
    os.system(cmd_str)
    time.sleep(1)
    with open(out_txt, 'r') as (f):
        for line in f.readlines():
            line = line.strip('\n')
            if 'coefficients xa xb xc' in line:
                params = line.replace('*', '').split(':')[1].strip()
                xa = float(params.split('  ')[0])
                xb = float(params.split('  ')[1])
                xc = float(params.split('  ')[2])

    return (
     xa, xb, xc)


def main(input_dir, output_dir):
    BaseUtil.mkDir(output_dir)
    gf2_pms1_gains_2019 = [
     0.1453, 0.1826, 0.1727, 0.1908]
    gf2_pms2_gains_2019 = [0.175, 0.1902, 0.177, 0.1968]
    dir_list = os.listdir(input_dir)
    for dir_name in dir_list:
        basename = dir_name
        sensor_name = basename.split('_')[1]
        if sensor_name == 'PMS1':
            ext_str = '-MSS1.tiff'
        if sensor_name == 'PMS2':
            ext_str = '-MSS2.tiff'
        mss_path = os.path.join(input_dir, dir_name, dir_name + ext_str)
        if not BaseUtil.isFile(mss_path):
            print('cannot find tiff file.', mss_path)
            continue
        out_dir = os.path.join(output_dir, dir_name)
        BaseUtil.mkDir(out_dir)
        xml_path = mss_path.replace('.tiff', '.xml')
        dom = xml.dom.minidom.parse(xml_path)
        root = dom.documentElement
        CenterTime_node = root.getElementsByTagName('CenterTime')[0]
        CenterTime_text = CenterTime_node.childNodes[0].data
        time_stamp = time.mktime(time.strptime(CenterTime_text, '%Y-%m-%d %H:%M:%S'))
        CenterTime_text = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_stamp - 28800))
        year = int(CenterTime_text.split(' ')[0].split('-')[0])
        month = int(CenterTime_text.split(' ')[0].split('-')[1])
        day = int(CenterTime_text.split(' ')[0].split('-')[2])
        hour = int(CenterTime_text.split(' ')[1].split(':')[0])
        minute = int(CenterTime_text.split(' ')[1].split(':')[1])
        TopLeftLatitude_node = root.getElementsByTagName('TopLeftLatitude')[0]
        TopLeftLatitude_text = float(TopLeftLatitude_node.childNodes[0].data)
        TopLeftLongitude_node = root.getElementsByTagName('TopLeftLongitude')[0]
        TopLeftLongitude_text = float(TopLeftLongitude_node.childNodes[0].data)
        TopRightLatitude_node = root.getElementsByTagName('TopRightLatitude')[0]
        TopRightLatitude_text = float(TopRightLatitude_node.childNodes[0].data)
        TopRightLongitude_node = root.getElementsByTagName('TopRightLongitude')[0]
        TopRightLongitude_text = float(TopRightLongitude_node.childNodes[0].data)
        BottomRightLatitude_node = root.getElementsByTagName('BottomRightLatitude')[0]
        BottomRightLatitude_text = float(BottomRightLatitude_node.childNodes[0].data)
        BottomRightLongitude_node = root.getElementsByTagName('BottomRightLongitude')[0]
        BottomRightLongitude_text = float(BottomRightLongitude_node.childNodes[0].data)
        BottomLeftLatitude_node = root.getElementsByTagName('BottomLeftLatitude')[0]
        BottomLeftLatitude_text = float(BottomLeftLatitude_node.childNodes[0].data)
        BottomLeftLongitude_node = root.getElementsByTagName('BottomLeftLongitude')[0]
        BottomLeftLongitude_text = float(BottomLeftLongitude_node.childNodes[0].data)
        maxLat = max([TopLeftLatitude_text, TopRightLatitude_text, BottomRightLatitude_text, BottomLeftLatitude_text])
        minLat = min([TopLeftLatitude_text, TopRightLatitude_text, BottomRightLatitude_text, BottomLeftLatitude_text])
        maxLon = max([TopLeftLongitude_text, TopRightLongitude_text, BottomRightLongitude_text, BottomLeftLongitude_text])
        minLon = min([TopLeftLongitude_text, TopRightLongitude_text, BottomRightLongitude_text, BottomLeftLongitude_text])
        centerLat = (maxLat + minLat) / 2
        centerLon = (maxLon + minLon) / 2
        waveList = [
         [
          0.45, 0.52],
         [
          0.52, 0.59],
         [
          0.63, 0.69],
         [
          0.77, 0.89]]
        tifObj = GeoTiffFile(mss_path)
        tifObj.readTif()
        out_tif_name = basename + '_REF.tiff'
        out_tif_path = os.path.join(out_dir, out_tif_name)
        driver = gdal.GetDriverByName('GTiff')
        ds = driver.Create(out_tif_path, tifObj.getWidth(), tifObj.getHeight(), tifObj.getBands(), gdal.GDT_Float32)
        for i in range(4):
            xa, xb, xc = cal_sixs(year, month, day, hour, minute, centerLon, centerLat, waveList[i])
            band_data = tifObj.getBandData(i)
            sensor_name = basename.split('_')[1]
            if sensor_name == 'PMS1':
                gainList = gf2_pms1_gains_2019
            if sensor_name == 'PMS2':
                gainList = gf2_pms2_gains_2019
            gain = gainList[i]
            band_data = band_data * gain
            ref_data = (xa * band_data - xb) / (1 + xc * (xa * band_data - xb))
            ds.GetRasterBand(i + 1).WriteArray(ref_data)
            print('finish band: ' + str(i + 1))

        rpb_file = mss_path.replace('.tiff', '.rpb')
        new_rpb_file_name = out_tif_name.replace('.tiff', '.rpb')
        BaseUtil.copyFile(rpb_file, out_dir, new_rpb_file_name)
        del ds
        del tifObj
        print('finish process: ' + dir_name)


if __name__ == '__main__':
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    main(input_dir, output_dir)
    print('end.')