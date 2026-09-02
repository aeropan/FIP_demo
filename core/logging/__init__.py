"""core.logging —— 飞书日志模块。

封装访问行为与用户反馈写入飞书多维表格的逻辑。
所有写入失败均静默处理（仅留服务端日志），确保不阻塞主流程。
"""

from .feishu_logger import FeishuLogger

__all__ = ["FeishuLogger"]
