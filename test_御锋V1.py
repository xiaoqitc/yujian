#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
御锋V1网络安全工具箱 - 功能测试脚本
"""

import sys
import os
import importlib.util

def test_imports():
    """测试必要的模块导入"""
    print("🔍 测试模块导入...")
    
    required_modules = [
        'tkinter',
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
        'inspect'
    ]
    
    optional_modules = [
        'dns.resolver',
        'requests',
        'Crypto.Cipher.AES',
        'Crypto.Util.Padding'
    ]
    
    print("必需模块:")
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            return False
    
    print("\n可选模块:")
    for module in optional_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ⚠️  {module} (可选)")
    
    return True

def test_main_program():
    """测试主程序文件"""
    print("\n🔍 测试主程序文件...")
    
    main_file = "御锋V1网络安全工具箱.py"
    if not os.path.exists(main_file):
        print(f"  ❌ 主程序文件 {main_file} 不存在")
        return False
    
    print(f"  ✅ 主程序文件 {main_file} 存在")
    
    # 尝试导入主程序模块
    try:
        spec = importlib.util.spec_from_file_location("main", main_file)
        if spec is None:
            print("  ❌ 无法创建模块规范")
            return False
        module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            print("  ❌ 模块加载器为空")
            return False
        spec.loader.exec_module(module)
        print("  ✅ 主程序模块导入成功")
        return True
    except Exception as e:
        print(f"  ❌ 主程序模块导入失败: {e}")
        return False

def test_sqlmap_integration():
    """测试SQLMap集成"""
    print("\n🔍 测试SQLMap集成...")
    
    sqlmap_dir = "CN_Sqlmap-main"
    sqlmap_file = os.path.join(sqlmap_dir, "sqlmap.py")
    
    if os.path.exists(sqlmap_dir):
        print(f"  ✅ SQLMap目录 {sqlmap_dir} 存在")
        if os.path.exists(sqlmap_file):
            print(f"  ✅ SQLMap主文件 {sqlmap_file} 存在")
            return True
        else:
            print(f"  ⚠️  SQLMap主文件 {sqlmap_file} 不存在")
            return False
    else:
        print(f"  ⚠️  SQLMap目录 {sqlmap_dir} 不存在")
        return False

def test_build_script():
    """测试打包脚本"""
    print("\n🔍 测试打包脚本...")
    
    build_file = "build.py"
    if os.path.exists(build_file):
        print(f"  ✅ 打包脚本 {build_file} 存在")
        
        # 检查打包脚本中的文件名引用
        try:
            with open(build_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "御锋V1网络安全工具箱.py" in content:
                    print("  ✅ 打包脚本中的文件名引用正确")
                    return True
                else:
                    print("  ❌ 打包脚本中的文件名引用不正确")
                    return False
        except Exception as e:
            print(f"  ❌ 读取打包脚本失败: {e}")
            return False
    else:
        print(f"  ❌ 打包脚本 {build_file} 不存在")
        return False

def test_documentation():
    """测试文档文件"""
    print("\n🔍 测试文档文件...")
    
    docs = [
        "README.md",
        "LICENSE",
        "requirements.txt",
        "README_新功能说明.md"
    ]
    
    all_exist = True
    for doc in docs:
        if os.path.exists(doc):
            print(f"  ✅ {doc} 存在")
        else:
            print(f"  ❌ {doc} 不存在")
            all_exist = False
    
    return all_exist

def test_startup_script():
    """测试启动脚本"""
    print("\n🔍 测试启动脚本...")
    
    startup_script = "启动御锋V1.bat"
    if os.path.exists(startup_script):
        print(f"  ✅ 启动脚本 {startup_script} 存在")
        return True
    else:
        print(f"  ❌ 启动脚本 {startup_script} 不存在")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("御锋V1网络安全工具箱 - 功能测试")
    print("=" * 60)
    
    tests = [
        ("模块导入测试", test_imports),
        ("主程序文件测试", test_main_program),
        ("SQLMap集成测试", test_sqlmap_integration),
        ("打包脚本测试", test_build_script),
        ("文档文件测试", test_documentation),
        ("启动脚本测试", test_startup_script)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！御锋V1网络安全工具箱准备就绪！")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 