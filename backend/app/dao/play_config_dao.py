from sqlalchemy import desc

from .base_dao import getDatabaseSession
from app.dao.models import PlayConfig, StartConfig, RouseConfig, DisturbConfig, NoiseConfig, TestCorpusConfig, WaitConfig, RouseCorpusConfig


class PlayConfigQueryDao(object):
    """播放配置查询类dao"""

    @classmethod
    def findPlayConfigById(cls, id: str) -> PlayConfig:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(PlayConfig).filter(PlayConfig.play_config_id == id)
            result = query.first()
            if not result:
                return None
        return result

    @classmethod
    def showAllPlayConfig(cls, filter_data: dict = None) -> list[PlayConfig]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(PlayConfig)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(PlayConfig, key):
                        column_attr = getattr(PlayConfig, key)
                        if key != "type" and isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results

    @classmethod
    def findStartConfigById(cls, id: str) -> StartConfig:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(StartConfig).filter(StartConfig.play_config_id == id)
            result = query.first()
            if not result:
                raise ValueError(f"StartConfig with id {id} not found.")
        return result

    @classmethod
    def showAllStartConfig(cls, filter_data: dict = None) -> list[StartConfig]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(StartConfig)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(StartConfig, key):
                        column_attr = getattr(StartConfig, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results
    
    @classmethod
    def findRouseConfigById(cls, id: str) -> RouseConfig:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(RouseConfig).filter(RouseConfig.play_config_id == id)
            result = query.first()
            if not result:
                raise ValueError(f"RouseConfig with id {id} not found.")
        return result

    @classmethod
    def showAllRouseConfig(cls, filter_data: dict = None) -> list[RouseConfig]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(RouseConfig)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(RouseConfig, key):
                        column_attr = getattr(RouseConfig, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results
    
    @classmethod
    def findDisturbConfigById(cls, id: str) -> DisturbConfig:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(DisturbConfig).filter(DisturbConfig.play_config_id == id)
            result = query.first()
            if not result:
                raise ValueError(f"DisturbConfig with id {id} not found.")
        return result

    @classmethod
    def showAllDisturbConfig(cls, filter_data: dict = None) -> list[DisturbConfig]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(DisturbConfig)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(DisturbConfig, key):
                        column_attr = getattr(DisturbConfig, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results
    
    @classmethod
    def findNoiseConfigById(cls, id: str) -> NoiseConfig:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(NoiseConfig).filter(NoiseConfig.play_config_id == id)
            result = query.first()
            if not result:
                raise ValueError(f"NoiseConfig with id {id} not found.")
        return result

    @classmethod
    def showAllNoiseConfig(cls, filter_data: dict = None) -> list[NoiseConfig]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(NoiseConfig)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(NoiseConfig, key):
                        column_attr = getattr(NoiseConfig, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results
    
    @classmethod
    def findTestCorpusConfigById(cls, id: str) -> TestCorpusConfig:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(TestCorpusConfig).filter(TestCorpusConfig.play_config_id == id)
            result = query.first()
            if not result:
                raise ValueError(f"TestCorpusConfig with id {id} not found.")
        return result

    @classmethod
    def showAllTestCorpusConfig(cls, filter_data: dict = None) -> list[TestCorpusConfig]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(TestCorpusConfig)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(TestCorpusConfig, key):
                        column_attr = getattr(TestCorpusConfig, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results
    
    @classmethod
    def showAllRouseCorpusConfig(cls, filter_data: dict = None) -> list[RouseCorpusConfig]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(RouseCorpusConfig)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(RouseCorpusConfig, key):
                        column_attr = getattr(RouseCorpusConfig, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results
    
    @classmethod
    def findWaitConfigById(cls, id: str) -> WaitConfig:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(WaitConfig).filter(WaitConfig.play_config_id == id)
            result = query.first()
            if not result:
                raise ValueError(f"WaitConfig with id {id} not found.")
        return result

    @classmethod
    def showAllWaitConfig(cls, filter_data: dict = None) -> list[WaitConfig]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(WaitConfig)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(WaitConfig, key):
                        column_attr = getattr(WaitConfig, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results


class PlayConfigOperateDao(object):
    """操作播放配置相关dao"""

    @classmethod
    def savePlayConfig(cls, config: PlayConfig) -> PlayConfig:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(config)
            session.commit()
            session.refresh(config)
        return config

    @classmethod
    def savePlayConfigList(cls, config: list[PlayConfig]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(config)
        return
    
    @classmethod
    def deletePlayConfig(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            config = session.query(PlayConfig).filter(PlayConfig.play_config_id == id).first()
            if not config:
                raise ValueError(f"PlayConfig with id {id} not found.")
            
            session.delete(config)
            session.commit()

    @classmethod
    def updatePlayConfig(cls, id: str, updated_data: dict) -> PlayConfig:
        """更新单条"""
        with getDatabaseSession(False) as session:
            config = session.query(PlayConfig).filter(PlayConfig.play_config_id == id).first()
            if not config:
                raise ValueError(f"PlayConfig with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            session.commit()
            session.refresh(config)
        return config

    @classmethod
    def saveStartConfig(cls, config: StartConfig) -> StartConfig:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(config)
            session.commit()
            session.refresh(config)
        return config

    @classmethod
    def saveStartConfigList(cls, config: list[StartConfig]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(config)
        return
    
    @classmethod
    def deleteStartConfig(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            config = session.query(StartConfig).filter(StartConfig.play_config_id == id).first()
            if not config:
                return
            
            session.delete(config)
            session.commit()

    @classmethod
    def updateStartConfig(cls, id: str, updated_data: dict) -> StartConfig:
        """更新单条"""
        with getDatabaseSession(False) as session:
            config = session.query(StartConfig).filter(StartConfig.play_config_id == id).first()
            if not config:
                raise ValueError(f"StartConfig with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            session.commit()
            session.refresh(config)
        return config
    
    @classmethod
    def saveRouseConfig(cls, config: RouseConfig) -> RouseConfig:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(config)
            session.commit()
            session.refresh(config)
        return config

    @classmethod
    def saveRouseConfigList(cls, config: list[RouseConfig]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(config)
        return
    
    @classmethod
    def deleteRouseConfig(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            config = session.query(RouseConfig).filter(RouseConfig.play_config_id == id)
            config_del = config.all()
            for i in config_del:
                session.delete(i)
                session.commit()

    @classmethod
    def updateRouseConfig(cls, id: str, updated_data: dict) -> RouseConfig:
        """更新单条"""
        with getDatabaseSession(False) as session:
            config = session.query(RouseConfig).filter(RouseConfig.play_config_id == id).first()
            if not config:
                raise ValueError(f"RouseConfig with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            session.commit()
            session.refresh(config)
        return config
    
    @classmethod
    def saveDisturbConfig(cls, config: DisturbConfig) -> DisturbConfig:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(config)
            session.commit()
            session.refresh(config)
        return config

    @classmethod
    def saveDisturbConfigList(cls, config: list[DisturbConfig]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(config)
        return
    
    @classmethod
    def deleteDisturbConfig(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            config = session.query(DisturbConfig).filter(DisturbConfig.play_config_id == id)
            config_del = config.all()
            for i in config_del:
                session.delete(i)
                session.commit()

    @classmethod
    def updateDisturbConfig(cls, id: str, updated_data: dict) -> DisturbConfig:
        """更新单条"""
        with getDatabaseSession(False) as session:
            config = session.query(DisturbConfig).filter(DisturbConfig.play_config_id == id).first()
            if not config:
                raise ValueError(f"DisturbConfig with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            session.commit()
            session.refresh(config)
        return config
    
    @classmethod
    def saveNoiseConfig(cls, config: NoiseConfig) -> NoiseConfig:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(config)
            session.commit()
            session.refresh(config)
        return config

    @classmethod
    def saveNoiseConfigList(cls, config: list[NoiseConfig]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(config)
        return
    
    @classmethod
    def deleteNoiseConfig(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            config = session.query(NoiseConfig).filter(NoiseConfig.play_config_id == id)
            config_del = config.all()
            for i in config_del:
                session.delete(i)
                session.commit()

    @classmethod
    def updateNoiseConfig(cls, id: str, updated_data: dict) -> NoiseConfig:
        """更新单条"""
        with getDatabaseSession(False) as session:
            config = session.query(NoiseConfig).filter(NoiseConfig.play_config_id == id).first()
            if not config:
                raise ValueError(f"NoiseConfig with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            session.commit()
            session.refresh(config)
        return config
    
    @classmethod
    def saveTestCorpusConfig(cls, config: TestCorpusConfig) -> TestCorpusConfig:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(config)
            session.commit()
            session.refresh(config)
        return config

    @classmethod
    def saveRouseCorpusConfig(cls, config: RouseCorpusConfig) -> RouseCorpusConfig:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(config)
            session.commit()
            session.refresh(config)
        return config

    @classmethod
    def saveTestCorpusConfigList(cls, config: list[TestCorpusConfig]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(config)
        return
    
    @classmethod
    def deleteTestCorpusConfig(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            config = session.query(TestCorpusConfig).filter(TestCorpusConfig.play_config_id == id)
            config_del = config.all()
            for i in config_del:
                session.delete(i)
                session.commit()

    @classmethod
    def deleteRouseCorpusConfig(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            config = session.query(RouseCorpusConfig).filter(RouseCorpusConfig.play_config_id == id)
            config_del = config.all()
            for i in config_del:
                session.delete(i)
                session.commit()

    @classmethod
    def updateTestCorpusConfig(cls, id: str, updated_data: dict) -> TestCorpusConfig:
        """更新单条"""
        with getDatabaseSession(False) as session:
            config = session.query(TestCorpusConfig).filter(TestCorpusConfig.play_config_id == id).first()
            if not config:
                raise ValueError(f"TestCorpusConfig with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            session.commit()
            session.refresh(config)
        return config
    
    @classmethod
    def saveWaitConfig(cls, config: WaitConfig) -> WaitConfig:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(config)
            session.commit()
            session.refresh(config)
        return config

    @classmethod
    def saveWaitConfigList(cls, config: list[WaitConfig]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(config)
        return
    
    @classmethod
    def deleteWaitConfig(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            config = session.query(WaitConfig).filter(WaitConfig.play_config_id == id)
            config_del = config.all()
            for i in config_del:
                session.delete(i)
                session.commit()

    @classmethod
    def updateWaitConfig(cls, id: str, updated_data: dict) -> WaitConfig:
        """更新单条"""
        with getDatabaseSession(False) as session:
            config = session.query(WaitConfig).filter(WaitConfig.play_config_id == id).first()
            if not config:
                raise ValueError(f"WaitConfig with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            session.commit()
            session.refresh(config)
        return config