from sqlalchemy import text
from .sqlite_gen import *

trigger = []
# 创建触发器，用于在插入数据时生成 id
trigger_sql1 = text("""
CREATE TRIGGER IF NOT EXISTS trg_generate_aud_id
AFTER INSERT ON corpus_audio
BEGIN
    UPDATE corpus_audio
    SET aud_id = 'audio_' || printf('%d', NEW.id)
    WHERE id = NEW.id;
END;
""")

trigger_sql2 = text("""
CREATE TRIGGER IF NOT EXISTS trg_generate_testcorpus_id
AFTER INSERT ON test_corpus
BEGIN
    UPDATE test_corpus
    SET corpus_id = 'testcorpus_' || printf('%d', NEW.id)
    WHERE id = NEW.id;
END;
""")

trigger_sql3 = text("""
CREATE TRIGGER IF NOT EXISTS trg_generate_rousecorpus_id
AFTER INSERT ON rouse_corpus
BEGIN
    UPDATE rouse_corpus
    SET corpus_id = 'rousecorpus_' || printf('%d', NEW.id)
    WHERE id = NEW.id;
END;
""")

trigger_sql4 = text("""
CREATE TRIGGER IF NOT EXISTS trg_generate_disturbcorpus_id
AFTER INSERT ON disturb_corpus
BEGIN
    UPDATE disturb_corpus
    SET corpus_id = 'disturbcorpus_' || printf('%d', NEW.id)
    WHERE id = NEW.id;
END;
""")

trigger_sql5 = text("""
CREATE TRIGGER IF NOT EXISTS trg_generate_backgroundnoise_id
AFTER INSERT ON background_noise
BEGIN
    UPDATE background_noise
    SET corpus_id = 'backgroundnoise_' || printf('%d', NEW.id)
    WHERE id = NEW.id;
END;
""")

trigger_sql6 = text("""
CREATE TRIGGER IF NOT EXISTS trg_generate_testproject_id
AFTER INSERT ON test_project
BEGIN
    UPDATE test_project
    SET project_id = 'project_' || printf('%d', NEW.id)
    WHERE id = NEW.id;
END;
""")

trigger_sql7 = text("""
CREATE TRIGGER IF NOT EXISTS trg_generate_plan_id
AFTER INSERT ON project_plan
BEGIN
    UPDATE project_plan
    SET plan_id = 'plan_' || printf('%d', NEW.id)
    WHERE id = NEW.id;
END;
""")

trigger_sql8 = text("""
CREATE TRIGGER IF NOT EXISTS trg_generate_result_id
AFTER INSERT ON test_result
BEGIN
    UPDATE test_result
    SET result_id = 'result_' || printf('%d', NEW.id)
    WHERE id = NEW.id;
END;
""")

trigger_sql9 = text("""
CREATE TRIGGER IF NOT EXISTS trg_generate_playconfig_id
AFTER INSERT ON play_config
BEGIN
    UPDATE play_config
    SET play_config_id = 'playconfig_' || printf('%d', NEW.id)
    WHERE id = NEW.id;
END;
""")

trigger.append(trigger_sql1)
trigger.append(trigger_sql2)
trigger.append(trigger_sql3)
trigger.append(trigger_sql4)
trigger.append(trigger_sql5)
trigger.append(trigger_sql6)
trigger.append(trigger_sql7)
trigger.append(trigger_sql8)
trigger.append(trigger_sql9)

# 创建触发器
def create_trigger_single(engine, sql):
    with engine.connect() as connection:
        connection.execute(sql)

def create_trigger(engine):
    for tt in trigger:
        create_trigger_single(engine, tt)