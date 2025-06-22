# 御锋V1网络安全工具箱 🛡️

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/xiaoqitc/yujian)

> 一个功能强大的网络安全工具集合，专为安全研究人员、渗透测试人员和网络安全爱好者设计

## 📋 目录

- [项目介绍](#项目介绍)
- [功能特性](#功能特性)
- [界面预览](#界面预览)
- [安装说明](#安装说明)
- [使用指南](#使用指南)
- [SQLMap工具详解](#sqlmap工具详解)
- [打包说明](#打包说明)
- [技术架构](#技术架构)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [联系方式](#联系方式)

## 🎯 项目介绍

御锋V1网络安全工具箱是一个基于Python和Tkinter开发的图形化网络安全工具集合。它集成了多种常用的网络安全功能，提供了直观易用的图形界面，让复杂的网络安全操作变得简单高效。

### 主要特点

- 🎨 **美观的图形界面** - 现代化的UI设计，支持中文显示
- 🔧 **功能丰富** - 集成多种网络安全工具
- 🚀 **易于使用** - 图形化操作，无需记忆复杂命令
- 🔒 **安全可靠** - 本地运行，保护用户隐私
- 📱 **跨平台支持** - 支持Windows、macOS、Linux

## ✨ 功能特性

### 🔐 解码/解密工具
- **Base64编码/解码** - 支持文本和文件的Base64转换
- **URL编码/解码** - 处理URL特殊字符编码
- **AES加密/解密** - 支持ECB和CBC模式
- **哈希计算** - MD5、SHA1、SHA256、SHA512
- **HMAC计算** - 支持多种哈希算法

### 🌐 网络工具
- **DNS解析工具** - 查询A、MX、NS、TXT等记录
- **FOFA查询工具** - 资产发现和搜索
- **端口扫描工具** - TCP/UDP端口扫描
- **测试请求工具** - HTTP请求测试和调试
- **网络诊断工具** - Ping、Traceroute等

### 🗂️ 文件工具
- **目录工具** - 快速打开目录，支持多种工具
- **文件哈希计算** - 计算文件的MD5、SHA1、SHA256
- **文件比较工具** - 比较文件内容和哈希值
- **编码工具** - 十六进制、二进制编码转换

### 🔧 开发工具
- **依赖管理** - 自动检测和安装Python依赖
- **打包工具** - 将Python脚本打包为EXE/APK
- **SQLMap工具** - 图形化SQL注入检测
- **系统信息** - 查看系统和环境信息

### 🔍 高级功能
- **快速搜索** - 支持关键词快速定位功能
- **命令预览** - 实时预览生成的命令
- **预设模板** - 常用配置模板
- **历史记录** - 操作历史记录
- **自定义滚动条** - 美观的滚动条设计

## 🆕 最新功能更新

### 1. 目录工具 📁
- **多种打开方式**：支持文件管理器、命令行、PowerShell、VS Code、记事本
- **快速访问**：一键打开当前目录、桌面、文档、下载文件夹
- **最近访问**：记录并快速访问最近使用的目录
- **跨平台支持**：Windows、macOS、Linux全平台兼容

### 2. SQLMap工具 🗡️
- **图形化界面**：无需记忆复杂命令，可视化配置SQLMap参数
- **多种输入方式**：支持URL参数和请求包文件两种输入
- **实时命令预览**：实时显示生成的SQLMap命令
- **预设模板**：内置多种常用检测模板，快速开始
- **命令管理**：支持复制、保存、执行SQLMap命令
- **请求包解析**：自动解析HTTP请求包中的参数
- **高级选项**：完整的SQLMap参数配置支持

### 3. 增强的滚动体验 📜
- **自定义滚动条**：美观的蓝色主题滚动条
- **双向滚动**：支持水平和垂直滚动
- **快速滚动按钮**：一键跳转到顶部/底部
- **键盘导航**：支持键盘快捷键滚动
- **搜索功能**：在文本内容中快速搜索和高亮

### 4. 依赖检测与安装 🔧
- **智能分析**：自动分析Python脚本的依赖关系
- **并行安装**：多线程并行安装依赖，大幅提升速度
- **多种扫描方式**：支持单文件、目录、当前目录扫描
- **标准库过滤**：自动过滤Python标准库，只安装第三方依赖
- **安装状态反馈**：实时显示安装进度和结果

## 🖼️ 界面预览

### 主界面
```
┌─────────────────────────────────────────────────────────┐
│                    御锋V1网络安全工具箱                      │
├─────────────────────────────────────────────────────────┤
│ [快速搜索: _______________] [搜索]                        │
├─────────────────────────────────────────────────────────┤
│ [解码/解密] [DNS解析] [FOFA查询] [端口扫描] [测试请求]      │
│ [打包工具] [依赖管理] [目录工具] [SQLMap] [依赖检测]        │
│ [系统信息] [网络工具] [文件工具] [编码工具] [关于]          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                    欢迎使用御锋V1网络安全工具箱！              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### SQLMap工具界面
```
┌─────────────────────────────────────────────────────────┐
│                    SQLMap工具                            │
├─────────────────────────────────────────────────────────┤
│ 输入方式: ○ URL参数  ○ 请求包文件                        │
├─────────────────────────────────────────────────────────┤
│ 目标URL: [http://example.com/vulnerable.php?id=1]       │
│ 参数: [id]                                              │
├─────────────────────────────────────────────────────────┤
│ 数据库类型: ○ MySQL ○ MSSQL ○ Oracle ○ PostgreSQL      │
│ 注入技术: ○ 布尔盲注 ○ 时间盲注 ○ 联合查询 ○ 错误注入      │
├─────────────────────────────────────────────────────────┤
│ 检测等级: [1] 风险等级: [1] 线程数: [10]                │
│ ☑ 获取数据 ☑ 批处理模式 ☑ 随机User-Agent                │
├─────────────────────────────────────────────────────────┤
│ 生成的命令:                                              │
│ python sqlmap.py -u "http://example.com/vulnerable.php  │
│ ?id=1" -p id --level 1 --risk 1 --threads 10 --batch   │
├─────────────────────────────────────────────────────────┤
│ [生成命令] [复制命令] [保存命令] [执行SQLMap]              │
└─────────────────────────────────────────────────────────┘
```

## 📦 安装说明

### 系统要求

- **操作系统**: Windows 7+ / macOS 10.12+ / Linux (Ubuntu 16.04+)
- **Python版本**: Python 3.6 或更高版本
- **内存**: 至少 512MB 可用内存
- **磁盘空间**: 至少 100MB 可用空间

### 安装步骤

#### 方法一：直接运行（推荐）

1. **克隆项目**
   ```bash
   git clone https://github.com/xiaoqitc/yujian.git
   cd yujian
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   python 御锋V1网络安全工具箱.py
   ```

#### 方法二：使用打包版本

1. **下载发布版本**
   - 访问 [Releases](https://github.com/xiaoqitc/yujian/releases)
   - 下载对应系统的可执行文件

2. **直接运行**
   - Windows: 双击 `御锋V1网络安全工具箱.exe`
   - macOS: 双击 `御锋V1网络安全工具箱.app`
   - Linux: 运行 `./御锋V1网络安全工具箱`

### 依赖安装

程序会自动检测并提示安装缺失的依赖，您也可以手动安装：

```bash
# 基础依赖
pip install requests dnspython pycryptodome

# 可选依赖（用于高级功能）
pip install beautifulsoup4 lxml
```

## 🚀 使用指南

### 快速开始

1. **启动程序**
   - 运行 `python 御锋V1网络安全工具箱.py`
   - 使用默认账号密码登录：`admin` / `admin`

2. **选择功能**
   - 点击顶部功能按钮选择工具
   - 使用快速搜索定位功能

3. **配置参数**
   - 根据工具要求填写参数
   - 使用预设模板快速配置

4. **执行操作**
   - 点击执行按钮
   - 查看结果和日志

### 常用功能示例

#### DNS解析
```
域名: example.com
记录类型: A
结果: 93.184.216.34
```

#### 端口扫描
```
目标: 192.168.1.1
端口范围: 1-100
结果: 80(开放), 443(开放), 22(开放)
```

#### SQLMap检测
```
URL: http://example.com/vulnerable.php?id=1
参数: id
技术: 布尔盲注
结果: 发现SQL注入漏洞
```

### 目录工具使用
1. 点击"目录工具"按钮
2. 选择目标目录（可手动输入或浏览选择）
3. 选择打开方式（文件管理器、命令行等）
4. 点击"打开目录"即可

### 依赖检测使用
1. 点击"依赖检测"按钮
2. 选择要分析的Python脚本或目录
3. 点击"开始分析依赖"
4. 查看分析结果
5. 点击"开始安装所有依赖"进行安装

## 🗡️ SQLMap工具详解

### 概述

SQLMap工具是御锋V1网络安全工具箱中的SQL注入检测模块，支持两种输入方式：

1. **URL参数方式**：直接输入目标URL和参数
2. **请求包文件方式**：上传HTTP请求包文件

### 功能特性

#### 输入方式
- **URL参数**：适用于GET请求的SQL注入检测
- **请求包文件**：适用于POST请求和复杂请求的SQL注入检测

#### 数据库支持
- MySQL、MSSQL、Oracle、PostgreSQL
- SQLite、Access、Firebird、Sybase

#### 注入技术
- **布尔盲注**：基于布尔逻辑的盲注
- **时间盲注**：基于时间延迟的盲注
- **联合查询**：使用UNION语句的注入
- **错误注入**：基于错误信息的注入
- **堆叠注入**：多语句注入

#### 高级选项
- **检测等级**：1-5级，等级越高检测越全面
- **风险等级**：1-3级，等级越高风险越大
- **线程数**：并发线程数量
- **代理设置**：支持HTTP代理
- **批处理模式**：自动确认所有提示
- **随机User-Agent**：随机化请求头

### 使用步骤

#### 1. URL参数方式
1. 选择"URL参数"输入方式
2. 填写目标URL，例如：`http://example.com/vulnerable.php?id=1`
3. 填写参数名，例如：`id`
4. 选择数据库类型和注入技术
5. 配置高级选项
6. 生成并执行命令

#### 2. 请求包文件方式
1. 选择"请求包文件"输入方式
2. 点击"浏览"选择HTTP请求包文件
3. 点击"预览请求包"查看文件内容
4. 系统会自动解析URL和参数
5. 配置其他选项
6. 生成并执行命令

### 预设模板

#### 基础检测模板
- 检测等级：1
- 风险等级：1
- 线程数：10
- 适用于快速检测是否存在SQL注入

#### 完整扫描模板
- 检测等级：5
- 风险等级：3
- 线程数：20
- 适用于深度扫描和全面检测

#### 数据获取模板
- 检测等级：3
- 风险等级：2
- 线程数：10
- 注入技术：联合查询
- 自动添加--dump参数
- 适用于获取数据库中的数据

### 请求包格式

#### GET请求示例
```
GET /vulnerable.php?id=1&name=test HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Accept: text/html,application/xhtml+xml
Connection: close
```

#### POST请求示例
```
POST /vulnerable.php HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Content-Type: application/x-www-form-urlencoded
Content-Length: 15
Connection: close

id=1&name=test
```

## 📦 打包说明

### 打包脚本说明

本项目提供了两个打包脚本：

#### 1. build.py - 通用打包脚本
- 支持多种打包格式
- 可选择仅构建EXE、创建安装包、创建ZIP压缩包
- 适合不同发布需求

#### 2. build_exe.py - EXE专用打包脚本
- 专门用于生成Windows可执行文件
- 自动包含SQLMap工具和相关资源
- 生成完整的发布包

### 使用方法

#### 方法一：使用通用打包脚本
```bash
python build.py
```

#### 方法二：使用EXE专用打包脚本
```bash
python build_exe.py
```

#### 方法三：使用启动脚本
```bash
启动御锋V1.bat
```

### 打包前准备

1. 确保已安装Python 3.6+
2. 安装所需依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 确保主程序文件 `御锋V1网络安全工具箱.py` 存在

### 打包选项

#### build.py 选项：
- 1. 仅构建可执行文件
- 2. 构建并创建安装包
- 3. 构建并创建ZIP压缩包
- 4. 完整构建（可执行文件 + 安装包 + ZIP）
- 5. 清理构建文件

#### build_exe.py 选项：
- 1. 仅构建可执行文件
- 2. 构建并创建发布包
- 3. 清理构建文件

### 输出文件

#### 构建结果
- `dist/御锋V1网络安全工具箱.exe` - 主程序可执行文件

#### 发布包内容
- `御锋V1网络安全工具箱.exe` - 主程序
- `启动御锋V1.bat` - 启动脚本
- `使用说明.txt` - 使用说明
- `README.md` - 项目说明
- `LICENSE` - 许可证
- `requirements.txt` - 依赖列表

### 注意事项

1. 首次打包可能需要较长时间，因为需要下载PyInstaller
2. 某些杀毒软件可能误报，这是正常现象
3. 打包后的文件较大，这是包含Python运行时的正常情况
4. 建议在打包前先测试主程序是否正常运行

### 故障排除

#### 常见问题：

1. **PyInstaller未安装**
   - 脚本会自动安装，如果失败请手动安装：
   ```bash
   pip install pyinstaller
   ```

2. **主程序文件未找到**
   - 确保 `御锋V1网络安全工具箱.py` 文件存在
   - 检查文件名是否正确

3. **构建失败**
   - 检查Python版本是否满足要求
   - 确保所有依赖已正确安装
   - 查看错误信息进行针对性解决

4. **文件过大**
   - 这是正常现象，EXE文件包含了Python运行时
   - 可以使用UPX压缩（脚本已启用）

## 🏗️ 技术架构

### 技术栈
- **前端**: Tkinter (Python GUI框架)
- **后端**: Python 3.6+
- **加密**: pycryptodome
- **网络**: requests, socket
- **解析**: dns.resolver, json

### 架构设计
```
┌─────────────────────────────────────────────────────────┐
│                    用户界面层 (UI Layer)                  │
├─────────────────────────────────────────────────────────┤
│                业务逻辑层 (Business Layer)                │
├─────────────────────────────────────────────────────────┤
│                工具集成层 (Tool Integration)             │
├─────────────────────────────────────────────────────────┤
│                系统接口层 (System Interface)             │
└─────────────────────────────────────────────────────────┘
```

### 核心模块

#### 1. 主程序模块 (`御锋V1网络安全工具箱.py`)
- 程序入口和主界面
- 功能模块调度
- 用户交互处理

#### 2. 工具模块
- **解码工具**: Base64、URL、AES、哈希
- **网络工具**: DNS、端口扫描、请求测试
- **文件工具**: 哈希计算、文件比较
- **开发工具**: 依赖管理、打包工具

#### 3. 辅助模块
- **密码管理**: 登录信息存储
- **搜索功能**: 文本搜索和高亮
- **滚动条**: 自定义滚动条组件

### 设计模式

- **MVC模式**: 分离界面、逻辑、数据
- **单例模式**: 主程序实例管理
- **工厂模式**: 工具模块创建
- **观察者模式**: 事件处理机制

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献方式

1. **报告问题**
   - 使用 [Issues](https://github.com/xiaoqitc/yujian/issues) 报告Bug
   - 提供详细的错误信息和复现步骤

2. **功能建议**
   - 在Issues中提出新功能建议
   - 描述功能需求和实现思路

3. **代码贡献**
   - Fork项目
   - 创建功能分支
   - 提交Pull Request

### 开发环境

```bash
# 克隆项目
git clone https://github.com/xiaoqitc/yujian.git

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 运行程序
python 御锋V1网络安全工具箱.py
```

### 代码规范

- 遵循PEP 8代码风格
- 添加适当的注释和文档
- 编写单元测试
- 使用类型提示

## 📄 许可证

本项目采用 [MIT许可证](LICENSE)。

```
MIT License

Copyright (c) 2024 小白

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🆓 免费开源

本工具完全免费开源，账号密码请查看GitHub或联系作者获取。

## ⚠️ 免责声明

**重要提醒**: 本工具仅供学习和研究使用，请勿用于非法用途。

- 使用者需自行承担使用风险
- 请遵守当地法律法规
- 仅在有授权的目标上使用
- 不得用于恶意攻击或非法活动

## 📞 联系方式

- **作者**: 小白
- **微信**: ccyuwu8888
- **QQ**: 1544185387
- **邮箱**: 1544185387@qq.com
- **GitHub**: [@xiaoqitc](https://github.com/xiaoqitc)

## 🙏 致谢

感谢以下开源项目的支持：

- [SQLMap](https://github.com/sqlmapproject/sqlmap) - SQL注入检测工具
- [Requests](https://github.com/psf/requests) - HTTP库
- [pycryptodome](https://github.com/Legrandin/pycryptodome) - 加密库
- [dnspython](https://github.com/rthalley/dnspython) - DNS工具包

## 📈 项目统计

![GitHub stars](https://img.shields.io/github/stars/xiaoqitc/yujian)
![GitHub forks](https://img.shields.io/github/forks/xiaoqitc/yujian)
![GitHub issues](https://img.shields.io/github/issues/xiaoqitc/yujian)
![GitHub pull requests](https://img.shields.io/github/issues-pr/xiaoqitc/yujian)

## 🔮 未来计划

- [ ] 添加更多编码/解码格式支持
- [ ] 集成更多网络安全工具
- [ ] 支持插件系统
- [ ] 添加报告生成功能
- [ ] 支持云端配置同步
- [ ] 添加更多数据库类型支持

---

⭐ **如果这个项目对您有帮助，请给我们一个Star！** ⭐ 