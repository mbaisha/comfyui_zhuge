import comfy.utils
import comfy.sd
import nodes
import folder_paths
import torch
import re
import json
import os
from nodes import MAX_RESOLUTION

# 全局状态存储
class ZhugeStateManager:
    _state_file = os.path.join(os.path.dirname(__file__), "zhuge_state.json")
    
    @classmethod
    def load_state(cls, node_id, default_state=None):
        """加载节点状态"""
        try:
            if os.path.exists(cls._state_file):
                with open(cls._state_file, 'r', encoding='utf-8') as f:
                    all_states = json.load(f)
                    return all_states.get(node_id, default_state)
        except:
            pass
        return default_state
    
    @classmethod
    def save_state(cls, node_id, state):
        """保存节点状态"""
        try:
            all_states = {}
            if os.path.exists(cls._state_file):
                with open(cls._state_file, 'r', encoding='utf-8') as f:
                    all_states = json.load(f)
            
            all_states[node_id] = state
            
            with open(cls._state_file, 'w', encoding='utf-8') as f:
                json.dump(all_states, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存状态失败: {e}")

class ZhugeTextSplitter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "split_char": ("STRING", {"default": "\\n"}),
                "start_index": ("INT", {"default": 0, "min": -100, "max": 100}),
                "end_index": ("INT", {"default": -1, "min": -100, "max": 100}),
                "prefix": ("STRING", {"default": ""}),
                "suffix": ("STRING", {"default": ""}),
                "auto_loop": ("BOOLEAN", {"default": False}),
                "reset": ("BOOLEAN", {"default": False}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "BOOLEAN")
    RETURN_NAMES = ("current_text", "current_index", "total_count", "has_more")
    FUNCTION = "split_text"
    CATEGORY = "zhuge/text_processing"
    OUTPUT_NODE = True

    def split_text(self, text, split_char, start_index, end_index, prefix, suffix, auto_loop, reset, unique_id=None):
        # 处理转义字符
        if split_char == "\\n":
            split_char = "\n"
        elif split_char == "\\t":
            split_char = "\t"
        
        # 分割文本
        lines = text.split(split_char)
        
        # 过滤空行
        lines = [line.strip() for line in lines if line.strip()]
        
        # 处理索引范围
        total_lines = len(lines)
        
        if start_index < 0:
            start_index = max(0, total_lines + start_index)
        else:
            start_index = min(start_index, total_lines - 1)
            
        if end_index < 0:
            end_index = total_lines + end_index
        else:
            end_index = min(end_index, total_lines - 1)
            
        start_index = max(0, start_index)
        end_index = min(total_lines - 1, end_index)
        
        if start_index > end_index:
            start_index, end_index = end_index, start_index
        
        # 获取当前需要处理的文本段
        selected_lines = lines[start_index:end_index + 1]
        total_selected = len(selected_lines)
        
        # 加载状态
        state = ZhugeStateManager.load_state(unique_id, {"current_index": 0})
        
        # 重置逻辑
        if reset:
            state = {"current_index": 0}
        
        current_index = state["current_index"]
        
        # 检查是否还有更多内容需要处理
        has_more = current_index < total_selected - 1
        
        # 获取当前文本并添加前后缀
        if current_index < total_selected:
            current_line = selected_lines[current_index]
            current_text = f"{prefix}{current_line}{suffix}"
        else:
            current_text = ""
            has_more = False
        
        # 更新状态
        if auto_loop:
            # 循环模式：到达末尾后回到开头
            state["current_index"] = (current_index + 1) % total_selected if total_selected > 0 else 0
            # 在循环模式下，只要还有内容就认为有更多
            has_more = total_selected > 0
        else:
            # 非循环模式：递增索引直到末尾
            state["current_index"] = current_index + 1
        
        # 保存状态
        ZhugeStateManager.save_state(unique_id, state)
        
        return (current_text, current_index, total_selected, has_more)

class ZhugeTextSplitInfo:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "split_char": ("STRING", {"default": "\\n"}),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("source_text", "total_count")
    FUNCTION = "get_split_info"
    CATEGORY = "zhuge/text_processing"

    def get_split_info(self, text, split_char):
        # 处理转义字符
        if split_char == "\\n":
            split_char = "\n"
        elif split_char == "\\t":
            split_char = "\t"
        
        # 分割文本并过滤空行
        lines = [line.strip() for line in text.split(split_char) if line.strip()]
        total_count = len(lines)
        
        return (text, total_count)

class ZhugeTextJoiner:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text1": ("STRING", {"default": ""}),
                "text2": ("STRING", {"default": ""}),
                "text3": ("STRING", {"default": ""}),
                "text4": ("STRING", {"default": ""}),
                "join_char": ("STRING", {"default": "\\n"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "join_texts"
    CATEGORY = "zhuge/text_processing"

    def join_texts(self, text1, text2, text3, text4, join_char):
        # 处理转义字符
        if join_char == "\\n":
            join_char = "\n"
        elif join_char == "\\t":
            join_char = "\t"
        
        # 过滤空文本并连接
        texts = [text for text in [text1, text2, text3, text4] if text.strip()]
        result = join_char.join(texts)
        
        return (result,)

class ZhugeTextReplacer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "search_pattern": ("STRING", {"default": ""}),
                "replace_with": ("STRING", {"default": ""}),
                "use_regex": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "replace_text"
    CATEGORY = "zhuge/text_processing"

    def replace_text(self, text, search_pattern, replace_with, use_regex):
        if not search_pattern:
            return (text,)
        
        try:
            if use_regex:
                result = re.sub(search_pattern, replace_with, text)
            else:
                result = text.replace(search_pattern, replace_with)
        except Exception as e:
            print(f"Text replace error: {e}")
            result = text
        
        return (result,)

class ZhugeTextCounter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "reset_counter": ("BOOLEAN", {"default": False}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("count", "count_text")
    FUNCTION = "count_text"
    CATEGORY = "zhuge/text_processing"
    OUTPUT_NODE = True

    def count_text(self, text, reset_counter, unique_id=None):
        # 统计字符数、单词数、行数
        char_count = len(text)
        word_count = len(text.split())
        line_count = len([line for line in text.split('\n') if line.strip()])
        
        count_info = f"字符: {char_count}, 单词: {word_count}, 行数: {line_count}"
        
        return (char_count, count_info)

# 节点注册
NODE_CLASS_MAPPINGS = {
    "ZhugeTextSplitter": ZhugeTextSplitter,
    "ZhugeTextSplitInfo": ZhugeTextSplitInfo,
    "ZhugeTextJoiner": ZhugeTextJoiner,
    "ZhugeTextReplacer": ZhugeTextReplacer,
    "ZhugeTextCounter": ZhugeTextCounter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ZhugeTextSplitter": "Zhuge Text Splitter",
    "ZhugeTextSplitInfo": "Zhuge Text Split Info",
    "ZhugeTextJoiner": "Zhuge Text Joiner", 
    "ZhugeTextReplacer": "Zhuge Text Replacer",
    "ZhugeTextCounter": "Zhuge Text Counter",
}
