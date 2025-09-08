@echo off
title 西冷资讯 AI协作OS - 本地开发服务器
color 0A
echo =====================================
echo 西冷资讯 AI协作OS - 本地服务启动器
echo =====================================
echo.

:: 检查main.py是否存在
if not exist "main.py" (
    echo [ERROR] 未找到main.py文件
    echo 请确保在backend目录下运行此脚本
    pause
    exit /b 1
)

:: 检查依赖是否安装
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] 检测到依赖未安装
    echo 正在自动安装依赖...
    call install_dependencies.bat
    if errorlevel 1 (
        echo [ERROR] 依赖安装失败，无法启动服务
        pause
        exit /b 1
    )
)

echo [INFO] 正在启动西冷资讯AI协作OS后端服务...
echo.
echo =====================================
echo 🚀 服务信息
echo =====================================
echo 📡 本地地址: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs  
echo 💓 健康检查: http://localhost:8000/health
echo 🔗 WebSocket: ws://localhost:8000/ws/chat/test
echo =====================================
echo.
echo 💡 提示: 按 Ctrl+C 停止服务
echo 🔧 开发模式: 支持代码热重载
echo.

:: 启动FastAPI服务（开发模式）
python main.py

:: 如果服务异常退出
echo.
echo [INFO] 服务已停止
echo 按任意键关闭窗口...
pause