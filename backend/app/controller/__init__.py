from app.controller import demo_router
from app.controller import corpus
from app.controller import project
from app.controller import synthesize_corpus
from app.controller import play_config
from app.controller import device
from app.controller import multi_corpus


# 定义路由列表
RegisterRouterList = []
RegisterRouterList.append(demo_router)
RegisterRouterList.append(corpus)
RegisterRouterList.append(project)
RegisterRouterList.append(synthesize_corpus)
RegisterRouterList.append(play_config)
RegisterRouterList.append(device)
RegisterRouterList.append(multi_corpus)
