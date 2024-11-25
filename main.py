import os
import subprocess
from pathlib import Path
import argparse
import json
from pymongo import MongoClient

import build_rootfs
import change_root
import download_package


def chroot_env(chroot_dir):

    subprocess.run(['xhost', '+SI:localuser:root'])
    change_root.configure_chroot_environment(chroot_dir)
    fd, real_root = change_root.create_chroot_environment(chroot_dir)
    subprocess.run('bash')
    change_root.unmount_chroot_environment(chroot_dir, fd, real_root)
    change_root.exit_chroot_environment(chroot_dir)


def chroot_pack_list(chroot_dir, package):
    #change_root.configure_chroot_environment(chroot_dir)
    #subprocess.run(['cp', 'configure/etc/hosts', os.path.join(chroot_dir, 'etc/hosts')])
    #subprocess.run(['cp', 'configure/etc/resolv.conf', os.path.join(chroot_dir, 'etc/resolv.conf')])
    subprocess.run(['cp', 'configure/etc/resolv.conf', os.path.join(chroot_dir, 'etc/resolv.conf')])
    fd, real_root = change_root.create_chroot_environment(chroot_dir)
    pack_list = download_package.list_deb(package)
    change_root.unmount_chroot_environment(chroot_dir, fd, real_root)
    #change_root.exit_chroot_environment(chroot_dir)
    return pack_list


def chroot_pack_download(chroot_dir, package):
    change_root.configure_chroot_environment(chroot_dir)
    subprocess.run(['mount', '--rbind', 'pack_zip', os.path.join(chroot_dir, 'media')])
    fd, real_root = change_root.create_chroot_environment(chroot_dir)
    pack_zip = download_package.download_deb(package)
    change_root.unmount_chroot_environment(chroot_dir, fd, real_root)
    subprocess.run(['umount', '-l', os.path.join(chroot_dir, 'media')])
    change_root.exit_chroot_environment(chroot_dir)

    return pack_zip

class Iso_file:
    def __init__(self, name, build_id, arch, sources):
        self.name = name
        self.id = build_id
        self.arch = arch
        self.sources = sources

    def to_dict(self):
        # 将对象转换为字典
        return self.__dict__

def main():
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument("--iso_file", type=str, default="ubuntu-18.04.6-desktop-amd64.iso")
    parser.add_argument("--value1", type=str)
    parser.add_argument("--value2", type=str)
    parser.add_argument("--value3", type=str)
    parser.add_argument("--value4", type=str)

    args = parser.parse_args()

    #iso_file = Path(args.iso_file)
    iso_file = args.iso_file

    iso_name = str(iso_file).removesuffix(".iso")

    iso_path = 'iso/' + iso_name  # iso路径
    chroot_dir = 'rootfs/' + iso_name  # 替换为实际的 chroot 目录

    value = args.value1
    pack_name = args.value2

    client = MongoClient("mongodb://localhost:27017/")
    db = client["example_db"]
    collection = db["Iso_files"]

    if value == 'build_rootfs':
        build_rootfs.build_rootfs(iso_name)
        iso_file = Iso_file(iso_name, args.value2, args.value3, args.value4)

        # 插入对象到数据库
        collection.insert_one(iso_file.to_dict())

        # 验证插入
        #result = collection.find_one({"name":  {"$regex": "020", "$options": "i"}})
        result = collection.find_one({"name":  iso_name})
        print("创建的信息:", result)

        # 关闭连接
        client.close()


    if value =='chroot':
         if os.path.exists(chroot_dir):
            chroot_env(chroot_dir)

    if value == 'list_pack':
        if os.path.exists(chroot_dir):
            pack_list = chroot_pack_list(chroot_dir,pack_name)
            # json_data = json.dumps(pack_list,ensure_ascii=False,indent=4)
            
            for pack in pack_list:
                pack_name = pack.split('/')
                json_data = json.dumps(pack_name,ensure_ascii=False,indent=4)
                with open("data.json", "w",encoding = 'utf-8') as file:
                    file.write(json_data)
                print(pack_name)
            # print(pack_list)
        else :
            print('没有rootfs文件夹')
    
    if value == 'download_pack':
        if os.path.exists(chroot_dir):
            chroot_pack_download(chroot_dir,pack_name)



if __name__ == '__main__':
    main()
