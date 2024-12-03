from sqlalchemy import func
from .base_dao import getDatabaseSession
from app.dao.models import TestResult, MultiResult


class ResultQueryDao(object):

    @classmethod
    def findTestResultById(cls, id: str) -> TestResult:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(TestResult).filter(TestResult.result_id == id)
            result = query.first()
            if not result:
                return None
        return result

    @classmethod
    def showAllTestResult(cls, filter_data: dict = None) -> TestResult:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(TestResult)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(TestResult, key):
                        query = query.filter(getattr(TestResult, key) == value)
            # Fetch all results with applied filters
            results = query.all()
            
        return results

    @classmethod
    def showAllMultiResult(cls, filter_data: dict = None) -> MultiResult:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(MultiResult)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(MultiResult, key):
                        query = query.filter(getattr(MultiResult, key) == value)
            # Fetch all results with applied filters
            results = query.all()
        return results

    @classmethod
    def getTurnListBySet(cls, project_id: str):
        with getDatabaseSession() as session:
            query = session.query(TestResult.turn_id).filter(TestResult.project_id == project_id)
            # Fetch all results with applied filters
            turns = query.all()

        return turns

    @classmethod
    def getMaxTurn(cls, project_id: str) -> int:
        with getDatabaseSession() as session:
            max_turn = session.query(func.max(TestResult.turn_id)).filter(TestResult.project_id == project_id).scalar()

        return max_turn


class ResultOperateDao(object):

    @classmethod
    def saveTestResult(cls, result: TestResult) -> TestResult:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(result)
            session.commit()
            session.refresh(result)
        return result

    @classmethod
    def saveTestResultList(cls, result: list[TestResult]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(result)
        return
    
    @classmethod
    def deleteTestResult(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            result = session.query(TestResult).filter(TestResult.result_id == id).first()
            if not result:
                raise ValueError(f"TestResult with id {id} not found.")
            
            session.delete(result)
            session.commit()

    @classmethod
    def updateTestResult(cls, id: str, updated_data: dict) -> TestResult:
        """更新单条"""
        with getDatabaseSession(False) as session:
            result = session.query(TestResult).filter(TestResult.result_id == id).first()
            if not result:
                raise ValueError(f"TestResult with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(result, key):
                    setattr(result, key, value)

            session.commit()
            session.refresh(result)
        return result

    @classmethod
    def saveMultiResult(cls, result: MultiResult) -> MultiResult:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(result)
            session.commit()
            session.refresh(result)
        return result

    @classmethod
    def saveMultiResultList(cls, result: list[MultiResult]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(result)
        return
    
    @classmethod
    def deleteMultiResult(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            result = session.query(MultiResult).filter(MultiResult.id == id).first()
            if not result:
                raise ValueError(f"MultiResult with id {id} not found.")
            
            session.delete(result)
            session.commit()

    @classmethod
    def updateMultiResult(cls, id: str, updated_data: dict) -> MultiResult:
        """更新单条"""
        with getDatabaseSession(False) as session:
            result = session.query(MultiResult).filter(MultiResult.id == id).first()
            if not result:
                raise ValueError(f"MultiResult with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(result, key):
                    setattr(result, key, value)

            session.commit()
            session.refresh(result)
        return result
 