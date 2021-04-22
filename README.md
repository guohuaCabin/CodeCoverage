# CodeCoverage


关于`iOS` 的代码覆盖率

**Script**: 该文件是获取`gcno` 和`gcda` 文件、解析为`info` 文件，并做一系列增量代码标记、增量代码平移等操作

**lcov:** 这里存放了`lcov` 工具，并针对`usr/bin` 中的`genthml` 做了定制化，增加了增量代码的处理

**sources**: 存放`gcno` 和`gcda` 文件

**htmlFile：** 存放最终生成的`html` 文件

**InfoFile:** 存放生成的`info` 文件