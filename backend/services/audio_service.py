import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import HTTPException, UploadFile
from config import UPLOAD_DIR, ALLOWED_AUDIO_FORMATS, MAX_FILE_SIZE

class AudioService:
    """音频处理服务"""
    
    def __init__(self):
        self.upload_dir = UPLOAD_DIR
        # 确保上传目录存在
        self.upload_dir.mkdir(exist_ok=True)
    
    async def save_audio_file(self, audio_file: UploadFile) -> dict:
        """
        保存上传的音频文件到临时目录
        返回文件信息
        """
        try:
            # 验证文件类型
            if audio_file.content_type and audio_file.content_type not in ALLOWED_AUDIO_FORMATS:
                raise HTTPException(
                    status_code=400, 
                    detail=f"不支持的音频格式: {audio_file.content_type}"
                )
            
            # 读取文件内容
            content = await audio_file.read()
            
            # 验证文件大小
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件太大，最大支持 {MAX_FILE_SIZE // 1024 // 1024}MB"
                )
            
            # 验证文件不为空
            if len(content) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="音频文件不能为空"
                )
            
            # 生成唯一文件名
            file_id = str(uuid.uuid4())
            file_extension = self._get_file_extension(audio_file.filename)
            filename = f"{file_id}{file_extension}"
            file_path = self.upload_dir / filename
            
            # 保存文件
            with open(file_path, "wb") as f:
                f.write(content)
            
            print(f"✅ 音频文件已保存: {filename}, 大小: {len(content)} bytes")
            
            return {
                "file_id": file_id,
                "filename": filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "content_type": audio_file.content_type or "audio/unknown",
                "duration_estimate": self._estimate_duration(len(content)),
                "status": "saved"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ 保存音频文件失败: {str(e)}")
            raise HTTPException(status_code=500, detail="文件保存失败")
    
    def _get_file_extension(self, filename: Optional[str]) -> str:
        """获取文件扩展名"""
        if not filename:
            return ".wav"  # 默认扩展名
        
        ext = Path(filename).suffix.lower()
        return ext if ext else ".wav"
    
    def _estimate_duration(self, file_size: int) -> float:
        """估算音频时长（秒）"""
        # 粗略估算：假设平均码率为128kbps
        estimated_seconds = (file_size * 8) / (128 * 1000)
        return round(estimated_seconds, 2)
    
    def cleanup_old_files(self, hours: int = 24):
        """清理超过指定小时数的临时文件"""
        import time
        current_time = time.time()
        cleaned_count = 0
        
        try:
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (hours * 3600):  # 转换为秒
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                            print(f"🗑️ 清理过期文件: {file_path.name}")
                        except Exception as e:
                            print(f"⚠️ 清理文件失败 {file_path.name}: {e}")
            
            if cleaned_count > 0:
                print(f"✅ 清理完成，删除了 {cleaned_count} 个过期文件")
                
        except Exception as e:
            print(f"⚠️ 文件清理过程出错: {e}")
    
    def get_upload_stats(self) -> dict:
        """获取上传目录统计信息"""
        try:
            files = list(self.upload_dir.iterdir())
            total_files = len([f for f in files if f.is_file()])
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            
            return {
                "total_files": total_files,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "upload_dir": str(self.upload_dir)
            }
        except Exception:
            return {
                "total_files": 0,
                "total_size_mb": 0,
                "upload_dir": str(self.upload_dir)
            }