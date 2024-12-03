from enum import Enum


class StatusCode(Enum):
    OK = (0, '成功')
    PROJECT_INIT_FAIL = (1, '项目初始化失败')

    @property
    def code(self):
        return self.value[0]

    @property
    def errmsg(self):
        return self.value[1]