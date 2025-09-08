import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 上传文件配置
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 支持的音频格式
ALLOWED_AUDIO_FORMATS = {
    "audio/wav", "audio/mpeg", "audio/mp3", 
    "audio/m4a", "audio/ogg", "audio/webm", "audio/mp4"
}

# 文件大小限制 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# 服务器配置
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8000))

# 云部署检测
IS_PRODUCTION = os.environ.get("RAILWAY_ENVIRONMENT_NAME") is not None or \
                os.environ.get("RENDER") is not None or \
                os.environ.get("HEROKU") is not None

# 日志配置
LOG_LEVEL = "INFO" if IS_PRODUCTION else "DEBUG"

# 临时文件清理时间（小时）
TEMP_FILE_CLEANUP_HOURS = 24