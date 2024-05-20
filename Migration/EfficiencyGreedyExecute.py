import heapq
import math

import threading

from collections import deque

from Calculator import Calculator


device_execute_time_line = {}  # 每個設備目前經过的時間
time_line = 0  # 系統經过的時間
data_lock = threading.Lock()  # 數據鎖
all_device_execute_data = {}  # 所有設備的執行數據


class EfficiencyGreedyExecute:
    calculator = None

    def __init__(self):
        pass

    def find_closest_free_MEC(self, mecSystem, wd_node, device_execute_time_line):
        # 寻找所有空闲的MEC服务器，由於仿真實驗並沒有真實執行任務，因此定義了一個包含每個設備執行任務的時間的字典，通過找到該字典中最小的值對应的鍵，該設備便在整個系統時間戳到逹該值時是空閒的。
        # 允許同一時間有多台設備處理空閒狀態，為了尽量貼近真實情況，減少誤差，且考慮計算延迟等情況，把該時間值取整作比較，並且相差1ms以內的設備都同時視為空閒設備
        closest_free_MEC = None
        min_value = min(value for key, value in device_execute_time_line.items() if "WD" not in key)
        free_device = [key for key, value in device_execute_time_line.items() if "WD" not in key and
                       (round(value) == round(min_value) or round(value) == round(min_value) + 1 or round(
                           value) == round(min_value) - 1)]
        min_distance = float('inf')
        # 找到空閒MEC中距離最小的
        for mec in free_device:
            edge_data = mecSystem.get_edge_data(wd_node, mec)

            distance = 0
            if edge_data is None:
                neighbors = list(mecSystem.neighbors(wd_node))  # 若服務器节点與移動設備沒有直接信道連接，需要由最近的服務器轉發
                sorted_neighbors = sorted(neighbors, key=lambda x: mecSystem.edges[wd_node, x]['distance'])
                min_distance_node = sorted_neighbors[0]
                edge_data_w_m = mecSystem.get_edge_data(wd_node, min_distance_node)
                edge_data_m1_m2 = mecSystem.get_edge_data(min_distance_node, mec)
                distance = edge_data_w_m["labels"]["distance"] + edge_data_m1_m2["labels"]["distance"]
            else:
                distance = edge_data["labels"]["distance"]
            if distance < min_distance:
                closest_free_MEC = mec
                min_distance = distance

        return closest_free_MEC

    # 插入排序
    def insertion_sort(self, dequeue):
        for i in range(1, len(dequeue)):
            key = dequeue[i]
            j = i - 1
            while j >= 0 and key[0] < dequeue[j][0]:
                dequeue[j + 1] = dequeue[j]
                j -= 1
            dequeue[j + 1] = key

    def count_and_sort_CVR(self, task_priority_queue, wd_node, mec):
        # 用这空閒MVC重排CVR
        for CVR in task_priority_queue:
            CVR[0] = self.calculator[wd_node].CALCULATE_CVR(CVR[1], wd_node, mec)
            CVR[2] = mec
        self.insertion_sort(task_priority_queue)
        return task_priority_queue

    def run(self, WD_num, MEC_num, mecSystem, taskGraphDict):
        device_average_task_delay = {}
        total_task_execute_time = 0
        total_task_delay_time = 0
        task_delay_form = {}
        global time_line
        global all_device_execute_data
        global device_execute_time_line
        device_execute_time_line = {device: 0 for device in mecSystem.nodes}

        threads = []
        for wd_node in mecSystem.nodes:  # 逐个計算移動設備經过的時間
            if "WD" in wd_node:
                executor = WDTaskExecutor(wd_node, mecSystem, taskGraphDict[wd_node])
                executor.start()
                threads.append(executor)

        for t in threads:
            t.join()
        # 系統執行完所有任務實際經過的時間

        average_all_task_complete_time = 0
        average_all_task_delay_time = 0
        for key, value in all_device_execute_data.items():
            # 計算平均執行時間
            total_task_execute_time += value["total_task_execute_time"]
            average_all_task_complete_time += value["average_task_complete_time"]
            # 計算平均任務時延
            average_all_task_delay_time += value["average_task_delay_time"]
        average_all_task_complete_time = average_all_task_complete_time / len(all_device_execute_data)
        average_all_task_delay_time = average_all_task_delay_time / len(all_device_execute_data)

        # 每個設備的平均任務時延
        for key, value in all_device_execute_data.items():
            device_average_task_delay[key] = value["average_task_delay_time"]

        return total_task_execute_time, time_line, average_all_task_complete_time, total_task_delay_time, average_all_task_delay_time, task_delay_form


class WDTaskExecutor(threading.Thread):
    def __init__(self, wd_node, mecSystem, taskGraph):
        threading.Thread.__init__(self)
        self.wd_node = wd_node
        self.mecSystem = mecSystem
        self.task_priority_queues = deque()
        self.calculator = Calculator(mecSystem, taskGraph)
        self.taskGraph = taskGraph
        self.all_task_status = {task: False for task in taskGraph.nodes if task not in ["Start", "Exit"]}
        self.device_task_delay_form = {}
        self.total_task_delay_time = 0
        self.total_task_execute_time = 0
        self.device_average_task_delay = 0
        self.total_tasks = len([task for task in taskGraph.nodes if task not in ["Start", "Exit"]])
        self.tasks_execute_device = {no: "" for no in taskGraph.nodes if no not in ["Start", "Exit"]}

    def find_closest_free_MEC(self, mecSystem, wd_node, device_execute_time_line):

        # 寻找所有空闲的MEC服务器，由於仿真實驗並沒有真實執行任務，因此定義了一個包含每個設備執行任務的時間的字典，通過找到該字典中最小的值對应的鍵，該設備便在整個系統時間戳到逹該值時是空閒的。
        # 允許同一時間有多台設備處理空閒狀態，為了尽量貼近真實情況，減少誤差，且考慮計算延迟等情況，把該時間值取整作比較，並且相差1ms以內的設備都同時視為空閒設備
        closest_free_MEC = None

        min_value = min(value for key, value in device_execute_time_line.items() if "WD" not in key)
        free_device = [key for key, value in device_execute_time_line.items() if "WD" not in key and
                       (round(value) == round(min_value) or round(value) == round(min_value) + 1 or round(
                           value) == round(min_value) - 1)]
        min_distance = float('inf')
        # 找到空閒MEC中距離最小的
        for mec in free_device:
            edge_data = mecSystem.get_edge_data(wd_node, mec)
            distance = 0
            if edge_data is None:
                neighbors = list(mecSystem.neighbors(wd_node))  # 若服務器节点與移動設備沒有直接信道連接，需要由最近的服務器轉發
                sorted_neighbors = sorted(neighbors, key=lambda x: mecSystem.edges[wd_node, x]["labels"]['distance'])
                min_distance_node = sorted_neighbors[0]
                edge_data_w_m = mecSystem.get_edge_data(wd_node, min_distance_node)
                edge_data_m1_m2 = mecSystem.get_edge_data(min_distance_node, mec)
                distance = edge_data_w_m["labels"]["distance"] + edge_data_m1_m2["labels"]["distance"]
            else:
                distance = edge_data["labels"]["distance"]

            if distance < min_distance:
                closest_free_MEC = mec
                min_distance = distance

        return closest_free_MEC

    # 插入排序
    def insertion_sort(self, dequeue):
        for i in range(1, len(dequeue)):
            key = dequeue[i]
            j = i - 1
            while j >= 0 and key[0] < dequeue[j][0]:
                dequeue[j + 1] = dequeue[j]
                j -= 1
            dequeue[j + 1] = key

    def count_and_sort_CVR(self, task_priority_queue, wd_node, mec):
        # 用这空閒MVC重排CVR
        for CVR in task_priority_queue:
            CVR[0] = self.calculator.CALCULATE_CVR(CVR[1], wd_node, mec)
            CVR[2] = mec
        self.insertion_sort(task_priority_queue)
        return task_priority_queue

    def run(self):
        global device_execute_time_line
        global time_line

        closest_free_MEC = self.find_closest_free_MEC(self.mecSystem, self.wd_node, device_execute_time_line)

        # 將起始任務加入優先級隊列
        start_successors = list(self.taskGraph.successors("Start"))

        for successor in start_successors:
            if successor == 'Exit':
                continue
            # 用雙端隊列儲存CVR
            # 隊列元素:(CVR,元素,MEC服務器)

            self.task_priority_queues.append(
                [self.calculator.CALCULATE_CVR(successor, self.wd_node, closest_free_MEC), successor,
                 closest_free_MEC])
        # 排序
        self.insertion_sort(self.task_priority_queues)
        device_execute_time_line[self.wd_node] = 0

        while any(self.task_priority_queues):

            if math.floor(device_execute_time_line[self.wd_node]) <= time_line:  # 本地設備空閒
                min_CVR = self.task_priority_queues.popleft()
                task_execute_time = self.calculator.LOCAL_CALCULATION_DELAY(min_CVR[1], self.wd_node)

                self.tasks_execute_device[min_CVR[1]] = self.wd_node  # 記錄任務在哪個設備上執行
                data_transport_back_time = 0  # 任務節點需要前置節點的數據才能執行
                for predecessor in self.taskGraph.predecessors(min_CVR[1]):
                    if predecessor == "Start":
                        continue
                    from_device = self.tasks_execute_device[min_CVR[1]]
                    if from_device == "" or from_device == self.wd_node : continue
                    data_transport_back_time += self.calculator.TASK_TRANSPORT_BACK_TIME(predecessor, from_device, self.wd_node)

                # 更新任務執行時間
                self.total_task_execute_time += task_execute_time
                with data_lock:
                    device_execute_time_line[self.wd_node] += task_execute_time + data_transport_back_time
                    time_line = max(device_execute_time_line.values())
                print("{} 上的任務 {} 已在本地执行".format(self.wd_node, min_CVR[1]))

                # 標記當前任務為已執行
                self.all_task_status[min_CVR[1]] = True

                # 更新任務的實際完成時間
                self.calculator.updateActualFinishTime(min_CVR[1], device_execute_time_line[self.wd_node])
                # 任務的完成時間減去任務的就緒時間，為任務延迟了多久才被執行
                task_delay_time = device_execute_time_line[self.wd_node] - self.calculator.TASK_READY_TIME(min_CVR[1])

                self.device_task_delay_form[min_CVR[1]] = task_delay_time
                self.total_task_delay_time += task_delay_time

                # 更新後繼任務的CVR並加入隊列
                for successor in self.taskGraph.successors(min_CVR[1]):
                    if successor == 'Exit':
                        continue
                    if all(self.all_task_status[predecessor] for predecessor in self.taskGraph.predecessors(successor)):
                        closest_free_MEC = self.find_closest_free_MEC(self.mecSystem, self.wd_node,
                                                                      device_execute_time_line)
                        self.task_priority_queues = self.count_and_sort_CVR(
                            self.task_priority_queues,
                            self.wd_node,
                            closest_free_MEC)
                        self.task_priority_queues.append(
                            [self.calculator.CALCULATE_CVR(successor, self.wd_node, closest_free_MEC), successor,
                             closest_free_MEC])
                        # 排序
                        self.insertion_sort(self.task_priority_queues)
            # else:
            for mec, time in device_execute_time_line.items():

                if math.floor(time) <= time_line and "WD" not in mec:
                    # 用这空閒MVC重排CVR
                    self.count_and_sort_CVR(self.task_priority_queues, self.wd_node, mec)
                    if len(self.task_priority_queues) == 0:
                        continue
                    max_CVR = self.task_priority_queues.pop()

                    self.tasks_execute_device[max_CVR[1]] = mec  # 記錄任務在哪個設備上執行

                    data_transport_back_time = 0  # 任務節點需要前置節點的數據才能執行
                    for predecessor in self.taskGraph.predecessors(max_CVR[1]):
                        if predecessor == "Start":
                            continue
                        from_device = self.tasks_execute_device[max_CVR[1]]
                        if from_device == "" or from_device == mec : continue
                        data_transport_back_time += self.calculator.TASK_TRANSPORT_BACK_TIME(predecessor, from_device,
                                                                                             mec)

                    task_execute_time = self.calculator.MEC_CALCULATION_DELAY(max_CVR[1], self.wd_node, mec)

                    # 更新任務執行時間
                    self.total_task_execute_time += task_execute_time
                    with data_lock:
                        device_execute_time_line[mec] += task_execute_time + data_transport_back_time
                        time_line = max(device_execute_time_line.values())
                    # 標記當前任務為已執行
                    print("{} 上的任務 {} 已決定迁移至 {} 上执行".format(self.wd_node, max_CVR[1], mec))
                    self.all_task_status[max_CVR[1]] = True

                    # 更新任務的實際完成時間
                    self.calculator.updateActualFinishTime(max_CVR[1],
                                                           device_execute_time_line[self.wd_node])
                    # 任務的完成時間減去任務的就緒時間，為任務延迟了多久才被執行
                    task_delay_time = device_execute_time_line[mec] - self.calculator.TASK_READY_TIME(
                        max_CVR[1])
                    self.total_task_delay_time += math.fabs(task_delay_time)
                    self.device_task_delay_form[max_CVR[1]] = math.fabs(task_delay_time)

                    # task_delay_form[max_CVR[1]] = task_delay_time

                    # 更新後繼任務的CVR並加入隊列
                    for successor in self.taskGraph.successors(max_CVR[1]):
                        if successor == 'Exit':
                            continue
                        if all(self.all_task_status[predecessor] for predecessor in
                               self.taskGraph.predecessors(successor)):
                            closest_free_MEC = self.find_closest_free_MEC(self.mecSystem, self.wd_node,
                                                                          device_execute_time_line)
                            self.task_priority_queues = self.count_and_sort_CVR(self.task_priority_queues,
                                                                                self.wd_node,
                                                                                closest_free_MEC)
                            self.task_priority_queues.append(
                                [self.calculator.CALCULATE_CVR(successor, self.wd_node, closest_free_MEC),
                                 successor,
                                 closest_free_MEC])
                        # 排序
                        self.insertion_sort(self.task_priority_queues)

        # 檢查是否所有任務都已成功執行
        assert all(status == True for status in self.all_task_status.values()), "有任務未能成功執行"

        # 系統執行完所有任務實際經過的時間
        with data_lock:
            time_line = max(device_execute_time_line.values()) + 1

        # 計算平均執行時間
        average_task_complete_time = self.total_task_execute_time / self.total_tasks
        # 計算平均任務時延
        average_task_delay_time = self.total_task_delay_time / self.total_tasks
        global all_device_execute_data
        with data_lock:
            all_device_execute_data[self.wd_node] = {"total_task_execute_time": self.total_task_execute_time,
                                                     "average_task_complete_time": average_task_complete_time,
                                                     "average_task_delay_time": average_task_delay_time,
                                                     "task_delay_from": self.device_task_delay_form}
        print(self.wd_node + "完成任务")
