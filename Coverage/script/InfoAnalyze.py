#!usr/bin/python
# -*- coding: utf-8 -*-

#导入标准库
import glob # 文件名模式匹配
import os # 对操作系统进行调用的接口模块
import sys # 获取系统相关信息
import shutil # 文件、文件夹、压缩包 处理模块
import re # 正则表达式模块
import string # 字符串模块


'''
解析 .info 文件
'''

# 导入某文件中的类
from lcovInfoModel import LcovInfo,LcovClassInfo,LcovClassDataInfo

# def定义一个函数 根据提交的更改信息使用lcov获取info
def getLcovInfo():
    # os.environ 获取系统环境变量
    rootPath = sys.path[0]
    coveragePath = rootPath + '/codeCoverageInfo/Coverage.info'
    os.chdir(rootPath) # 改变当前脚本工作目录；相当于shell下cd,及切到当前脚本的绝对路径
    lcovInfo = LcovInfo()
    # 判断当前路径下是否存在 Coverage.info 文件
    if not os.path.exists(coveragePath):
        print ('Error:No Coverage.info')
        exit(1)
    # 判断 Coverage.info 文件大小
    if os.path.getsize(coveragePath) == 0:
        print ('Error:Coverage.info size is 0')
        os.remove(coveragePath)
        exit(1)

    ##遍历.info文件 

    #获取info文件内容
    infoContent = open(coveragePath,'r').read()
    #根据end_of_record分割
    fileInfoList = infoContent.split('end_of_record\n')

    #类名匹配规则
    classNameRe = re.compile('SF:(.*)')
    FNRe = re.compile('FN:(.*)')
    FNDARe = re.compile('FNDA:(.*)')
    DARe = re.compile('\nDA:(.*)')

    # 遍历每个class类，获取daList
    for fileInfo in fileInfoList:
        if not fileInfo:
            continue
        # 类名匹配
        classNameResult = classNameRe.findall(fileInfo)
        if len(classNameResult) == 0:
            continue
        #获取到类名
        className = classNameResult[0].strip().split('/')[-1]
        lcovClassInfo = lcovInfo.lcovClassInfo(className)
        lcovClassInfo.classNamePath = classNameResult[0]
        lcovClassInfo.fileInfo = fileInfo
        
        FNList = FNRe.findall(fileInfo)
        DAList = DARe.findall(fileInfo)
        
        nextFNNumber = 0
        for da in DAList:
            lineNo = da.strip().split(',')[0]
            exeCount = da.strip().split(',')[-1]
            ## 找该行所在的方法名
            for index in range(len(FNList)):
                curFNNumber = FNList[index].strip().split(',')[0]
                if index < len(FNList)-1:
                    nextFNNumber = FNList[index+1].strip().split(',')[0]
                else:
                    nextFNNumber = DAList[len(DAList)-1].strip().split(',')[0]
                if lineNo >= curFNNumber and lineNo < nextFNNumber:
                    ## 方法名
                    funName = FNList[index].strip().split(',')[-1]
                    classDataInfo = LcovClassDataInfo()
                    classDataInfo.lineNo = lineNo
                    classDataInfo.funName = funName
                    classDataInfo.exeCount = exeCount
                    lcovClassInfo.daList.append(classDataInfo)
    return lcovInfo

if __name__ == "__main__":
    # 生成Info文件
    getLcovInfo()

