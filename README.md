# ComfyUI Zhuge 自定义节点集

一组用于 ComfyUI 的自定义节点，提供文本处理和循环功能。

## 安装

1. 将整个 `comfyui_zhuge` 文件夹复制到 ComfyUI 的 `custom_nodes` 目录
2. 重启 ComfyUI

## 文本处理节点 (zhuge/text_processing)

### Zhuge Text Splitter (核心节点)
整合了文本分割和批量处理功能的多行文本处理器。

**输入参数:**
- `text`: 多行文本
- `split_char`: 分割字符（默认 \n）
- `start_index`: 起始索引（默认 0）
- `end_index`: 结束索引（默认 -1）
- `prefix`: 文本前缀
- `suffix`: 文本后缀
- `auto_loop`: 是否自动循环（默认 False）
- `reset`: 重置索引（默认 False）

**输出:**
- `current_text`: 当前处理的文本行（带前后缀）
- `current_index`: 当前索引
- `total_count`: 总行数
- `has_more`: 是否还有更多行需要处理

### Zhuge Text Split Info
文本分割信息统计器，输出原始文本和分割数量。

**输入:**
- `text`: 多行文本
- `split_char`: 分割字符

**输出:**
- `source_text`: 原始文本
- `total_count`: 分割后的总行数

### 其他辅助节点
- **Zhuge Text Joiner**: 文本合并器
- **Zhuge Text Replacer**: 文本替换器
- **Zhuge Text Counter**: 文本统计器

## 使用示例

### 基本文本分割
1. 连接 `Zhuge Text Splitter` 到您的文本输入
2. 设置分割符和索引范围
3. 点击执行，节点会输出当前行的文本
4. 使用 `has_more` 信号控制是否继续处理

### 自动循环处理
1. 启用 `auto_loop` 参数
2. 节点会在到达末尾后自动回到开头
3. 配合工作流触发器实现连续处理

### 文本信息统计
1. 使用 `Zhuge Text Split Info` 节点分析文本
2. 获取总行数信息用于流程控制

## 特性

- **状态保持**: 使用文件系统保存处理状态
- **灵活配置**: 支持索引范围、前后缀添加
- **循环模式**: 支持自动循环处理
- **可视化反馈**: 实时显示处理状态
- **一键重置**: 方便重新开始处理

详细解释 auto_loop 和 reset 参数的作用：
auto_loop (自动循环)
作用：控制当处理完所有文本行后的行为

当 auto_loop = False (默认值)：
节点会从第一行开始处理，逐行输出
到达最后一行后，has_more 会变为 False
索引会停留在末尾，不会自动回到开头
用途：一次性处理所有行，处理完成后停止

当 auto_loop = True：
节点会从第一行开始处理，逐行输出
到达最后一行后，索引会自动重置为0（回到第一行）
has_more 会一直保持为 True（只要有内容）
用途：无限循环处理，适合需要反复处理相同内容的场景