#!usr/bin/python 
# -*- coding: utf-8 -*-

#导入标准库
import glob # 文件名模式匹配
import os,sys,stat # 对操作系统进行调用的接口模块
import shutil # 文件、文件夹、压缩包 处理模块
import zipfile
import re # 正则表达式模块
import string # 字符串模块
# import gainResult
import threading
#路径
rootPath = sys.path[0]
locvPath = '/lcov/usr/bin/lcov'
genhtmlPath = '/lcov/usr/bin/genhtml'

#解压缩
def un_zip(file_name,path,sourcesPath):
  fileP = path + '/' + file_name
  print("压缩文件路径\n"+fileP)
  zip_file = zipfile.ZipFile(fileP)
  if os.path.isdir(sourcesPath):
      pass
  else:
      os.makedirs(sourcesPath, mode=0o777)
  for names in zip_file.namelist():
      zip_file.extract(names,sourcesPath)
  zip_file.close()

# 根据gcda及gcno文件生成Info文件
def generateInfo(projectName):
  # FIX:QGH
  # filePath = '/Users/qinguohua/Developer/Mistong/XHX/LiveSDK_Cover/'+ projectName  + '/Example/Pods/'
  # projectName  = projectName.split('_',3)[1]
  filePath = '/Users/qinguohua/Developer/Mistong/XHX/LiveSDK_Cover/XHXLiveSDK/Classes/'
  projectName = 'XHXLiveSDK'
  # os.chdir(os.path.join(os.getcwd(), ".."))# 切到项目路径
  uploadPath = os.getcwd() + '/upload'
  sourcesPath = rootPath + '/sources'
  # 定义source路径
  # 如果sources文件目录存在,删除并重建该路径  
  # if os.path.isdir(sourcesPath): 
  #     shutil.rmtree(sourcesPath)
  # 新建sources路径
  print(sourcesPath)
  gcnoName = projectName + '_gcno.zip'
  gcdaName = projectName + '_gcda.zip'
  # threading.Thread(un_zip(str(gcnoName),str(uploadPath),str(sourcesPath))).start
  # threading.Thread(un_zip(str(gcdaName),str(uploadPath),str(sourcesPath))).start

  # os.system 运行shell命令，直接显示.
  # -c 从编译产物中收集覆盖率信息
  # -b 以分支覆盖率形式报告
  # -d 指定编译产物的路径
  # -o 指定覆盖率输出的文件名称
  # 此处使用lcov到sourcesPath目录寻找代码覆盖率文件并收集覆盖率信息,以分支覆盖率形式输出到当前脚本所在目录下的Coverage.info文件中
  lcov = rootPath + locvPath
  coverageInfoPath = rootPath + '/codeCoverageInfo'
  print(coverageInfoPath)
  if not os.path.isdir(coverageInfoPath):
    print('创建info文件夹')
    os.makedirs(coverageInfoPath, mode=0o777)
  print("\n filePath=%s \n  sourcePath:%s \n  coverageInfoPath==%s"%(filePath,sourcesPath,coverageInfoPath))
  infoPath = coverageInfoPath + '/Coverage.info'
  # try:
  #   infoFile = open(infoPath ,'w')
  #   infoFile.close()
  #   os.chmod(str(infoPath),stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
  # except Exception,e:
  #   print('创建Info文件失败:%s'%e)
  ENABLE_BRANCH = "--rc lcov_branch_coverage=1"
  #os.system(lcov + ' -c -b %s -d %s -o \"%s/Coverage.info\" %s 1>/dev/null' %(filePath, sourcesPath,coverageInfoPath, ENABLE_BRANCH))
  # 如果Coverage.info文件不存在
  if not os.path.exists(infoPath):
    # 提示错误信息
    print ('Error:failed to generate Coverage.info')
    exit(1)
  # 如果Coverage.info大小为0
  if os.path.getsize(infoPath) == 0:
    # 提示错误信息
    print ('Error:Coveragte.info size is 0')
    # 移除Coverage.info文件
   # os.remove(infoPath)
    exit(1)

  # 如果 codeCoverageDiff.info 文件存在
  # 将 codeCoverageDiff.info 转为html格式
  genhtml = rootPath + genhtmlPath
  os.system(genhtml + ' --branch-coverage -o %s/html/original %s \"%s/Coverage.info\" 1>/dev/null'%(rootPath,ENABLE_BRANCH,coverageInfoPath)) 


'''
合并基准数据和执行测试文件后生成的覆盖率数据 ( -a 合并文件)
  lcov -a init.info -a cover.info -o total.info

过滤不需要关注的源文件路径和信息
  --remove 删除统计信息中如下的代码或文件，支持正则
  lcov --remove total.info '*/usr/include/*' '*/usr/lib/*' '*/usr/lib64/*' '*/usr/local/include/*' '*/usr/local/lib/*' '*/usr/local/lib64/*' '*/third/*' 'testa.cpp' -o final.info
'''
