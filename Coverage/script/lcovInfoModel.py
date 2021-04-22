#!usr/bin/python
# -*- coding: utf-8 -*-

#导入标准库
import glob # 文件名模式匹配
import os # 对操作系统进行调用的接口模块
import sys # 获取系统相关信息
import shutil # 文件、文件夹、压缩包 处理模块
import re # 正则表达式模块
import string # 字符串模块


class LcovInfo:
  def __init__(self):
    self.fileInfoList = []

  def lcovClassInfo(self,classname):
    for classInfo in self.fileInfoList:
      if classInfo.classname == classname:
        return classInfo
    classInfo = LcovClassInfo(classname)
    self.fileInfoList.append(classInfo)
    return classInfo
    


class LcovClassInfo:
  def __init__(self,classname):
    self.classname = classname
    self.classNamePath = ''
    self.classInfo = ''#fileInfo内容：每个类的内容
    self.daList = [] #classInfo根据FN、FNDA、DA匹配规则解析的执行信息
    

class LcovClassDataInfo:
    def __init__(self):
        self.lineNo = 0
        self.exeCount = 0
        self.funName = ''
        self.isNewLine = False


