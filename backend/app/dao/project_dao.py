from sqlalchemy import desc

from .base_dao import getDatabaseSession
from app.dao.models import TestProject


class ProjectQueryDao(object):
    """音频查询类dao"""

    @classmethod
    def findTestProjectById(cls, id: str, turn_id=None) -> TestProject:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(TestProject).filter(TestProject.project_id == id)
            if turn_id:
                query = query.filter(TestProject.turn_id == turn_id)
            result = query.first()
            if not result:
                return None
        return result

    @classmethod
    def showAllTestProject(cls, filter_data: dict = None) -> list[TestProject]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(TestProject)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(TestProject, key):
                        column_attr = getattr(TestProject, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
            
        return results


class ProjectOperateDao(object):
    """操作音频相关dao"""

    @classmethod
    def saveTestProject(cls, project: TestProject) -> TestProject:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(project)
            session.commit()
            session.refresh(project)
        return project

    @classmethod
    def saveTestProjectList(cls, project: list[TestProject]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(project)
        return
    
    @classmethod
    def deleteTestProject(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            project = session.query(TestProject).filter(TestProject.project_id == id).first()
            if not project:
                raise ValueError(f"TestProject with id {id} not found.")
            
            session.delete(project)
            session.commit()

    @classmethod
    def updateTestProject(cls, id: str, updated_data: dict) -> TestProject:
        """更新单条"""
        with getDatabaseSession(False) as session:
            project = session.query(TestProject).filter(TestProject.project_id == id).first()
            if not project:
                raise ValueError(f"TestProject with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(project, key):
                    setattr(project, key, value)

            session.commit()
            session.refresh(project)
        return project

 