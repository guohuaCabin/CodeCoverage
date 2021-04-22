#!usr/bin/python
# -*- coding: utf-8 -*-

#导入标准库
import glob # 文件名模式匹配
import os # 对操作系统进行调用的接口模块
import sys # 获取系统相关信息
import shutil # 文件、文件夹、压缩包 处理模块
import re # 正则表达式模块
import string # 字符串模块


class CommitDiff:
    def __init__(self):
        self.classDiffInfoList = [] #提交的每个类内容列表
        
    #判断类列表中是否包含该类
    def contains_classdiff(self,className):
        for classDiffInfo in self.classDiffInfoList :
            if classDiffInfo.className == className:
                return True
        return False    

    # 根据类名获取该类的差异代码，如果数组中没有，初始化一个
    def classDiffInfo(self,className):
        for diffInfo in self.classDiffInfoList:
            if diffInfo.className == className:
                return diffInfo
        #如果不存在，初始化一个classdiff，并添加到classdiffs
        diffInfo = ClassDiffInfo(className)
        self.classDiffInfoList.append(diffInfo)
        return diffInfo

    
#类列表中的内容
class ClassDiffInfo:
    def __init__(self,classname):
        self.className = classname
        self.blockInfoList = [] #提交的块列表
    

#每个块中的信息 （增 / 删行数）
class BlockInfo:
    def __init__(self):
        self.delLine = 0
        self.delCount = 0
        self.addLine = 0
        self.addCount = 0
