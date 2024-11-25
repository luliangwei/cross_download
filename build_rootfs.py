import os
import re
import shutil
import subprocess
import tarfile


def filter_members(tf, file_name):
    # 修改提取压缩包的路径
    folder_length = len("binary/casper/")
    for member in tf.getmembers():
        if member.path.startswith("binary/casper/"):
            member.path = member.path[folder_length:]
            member.path = 'root_images/' + file_name + '/' + member.path
            yield member


def extract_img_file(img_file, output_dir):
    # 检查输出目录是否存在，存在则删除
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    if os.path.exists('/tmp/rootfs_file'):
        shutil.rmtree('/tmp/rootfs_file')

    # 判断文件扩展名
    if img_file.endswith('.img'):

        # 将回环设备挂载到临时目录
        if not os.path.exists('/tmp/rootfs_file'):
            os.makedirs('/tmp/rootfs_file')
        subprocess.run(['mount', '-o', 'loop', img_file, '/tmp/rootfs_file'])

        # 复制挂载目录中的内容到目标文件夹
        # shutil.copytree('/mnt/temp', output_dir, symlinks=True)
        subprocess.run(['cp', '-r', '/tmp/rootfs_file', output_dir])

        # 卸载挂载的文件系统和回环设备
        subprocess.run(['umount', '/tmp/rootfs_file'])
        subprocess.run(['losetup', '-d', '/dev/loop0'])

    elif img_file.endswith('.squashfs'):
        # 解压 squashfs 文件
        subprocess.run(['unsquashfs', '-f', '-d', output_dir, img_file])

    if os.path.exists('/tmp/rootfs_file'):
        shutil.rmtree('/tmp/rootfs_file')


def find_rootfs(iso_file, rootfs_ext=None):
    # 检查输出目录是否存在，存在则删除
    if os.path.exists('/tmp/iso_file'):
        subprocess.run(['umount', '/tmp/iso_file'])
        shutil.rmtree('/tmp/iso_file')
    # 获取 ISO 文件中的文件列表
    os.makedirs('/tmp/iso_file')
    subprocess.run(['mount', '-o', 'loop', 'iso/' + iso_file + '.iso', '/tmp/iso_file'])
    files = os.listdir('/tmp/iso_file')
    # 打印文件列表

    if 'casper' in files:
        casper_list = os.listdir('/tmp/iso_file/casper')
        # 打印casper文件列表
        for casper_file in casper_list:

            pattern = r"\.tar\.gz$"
            if re.search(pattern, casper_file):
                rootfs_ext = '.img'
                # 检查输出目录是否存在，存在则删除
                if os.path.exists('root_images/' + iso_file):
                    shutil.rmtree('root_images/' + iso_file)

                with tarfile.open('/tmp/iso_file/casper/' + casper_file, "r:gz") as tar:
                    tar.extractall(members=filter_members(tar, iso_file))
                break
        else:
            if 'filesystem.squashfs' in casper_list:
                # squashfs文件提取
                rootfs_ext = '.squashfs'
                # 检测squashfs文件是否存在，存在则删除
                if os.path.exists('root_images/' + iso_file):
                    shutil.rmtree('root_images/' + iso_file)
                os.makedirs('root_images/' + iso_file)
                # 拷贝squashfs文件
                shutil.copyfile('/tmp/iso_file/casper/filesystem.squashfs', 'root_images/' + iso_file + '/' + iso_file+rootfs_ext)

    elif 'boot' in files:
        boot_list = os.listdir('/tmp/iso_file/boot')

        for boot_file in boot_list:
            pattern = r"\.tar\.gz$"
            if re.search(pattern, boot_file):
                rootfs_ext = '.img'
                # 检查输出目录是否存在，存在则删除
                if os.path.exists('root_images/' + iso_file):
                    shutil.rmtree('root_images/' + iso_file)
                os.makedirs('root_images/' + iso_file)

                with tarfile.open('/tmp/iso_file/boot/' + boot_file, "r:gz") as tar:
                    tar.extractall('root_images/'+iso_file)
                break
    else:
        print('there is not have rootfs, please check iso!!!')

    # 删除中间文件
    subprocess.run(['umount', '/tmp/iso_file'])
    shutil.rmtree('/tmp/iso_file')
    return rootfs_ext


def build_rootfs(iso_file):

    output_dir = 'rootfs/' + iso_file
    find_rootfs(iso_file)

    images_list = os.listdir('root_images/'+iso_file)
    pattern = r"\.(img|squashfs)$"
    img_file = [file for file in images_list if re.search(pattern, file)]
    extract_img_file('root_images/' + iso_file + '/'+str(img_file)[2:-2], output_dir)

