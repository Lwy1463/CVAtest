from sqlalchemy import desc

from .base_dao import getDatabaseSession
from app.dao.models import ProjectPlan, TCorpusTree, RCorpusTree, DCorpusTree, BNoiseTree, TestCorpus, RouseCorpus, DisturbCorpus, BackgroundNoise


class PlanQueryDao(object):
    """程序树类dao"""

    @classmethod
    def findProjectPlanById(cls, id: str) -> ProjectPlan:
        """单条查询示例"""
        with getDatabaseSession() as session:
            query = session.query(ProjectPlan).filter(ProjectPlan.plan_id == id)
            result = query.first()
            if not result:
                return None
        return result

    @classmethod
    def showAllProjectPlan(cls, filter_data: dict = None) -> list[ProjectPlan]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(ProjectPlan)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(ProjectPlan, key):
                        column_attr = getattr(ProjectPlan, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results

    @classmethod
    def findAllTCorpusByTreeId(cls, plan_id: str):
        """根据 plan_id 查询所有的 TestCorpus """
        ret = []
        with getDatabaseSession() as session:
            query = session.query(TCorpusTree).filter(TCorpusTree.plan_id == plan_id)
            result = query.all()
            if not result:
                return ret
            else:
                for i in result:
                    # temp = session.query(TestCorpus).filter(TestCorpus.corpus_id == i.corpus_id)
                    # corpus = temp.first() # 此地方可能会存在语料已经被删除，但是项目和步骤树内没被删除的情况，后续优化
                    ret.append(i.corpus_id)
                return ret

    @classmethod
    def findAllRCorpusByTreeId(cls, plan_id: str):
        """根据 plan_id 查询所有的 RouseCorpus """
        ret = []
        with getDatabaseSession() as session:
            query = session.query(RCorpusTree).filter(RCorpusTree.plan_id == plan_id)
            result = query.all()
            if not result:
                return ret
            else:
                for i in result:
                    temp = session.query(RouseCorpus).filter(RouseCorpus.corpus_id == i.corpus_id)
                    corpus = temp.first() 
                    ret.append(corpus)
                return ret

    @classmethod
    def findAllDCorpusByTreeId(cls, plan_id: str):
        """根据 plan_id 查询所有的 DisturbCorpus """
        ret = []
        with getDatabaseSession() as session:
            query = session.query(DCorpusTree).filter(DCorpusTree.plan_id == plan_id)
            result = query.all()
            if not result:
                return ret
            else:
                for i in result:
                    temp = session.query(DisturbCorpus).filter(DisturbCorpus.corpus_id == i.corpus_id)
                    corpus = temp.first()
                    ret.append(corpus)
                return ret

    @classmethod
    def findAllNoiseByTreeId(cls, plan_id: str):
        """根据 plan_id 查询所有的 BackgroundNoise """
        ret = []
        with getDatabaseSession() as session:
            query = session.query(BNoiseTree).filter(BNoiseTree.plan_id == plan_id)
            result = query.all()
            if not result:
                return ret
            else:
                for i in result:
                    temp = session.query(BackgroundNoise).filter(BackgroundNoise.corpus_id == i.corpus_id)
                    corpus = temp.first()
                    ret.append(corpus)
                return ret
            
    @classmethod
    def showAllTCorpusTree(cls, filter_data: dict = None) -> list[TCorpusTree]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(TCorpusTree)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(TCorpusTree, key):
                        column_attr = getattr(TCorpusTree, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results

    @classmethod
    def showAllRCorpusTree(cls, filter_data: dict = None) -> list[RCorpusTree]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(RCorpusTree)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(RCorpusTree, key):
                        column_attr = getattr(RCorpusTree, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results
    
    @classmethod
    def showAllDCorpusTree(cls, filter_data: dict = None) -> list[DCorpusTree]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(DCorpusTree)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(DCorpusTree, key):
                        column_attr = getattr(DCorpusTree, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results
    
    @classmethod
    def showAllBNoiseTree(cls, filter_data: dict = None) -> list[BNoiseTree]:
        """根据 filter_data 查询所有"""
        with getDatabaseSession() as session:
            query = session.query(BNoiseTree)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(BNoiseTree, key):
                        column_attr = getattr(BNoiseTree, key)
                        if isinstance(value, str):  # 如果值是字符串，则尝试使用模糊匹配
                            query = query.filter(column_attr.like(f"%{value}%"))
                        else:  # 否则使用精确匹配
                            query = query.filter(column_attr == value)
            # Fetch all results with applied filters
            results = query.all()
        return results


class PlanOperateDao(object):
    """操作程序树相关dao"""

    @classmethod
    def saveProjectPlan(cls, plan: ProjectPlan) -> ProjectPlan:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(plan)
            session.commit()
            session.refresh(plan)
        return plan

    @classmethod
    def saveProjectPlanList(cls, plan: list[ProjectPlan]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(plan)
        return
    
    @classmethod
    def deleteProjectPlan(cls, id: str) -> None:
        """删除单条"""
        with getDatabaseSession(False) as session:
            plan = session.query(ProjectPlan).filter(ProjectPlan.plan_id == id).first()
            if not plan:
                raise ValueError(f"ProjectPlan with id {id} not found.")
            else:
                a = session.query(TCorpusTree).filter(TCorpusTree.plan_id == plan.plan_id)
                a_del = a.all()
                for i in a_del:
                    session.delete(i)
                    session.commit()
                b = session.query(RCorpusTree).filter(RCorpusTree.plan_id == plan.plan_id)
                b_del = b.all()
                for i in b_del:
                    session.delete(i)
                    session.commit()
                c = session.query(DCorpusTree).filter(DCorpusTree.plan_id == plan.plan_id)
                c_del = c.all()
                for i in c_del:
                    session.delete(i)
                    session.commit()
                d = session.query(BNoiseTree).filter(BNoiseTree.plan_id == plan.plan_id)
                d_del = d.all()
                for i in d_del:
                    session.delete(i)
                    session.commit()

            session.delete(plan)
            session.commit()

    @classmethod
    def updateProjectPlan(cls, id: str, updated_data: dict) -> ProjectPlan:
        """更新单条"""
        with getDatabaseSession(False) as session:
            plan = session.query(ProjectPlan).filter(ProjectPlan.plan_id == id).first()
            if not plan:
                raise ValueError(f"ProjectPlan with id {id} not found.")
            
            for key, value in updated_data.items():
                if hasattr(plan, key):
                    setattr(plan, key, value)

            session.commit()
            session.refresh(plan)
        return plan

    @classmethod
    def updateProjectPlanTree(cls, id: str, updated_data: dict) -> ProjectPlan:
        """更新单条"""
        with getDatabaseSession(False) as session:
            plan = session.query(ProjectPlan).filter(ProjectPlan.plan_id == id).first()
            if not plan:
                raise ValueError(f"ProjectPlan with id {id} not found.")
            # 现在更新表是直接删了重新创建的，后续优化
            a = session.query(TCorpusTree).filter(TCorpusTree.plan_id == plan.plan_id)
            a_del = a.all()
            for i in a_del:
                session.delete(i)
                session.commit()
            b = session.query(RCorpusTree).filter(RCorpusTree.plan_id == plan.plan_id)
            b_del = b.all()
            for i in b_del:
                session.delete(i)
                session.commit()
            c = session.query(DCorpusTree).filter(DCorpusTree.plan_id == plan.plan_id)
            c_del = c.all()
            for i in c_del:
                session.delete(i)
                session.commit()
            d = session.query(BNoiseTree).filter(BNoiseTree.plan_id == plan.plan_id)
            d_del = d.all()
            for i in d_del:
                session.delete(i)
                session.commit()
            for key, value in updated_data.items():
                if type(value) != list:
                    if key == "testCorpusList" and len(value) != 0:
                        corpus_list = []
                        for id in value:
                            temp = session.query(TestCorpus).filter(TestCorpus.corpus_id == id)
                            a = temp.first()
                            if not a:
                                raise ValueError(f"TestCorpus with id {id} not found.")
                            corpus = TCorpusTree(plan_id = plan.plan_id, corpus_id = id)
                            corpus_list.append(corpus)
                        session.bulk_save_objects(corpus_list)
                    if key == "rouseCorpusList" and len(value) != 0:
                        corpus_list = []
                        for id in value:
                            temp = session.query(RouseCorpus).filter(RouseCorpus.corpus_id == id)
                            a = temp.first()
                            if not a:
                                raise ValueError(f"RouseCorpus with id {id} not found.")
                            corpus = RCorpusTree(plan_id = plan.plan_id, corpus_id = id)
                            corpus_list.append(corpus)
                        session.bulk_save_objects(corpus_list)
                    if key == "disturbCorpusList" and len(value) != 0:
                        corpus_list = []
                        for id in value:
                            temp = session.query(DisturbCorpus).filter(DisturbCorpus.corpus_id == id)
                            a = temp.first()
                            if not a:
                                raise ValueError(f"DisturbCorpus with id {id} not found.")
                            corpus = DCorpusTree(plan_id = plan.plan_id, corpus_id = id)
                            corpus_list.append(corpus)
                        session.bulk_save_objects(corpus_list)
                    if key == "backgroundNoiseList" and len(value) != 0:
                        corpus_list = []
                        for id in value:
                            temp = session.query(BackgroundNoise).filter(BackgroundNoise.corpus_id == id)
                            a = temp.first()
                            if not a:
                                raise ValueError(f"BackgroundNoise with id {id} not found.")
                            corpus = BNoiseTree(plan_id = plan.plan_id, corpus_id = id)
                            corpus_list.append(corpus)
                        session.bulk_save_objects(corpus_list)
                if type(value) != list and hasattr(plan, key):
                    setattr(plan, key, value)

            session.commit()
            session.refresh(plan)
        return plan

    @classmethod
    def saveTCorpusTree(cls, corpus: TCorpusTree) -> TCorpusTree:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(corpus)
            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def updateTCorpusTree(cls, updated_data: dict, filter_data: dict = None):
        """更新单条"""
        with getDatabaseSession(False) as session:
            query = session.query(TCorpusTree)
            if filter_data:
                for key, value in filter_data.items():
                    if hasattr(TCorpusTree, key):
                        query = query.filter(getattr(TCorpusTree, key) == value)
            # Fetch all results with applied filters
            results = query.all()
            for plan in results:
                for key, value in updated_data.items():
                    if hasattr(plan, key):
                        setattr(plan, key, value)

                session.commit()
                session.refresh(plan)

    @classmethod
    def saveTCorpusTreeList(cls, corpus: list[TCorpusTree]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(corpus)
        return

    @classmethod
    def saveRCorpusTree(cls, corpus: RCorpusTree) -> RCorpusTree:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(corpus)
            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def saveRCorpusTreeList(cls, corpus: list[RCorpusTree]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(corpus)
        return

    @classmethod
    def saveDCorpusTree(cls, corpus: DCorpusTree) -> DCorpusTree:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(corpus)
            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def saveDCorpusTreeList(cls, corpus: list[DCorpusTree]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(corpus)
        return

    @classmethod
    def saveBNoiseTree(cls, corpus: BNoiseTree) -> BNoiseTree:
        """添加单条"""
        with getDatabaseSession(False) as session:
            session.add(corpus)
            session.commit()
            session.refresh(corpus)
        return corpus

    @classmethod
    def saveBNoiseTreeList(cls, corpus: list[BNoiseTree]):
        """添加多条"""
        with getDatabaseSession() as session:
            session.bulk_save_objects(corpus)
        return

    @classmethod
    def  deleteTCorpusTree(cls, plan_id: str) -> None:
 
        with getDatabaseSession(False) as session:
            a = session.query(TCorpusTree).filter(TCorpusTree.plan_id == plan_id)
            a_del = a.all()
            for i in a_del:
                session.delete(i)
                session.commit()

    @classmethod
    def  deleteRCorpusTree(cls, plan_id: str) -> None:
 
        with getDatabaseSession(False) as session:
            a = session.query(RCorpusTree).filter(RCorpusTree.plan_id == plan_id)
            a_del = a.all()
            for i in a_del:
                session.delete(i)
                session.commit()

    @classmethod
    def  deleteDCorpusTree(cls, plan_id: str) -> None:
 
        with getDatabaseSession(False) as session:
            a = session.query(DCorpusTree).filter(DCorpusTree.plan_id == plan_id)
            a_del = a.all()
            for i in a_del:
                session.delete(i)
                session.commit()

    @classmethod
    def  deleteBNoiseTree(cls, plan_id: str) -> None:
 
        with getDatabaseSession(False) as session:
            a = session.query(BNoiseTree).filter(BNoiseTree.plan_id == plan_id)
            a_del = a.all()
            for i in a_del:
                session.delete(i)
                session.commit()