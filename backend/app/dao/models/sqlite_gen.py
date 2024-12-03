from sqlalchemy import Column, Index, String, TIMESTAMP, text, ForeignKey, Integer, DateTime, Boolean, Float
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import declarative_base, relationship
from app.utils.utils import get_beijing_time

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        Index('idx_nick_name', 'nick_name'),
        Index('idx_phone', 'phone'),
        {'comment': '用户表'}
    )

    id = Column(BIGINT, primary_key=True, comment='主键')
    union_id = Column(String(64), nullable=False, server_default=text("''"), comment='微信开放平台下的用户唯一标识')
    open_id = Column(String(64), nullable=False, server_default=text("''"), comment='微信openid')
    nick_name = Column(String(32), nullable=False, server_default=text("''"), comment='昵称')
    password = Column(String(64), nullable=False, server_default=text("''"), comment='密码')
    avatar = Column(String(255), nullable=False, server_default=text("''"), comment='头像')
    phone = Column(String(11), nullable=False, server_default=text("''"), comment='手机号')
    email = Column(String(50), nullable=False, server_default=text("''"), comment='电子邮箱')
    last_login = Column(String(20), nullable=False, server_default=text("''"), comment='上次登录时间')
    delete_at = Column(String(20), nullable=False, server_default=text("''"), comment='删除时间')
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')

class CorpusAudio(Base):
    __tablename__ = "corpus_audio"

    id = Column(Integer, primary_key=True, autoincrement=True)  # 自增字段
    aud_id = Column(String(64), unique=True, index=True)
    corpus_id = Column(String(64), nullable=True)
    aud_url = Column(String(255), nullable=True, comment='语料路径,存的完整路径')
    pinyin = Column(String(64), nullable=True)
    audio_duration = Column(String(32), nullable=True)

class TestCorpus(Base):
    __tablename__ = "test_corpus"
    __table_args__ = (
        Index('corpus_label', 'label'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    corpus_id = Column(String(64), unique=True, index=True)
    aud_id = Column(String(64), nullable=True, comment='语料id')
    text = Column(String(64), nullable=True, comment='语料文本')
    pinyin = Column(String(64), nullable=True, comment='语料拼音')
    test_scenario = Column(String(64), nullable=True, comment='测试场景')
    evaluation_metric = Column(String(32), nullable=True, comment='评估指标')
    audio_url = Column(String(64), nullable=True, comment='语料路径,其实存的只是名字')
    audio_duration = Column(String(32), nullable=True, comment='语料时长')
    speaker = Column(String(64), nullable=True, comment='声音')
    language = Column(String(64), nullable=True, comment='语言')
    label = Column(String(64), nullable=True, comment='其他标签')
    operation = Column(String(64), nullable=True, comment='操作')
    car_function = Column(String(64), nullable=True, comment='测试车机功能')
    expect_result = Column(String(255), nullable=True, comment='预期结果')
    test_type = Column(String(64), nullable=True, comment='测试类型')
    audio_path = Column(String(256), nullable=True, comment='语料路径')
    is_tts = Column(Boolean, default=False, comment='是否tts生成')

class MultiCorpus(Base):
    __tablename__ = "multi_corpus"
    __table_args__ = (
        Index('find_corpus_id', 'corpus_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    corpus_id = Column(String(64), nullable=True, comment='多伦语料id')
    corpus_name = Column(String(64), nullable=True, comment='多伦语料名字')
    testcorpus_id = Column(String(64), nullable=True, comment='测试语料id')
    is_delete = Column(Boolean, nullable=True, comment='假删除，标记位')

class RouseCorpus(Base):
    __tablename__ = "rouse_corpus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corpus_id = Column(String(64), unique=True, index=True)
    aud_id = Column(String(64), nullable=True, comment='语料id')
    text = Column(String(64), nullable=True, comment='语料文本')
    pinyin = Column(String(64), nullable=True, comment='语料拼音')
    test_scenario = Column(String(64), nullable=True, comment='测试场景')
    test_object = Column(String(32), nullable=True, comment='测试对象')
    audio_url = Column(String(64), nullable=True, comment='语料路径')
    audio_duration = Column(String(32), nullable=True, comment='语料时长')
    speaker = Column(String(64), nullable=True, comment='声音')
    language = Column(String(64), nullable=True, comment='语言')
    label = Column(String(64), nullable=True, comment='其他标签')
    operation = Column(String(64), nullable=True, comment='操作')
    audio_path = Column(String(256), nullable=True, comment='语料路径')
    is_tts = Column(Boolean, default=False, comment='是否tts生成')

class DisturbCorpus(Base):
    __tablename__ = "disturb_corpus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corpus_id = Column(String(64), unique=True, index=True)
    aud_id = Column(String(64), nullable=True, comment='语料id')
    text = Column(String(64), nullable=True, comment='语料文本')
    pinyin = Column(String(64), nullable=True, comment='语料拼音')
    audio_url = Column(String(64), nullable=True, comment='语料路径')
    audio_duration = Column(String(32), nullable=True, comment='语料时长')
    speaker = Column(String(64), nullable=True, comment='声音')
    language = Column(String(64), nullable=True, comment='语言')
    label = Column(String(64), nullable=True, comment='其他标签')
    operation = Column(String(64), nullable=True, comment='操作')
    audio_path = Column(String(256), nullable=True, comment='语料路径')
    is_tts = Column(Boolean, default=False, comment='是否tts生成')

class BackgroundNoise(Base):
    __tablename__ = "background_noise"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corpus_id = Column(String(64), unique=True, index=True)
    aud_id = Column(String(64), nullable=True, comment='语料id')
    text = Column(String(64), nullable=True)
    noise_environ = Column(String(64), nullable=True, comment='噪声环境')
    pinyin = Column(String(64), nullable=True, comment='语料拼音')
    audio_url = Column(String(64), nullable=True, comment='语料路径')
    audio_duration = Column(String(32), nullable=True, comment='语料时长')
    label = Column(String(64), nullable=True, comment='其他标签')
    operation = Column(String(64), nullable=True, comment='操作')
    audio_path = Column(String(256), nullable=True, comment='语料路径')


class TestProject(Base):
    __tablename__ = "test_project"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(64), unique=True, index=True)
    project_name = Column(String(64), nullable=True, comment='项目名称')
    project_code = Column(String(64), nullable=True, comment='项目编号')
    description = Column(String(255), nullable=True, comment='项目描述')
    test_object = Column(String(64), nullable=True, comment='测试对象')
    project_status = Column(String(64), nullable=True, comment='项目状态')
    project_process = Column(String(32), nullable=True, comment='项目进度')

class ProjectPlan(Base):
    __tablename__ = "project_plan"
    __table_args__ = (
        Index('find_play_config_id1', 'play_config_id'),
        Index('find_project_id1', 'project_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(String(64), unique=True, index=True)
    plan_name = Column(String(64), nullable=True, comment='方案名字')
    project_id = Column(String(64), nullable=True, comment='方案所属项目id')
    play_config_id = Column(String(64), nullable=True, comment='对应播放配置id')
    plan_status = Column(String(64), nullable=True, comment='项目状态')
    type = Column(String(64), nullable=True, comment='播放配置类型 唤醒 rouse 非唤醒 interaction')
    # 唤醒
    wakeup_time = Column(Float, nullable=True, default=None, comment='唤醒时间')
    wakeup_success_rate = Column(Float, nullable=True, default=None, comment='唤醒成功率')
    # 误唤醒
    false_wakeup_times = Column(Float, nullable=True, default=None, comment='误唤醒次数')
    # 单次交互 '交互成功率' 在多轮对话中复用
    interaction_success_rate = Column(Float, nullable=True, default=None, comment='交互成功率')
    word_recognition_rate = Column(Float, nullable=True, default=None, comment='字识别率') # 如果为 false 则不需要ocr识别
    response_time = Column(Float, nullable=True, default=None, comment='响应时间')

class TestResult(Base):
    __tablename__ = "test_result"
    __table_args__ = (
        Index('find_project_id', 'project_id'),
        Index('find_turn_id', 'turn_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(String(64), unique=True, index=True)
    time = Column(DateTime, default=get_beijing_time)
    project_id = Column(String(64), nullable=True, comment='结果对应的项目id')
    plan_id = Column(String(64), nullable=True, comment='该条语料对应的方案id')
    corpus_id = Column(String(64), nullable=True, comment='语料id')
    turn_id = Column(Integer, nullable=False, default=1,comment='第几轮')
    test_scenario = Column(String(64), nullable=True, comment='测试场景')
    text = Column(String(64), nullable=True, comment='语料文本')
    result = Column(String(64), nullable=True, comment='测试结果')
    image = Column(String(64), nullable=True, comment='备用结果判断')
    score = Column(Integer, nullable=False, default=-1, comment='测试结果通过模型出来的分数')
    asr_result = Column(String(255), nullable=True, comment='语音转文字出来的结果')
    mic_audio_url = Column(String(255), nullable=True, comment='车机响应录音url')
    ocr_pic_url = Column(String(64), nullable=True, comment='ocr图片路径')
    ocr_result = Column(String(255), nullable=True, comment='ocr识别文字内容')
    ocr_accuracy_rate = Column(Float, nullable=True, default=None, comment='ocr识别车机文字和text的准确率')
    relative_interval = Column(Integer, nullable=False, default=0, comment='相对间隔时间，单位秒')
    response_time = Column(Float, nullable=True, default=None, comment='测试响应时间, 单位 秒')
    expect_result = Column(String(255), nullable=True, comment='预期结果')

class MultiResult(Base):
    __tablename__ = "multis_result"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(64), nullable=True, comment='结果对应的项目id')
    plan_id = Column(String(64), nullable=True, comment='该条语料对应的方案id')
    multicorpus_id = Column(String(64), nullable=True, comment='多伦语料id')
    turn_id = Column(Integer, nullable=False, default=1,comment='第几轮')
    result = Column(String(64), nullable=True, comment='测试结果')
    reason = Column(String(64), nullable=True, comment='评估理由')
    success_rate = Column(String(64), nullable=True, comment='执行成功率')
    time = Column(DateTime, default=get_beijing_time)

class TCorpusTree(Base):
    __tablename__ = "tcorpus_tree"
    __table_args__ = (
        Index('find_corpus_id1', 'corpus_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(64), nullable=True, comment='方案id')
    corpus_id = Column(String(64), nullable=True, comment='语料id')
    score = Column(Integer, nullable=False, default=-1, comment='测试结果')

class RCorpusTree(Base):
    __tablename__ = "rcorpus_tree"
    __table_args__ = (
        Index('find_corpus_id2', 'corpus_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(64), nullable=True, comment='方案id')
    corpus_id = Column(String(64), nullable=True, comment='语料id')

class DCorpusTree(Base):
    __tablename__ = "dcorpus_tree"
    __table_args__ = (
        Index('find_corpus_id3', 'corpus_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(64), nullable=True, comment='方案id')
    corpus_id = Column(String(64), nullable=True, comment='语料id')

class BNoiseTree(Base):
    __tablename__ = "bnoise_tree"
    __table_args__ = (
        Index('find_corpus_id4', 'corpus_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(64), nullable=True, comment='方案id')
    corpus_id = Column(String(64), nullable=True, comment='语料id')

class PlayConfig(Base):
    __tablename__ = "play_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    play_config_id = Column(String(64), unique=True, index=True)
    config_name = Column(String(64), nullable=True, comment='播放配置名')
    description = Column(String(64), nullable=True, comment='配置描述')
    type = Column(String(255), nullable=True, comment='播放配置类型 唤醒 rouse 非唤醒 interaction')

# 开始
class StartConfig(Base):
    __tablename__ = "start_config"
    __table_args__ = (
        Index('find_play_config_id2', 'play_config_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    play_config_id = Column(String(64), nullable=True, comment='对应播放配置id')
    circle = Column(String(32), nullable=True, comment='循环次数')
    seat = Column(Integer, nullable=False, comment='该配置所在配置列表中的位置')
    # 唤醒
    wakeup_time = Column(Boolean, default=False, comment='唤醒时间')
    wakeup_success_rate = Column(Boolean, default=False, comment='唤醒成功率')
    # 误唤醒
    false_wakeup_times = Column(Boolean, default=False, comment='误唤醒次数')
    # 单次交互 '交互成功率' 在多轮对话中复用
    interaction_success_rate = Column(Boolean, default=False, comment='交互成功率')
    word_recognition_rate = Column(Boolean, default=False, comment='字识别率') # 如果为 false 则不需要ocr识别
    response_time = Column(Boolean, default=False, comment='响应时间')

# 嵌入唤醒
class RouseConfig(Base):
    __tablename__ = "rouse_config"
    __table_args__ = (
        Index('find_play_config_id3', 'play_config_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    play_config_id = Column(String(64), nullable=True, comment='对应播放配置id')
    wakeUpWaitDifferent = Column(Integer, nullable=False, default=0, comment='不同语料间唤醒等待时间 单位ms')
    wakeUpWaitRepeated = Column(Integer, nullable=False, default=0, comment='语料重复时唤醒等待时间 单位ms')
    frequencyDifferent = Column(String(64), nullable=True, comment='不同语料间唤醒频率 first 仅一次 every 每次 interval 间隔frequency_interval次')
    frequencyRepeated = Column(String(64), nullable=True, comment='语料重复时唤醒频率 none 不嵌入 every 每次')
    frequencyIntervalDifferent = Column(Integer, nullable=False, default=0, comment='不同语料间间隔次数，当上面为 interval 的时候起作用')
    channel = Column(String(64), nullable=True, comment='播放通道配置')
    gain = Column(Integer, nullable=False, default=0, comment='增益配置')
    seat = Column(Integer, nullable=False, comment='该配置所在配置列表中的位置')

# 播放干扰语料
class DisturbConfig(Base):
    __tablename__ = "disturb_config"
    __table_args__ = (
        Index('find_play_config_id4', 'play_config_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    play_config_id = Column(String(64), nullable=True, comment='对应播放配置id')
    channel = Column(String(64), nullable=True, comment='播放通道配置')
    gain = Column(Integer, nullable=False, default=0, comment='增益配置')
    seat = Column(Integer, nullable=False, comment='该配置所在配置列表中的位置')

# 播放背景噪声
class NoiseConfig(Base):
    __tablename__ = "noise_config"
    __table_args__ = (
        Index('find_play_config_id5', 'play_config_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    play_config_id = Column(String(64), nullable=True, comment='对应播放配置id')
    channel = Column(String(64), nullable=True, comment='播放通道配置')
    gain = Column(Integer, nullable=False, default=0, comment='增益配置')
    seat = Column(Integer, nullable=False, comment='该配置所在配置列表中的位置')

# 播放测试语料
class TestCorpusConfig(Base):
    __tablename__ = "testcorpus_config"
    __table_args__ = (
        Index('find_play_config_id6', 'play_config_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    play_config_id = Column(String(64), nullable=True, comment='对应播放配置id')
    repeat = Column(Integer, nullable=False, default=1, comment='重复次数')
    wait_time = Column(Integer, nullable=False, default=1, comment='无声音等待时间s')
    timout = Column(Integer, nullable=False, default=10, comment='最长录制时间s')
    channel = Column(String(64), nullable=True, comment='播放通道配置')
    gain = Column(Integer, nullable=False, default=0, comment='增益配置')
    seat = Column(Integer, nullable=False, comment='该配置所在配置列表中的位置')

# 唤醒场景 播放唤醒语料
class RouseCorpusConfig(Base):
    __tablename__ = "rousecorpus_config"
    __table_args__ = (
        Index('find_play_config_id7', 'play_config_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    play_config_id = Column(String(64), nullable=True, comment='对应播放配置id')
    repeat = Column(Integer, nullable=False, default=1, comment='重复次数')
    channel = Column(String(64), nullable=True, comment='播放通道配置')
    gain = Column(Integer, nullable=False, default=0, comment='增益配置')
    seat = Column(Integer, nullable=False, comment='该配置所在配置列表中的位置')

# 等待
class WaitConfig(Base):
    __tablename__ = "wait_config"
    __table_args__ = (
        Index('find_play_config_id8', 'play_config_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    play_config_id = Column(String(64), nullable=True, comment='对应播放配置id')
    duration = Column(Integer, nullable=False, default=0, comment='等待时长')
    seat = Column(Integer, nullable=False, comment='该配置所在配置列表中的位置')

class ReviewResult(Base):
    __tablename__ = "review_result"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(64), nullable=True, comment='结果对应的项目id')
    turn_id = Column(Integer, nullable=False, default=1, comment='第几轮')
    video_path = Column(String(64), nullable=True, comment='视频名字')

