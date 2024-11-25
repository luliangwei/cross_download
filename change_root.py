import os
import subprocess
import shutil


def configure_chroot_environment(chroot_dir):
    # 配置 chroot 环境
    # 挂载 proc 和 dev 文件系统到 chroot 环境
    subprocess.run(['mount', '-t', 'proc', 'proc', os.path.join(chroot_dir, 'proc')])
    subprocess.run(['mount', '-t', 'sysfs', 'sys', os.path.join(chroot_dir, 'sys')])
    subprocess.run(['mount', '--rbind', '/dev', os.path.join(chroot_dir, 'dev')])
    #subprocess.run(['mount', '--rbind', '/run', os.path.join(chroot_dir, 'run')])

    if os.path.exists(os.path.join(chroot_dir,'etc/apt/sources.list.d')):
        shutil.rmtree(os.path.join(chroot_dir, 'etc/apt/sources.list.d'))

    os.remove(os.path.join(chroot_dir, 'etc/resolv.conf'))
    # 设置网络配置
    # 这里可以根据需求进行配置，例如复制主机上的网络配置文件到挂载的根文件系统
    subprocess.run(['cp', 'configure/etc/resolv.conf', os.path.join(chroot_dir, 'etc/resolv.conf')])
    #subprocess.run(['cp', 'configure/etc/apt/sources.list', os.path.join(chroot_dir, 'etc/apt/sources.list')])


def create_chroot_environment(chroot_dir):
    # 进入 chroot 环境
    fd = os.getcwd()
    real_root = os.open("/", os.O_RDONLY)

    # 设置 chroot 环境的根目录
    os.chroot(chroot_dir)
    os.chdir('/')

    return fd, real_root


def unmount_chroot_environment(chroot_dir, fd, real_root):
    # 退出 chroot 环境
    os.fchdir(real_root)
    os.chroot('.')
    os.chdir(fd)


def exit_chroot_environment(chroot_dir):
    # 退出chroot的bash环境卸载 chroot dev和proc
    #subprocess.run(['umount', '-l', chroot_dir + '/dev/'])
    subprocess.run(['umount', '-l', chroot_dir + '/proc/'])
    subprocess.run(['umount', '-l', chroot_dir + '/sys/'])
    #subprocess.run(['umount', '-l', chroot_dir + '/run/'])



