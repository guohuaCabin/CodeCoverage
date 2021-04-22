#!usr/bin/python
# -*- coding: utf-8 -*-

#导入标准库
import glob # 文件名模式匹配
import os,stat # 对操作系统进行调用的接口模块
import sys # 获取系统相关信息
import shutil # 文件、文件夹、压缩包 处理模块
import re # 正则表达式模块
import string # 字符串模块

from GitDiffModel  import ClassDiffInfo, CommitDiff, BlockInfo

'''
git 文件分析
'''
rootPath = sys.path[0]

# 生成提交更改信息
def generateCommitDiff(projectName,branchName): 
  print('git 文件分析---开始starting')
  commitDiff = CommitDiff()
  os.chdir(rootPath) 
  #FIX:QGH
  #projectPath = '/Users/qinguohua/Developer/Mistong/XHX/LiveSDK_Cover/'+ projectName
  projectPath = '/Users/qinguohua/Developer/Mistong/XHX/LiveSDK_Cover/'
  diffPath = rootPath + '/diff.txt'
  
  totalLine = ''
  # tmpFile = open(str(diffPath),'w+')
  # 切到项目目录获取git diff 差异代码
  # os.chdir(projectPath)
  # commitC = os.popen('git diff %s origin/master'%branchName)
  # os.chdir(os.path.join(rootPath, "..")) 
  commitC = open(diffPath)
  classNameRe = re.compile('diff --git a\/([\s\S]*)') #匹配 diff --git
  for line in commitC:
#    print('差异代码:%s \n',%line)
    result = classNameRe.findall(line)
    if result:
      # 获取类名
      className = result[0].strip().split('/')[-1]
      if commitDiff.contains_classdiff(className):
        classDiffInfo = commitDiff.classDiffInfo(className)
      else:
        # 初始化类信息
        classDiffInfo = ClassDiffInfo(className)
      # 添加到类列表中
      commitDiff.classDiffInfoList.append(classDiffInfo)

    totalLine = totalLine + line

  # tmpFile.write(totalLine)
  # tmpFile.close()

  commitC.close()

  if not os.path.exists(rootPath + '/diff.txt'):
    print ('No diff file')
    exit(1)

  # 打开diff文件
  diffFile = open(rootPath + '/diff.txt')

  # 增量代码获取 正则过滤表达式
  blockRe = re.compile('@@ (.*) @@') # 匹配代码块的增删行信息

  delLineRe = re.compile('\-(.*)') # 匹配类名（使用‘-’为正则匹配，匹配删除代码）
  addLineRe = re.compile('\+(.*)') # 匹配类名（使用‘+’为正则匹配，是只匹配增量代码）

  blockNumberRe = re.compile('\@\@ \-(\d+),*(\d*) \+(\d+),*(\d*) \@\@') # 匹配代码块中增加删除块的行号信息

  classList = totalLine.split('diff --git ')
  
  for diffGit in classList:
    #去掉为空的
    if not diffGit :
      continue
    #去掉不包含代码块的
    if not blockRe.search(diffGit):
      continue    
    classResult = blockRe.split(diffGit)
    className = classResult[0].strip().split('/')[-1]
    #过滤掉非.h 和 .m文件
    if (className.find('.m') == -1) and  (className.find('.h') ==  -1):
       continue
    
    if commitDiff.contains_classdiff(className):
        #根据类名获取每个类的代码差异内容
       # print("有================" + className)
        classDiffInfo = commitDiff.classDiffInfo(className)
        classDiffInfo.blockInfoList = []        
        blockNumberResult = blockNumberRe.findall(diffGit)
        #删除数组中的第一个元素，（diff --git部分）
        del(classResult[0])
        blockCodeList = classResult[1::2] #匹配代码块中增加删除块的行号信息
        for index in range(len(blockNumberResult)):
          #代码块的增减行数信息
          (delChangelineIndex,delNumber,addChangelineIndex,addNumber) = blockNumberResult[index]
          #代码块的字符串
          blockCodeStr = blockCodeList[index]
          blockList = []
          blockCodeLines = blockCodeStr.split('\n')
          #删除@@后面的那行方法名
          del(blockCodeLines[0])
          
          blockInfo = BlockInfo()
          totalAddLineCount = 0
          totalDelLineCount = 0
          #遍历代码块，匹配增删行
          '''
          不完美，之后解决下
          '''
          for lineIndex in range(len(blockCodeLines)):
            blockInfo = BlockInfo()
            blockLineCode = blockCodeLines[lineIndex]
            #添加删除行的信息
            if blockLineCode.startswith('-',0,1):
              delResult = delLineRe.findall(blockLineCode)
              
              if delResult:
                totalDelLineCount += 1
                if blockInfo.delLine == 0:
                  blockInfo.delLine = int(delChangelineIndex) + lineIndex - totalAddLineCount
                blockInfo.delCount = 1

                if blockInfo.addLine == 0 :
                  blockInfo.addLine = blockInfo.delLine
                  blockInfo.addCount = 0

              if blockInfo.delLine != 0 :
                classDiffInfo.blockInfoList.append(blockInfo)      
            #添加增加行的信息
            #判断line的开头是否是‘+   ’
            if blockLineCode.startswith('+',0,1):
              addResult = addLineRe.findall(blockLineCode)
              
              if addResult:
                totalAddLineCount += 1
                addlineNo = int(addChangelineIndex) + lineIndex - totalDelLineCount
                haveBlockInfo = False
                for preBlockInfo in classDiffInfo.blockInfoList:
                  if preBlockInfo.addLine == addlineNo :
                    haveBlockInfo = True
                    preBlockInfo.addCount = 1
                    break
                if haveBlockInfo == False:
                  if blockInfo.addLine == 0 :
                    blockInfo.addLine = addlineNo
                  blockInfo.addCount = 1

                  if blockInfo.delLine == 0:
                    blockInfo.delLine = blockInfo.addLine
                    blockInfo.delCount = 0
            
                  if blockInfo.delLine != 0 :
                    classDiffInfo.blockInfoList.append(blockInfo)
  print('git 文件分析--- 结束 end')
  return commitDiff
