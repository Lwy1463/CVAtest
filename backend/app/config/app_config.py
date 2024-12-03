from pydantic_settings import BaseSettings
import os
import queue
import sys
import threading

class AppConfigSettings(BaseSettings):
    # 基础配置
    app_name: str = "CVAtest"
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    app_env: str = "dev"
    app_debug: bool = False
    # 数据库配置
    db_dsn: str = "sqlite:///cavtest.db"  # mysql+pymysql://username:password@localhost:3306/database_name
    db_echo_sql: bool = False  # 使用打印SQL日志信息
    db_pool_size: int = 10  # 连接池中的初始连接数，默认为 5
    db_max_overflow: int = 20  # 连接池中允许的最大超出连接数
    
    # 文件存储位置配置
    current_dir: str = os.path.dirname(os.path.abspath(__file__))
    abs_path: str = os.path.abspath(current_dir)
    base_dir: str = os.path.dirname(os.path.dirname(abs_path))
    audio_path: str = os.path.join(base_dir, 'audio')
    mic_path: str = os.path.join(base_dir, 'mic_audio')
    rouse_corpus_path: str = os.path.join(audio_path, 'rouse_corpus')
    synthesize_corpus_path: str = os.path.join(audio_path, 'synthesize')
    test_corpus_path: str = os.path.join(audio_path, 'test_corpus')

    # 照片存储目录
    photo_dir: str = os.path.join(base_dir, 'photo')

    # 视频存储目录
    video_dir: str = os.path.join(base_dir, 'video')

    # 视频存储目录
    excel_dir: str = os.path.join(base_dir, 'excel')

    # ASR
    asr_use_gpu: bool = sys.platform != 'darwin'

    # OPENAI
    OPENAI_API_KEY: str = "403230cf3413434fbad5c7563005b73b"
    OPENAI_API_BASE: str = "http://183.66.251.10:38000/v1"

globalAppSettings = AppConfigSettings()
if not os.path.exists(globalAppSettings.photo_dir):
    os.makedirs(globalAppSettings.photo_dir)
if not os.path.exists(globalAppSettings.video_dir):
    os.makedirs(globalAppSettings.video_dir)
if not os.path.exists(globalAppSettings.rouse_corpus_path):
    os.makedirs(globalAppSettings.rouse_corpus_path)
if not os.path.exists(globalAppSettings.synthesize_corpus_path):
    os.makedirs(globalAppSettings.synthesize_corpus_path)
if not os.path.exists(globalAppSettings.test_corpus_path):
    os.makedirs(globalAppSettings.test_corpus_path)
if not os.path.exists(globalAppSettings.mic_path):
    os.makedirs(globalAppSettings.mic_path)
if not os.path.exists(globalAppSettings.excel_dir):
    os.makedirs(globalAppSettings.excel_dir)

LLMJudge_Queue = queue.Queue()
Queue_lock = threading.Lock()
