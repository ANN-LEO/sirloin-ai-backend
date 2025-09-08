from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
import uvicorn
import json
import uuid
import os
from pathlib import Path
from services.audio_service import AudioService
from config import HOST, PORT

# 初始化FastAPI应用
app = FastAPI(
    title="西冷资讯 AI协作OS - 后端仓库",
    description="MVP后端服务，提供文本和语音交互能力",
    version="1.0.0"
)

# CORS中间件配置 - 云部署版本
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
audio_service = AudioService()

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, chat_id: str):
        await websocket.accept()
        self.active_connections[chat_id] = websocket
        print(f"Chat {chat_id} connected")
    
    def disconnect(self, chat_id: str):
        if chat_id in self.active_connections:
            del self.active_connections[chat_id]
            print(f"Chat {chat_id} disconnected")

manager = ConnectionManager()

# 数据模型
class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None
    chat_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    timestamp: str
    status: str

# ================================
# 核心API接口
# ================================

@app.get("/")
async def warehouse_heartbeat():
    """仓库心跳信号 - 所有Agent识别的基础接口"""
    return {"status": "Warehouse is online"}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "websocket": "online",
            "chat": "online",
            "transcribe": "online",
            "file_storage": "online"
        },
        "version": "1.0.0"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """文本聊天接口"""
    try:
        user_message = message.message.strip()
        
        if not user_message:
            raise HTTPException(status_code=400, detail="消息内容不能为空")
        
        # 智能回复逻辑
        reply = await _generate_ai_reply(user_message)
        
        print(f"收到聊天消息: {user_message[:50]}...")
        print(f"生成回复: {reply[:50]}...")
        
        return ChatResponse(
            reply=reply,
            timestamp=datetime.now().isoformat(),
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"聊天处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail="聊天服务暂时不可用")

@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """语音文件上传和处理接口"""
    try:
        if not audio_file:
            raise HTTPException(status_code=400, detail="未检测到音频文件")
        
        # 保存音频文件
        file_info = await audio_service.save_audio_file(audio_file)
        
        # 模拟转录结果
        mock_transcription = await _generate_mock_transcription(file_info)
        
        return {
            "transcription": mock_transcription,
            "file_info": file_info,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"音频转录失败: {str(e)}")
        raise HTTPException(status_code=500, detail="音频处理服务暂时不可用")

@app.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    """WebSocket实时聊天端点"""
    await manager.connect(websocket, chat_id)
    try:
        while True:
            # 接收消息（文本或二进制）
            data = await websocket.receive()
            
            if "text" in data:
                # 文本消息处理
                message = json.loads(data["text"])
                
                # 生成AI回复
                ai_reply = await _generate_ai_reply(message.get("content", ""))
                
                response = {
                    "type": "ai_response",
                    "content": ai_reply,
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed"
                }
                
                await websocket.send_text(json.dumps(response, ensure_ascii=False))
            
            elif "bytes" in data:
                # 音频数据处理
                audio_data = data["bytes"]
                print(f"收到音频数据，大小: {len(audio_data)} bytes")
                
                # 模拟语音转文字处理
                mock_transcription = "这是模拟的语音转文字结果：" + _generate_mock_voice_content(len(audio_data))
                
                response = {
                    "type": "transcription",
                    "content": mock_transcription,
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send_text(json.dumps(response, ensure_ascii=False))
    
    except WebSocketDisconnect:
        manager.disconnect(chat_id)

# ================================
# 辅助函数
# ================================

async def _generate_ai_reply(user_message: str) -> str:
    """生成智能AI回复"""
    message_lower = user_message.lower()
    
    if any(keyword in message_lower for keyword in ["资讯", "新闻", "最新", "技术"]):
        return """🔍 找到了3条增材制造最新资讯：

📈 **技术突破**：新型陶瓷3D打印材料发布，耐高温性能提升60%
🏭 **产业动态**：西门子宣布在华建设金属3D打印研发中心  
💰 **投资热点**：某3D打印初创公司完成5000万A轮融资

点击任意链接获取详细分析，或告诉我"生成报告"为您制作深度分析稿件。"""

    elif any(keyword in message_lower for keyword in ["写", "生成", "文章", "稿件", "报告"]):
        return """✍️ 正在为您生成专业内容稿件...

📋 **建议结构**：
• 标题：抓住核心技术亮点
• 导语：30秒快速吸引读者注意力  
• 主体：数据支撑+案例分析+行业对比
• 结语：趋势预判和投资建议

🎯 **预览功能**：稿件生成后将自动弹出预览窗口，支持实时编辑和格式调整。

请提供具体主题或选择上述资讯，我将为您量身定制高质量内容。"""

    elif any(keyword in message_lower for keyword in ["预览", "编辑", "发布"]):
        return """🖥️ 启动预览IDE模式...

将为您打开：
• 📝 所见即所得的编辑界面
• 🎨 多平台适配预览（微信公众号/小红书/知乎）
• 📊 内容质量评分和SEO优化建议
• 🚀 一键发布到各大平台

点击下方链接进入预览模式：
🔗 [打开预览IDE] (模拟链接，实际会触发弹窗)"""

    elif any(keyword in message_lower for keyword in ["帮助", "功能", "怎么用", "介绍"]):
        return """👋 欢迎使用西冷资讯AI协作OS！

🌟 **核心能力**：
🔍 **智能资讯搜集**：实时抓取行业最新动态
✍️ **专业内容创作**：生成高质量媒体稿件  
🎙️ **语音交互**：按住说话，解放双手操作
📱 **多平台适配**：一稿多投，自动格式优化
🖥️ **实时预览IDE**：所见即所得编辑体验

💡 **试试这些指令**：
• "找今天3D打印的最新突破"
• "写一篇金属打印的深度分析"  
• "语音输入功能测试"

开始您的AI协作之旅吧！"""
    
    else:
        return f"""💬 收到您的消息："{user_message}"

🤖 我是西冷资讯AI协作OS，专注于增材制造/3D打印领域的智能内容协作。

🎯 **即刻体验**：
• 语音交互：长按录音键说话
• 资讯搜索：告诉我您关注的技术方向
• 内容创作：让我为您写专业分析稿

有什么我可以帮助您的吗？让我们开始高效的人机协作！"""

async def _generate_mock_transcription(file_info: dict) -> str:
    """生成模拟的语音转录结果"""
    file_size_kb = file_info["file_size"] // 1024
    
    if file_size_kb < 10:
        return "用户说：帮我找一下最新的金属3D打印技术突破。"
    elif file_size_kb < 50:
        return "用户说：我需要写一篇关于增材制造行业发展现状的深度分析文章，请帮我收集相关的市场数据、技术趋势和典型应用案例。"
    else:
        return "用户说：请为我生成一份详细的增材制造行业报告，包括全球市场规模、主要技术路线对比、重点厂商分析、应用领域拓展情况，以及未来三年的发展趋势预测。这份报告将用于我们公司的战略投资决策。"

def _generate_mock_voice_content(audio_size: int) -> str:
    """根据音频大小生成对应的语音内容"""
    if audio_size < 10000:  # 小于10KB
        return "找最新的3D打印资讯"
    elif audio_size < 50000:  # 小于50KB
        return "帮我写一篇关于航空航天3D打印应用的技术分析文章"
    else:
        return "我需要一份完整的增材制造行业调研报告，包括技术发展、市场现状和投资机会分析"

# ================================
# 服务启动
# ================================

if __name__ == "__main__":
    print("🚀 西冷资讯AI协作OS后端仓库启动中...")
    print(f"📡 服务地址: http://{HOST}:{PORT}")
    print("📁 文件上传目录已就绪")
    print("🔗 WebSocket连接就绪")
    print("✅ 仓库已上线，等待Agent连接...")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,  # 生产环境关闭热重载
        log_level="info"
    )