from sqlalchemy import desc

from .base_dao import getDatabaseSession
from app.dao.models import CorpusAudio, TestCorpus, RouseCorpus, DisturbCorpus, BackgroundNoise, MultiCorpus


class CorpusQueryDao(object):
    """音频查询类dao"""

    @classmethod
    def findTestCorpusById(cls, id: str) -> TestCorpus:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(TestCorpus).filter(TestCorpus.corpus_id == id)
            result = query.first()
            if not result:
                # raise ValueError(f"TestCorpus with id {id} not found.")
                return None
        return result
    
    @classmethod
    def findRouseCorpusById(cls, id: str) -> RouseCorpus:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(RouseCorpus).filter(RouseCorpus.corpus_id == id)
            result = query.first()
            if not result:
                # raise ValueError(f"RouseCorpus with id {id} not found.")
                return None
        return result

    @classmethod
    def findDisturbCorpusById(cls, id: str) -> DisturbCorpus:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(DisturbCorpus).filter(DisturbCorpus.corpus_id == id)
            result = query.first()
            if not result:
                raise ValueError(f"DisturbCorpus with id {id} not found.")
        return result
    
    @classmethod
    def findBackgroundNoiseById(cls, id: str) -> BackgroundNoise:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(BackgroundNoise).filter(BackgroundNoise.corpus_id == id)
            result = query.first()
            if not result:
                raise ValueError(f"BackgroundNoise with id {id} not found.")
        return result
    
    @classmethod
    def findAudioById(cls, id: str) -> CorpusAudio:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(CorpusAudio).filter(CorpusAudio.aud_id == id)
            result = query.first()
            if not result:
                # raise ValueError(f"CorpusAudio with id {id} not found.")
                return None
        return result

    @classmethod
    def showAllTestCorpus(cls, filter_data: dict = None) -> list[TestCorpus]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(TestCorpus)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(TestCorpus, key):
                        column_attr = getattr(TestCorpus, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
            
        return results
    
    @classmethod
    def showAllRouseCorpus(cls, filter_data: dict = None) -> list[RouseCorpus]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(RouseCorpus)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(RouseCorpus, key):
                        column_attr = getattr(RouseCorpus, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
            
        return results
    
    @classmethod
    def showAllDisturbCorpus(cls, filter_data: dict = None) -> list[DisturbCorpus]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(DisturbCorpus)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(DisturbCorpus, key):
                        column_attr = getattr(DisturbCorpus, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
            
        return results
    
    @classmethod
    def showAllBackgroundNoise(cls, filter_data: dict = None) -> list[BackgroundNoise]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(BackgroundNoise)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(BackgroundNoise, key):
                        column_attr = getattr(BackgroundNoise, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
            
        return results
    
    @classmethod
    def findMultiCorpusById(cls, id: str) -> MultiCorpus:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(MultiCorpus).filter(MultiCorpus.corpus_id == id)
            result = query.all()
        return result

    @classmethod
    def showAllMultiCorpus(cls, filter_data: dict = None) -> list[MultiCorpus]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(MultiCorpus)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(MultiCorpus, key):
                        column_attr = getattr(MultiCorpus, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results

class CorpusOperateDao(object):
    """操作音频相关dao"""

    @classmethod
    def saveTestCorpus(cls, corpus: TestCorpus) -> TestCorpus:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(corpus)
            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def saveTestCorpusList(cls, corpus: list[TestCorpus]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(corpus)
        return
    
    @classmethod
    def deleteTestCorpus(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            corpus = session.query(TestCorpus).filter(TestCorpus.corpus_id == id).first()
            if not corpus:
                raise ValueError(f"TestCorpus with id {id} not found.")
            
            session.delete(corpus)
            session.commit()

    @classmethod
    def updateTestCorpus(cls, id: str, updated_data: dict) -> TestCorpus:
        """更新单条"""
        with getDatabaseSession(False) as session:
            corpus = session.query(TestCorpus).filter(TestCorpus.corpus_id == id).first()
            if not corpus:
                raise ValueError(f"TestCorpus with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(corpus, key):
                    setattr(corpus, key, value)

            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def saveRouseCorpus(cls, corpus: RouseCorpus) -> RouseCorpus:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(corpus)
            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def saveRouseCorpusList(cls, corpus: list[RouseCorpus]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(corpus)
        return
    
    @classmethod
    def deleteRouseCorpus(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            corpus = session.query(RouseCorpus).filter(RouseCorpus.corpus_id == id).first()
            if not corpus:
                raise ValueError(f"RouseCorpus with id {id} not found.")
            
            session.delete(corpus)
            session.commit()

    @classmethod
    def updateRouseCorpus(cls, id: str, updated_data: dict) -> RouseCorpus:
        """更新单条"""
        with getDatabaseSession(False) as session:
            corpus = session.query(RouseCorpus).filter(RouseCorpus.corpus_id == id).first()
            if not corpus:
                raise ValueError(f"RouseCorpus with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(corpus, key):
                    setattr(corpus, key, value)

            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def saveDisturbCorpus(cls, corpus: DisturbCorpus) -> DisturbCorpus:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(corpus)
            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def saveDisturbCorpusList(cls, corpus: list[DisturbCorpus]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(corpus)
        return
    
    @classmethod
    def deleteDisturbCorpus(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            corpus = session.query(DisturbCorpus).filter(DisturbCorpus.corpus_id == id).first()
            if not corpus:
                raise ValueError(f"DisturbCorpus with id {id} not found.")
            
            session.delete(corpus)
            session.commit()

    @classmethod
    def updateDisturbCorpus(cls, id: str, updated_data: dict) -> DisturbCorpus:
        """更新单条"""
        with getDatabaseSession(False) as session:
            corpus = session.query(DisturbCorpus).filter(DisturbCorpus.corpus_id == id).first()
            if not corpus:
                raise ValueError(f"DisturbCorpus with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(corpus, key):
                    setattr(corpus, key, value)

            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def saveBackgroundNoise(cls, corpus: BackgroundNoise) -> BackgroundNoise:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(corpus)
            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def saveBackgroundNoiseList(cls, corpus: list[BackgroundNoise]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(corpus)
        return
    
    @classmethod
    def deleteBackgroundNoise(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            corpus = session.query(BackgroundNoise).filter(BackgroundNoise.corpus_id == id).first()
            if not corpus:
                raise ValueError(f"BackgroundNoise with id {id} not found.")
            
            session.delete(corpus)
            session.commit()

    @classmethod
    def updateBackgroundNoise(cls, id: str, updated_data: dict) -> BackgroundNoise:
        """更新单条"""
        with getDatabaseSession(False) as session:
            corpus = session.query(BackgroundNoise).filter(BackgroundNoise.corpus_id == id).first()
            if not corpus:
                raise ValueError(f"BackgroundNoise with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(corpus, key):
                    setattr(corpus, key, value)

            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def saveAudio(cls, audio: CorpusAudio) -> CorpusAudio:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(audio)
            session.commit()
            session.refresh(audio)
        return audio
    
    @classmethod
    def saveAudioList(cls, audio: list[CorpusAudio]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(audio)
        return
    
    @classmethod
    def deleteAudio(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            audio = session.query(CorpusAudio).filter(CorpusAudio.aud_id == id).first()
            if not audio:
                raise ValueError(f"Audio with id {id} not found.")
            
            session.delete(audio)
            session.commit()

    @classmethod
    def updateAudio(cls, id: str, updated_data: dict) -> CorpusAudio:
        """更新单条"""
        with getDatabaseSession(False) as session:
            audio = session.query(CorpusAudio).filter(CorpusAudio.aud_id == id).first()
            if not audio:
                raise ValueError(f"Audio with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(audio, key):
                    setattr(audio, key, value)

            session.commit()
            session.refresh(audio)
        return audio

    @classmethod
    def saveMultiCorpus(cls, corpus: MultiCorpus) -> MultiCorpus:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(corpus)
            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def saveMultiCorpusList(cls, corpus: list[MultiCorpus]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(corpus)
        return
    
    @classmethod
    def deleteMultiCorpus(cls, id: str) -> None:
        """删除所有corpus_id对应的数据"""
        with getDatabaseSession(False) as session:
            corpus = session.query(MultiCorpus).filter(MultiCorpus.corpus_id == id)
            a_del = corpus.all()
            for i in a_del:
                session.delete(i)
                session.commit()

    @classmethod
    def updateMultiCorpus(cls, id: str, updated_data: dict) -> MultiCorpus:
        """更新单条"""
        with getDatabaseSession(False) as session:
            corpus = session.query(MultiCorpus).filter(MultiCorpus.corpus_id == id).first()
            if not corpus:
                raise ValueError(f"MultiCorpus with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(corpus, key):
                    setattr(corpus, key, value)

            session.commit()
            session.refresh(corpus)
        return corpus
