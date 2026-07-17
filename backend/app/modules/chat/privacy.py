"""AI 问答隐私工具：发送外部模型和日志前做基础敏感信息脱敏。"""
import re


def sanitize_text(text: str | None) -> str:
    value = text or ""
    value = re.sub(r"1\d{10}", "[手机号]", value)
    value = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "[邮箱]", value)
    return re.sub(r"\d{4}-\d{1,2}-\d{1,2}", "[日期]", value)
