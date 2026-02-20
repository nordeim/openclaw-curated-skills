"""
FIS 3.1 Lite - Task Router
长任务自动分派到 SubAgent 的判断逻辑
"""

from typing import Dict, Any
import re

# 任务类型分类
def classify_task(task_description: str) -> Dict[str, Any]:
    """
    分析任务描述，判断是否应使用 SubAgent
    
    Args:
        task_description: 任务描述
        
    Returns:
        {
            "use_subagent": bool,
            "reason": str,
            "estimated_time": str,  # "quick" | "medium" | "long"
            "recommended_role": str  # "worker" | "researcher" | "reviewer" | "formatter"
        }
    """
    desc_lower = task_description.lower()
    
    # 关键词匹配 - 强制使用 SubAgent
    long_task_keywords = [
        "调研", "research", "调查", "分析", "analyze",
        "统计", "count", "计算", "calculate",
        "生成", "generate", "创建", "create",
        "批量", "batch", "多个", "multiple",
        "整理", "organize", "清理", "cleanup",
        "检查", "check", "验证", "verify",
        "搜索", "search", "查询", "query",
        "下载", "download", "上传", "upload",
        "同步", "sync", "备份", "backup",
        "编译", "build", "测试", "test",
        "部署", "deploy", "发布", "publish"
    ]
    
    # 关键词匹配 - 快速任务，主会话处理
    quick_task_keywords = [
        "是什么", "什么是", "how to", "怎么",
        "解释", "explain", "说明", "describe",
        "比较", "compare", "对比", "vs",
        "推荐", "recommend", "建议", "suggest",
        "是", "否", "yes", "no",
        "打开", "查看", "show", "display"
    ]
    
    # 检查是否匹配长任务关键词
    for keyword in long_task_keywords:
        if keyword in desc_lower:
            return {
                "use_subagent": True,
                "reason": f"检测到长任务关键词: '{keyword}'",
                "estimated_time": "medium",
                "recommended_role": _infer_role(task_description)
            }
    
    # 检查是否匹配快速任务关键词
    for keyword in quick_task_keywords:
        if keyword in desc_lower:
            return {
                "use_subagent": False,
                "reason": f"快速问答类任务，主会话直接处理",
                "estimated_time": "quick",
                "recommended_role": None
            }
    
    # 默认策略：中等复杂度的任务使用 SubAgent
    # 根据描述长度判断
    word_count = len(task_description.split())
    if word_count > 20:
        return {
            "use_subagent": True,
            "reason": "任务描述较长，可能涉及多步骤操作",
            "estimated_time": "medium",
            "recommended_role": _infer_role(task_description)
        }
    
    return {
        "use_subagent": False,
        "reason": "简单任务，主会话直接处理更高效",
        "estimated_time": "quick",
        "recommended_role": None
    }


def _infer_role(task_description: str) -> str:
    """根据任务描述推断推荐角色"""
    desc_lower = task_description.lower()
    
    if any(k in desc_lower for k in ["review", "检查", "验证", "审核", "审查", "verify", "check"]):
        return "reviewer"
    elif any(k in desc_lower for k in ["research", "调研", "调查", "分析", "analyze", "研究"]):
        return "researcher"
    elif any(k in desc_lower for k in ["format", "整理", "格式化", "排版", "clean", "清理"]):
        return "formatter"
    else:
        return "worker"


def should_use_subagent(task_description: str, context: Dict[str, Any] = None) -> bool:
    """
    快速判断是否应使用 SubAgent
    
    使用场景:
        if should_use_subagent("帮我整理文件夹"):
            # 创建 SubAgent
            card = manager.spawn(...)
        else:
            # 主会话直接处理
            pass
    """
    result = classify_task(task_description)
    return result["use_subagent"]


# 预定义的任务模式
TASK_PATTERNS = {
    "file_organization": {
        "patterns": [r"整理.*文件", r"organize.*files?", r"清理.*目录", r"cleanup.*folder"],
        "use_subagent": True,
        "role": "worker",
        "timeout": 30
    },
    "code_analysis": {
        "patterns": [r"分析.*代码", r"analyze.*code", r"统计.*行数", r"count.*lines"],
        "use_subagent": True,
        "role": "researcher", 
        "timeout": 20
    },
    "git_operations": {
        "patterns": [r"git.*status", r"提交.*更改", r"push.*commit", r"同步.*仓库"],
        "use_subagent": True,
        "role": "worker",
        "timeout": 15
    },
    "quick_query": {
        "patterns": [r"是什么", r"how to", r"怎么", r"为什么"],
        "use_subagent": False,
        "role": None,
        "timeout": 0
    }
}


def match_task_pattern(task_description: str) -> Dict[str, Any]:
    """
    匹配预定义任务模式
    
    Returns:
        匹配的模式配置，或默认配置
    """
    for pattern_name, config in TASK_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, task_description, re.IGNORECASE):
                return {
                    "matched_pattern": pattern_name,
                    **config
                }
    
    # 无匹配，返回 classify_task 结果
    classification = classify_task(task_description)
    return {
        "matched_pattern": None,
        "use_subagent": classification["use_subagent"],
        "role": classification["recommended_role"],
        "timeout": 30 if classification["estimated_time"] == "medium" else 60
    }


# 使用示例
if __name__ == "__main__":
    # 测试用例
    test_tasks = [
        "帮我整理 downloads 文件夹里的文件",
        "统计 workspace 目录下的 Python 文件行数",
        "GitHub 是什么？",
        "解释 FIS 架构的核心概念",
        "检查 system 目录下有没有重复文件",
        "创建一个新的 Python 脚本生成周报"
    ]
    
    for task in test_tasks:
        result = classify_task(task)
        pattern = match_task_pattern(task)
        print(f"\n任务: {task}")
        print(f"  使用 SubAgent: {result['use_subagent']}")
        print(f"  原因: {result['reason']}")
        print(f"  推荐角色: {result['recommended_role']}")
        print(f"  匹配模式: {pattern.get('matched_pattern', '动态判断')}")
