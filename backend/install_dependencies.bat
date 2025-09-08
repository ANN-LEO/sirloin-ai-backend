@echo off
echo =====================================
echo 西冷资讯 AI协作OS - 后端依赖安装器
echo =====================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未检测到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python环境检查通过
echo.

echo [INFO] 正在安装Python依赖包...
echo.

:: 升级pip
echo [INFO] 升级pip...
python -m pip install --upgrade pip

:: 安装依赖
echo [INFO] 安装项目依赖...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] 依赖安装失败，请检查网络连接
    echo 建议使用国内镜像源: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    pause
    exit /b 1
)

echo.
echo =====================================
echo [SUCCESS] 所有依赖安装完成！
echo =====================================
echo.
echo 下一步操作：
echo 1. 运行 start_local.bat 启动本地服务
echo 2. 或部署到云平台进行公网访问
echo.
pause