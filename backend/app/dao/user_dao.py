from sqlalchemy import desc

from .base_dao import getDatabaseSession
from app.dao.models import User


class UserQueryDao(object):
    """用户查询类dao"""

    @classmethod
    def findByPhone(cls, phone: str) -> User:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(User).filter(User.phone == phone)
            result = query.first()
        return result


class UserOperateDao(object):
    """操作用户相关dao"""

    @classmethod
    def saveUser(cls, user: User) -> User:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    @classmethod
    def saveUserList(cls, users: list[User]):
        """添加单条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(users)
        return