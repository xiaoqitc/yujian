#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
御锋V1网络安全工具箱 - 自动打包脚本
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("PyInstaller安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller安装失败: {e}")
        return False

def create_spec_file():
    """创建PyInstaller配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['御锋V1网络安全工具箱.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.filedialog',
        'base64',
        'hashlib',
        'hmac',
        'socket',
        'json',
        'os',
        'platform',
        'sys',
        'threading',
        'time',
        'subprocess',
        're',
        'concurrent.futures',
        'shutil',
        'tempfile',
        'zipfile',
        'random',
        'string',
        'py_compile',
        'importlib.util',
        'inspect',
        'dns.resolver',
        'requests',
        'Crypto.Cipher.AES',
        'Crypto.Util.Padding',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='御锋V1网络安全工具箱',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('御锋V1网络安全工具箱.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("PyInstaller配置文件创建成功！")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 检查是否存在spec文件
    if not os.path.exists('御锋V1网络安全工具箱.spec'):
        create_spec_file()
    
    try:
        # 使用PyInstaller构建
        cmd = [sys.executable, "-m", "PyInstaller", "御锋V1网络安全工具箱.spec"]
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("构建成功！")
            return True
        else:
            print("构建失败！")
            return False
    except subprocess.CalledProcessError as e:
        print(f"构建过程中出现错误: {e}")
        return False

def create_installer():
    """创建安装包"""
    print("正在创建安装包...")
    
    # 检查构建结果
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("未找到构建结果，请先运行构建")
        return False
    
    # 创建发布目录
    release_dir = Path("release")
    release_dir.mkdir(exist_ok=True)
    
    # 复制文件到发布目录
    for item in dist_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, release_dir)
        elif item.is_dir():
            shutil.copytree(item, release_dir / item.name, dirs_exist_ok=True)
    
    # 复制必要文件
    files_to_copy = [
        "README.md",
        "LICENSE",
        "requirements.txt"
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, release_dir)
    
    print(f"安装包已创建在 {release_dir} 目录中")
    return True

def create_zip_package():
    """创建ZIP压缩包"""
    print("正在创建ZIP压缩包...")
    
    release_dir = Path("release")
    if not release_dir.exists():
        print("未找到发布目录，请先创建安装包")
        return False
    
    # 获取系统信息
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    # 创建ZIP文件名
    zip_name = f"御锋V1网络安全工具箱-{system}-{arch}.zip"
    
    try:
        shutil.make_archive(
            f"御锋V1网络安全工具箱-{system}-{arch}",
            'zip',
            release_dir
        )
        print(f"ZIP压缩包创建成功: {zip_name}")
        return True
    except Exception as e:
        print(f"创建ZIP压缩包失败: {e}")
        return False

def clean_build_files():
    """清理构建文件"""
    print("正在清理构建文件...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["御锋V1网络安全工具箱.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除目录: {dir_name}")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"已删除文件: {file_name}")

def main():
    """主函数"""
    print("=" * 50)
    print("御锋V1网络安全工具箱 - 自动打包脚本")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("错误: 需要Python 3.6或更高版本")
        return
    
    # 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("无法安装PyInstaller，请手动安装后重试")
            return
    
    # 检查主程序文件
    if not os.path.exists('御锋V1网络安全工具箱.py'):
        print('错误: 未找到主程序文件 御锋V1网络安全工具箱.py')
        return
    
    # 构建选项
    print("\n请选择操作:")
    print("1. 仅构建可执行文件")
    print("2. 构建并创建安装包")
    print("3. 构建并创建ZIP压缩包")
    print("4. 完整构建（可执行文件 + 安装包 + ZIP）")
    print("5. 清理构建文件")
    print("0. 退出")
    
    try:
        choice = input("\n请输入选择 (0-5): ").strip()
    except KeyboardInterrupt:
        print("\n用户取消操作")
        return
    
    if choice == "0":
        print("退出打包脚本")
        return
    elif choice == "1":
        if build_executable():
            print("构建完成！")
        else:
            print("构建失败！")
    elif choice == "2":
        if build_executable() and create_installer():
            print("构建和安装包创建完成！")
        else:
            print("操作失败！")
    elif choice == "3":
        if build_executable() and create_installer() and create_zip_package():
            print("构建和ZIP压缩包创建完成！")
        else:
            print("操作失败！")
    elif choice == "4":
        if build_executable() and create_installer() and create_zip_package():
            print("完整构建完成！")
        else:
            print("操作失败！")
    elif choice == "5":
        clean_build_files()
        print("清理完成！")
    else:
        print("无效选择！")
        return
    
    print("\n打包脚本执行完成！")

if __name__ == "__main__":
    main() 