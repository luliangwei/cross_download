import os
import zipfile


def list_deb(package):

    os.system('apt update')
    pack_list = os.popen('apt list | grep ' + package).readlines()
    return pack_list


def download_deb(package):

    pack_path = '/var/cache/apt/archives/'
    os.system('apt update')
    os.system('apt install -y ' + package + ' -d && exit')
    os.rmdir(pack_path + 'partial')
    os.remove(pack_path + 'lock')

    with zipfile.ZipFile('/media/'+package+'.zip', 'w') as pack_zip:
        for item in os.listdir(pack_path):
            print(pack_path+item)
            pack_zip.write(pack_path+item, arcname=item)
    pack_zip.close()
    os.system('rm -rf /var/cache/apt/archives/')

    return pack_zip

