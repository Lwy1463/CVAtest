from .base_dao import getDatabaseSession
from app.dao.models import ReviewResult

class ReviewResultDao(object):
    @classmethod
    def getAll(cls) -> ReviewResult:
        with getDatabaseSession() as session:
            query = session.query(ReviewResult)
            # Fetch all results with applied filters
            results = query.all()

        return results

    @classmethod
    def getByPorject(cls, project_id: str) -> ReviewResult:
        with getDatabaseSession() as session:
            query = session.query(ReviewResult).filter(ReviewResult.project_id == project_id)
            # Fetch all results with applied filters
            results = query.all()

        return results

    @classmethod
    def getByPorjectAndTurn(cls, project_id: str, turn_id: int) -> ReviewResult:
        with getDatabaseSession() as session:
            query = session.query(ReviewResult).filter(ReviewResult.project_id == project_id).filter(
                ReviewResult.turn_id == turn_id
            )
            # Fetch all results with applied filters
            results = query.first()

        return results

    @classmethod
    def save(cls, data: ReviewResult) -> ReviewResult:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(data)
            session.commit()
            session.refresh(data)
        return data

    @classmethod
    def saveList(cls, datas: list[ReviewResult]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(datas)
        return
