import heapq
import math
from collections import deque

from Calculator import Calculator


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

    def run(self, WD_num, MEC_num, mecSystem, taskGraph):
        calculator = Calculator(mecSystem, taskGraph)
        self.calculator = calculator
        task_status = {task: False for task in taskGraph.nodes if task not in ["Start", "Exit"]}
        total_tasks = len(task_status)
        device_execute_time_line = {device: 0 for device in mecSystem.nodes()}  # 每個設備執行了多長時間

        total_task_execute_time = 0
        total_task_delay_time = 0
        task_delay_form = {}

        task_priority_queue = deque()
        time_line = 0

        wd_node = "WD0"

        # 最近的空閒MEC
        closest_free_MEC = self.find_closest_free_MEC(mecSystem, wd_node, device_execute_time_line)

        # 將起始任務加入優先級隊列
        start_successors = list(taskGraph.successors("Start"))
        for successor in start_successors:
            if successor == 'Exit':
                continue
            # 用雙端隊列儲存CVR
            # 隊列元素:(CVR,元素,MEC服務器)
            task_priority_queue.append(
                [calculator.CALCULATE_CVR(successor, wd_node, closest_free_MEC), successor, closest_free_MEC])
        # 排序
        self.insertion_sort(task_priority_queue)

        while task_priority_queue:
            time_line = min(device_execute_time_line.values())
            if math.floor(device_execute_time_line[wd_node]) <= time_line:  # 本地設備空閒
                min_CVR = task_priority_queue.popleft()
                task_execute_time = calculator.LOCAL_CALCULATION_DELAY(min_CVR[1], wd_node)
                # 更新任務執行時間
                device_execute_time_line[wd_node] += task_execute_time
                total_task_execute_time += task_execute_time
                # 標記當前任務為已執行
                task_status[min_CVR[1]] = True

                # 更新任務的實際完成時間
                calculator.updateActualFinishTime(min_CVR[1], device_execute_time_line[wd_node])
                # 任務的完成時間減去任務的就緒時間，為任務延迟了多久才被執行
                task_delay_time = device_execute_time_line[wd_node] - calculator.TASK_READY_TIME(min_CVR[1])
                total_task_delay_time += task_delay_time
                task_delay_form[min_CVR[1]] = task_delay_time

                # 更新後繼任務的CVR並加入隊列
                for successor in taskGraph.successors(min_CVR[1]):
                    if successor == 'Exit':
                        continue
                    if all(task_status[predecessor] for predecessor in taskGraph.predecessors(successor)):
                        closest_free_MEC = self.find_closest_free_MEC(mecSystem, wd_node, device_execute_time_line)
                        task_priority_queue = self.count_and_sort_CVR(task_priority_queue, wd_node,
                                                                           closest_free_MEC)
                        task_priority_queue.append(
                            [calculator.CALCULATE_CVR(successor, wd_node, closest_free_MEC), successor,
                             closest_free_MEC])

                # 排序
                self.insertion_sort(task_priority_queue)
            else:
                for mec, time in device_execute_time_line.items():
                    if math.floor(time) <= time_line and "WD" not in mec:
                        # 用这空閒MVC重排CVR
                        self.count_and_sort_CVR(task_priority_queue, wd_node, mec)
                        max_CVR = task_priority_queue.pop()
                        task_execute_time = calculator.MEC_CALCULATION_DELAY(max_CVR[1], wd_node, mec)
                        # 更新任務執行時間
                        device_execute_time_line[mec] += task_execute_time
                        total_task_execute_time += task_execute_time
                        # 標記當前任務為已執行
                        task_status[max_CVR[1]] = True

                        # 更新任務的實際完成時間
                        calculator.updateActualFinishTime(max_CVR[1], device_execute_time_line[wd_node])
                        # 任務的完成時間減去任務的就緒時間，為任務延迟了多久才被執行
                        task_delay_time = device_execute_time_line[mec] - calculator.TASK_READY_TIME(max_CVR[1])
                        total_task_delay_time += task_delay_time
                        task_delay_form[max_CVR[1]] = task_delay_time

                        # 更新後繼任務的CVR並加入隊列
                        for successor in taskGraph.successors(max_CVR[1]):
                            if successor == 'Exit':
                                continue
                            if all(task_status[predecessor] for predecessor in taskGraph.predecessors(successor)):
                                closest_free_MEC = self.find_closest_free_MEC(mecSystem, wd_node,
                                                                              device_execute_time_line)
                                task_priority_queue = self.count_and_sort_CVR(task_priority_queue, wd_node,
                                                                                   closest_free_MEC)
                                task_priority_queue.append(
                                    [calculator.CALCULATE_CVR(successor, wd_node, closest_free_MEC), successor,
                                     closest_free_MEC])
                        # 排序
                        self.insertion_sort(task_priority_queue)

        # 檢查是否所有任務都已成功執行
        assert all(status == True for status in task_status.values()), "有任務未能成功執行"

        #系統執行完所有任務實際經過的時間
        time_line = max(device_execute_time_line.values())
        # 計算平均執行時間
        average_task_complete_time = total_task_execute_time / total_tasks
        # 計算平均任務時延
        average_task_delay_time = total_task_delay_time / total_tasks

        return total_task_execute_time, time_line, average_task_complete_time,total_task_delay_time,average_task_delay_time,task_delay_form
