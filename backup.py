def run(self, WD_num, MEC_num, mecSystem, taskGraphDict):
    allDeviceCalculator = {}
    all_task_status = {}
    total_tasks = {}
    wdNo = 0
    for wd in mecSystem.nodes:
        if "WD" in wd:
            allDeviceCalculator[wd] = Calculator(mecSystem, taskGraphDict[wd])

            all_task_status[wd] = {task: False for task in taskGraphDict[wd].nodes if task not in ["Start", "Exit"]}
            total_tasks[wd] = len(all_task_status[wd])

    # calculator = Calculator(mecSystem, taskGraph)
    self.calculator = allDeviceCalculator
    # task_status = {task: False for task in taskGraph.nodes if task not in ["Start", "Exit"]}
    # total_tasks = len(task_status)
    device_execute_time_line = {device: 0 for device in mecSystem.nodes()}  # 每個設備執行了多長時間

    total_task_execute_time = 0
    total_task_delay_time = 0
    device_task_delay_form = {device: {} for device in mecSystem.nodes()}
    device_average_task_delay = {device: 0 for device in mecSystem.nodes()}
    task_delay_form = {}

    task_priority_queues = {wd: deque() for wd in mecSystem.nodes if "WD" in wd}  # 每台wd一個隊列
    # task_priority_queue = deque()
    time_line = 0

    wd_node = "WD0"

    for wd_node in mecSystem.nodes:  # 逐个計算移動設備經过的時間
        if "WD" in wd_node:
            # 最近的空閒MEC
            closest_free_MEC = self.find_closest_free_MEC(mecSystem, wd_node, device_execute_time_line)

            # 將起始任務加入優先級隊列
            start_successors = list(taskGraphDict[wd_node].successors("Start"))
            for successor in start_successors:
                if successor == 'Exit':
                    continue
                # 用雙端隊列儲存CVR
                # 隊列元素:(CVR,元素,MEC服務器)
                task_priority_queues[wd_node].append(
                    [allDeviceCalculator[wd_node].CALCULATE_CVR(successor, wd_node, closest_free_MEC), successor,
                     closest_free_MEC])
            # 排序
            self.insertion_sort(task_priority_queues[wd_node])

    while any(task_priority_queues[wd_node] for wd_node in mecSystem.nodes if "WD" in wd_node):
        for wd_node in mecSystem.nodes:
            if "WD" in wd_node:
                time_line = device_execute_time_line[wd_node]
                if math.floor(device_execute_time_line[wd_node]) <= time_line:  # 本地設備空閒
                    min_CVR = task_priority_queues[wd_node].popleft()
                    task_execute_time = allDeviceCalculator[wd_node].LOCAL_CALCULATION_DELAY(min_CVR[1], wd_node)
                    # 更新任務執行時間
                    device_execute_time_line[wd_node] += task_execute_time
                    total_task_execute_time += task_execute_time

                    # 標記當前任務為已執行
                    all_task_status[wd_node][min_CVR[1]] = True

                    # 更新任務的實際完成時間
                    allDeviceCalculator[wd_node].updateActualFinishTime(min_CVR[1], device_execute_time_line[wd_node])
                    # 任務的完成時間減去任務的就緒時間，為任務延迟了多久才被執行
                    task_delay_time = device_execute_time_line[wd_node] - allDeviceCalculator[wd_node].TASK_READY_TIME(
                        min_CVR[1])
                    device_task_delay_form[wd_node][min_CVR[1]] = task_delay_time
                    total_task_delay_time += task_delay_time
                    device_average_task_delay[wd_node] += task_delay_time

                    # 更新後繼任務的CVR並加入隊列
                    for successor in taskGraphDict[wd_node].successors(min_CVR[1]):
                        if successor == 'Exit':
                            continue
                        if all(all_task_status[wd_node][predecessor] for predecessor in
                               taskGraphDict[wd_node].predecessors(successor)):
                            closest_free_MEC = self.find_closest_free_MEC(mecSystem, wd_node,
                                                                          device_execute_time_line)
                            task_priority_queues[wd_node] = self.count_and_sort_CVR(task_priority_queues[wd_node],
                                                                                    wd_node,
                                                                                    closest_free_MEC)
                            task_priority_queues[wd_node].append(
                                [allDeviceCalculator[wd_node].CALCULATE_CVR(successor, wd_node, closest_free_MEC),
                                 successor,
                                 closest_free_MEC])
                    # 排序
                    self.insertion_sort(task_priority_queues[wd_node])
                else:
                    for mec, time in device_execute_time_line.items():
                        if math.floor(time) <= time_line and "WD" not in mec:
                            # 用这空閒MVC重排CVR
                            self.count_and_sort_CVR(task_priority_queues[wd_node], wd_node, mec)
                            max_CVR = task_priority_queues[wd_node].pop()
                            task_execute_time = allDeviceCalculator[wd_node].MEC_CALCULATION_DELAY(max_CVR[1], wd_node,
                                                                                                   mec)
                            # 更新任務執行時間
                            device_execute_time_line[mec] += task_execute_time
                            total_task_execute_time += task_execute_time
                            # 標記當前任務為已執行
                            all_task_status[max_CVR[1]] = True

                            # 更新任務的實際完成時間
                            allDeviceCalculator[wd_node].updateActualFinishTime(max_CVR[1],
                                                                                device_execute_time_line[wd_node])
                            # 任務的完成時間減去任務的就緒時間，為任務延迟了多久才被執行
                            task_delay_time = device_execute_time_line[mec] - allDeviceCalculator[
                                wd_node].TASK_READY_TIME(max_CVR[1])
                            total_task_delay_time += task_delay_time
                            device_task_delay_form[wd_node][max_CVR[1]] = task_delay_time
                            device_average_task_delay[wd_node] += task_delay_time
                            # task_delay_form[max_CVR[1]] = task_delay_time

                            # 更新後繼任務的CVR並加入隊列
                            for successor in taskGraphDict[wd_node].successors(max_CVR[1]):
                                if successor == 'Exit':
                                    continue
                                if all(all_task_status[predecessor] for predecessor in
                                       taskGraphDict[wd_node].predecessors(successor)):
                                    closest_free_MEC = self.find_closest_free_MEC(mecSystem, wd_node,
                                                                                  device_execute_time_line)
                                    task_priority_queues[wd_node] = self.count_and_sort_CVR(
                                        task_priority_queues[wd_node], wd_node,
                                        closest_free_MEC)
                                    task_priority_queues[wd_node].append(
                                        [allDeviceCalculator[wd_node].CALCULATE_CVR(successor, wd_node,
                                                                                    closest_free_MEC), successor,
                                         closest_free_MEC])
                            # 排序
                            self.insertion_sort(task_priority_queues[wd_node])

    # 檢查是否所有任務都已成功執行
    assert all(status == True for status in all_task_status[wd_node].values()), "有任務未能成功執行"

    # 系統執行完所有任務實際經過的時間
    time_line = max(device_execute_time_line.values())
    # 計算平均執行時間
    average_task_complete_time = total_task_execute_time / sum(total_tasks.values())
    # 計算平均任務時延
    average_task_delay_time = total_task_delay_time / sum(total_tasks.values())
    # 每個設備的平均任務時延
    for key, value in device_average_task_delay:
        device_average_task_delay[key] = value / total_tasks[key]

    return total_task_execute_time, time_line, average_task_complete_time, total_task_delay_time, average_task_delay_time, task_delay_form, device_average_task_delay
