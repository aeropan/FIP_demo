"""core.logging.feishu_logger —— 飞书多维表格日志写入。

通过飞书开放平台 API 将访问行为与用户反馈写入多维表格：
- tenant_access_token 获取与缓存（过期前 5 分钟刷新，线程安全）
- 行为日志写入运行日志表
- 用户反馈写入反馈表，并可同时在行为表写入一条 feedback 行为

设计原则：
- 失败静默：所有异常捕获后仅 logging.warning，不向上抛出，确保不阻塞主流程。
- 空配置 no-op：APP_ID / APP_SECRET / APP_TOKEN 任一为空时，所有写入直接跳过。
- 依赖最小化：仅使用标准库 urllib.request，不引入第三方 HTTP 库。
- 字段值统一为字符串；行为值截断到 2000 字符，避免超出文本列上限。
"""

from __future__ import annotations

import json
import logging
import threading
import urllib.request
from datetime import datetime
from typing import Optional

from core.config import (
    FEISHU_APP_ID,
    FEISHU_APP_SECRET,
    FEISHU_APP_TOKEN,
    FEISHU_BEHAVIOR_TABLE_ID,
    FEISHU_FEEDBACK_TABLE_ID,
)

logger = logging.getLogger(__name__)

_FEISHU_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
_FEISHU_BITERABLE_BASE = "https://open.feishu.cn/open-apis/bitable/v1/apps"
_BEHAVIOR_VALUE_MAX = 2000


class FeishuLogger:
    """封装飞书多维表格写入逻辑（线程安全，失败静默）。"""

    def __init__(self) -> None:
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0  # 到期时刻（时间戳，秒）
        self._lock = threading.Lock()
        # 配置缺失时整体 no-op
        self._enabled = bool(FEISHU_APP_ID and FEISHU_APP_SECRET and FEISHU_APP_TOKEN)

    # ------------------------------------------------------------------
    # token 管理
    # ------------------------------------------------------------------
    def _get_token(self) -> Optional[str]:
        """获取并缓存 tenant_access_token；过期前 5 分钟自动刷新。"""
        if not self._enabled:
            return None
        now = datetime.now().timestamp()
        with self._lock:
            # 仍在有效期内（留 5 分钟余量）直接复用
            if self._token and now < (self._token_expires_at - 300):
                return self._token
            try:
                req = urllib.request.Request(
                    _FEISHU_TOKEN_URL,
                    data=json.dumps(
                        {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                if body.get("code") != 0:
                    logger.warning("[FeishuLogger] 获取 tenant_access_token 失败: %s", body)
                    self._token = None
                    return None
                self._token = body.get("tenant_access_token")
                # expire 单位为秒；提前 5 分钟刷新
                expire = int(body.get("expire", 7200))
                self._token_expires_at = now + expire
                return self._token
            except Exception as exc:  # noqa: BLE001
                logger.warning("[FeishuLogger] 获取 tenant_access_token 异常: %s", exc)
                self._token = None
                return None

    # ------------------------------------------------------------------
    # 底层写入
    # ------------------------------------------------------------------
    def _create_record(self, table_id: str, fields: dict) -> bool:
        """向指定多维表格写入一条记录，返回是否成功。"""
        token = self._get_token()
        if not token or not table_id:
            return False
        url = f"{_FEISHU_BITERABLE_BASE}/{FEISHU_APP_TOKEN}/tables/{table_id}/records"
        payload = {"fields": {k: str(v) for k, v in fields.items()}}
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            if body.get("code") != 0:
                logger.warning("[FeishuLogger] 写入记录失败 table=%s: %s", table_id, body)
                return False
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("[FeishuLogger] 写入记录异常 table=%s: %s", table_id, exc)
            return False

    # ------------------------------------------------------------------
    # 对外方法
    # ------------------------------------------------------------------
    def log_behavior(
        self,
        user_id: str,
        behavior_type: str,
        behavior_value: str,
        ip_address: str,
        user_agent: str,
        timestamp: str,
    ) -> None:
        """写入运行日志表一条行为记录。所有异常静默处理。"""
        if not self._enabled:
            return
        fields = {
            "用户标识": user_id or "",
            "行为时间": timestamp or "",
            "行为类型": behavior_type or "",
            "行为值": (behavior_value or "")[:_BEHAVIOR_VALUE_MAX],
            "IP地址": ip_address or "",
            "用户代理": user_agent or "",
        }
        self._create_record(FEISHU_BEHAVIOR_TABLE_ID, fields)

    def log_feedback(
        self,
        user_id: str,
        name: str,
        source: str,
        contact_type: str,
        contact: str,
        content: str,
        timestamp: str,
    ) -> None:
        """写入反馈表一条记录，并同时在行为流水表写入一条 feedback 行为。"""
        if not self._enabled:
            return
        feedback_fields = {
            "用户标识": user_id or "",
            "称呼": name or "",
            "获取方式": source or "",
            "联系类型": contact_type or "",
            "联系方式": contact or "",
            "意见内容": content or "",
            "提交时间": timestamp or "",
        }
        self._create_record(FEISHU_FEEDBACK_TABLE_ID, feedback_fields)
        # 同时在行为流水表写入一条 feedback 行为，便于统一查看
        self.log_behavior(
            user_id=user_id,
            behavior_type="feedback",
            behavior_value="提交反馈",
            ip_address="",
            user_agent="",
            timestamp=timestamp,
        )

    def log_feedback_behavior(self, user_id: str, timestamp: str) -> None:
        """可选：仅在行为表写入一条 feedback 行为（不写反馈表）。"""
        if not self._enabled:
            return
        self.log_behavior(
            user_id=user_id,
            behavior_type="feedback",
            behavior_value="提交反馈",
            ip_address="",
            user_agent="",
            timestamp=timestamp,
        )
