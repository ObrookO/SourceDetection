# GitHub敏感信息扫描
一、项目介绍

   扫描GitHub上的敏感信息，减少敏感信息泄漏造成的损失。目前仅支持master分支搜索。

二、使用说明：
    
   1、此项目基于python3.7.3，使用前请确保系统安装了python3.7.3。
   
   2、使用命令 `pip3 install -r requirements.txt` 安装依赖包。
   
   3、添加配置信息，配置文件位于conf/app.conf。
   
    [main]                              # 主要配置，名称不可变
    username=xxx                        # GitHub用户名
    password=xxx                        # GitHub密码
    keywords=xxx                        # 搜索关键词，若有多个，形式为：xxx,xxx,xxx
    
    [es]                                # es相关配置，名称不可变
    host=xxx                            # es地址，若有多个，形式为：xxx,xxx,xxx,如不填默认使用127.0.0.1:9200
   
   
   4、运行
   
   执行以下命令来运行程序：
   
   `python3 src/sd.py`
