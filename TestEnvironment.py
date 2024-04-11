import networkx as nx
import numpy as np
import random
import math
import matplotlib.pyplot as plt

from Calculator import Calculator
from MECSystemGenerator import MECSystemGenerator
from Migration.EfficiencyGreedyExecute import EfficiencyGreedyExecute
from Migration.LocalExecute import LocalExecute
from TaskDAGGenerator import TaskDAGGenerator


# 在此進行不同環境不同迁移算法的測試，並生成數據
class TestEnvironment:
    def __init__(self):
        self.WD_count_scope = [1, 1]
        self.MEC_count_scope = [1, 5]

    def local_execute(self, times):
        mecSystemGenerator = MECSystemGenerator()
        taskDAGGenerator = TaskDAGGenerator()

        total_response_times = []  # 存儲每次測試的總任務加權響應時間
        avg_task_delays = []  # 存儲每次測試的平均任務時延
        task_delays_form_list = []

        for i in range(times):
            print("#########生成MEC系統拓樸中#########")
            wd_count = random.randint(self.WD_count_scope[0], self.WD_count_scope[1])
            mecSystem = mecSystemGenerator.generateMEC(wd_count, random.randint(self.MEC_count_scope[0],
                                                                                self.MEC_count_scope[1]))

            print("#########生成任務DAG圖中#########")
            edges, into_degree, out_degree, position = taskDAGGenerator.DAG_generate()
            taskGraph = taskDAGGenerator.transform_networkx_DAG(position, edges)

            print("##########本地執行仿真測試##########")
            localExecute = LocalExecute()
            total_task_complete_time, average_task_complete_time, average_task_delay_time, task_delay_form = localExecute.run(
                'WD0', mecSystem, taskGraph)
            avg_task_delays.append(average_task_delay_time)
            total_response_times.append(average_task_complete_time)
            task_delays_form_list.append(task_delay_form.values())

            # 輸出每次測試的結果
            print(f"測試 {i + 1}:")
            print(f"總任務執行時間: {total_task_complete_time}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()

        plt.figure(figsize=(12, 6))

        for i, line_data in enumerate(task_delays_form_list):
            x = range(len(line_data))
            y = line_data
            plt.plot(x, y, color='black', label=f'Line {i + 1}')
        #plt.plot(range(len(task_delays_form_list[0])), task_delays_form_list[0], color='black', label=f'Line {i + 1}')
        plt.xlabel('task')
        plt.ylabel('delay_time')
        plt.title('Multiple Lines Chart')
        plt.legend()
        plt.grid(True)
        plt.savefig('./Image/折線圖.png')
        plt.show()

        return total_response_times, avg_task_delays

    def efficiency_greedy_execute(self, times):
        mecSystemGenerator = MECSystemGenerator()
        taskDAGGenerator = TaskDAGGenerator()

        total_response_times = []  # 存儲每次測試的總任務加權響應時間
        avg_task_delays = []  # 存儲每次測試的平均任務時延

        for i in range(times):
            print("#########生成MEC系統拓樸中#########")
            wd_count = random.randint(self.WD_count_scope[0], self.WD_count_scope[1])
            mec_count = random.randint(self.MEC_count_scope[0], self.MEC_count_scope[1])
            mecSystem = mecSystemGenerator.generateMEC(wd_count, mec_count)

            print("#########生成任務DAG圖中#########")
            edges, into_degree, out_degree, position = taskDAGGenerator.DAG_generate()
            taskGraph = taskDAGGenerator.transform_networkx_DAG(position, edges)

            print("##########本地執行仿真測試##########")
            greedyExecuter = EfficiencyGreedyExecute()
            total_task_execute_time, time_line, average_task_complete_time, total_task_delay_time, average_task_delay_time, task_delay_form = greedyExecuter.run(
                wd_count, mec_count, mecSystem, taskGraph)
            avg_task_delays.append(average_task_delay_time)
            total_response_times.append(average_task_complete_time)

            # 輸出每次測試的結果
            print(f"測試 {i + 1}:")
            print(f"所有任務執行需時: {total_task_execute_time}")
            print(f"系統執行完任務經過的實際時間: {time_line}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()

        return total_response_times, avg_task_delays

    def execute_task(self, task_id, on_mec=True):
        # 根據任務ID和是否在MEC上執行來更新任務狀態
        pass

    def update_environment(self):
        # 根據當前任務狀態和MEC系統狀態更新環境
        pass


if __name__ == '__main__':
    testEnvironment = TestEnvironment()
    testEnvironment.efficiency_greedy_execute(10)
    #testEnvironment.local_execute(10)
