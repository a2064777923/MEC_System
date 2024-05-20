import math

import random


import networkx as nx


class Calculator:
    MECGraph = nx.DiGraph()
    taskGraph = nx.DiGraph()

    def __init__(self, MECG, taskG):
        self.MECGraph = MECG
        self.taskGraph = taskG
        for node in self.MECGraph.nodes:
            if node != 'Start' and node != 'Exit':
                self.MECGraph.nodes[node]['task_queue'] = []

    # 本地計算時延，返回任務在該設備上需要執行的微秒數
    def LOCAL_CALCULATION_DELAY(self, task, WD_no):
        cycles = self.taskGraph.nodes[task]["Cycles"] * self.taskGraph.nodes[task]["DataIn"] * 8 * 1024  # KB轉bits
        WDcFrequency = self.MECGraph.nodes[WD_no]["labels"]["calculation"]  # 因為單位是Ghz，需進行轉換
        WDcFrequency *= math.pow(10, 9)
        return (cycles / WDcFrequency) * 1000  # s轉ms

    # MEC時延，計算時延+傳輸時延
    def MEC_CALCULATION_DELAY(self, task, WD_no, MEC_no):
        dataIn = self.taskGraph.nodes[task]["DataIn"] * 8 * 1024  # KB轉bits
        cycles = self.taskGraph.nodes[task]["Cycles"] * dataIn
        MECcFrequency = self.MECGraph.nodes[MEC_no]["labels"]["calculation"]
        MECcFrequency *= math.pow(10, 9)
        edge_data = self.MECGraph.get_edge_data(WD_no, MEC_no)

        maxTSpeed = 0
        transportTime = 0
        if edge_data is None:
            neighbors = list(self.MECGraph.neighbors(WD_no))  # 若服務器节点與移動設備沒有直接信道連接，需要由最近的服務器轉發
            sorted_neighbors = sorted(neighbors, key=lambda x: self.MECGraph.edges[WD_no, x]["labels"]['distance'])
            min_distance_node = sorted_neighbors[0]
            edge_data_w_m = self.MECGraph.get_edge_data(WD_no, min_distance_node)
            edge_data_m1_m2 = self.MECGraph.get_edge_data(min_distance_node, MEC_no)
            transportTime1 = dataIn / (edge_data_w_m["labels"]["maxTransmissionSpeed"] * 1024 * 1024 * 8)
            transportTime2 = dataIn / (edge_data_m1_m2["labels"]["maxTransmissionSpeed"] * 1024 * 1024 * 8)
            maxTSpeed = edge_data_w_m["labels"]["maxTransmissionSpeed"] * 1024 * 1024 * 8
            transportTime = transportTime1 + transportTime2
            transportTime *= 1000
        else:
            maxTSpeed = edge_data["labels"]["maxTransmissionSpeed"] * 1024 * 1024 * 8  # MB/s轉bits/s

            transportTime = dataIn / maxTSpeed * 1000

        return (cycles / MECcFrequency) * 1000 + transportTime  # s轉ms


    # 任務結果回傳時間
    def TASK_TRANSPORT_BACK_TIME(self, task, from_device, MEC_no):
        dataIn = random.uniform(self.taskGraph.nodes[task]["DataIn"]/20, self.taskGraph.nodes[task]["DataIn"]/5) * 8 * 1024  # KB轉bits

        edge_data = self.MECGraph.get_edge_data(from_device, MEC_no)
        transportTime = 0
        if edge_data is None:
            neighbors = list(self.MECGraph.neighbors(from_device))  # 若服務器节点與移動設備沒有直接信道連接，需要由最近的服務器轉發
            sorted_neighbors = sorted(neighbors, key=lambda x: self.MECGraph.edges[from_device, x]["labels"]['distance'])
            min_distance_node = sorted_neighbors[0]
            edge_data_w_m = self.MECGraph.get_edge_data(from_device, min_distance_node)
            edge_data_m1_m2 = self.MECGraph.get_edge_data(min_distance_node, MEC_no)
            transportTime1 = dataIn / (edge_data_w_m["labels"]["maxTransmissionSpeed"] * 1024 * 1024 * 8)
            transportTime2 = dataIn / (edge_data_m1_m2["labels"]["maxTransmissionSpeed"] * 1024 * 1024 * 8)
            transportTime = transportTime1 + transportTime2
            transportTime *= 1000
        else:
            maxTSpeed = edge_data["labels"]["maxTransmissionSpeed"] * 1024 * 1024 * 8  # MB/s轉bits/s
            transportTime = dataIn / maxTSpeed * 1000

        return transportTime  # s轉ms

    # 計算計算通信比CVR
    def CALCULATE_CVR(self, task, WD_no, MEC_no):
        dataIn = self.taskGraph.nodes[task]["DataIn"] * 8 * 1024  # KB轉bits
        cycles = self.taskGraph.nodes[task]["Cycles"] * dataIn
        MECcFrequency = self.MECGraph.nodes[MEC_no]["labels"]["calculation"]
        MECcFrequency *= math.pow(10, 9)
        edge_data = self.MECGraph.get_edge_data(WD_no, MEC_no)


        if edge_data is None:
            neighbors = list(self.MECGraph.neighbors(WD_no))  # 若服務器节点與移動設備沒有直接信道連接，需要由最近的服務器轉發
            sorted_neighbors = sorted(neighbors, key=lambda x: self.MECGraph.edges[WD_no, x]["labels"]['distance'])
            min_distance_node = sorted_neighbors[0]
            edge_data_w_m = self.MECGraph.get_edge_data(WD_no, min_distance_node)
            edge_data_m1_m2 = self.MECGraph.get_edge_data(min_distance_node, MEC_no)
            transportTime1 = dataIn / (edge_data_w_m["labels"]["maxTransmissionSpeed"] * 1024 * 1024 * 8)
            transportTime2 = dataIn / (edge_data_m1_m2["labels"]["maxTransmissionSpeed"] * 1024 * 1024 * 8)
            transportTime = transportTime1 + transportTime2
            transportTime *= 1000
        else:
            maxTSpeed = edge_data["labels"]["maxTransmissionSpeed"] * 1024 * 1024 * 8  # MB/s轉bits/s
            transportTime = dataIn / maxTSpeed * 1000

        return (cycles / MECcFrequency) / transportTime


    def updateActualFinishTime(self, task, ActualFinishTime):
        self.taskGraph.nodes[task]["actualFinishTime"] = ActualFinishTime

    # 任務的就緒時間為所有前驅任務的實際執行時間中取最大值
    def TASK_READY_TIME(self, task):
        predecessors = self.taskGraph.predecessors(task)
        # 初始化最大值為負無窮
        max_actual_finish_time = float('-inf')

        # 找到所有前驅節點中"actualFinishTime"標籤的最大值
        for predecessor in predecessors:
            if predecessor == 'Start':
                return 0
            actual_finish_time = self.taskGraph.nodes[predecessor]['actualFinishTime']
            if actual_finish_time > max_actual_finish_time:
                max_actual_finish_time = actual_finish_time
        self.taskGraph.nodes[task]["readyTime"] = max_actual_finish_time
        return max_actual_finish_time

    # 任務最早可被計算單元執行的時間，為任務就緒時間及計算單元空閒時間的最大值
    def EARLIEST_EXECUTABLE_TIME(self, processUnit, task):
        availableTime = sum(self.MECGraph.nodes[processUnit]["task_queue"])
        EarliestExecutableTime = max(availableTime, self.taskGraph.nodes[task]["readyTime"])
        return EarliestExecutableTime

    def MAX_TOLERANCE_DELAY(self, task, processUnit):

        # 定義遞歸函數來計算最大容忍時延
        def recursive_delay_calculation(current_task):
            # 如果當前任務是Exit，直接返回
            if current_task == 'Exit':
                return current_task, 0
            # 獲取當前任務的所有後繼任務
            successors = list(self.taskGraph.successors(current_task))
            # 如果沒有後繼任務，表示當前任務是出口任務，返回其最大容忍時延
            if successors[0] == 'Exit':
                return successors[0], self.taskGraph.nodes[current_task]['MaxDelayTime']
            # 遍歷所有後繼任務，遞歸計算最大容忍時延
            max_delay = 0
            max_delay_successor = task
            for successor in successors:
                successor_max_delay_successor, successor_max_delay = recursive_delay_calculation(successor)
                successor_delay = successor_max_delay - self.LOCAL_CALCULATION_DELAY(task, processUnit)
                self.taskGraph.nodes[successor]['MaxDelayTime'] = successor_delay
                if successor_delay > max_delay:
                    max_delay_successor = successor
                max_delay = max(max_delay, successor_delay)

            return max_delay_successor, max_delay

        # 從指定的任務開始計算最大容忍時延
        max_delay_successor, max_delay = recursive_delay_calculation(task)

        return max_delay - self.LOCAL_CALCULATION_DELAY(max_delay_successor, processUnit)
