import numpy as np

# 定义任务集合Q
tasks = {
    'T1': {'Di_in': 100, 'Ci': 50, 'Di_out': 50},
    'T2': {'Di_in': 150, 'Ci': 80, 'Di_out': 70},
    'T3': {'Di_in': 120, 'Ci': 70, 'Di_out': 60}
}

# 定义网络实体特征
N = 5  # 网络设备数量
Hi = np.random.rand(N)  # 生成随机信道增益
Pi = np.random.rand(N)  # 生成随机平均功率


# 计算通信速率
def calculate_Rv_wd(Hi, Pi, N0=1):
    Rv_wd = np.zeros(N)
    for i in range(N):
        Rv_wd[i] = B * np.log2(1 + Hi[i] * Pi[i] / N0)
    return Rv_wd


# 计算通信比(CVR)
def calculate_CVR(task, Rv_wd):
    Ki = task['Ci']
    di = (task['Di_in'] + task['Di_out']) / Rv_wd
    CVR = Ki / di
    return CVR


# 贪心算法任务迁移策略
def greedy_task_migration(tasks, Rv_wd):
    tasks_queue = list(tasks.keys())
    local_execution_queue = []
    mec_execution_queue = []

    while tasks_queue:
        CVRs = [calculate_CVR(tasks[task], Rv_wd) for task in tasks_queue]
        min_CVR_index = np.argmin(CVRs)
        min_CVR_task = tasks_queue.pop(min_CVR_index)

        if is_device_idle():
            local_execution_queue.append(min_CVR_task)
        elif is_server_idle():
            mec_execution_queue.append(min_CVR_task)

    return local_execution_queue, mec_execution_queue


# 检查设备是否空闲
def is_device_idle():
    return True  # 简化为始终空闲


# 检查服务器是否空闲
def is_server_idle():
    return True  # 简化为始终空闲


# 模拟数据
B = 10
Rv_wd = calculate_Rv_wd(Hi, Pi)

# 执行贪心算法任务迁移策略
local_tasks, mec_tasks = greedy_task_migration(tasks, Rv_wd)

print("本地执行任务队列:", local_tasks)
print("MEC执行任务队列:", mec_tasks)
