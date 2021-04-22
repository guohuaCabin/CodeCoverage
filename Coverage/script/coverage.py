#!usr/bin/python
# -*- coding: utf-8 -*-

#导入标准库
import glob # 文件名模式匹配
import os,stat # 对操作系统进行调用的接口模块
import sys # 获取系统相关信息
import shutil # 文件、文件夹、压缩包 处理模块
import re # 正则表达式模块
import string # 字符串模块
import copy
import webbrowser



# 导入文件
import GitDiffAnalyze
import InfoAnalyze
import GenerateNewResultInfo
from GitDiffModel  import ClassDiffInfo, CommitDiff, BlockInfo
from lcovInfoModel import LcovInfo,LcovClassInfo,LcovClassDataInfo


rootPath = sys.path[0]
genhtmlPath = '/lcov/usr/bin/genhtml'
genhtml = rootPath + genhtmlPath
genhtml_pl = rootPath + '/lcov/usr/bin/genhtml.pl'

LineTranslationInfoName = 'Coverage_LineTranslation.info'
LineMarkInfoName = 'Coverage_LineMark.info'

lineTranslationInfoPath = rootPath + '/codeCoverageInfo'
lineMarkInfoPath = rootPath + '/codeCoverageInfo'


# 创建实例
#diffFile = CommitDiff()
#lcovInfo = LcovInfo()

'''
生成行号平移后的 info 文件：
1. 根据 diffFile 解析结果，遍历 blockInfo 匹配起始修改行号 delLine 及修改行数 diffline = addCount - delCount，
将 info 的解析结果进行行号匹配和增 / 删操作 if (lineNo > delLine) lineNo += diffLine，修改 fileInfoList
2. 将新的 fileInfoList 中的数据根据 info 的结构进行写入文件操作

'''
#行号平移，在行号平移的过程中会修改daList里的数据，所以在做行号平移之前先完成行号标记
def lineTranslationHandleInfo(lcovInfo,diffFile):
    if lcovInfo == None:
        return
    for fileInfo in lcovInfo.fileInfoList:
        infoClassName = fileInfo.classname
        #git diff中不包含该类，过滤掉
        if not diffFile.contains_classdiff(infoClassName):
            continue
        diffInfo = diffFile.classDiffInfo(infoClassName)
    #    print(diffInfo.blockInfoList)
    #    print("=========================================")
        #遍历代码块中修改的行，根据if (lineNo > delLine) lineNo += diffLine做判断，修改fileInfoList数组中的DA
        for changeLineInfo in diffInfo.blockInfoList:
            # print('加======%s'%(changeLineInfo.addCount)  )
            # print('减======%s'%(changeLineInfo.delCount)  )
            # print('删行======%s'%(changeLineInfo.delLine)  )
            diffLine = changeLineInfo.addCount - changeLineInfo.delCount
            delLine = changeLineInfo.delLine
            #遍历DAList修改行号
            for da in fileInfo.daList:
                lineNo = da.lineNo
                if  int(lineNo) > int(delLine):
                    lineNoInt = int(lineNo) + int(diffLine)
                    lineNo = str(lineNoInt)
                    da.lineNo = lineNo

    #将fileInfoList中的数据根据info的结构写入新的info文件
    #创建路径
    if not os.path.isdir(lineTranslationInfoPath):
       os.makedirs(lineTranslationInfoPath)

    lineTranslationInfo = lineTranslationInfoPath + '/' + LineTranslationInfoName
    # print('lineTranslationInfo=========%s'%lineTranslationInfo)
    if os.path.exists(lineTranslationInfo):
        os.remove(lineTranslationInfo)
    infoFileW = open(lineTranslationInfo,'w')

    for fileInfo in lcovInfo.fileInfoList:
        classNamePath = fileInfo.classNamePath
        infoFileW.write('SF:'+classNamePath+'\n')
        preFunName = ''
        FNF = 0 #函数总数
        FNH = 0 #函数执行数
        LF = 0 #代码总行数
        LH = 0 #代码执行行数
        FNList = []
        FNDAList = []
        DAList = []
        for da in fileInfo.daList:
            funName = da.funName
            if funName != preFunName:
                FN = 'FN:%s,%s\n'%(da.lineNo,da.funName)
                FNDA = 'FNDA:%s,%s\n'%(da.exeCount,da.funName)
                FNList.append(FN)
                FNDAList.append(FNDA)
                preFunName = funName
                FNF += 1
                if int(da.exeCount) != 0 :
                    FNH += 1


            DA = 'DA:%s,%s\n'%(da.lineNo,da.exeCount)
            DAList.append(DA)
            if int(da.exeCount) != 0 :
                LH += 1
            LF += 1
        
        FNFStr = 'FNF:%s\n'%FNF
        FNHStr = 'FNH:%s\n'%FNH
        LHStr = 'LH:%s\n'%LH
        LFStr = 'LF:%s\n'%LF
        writeLineTranslationInfo(FNList,FNDAList,DAList,FNFStr,FNHStr,LHStr,LFStr,infoFileW)
        infoFileW.write('end_of_record\n')

    infoFileW.close()
    #生成行号平移的html
    #os.system(genhtml + ' --branch-coverage --diff-coverage -o html/result --rc lcov_branch_coverage=1 %s 1>/dev/null'%lineTranslationInfo)
    #os.system(genhtml_pl + ' --branch-coverage --diff-coverage -o html/result --rc lcov_branch_coverage=1 %s 1>/dev/null'%lineTranslationInfo)

def writeLineTranslationInfo(FNList,FNDAList,DAList,FNF,FNH,LH,LF,infoFileW):
    for fn in FNList:
        infoFileW.write(fn)
    
    for fnda in FNDAList:
        infoFileW.write(fnda)
    
    infoFileW.write(FNF)
    infoFileW.write(FNH)

    for da in DAList:
        infoFileW.write(da)

    infoFileW.write(LF)
    infoFileW.write(LH)

'''
生成行号标记后的 info 文件：
1. 根据 diffFile 解析结果，遍历 blockInfo 匹配起始修改行号 addLine 及修改行数 addCount，
将 info 的解析结果进行行号匹配和标记 if (lineNo ∈ [addLine, addLine + addCount)) daInfo.isNewLine = true，修改 fileInfoList
2. 将新的 fileInfoList 中的数据根据 info 的结构进行写入文件操作，同时将新增的 CA、CF、CH 数据填入 info 文件。
'''
# 做标记处理
def gotoMarkHandle(lcovInfo,diffFile):
    for fileInfo in lcovInfo.fileInfoList:
        infoClassName = fileInfo.classname
        #git diff中不包含该类，过滤掉
        # if not diffFile.contains_classdiff(infoClassName):
        #     continue
        
        diffInfo = diffFile.classDiffInfo(infoClassName)
        for changeLineInfo in diffInfo.blockInfoList:
            upLine = changeLineInfo.addLine + changeLineInfo.addCount
            addLine = changeLineInfo.addLine
            #遍历DAList修改行号
            for da in fileInfo.daList:
                lineNo = da.lineNo
                if  int(lineNo) >= int(addLine) and int(lineNo) < int(upLine):
                    da.isNewLine = True
    return lcovInfo
## 写入.info文件
def gotoWriteInfoFile(lcovInfo,diffFile):
    #行号标记将fileInfoList中的数据根据info的结构写入新的info文件
    if not os.path.isdir(lineMarkInfoPath):
       os.makedirs(lineMarkInfoPath)
    LineMarkInfo = lineMarkInfoPath + '/' + LineMarkInfoName
    if os.path.exists(LineMarkInfo):
        os.remove(LineMarkInfo)
    infoFileW = open(LineMarkInfo,'w')
    for fileInfoModel in lcovInfo.fileInfoList:
        fileInfo = fileInfoModel.fileInfo
        #获取到类名
        className = fileInfoModel.classname
        #git diff中不包含该类，过滤掉
        if not diffFile.contains_classdiff(className):
            continue
        lines = fileInfo.split('\n')
        for line in lines:
            if len(line) == 0:
                continue
            infoFileW.write(line+'\n')
        CA = 0 #差异代码行及执行次数
        CF = 0 #差异代码行总数
        CH = 0 #差异代码行执行数
        for da in fileInfoModel.daList:
            if int(da.exeCount) != 0 and da.isNewLine:
                    CH += 1
            
            if da.isNewLine:
                CA = 'CA:%s,%s\n'%(da.lineNo,da.exeCount)
                infoFileW.write(CA)
                CF += 1
        if(CF != 0):
            CFStr = 'CF:%s\n'%CF
            infoFileW.write(CFStr)
        if(CH != 0):
            CHStr = 'CH:%s\n'%CH 
            infoFileW.write(CHStr)
        infoFileW.write('end_of_record\n')

    infoFileW.close()
    return LineMarkInfo

#行号标记处理
def lineMarkHandleInfo(lcovInfo,diffFile):
    if lcovInfo == None:
        return
    mark_lcovInfo = gotoMarkHandle(lcovInfo,diffFile)

    LineMarkInfo = gotoWriteInfoFile(mark_lcovInfo,diffFile)
    print('生成增量代码覆盖率html文件----开始')
    #生成行号平移的html
    os.system('perl %s --branch-coverage -o result/coverageLineMark_html --rc lcov_diff_coverage=1 %s'%(genhtml_pl,LineMarkInfo))
    print('生成增量代码覆盖率html文件---------结束') 

def main():
    projectName = "XHXLiveSDK" #sys.argv[1]
    branchName = "origin/feature/feature_CodeCover_qgh" #sys.argv[2]
    msg = "dfsedfsd"#sys.argv[3]
    # 获取git中提交的更改信息
    print('--GitDiffAnalyze 执行开始ing--')
    diffFile =  GitDiffAnalyze.generateCommitDiff(projectName,branchName)
    print('--GitDiffAnalyze 执行结束--')
    
    # 生成Info文件
    print('--GenerateNewResultInfo 执行开始ing--')
    GenerateNewResultInfo.generateInfo(projectName)
    print('--GenerateNewResultInfo 执行结束--')
    
    # 获取lcovinfo
    print('--InfoAnalyze  执行开始ing--')
    lcovInfo = InfoAnalyze.getLcovInfo()
    print('--InfoAnalyze  执行结束--')
    
    print('--行号平移 执行开始ing--')
    # lineTranslationHandleInfo(lcovInfo,diffFile)
    print('--行号平移 执行end--')
    # 获取行号平移和增量行号标记后的.info文件
    
    print('--行号标记  执行开始ing--')
    lineMarkHandleInfo(lcovInfo,diffFile)
    print('--行号标记  执行end--')


if __name__ == "__main__":    
    main() 
    print("****end****") 
