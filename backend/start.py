"""
西冷资讯 AI协作OS - 云部署启动脚本
"""
import uvicorn
import os
from main import app

# 云平台环境检测
def detect_platform():
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        return "Railway"
    elif os.environ.get("RENDER"):
        return "Render" 
    elif os.environ.get("HEROKU"):
        return "Heroku"
    else:
        return "Local"

if __name__ == "__main__":
    platform = detect_platform()
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 西冷资讯 AI协作OS 启动中...")
    print(f"🌐 运行平台: {platform}")
    print(f"📡 端口: {port}")
    print("✅ 所有服务已就绪")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=port,
        reload=False,  # 生产环境关闭热重载
        log_level="info"
    )