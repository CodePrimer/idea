import os
import time

def copy_file(source_file, target_dir, target_name=None):

    if not os.path.isfile(source_file):
        print("file not exist.")
        return False
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    try:
        if target_name:
            save_name = target_name
        else:
            save_name = os.path.basename(source_file)
        target_file_path = os.path.join(target_dir, save_name)
        if not os.path.exists(target_file_path) or (
                os.path.exists(target_file_path) and (
                os.path.getsize(target_file_path) != os.path.getsize(source_file))):
            with open(target_file_path, "wb") as ft:
                with open(source_file, "rb") as fs:
                    ft.write(fs.read())
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    dir_path = r'E:'
    copy_dir = r'E:\Y'
    folder_list = os.listdir(dir_path)
    day_list = ['20200624', '20200625', '20200626', '20200627', '20200628', '20200629', '20200630']
    time_list = ['0100', '0200', '0300', '0400', '0500', '0600', '0700']
    band_list = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B13', 'B15']
    seg_list = ['S0210', 'S0310', 'S0410']

    for each in folder_list:
        if each not in day_list:
            continue
        cur_dir = os.path.join(dir_path, each)
        file_list = os.listdir(cur_dir)
        for file_name in file_list:
            time_str = file_name.split('_')[3]
            band_str = file_name.split('_')[4]
            seg_info = file_name.split('_')[7]
            seg_str = seg_info.split('.')[0]
            if time_str not in time_list or band_str not in band_list or seg_str not in seg_list:
                continue
            file_path = os.path.join(cur_dir, file_name)
            print(file_path)
            copy_file(file_path, r'E:\Y')
            time.sleep(1)

    print('finish')
