#!/usr/bin/env python3
"""蜜漾美妆 - 一键启动脚本"""
import uvicorn
from backend.app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    print("""
    ╔══════════════════════════════════╗
    ║     🌸 智颜 v1.0           ║
    ║     AI 智能美妆护肤助手          ║
    ╚══════════════════════════════════╝
    """)
    print(f"🔗 API 文档:    http://localhost:{settings.PORT}/docs")
    print(f"💡 前端服务:    http://localhost:6688 (Vue Dev Server)")
    print()

    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
