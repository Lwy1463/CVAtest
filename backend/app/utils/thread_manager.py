import threading

class ThreadManager:
    def __init__(self):
        self.threads = {}  # 主线程的管理
        self.sub_threads = {}  # 子线程的管理

    def start_thread(self, project_id, target, *args):
        # 检查是否已有主线程在运行
        if project_id in self.threads and self.threads[project_id].is_alive():
            raise ValueError(f"Project with id {project_id} is already running")
        
        # 创建并启动主线程
        thread = threading.Thread(target=target, args=(self, *args), name=f"ProjectThread-{project_id}", daemon=True)
        self.threads[project_id] = thread
        thread.start()
        return thread

    def start_sub_thread(self, project_id, sub_thread_id, target, *args):
        # 确保主线程的子线程字典存在
        if project_id not in self.sub_threads:
            self.sub_threads[project_id] = {}

        # 创建并启动子线程
        sub_thread = threading.Thread(target=target, args=args, name=f"SubThread-{sub_thread_id}", daemon=True)
        self.sub_threads[project_id][sub_thread_id] = sub_thread
        sub_thread.start()
        return sub_thread


    def stop_thread(self, project_id):
        # 停止主线程的逻辑（假设线程能被安全终止）
        if project_id in self.threads:
            del self.threads[project_id]
        
        # 停止所有子线程
        if project_id in self.sub_threads:
            for sub_thread_id, sub_thread in self.sub_threads[project_id].items():
                # 假设子线程能被安全地终止
                print(f"Stopping sub-thread {sub_thread_id} of project {project_id}")
            # 清理子线程的字典
            del self.sub_threads[project_id]


# 创建 ThreadManager 实例
thread_manager = ThreadManager()