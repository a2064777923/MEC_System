
import time

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
        self.WD_count_scope = [1, 3]
        self.MEC_count_scope = [1, 6]

    # 設定次數的隨機測試
    def local_execute(self, times,taskDAG_nodes = -1):

        mecSystemGenerator = MECSystemGenerator()
        taskDAGGenerator = TaskDAGGenerator()

        total_response_times = []  # 存儲每次測試的總任務加權響應時間
        avg_task_delays = []  # 存儲每次測試的平均任務時延
        task_delays_form_list = []

        for i in range(times):
            print("#########生成MEC系統拓樸中#########")
            wd_count = 1
            mecSystem = mecSystemGenerator.generateMEC(wd_count, random.randint(self.MEC_count_scope[0],
                                                                                self.MEC_count_scope[1]))

            print("#########生成任務DAG圖中#########")
            if taskDAG_nodes != -1:
                size,edges, into_degree, out_degree, position = taskDAGGenerator.DAG_generate(mode = "local", size= taskDAG_nodes)
            else:
                size,edges, into_degree, out_degree, position = taskDAGGenerator.DAG_generate()
            taskGraph = taskDAGGenerator.transform_networkx_DAG(size, position, edges)

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

        plt.rcParams['font.family'] = 'SimHei'
        plt.figure(figsize=(12, 6))

        for i, line_data in enumerate(task_delays_form_list):
            x = range(len(line_data))


            y = line_data
            plt.plot(x, y, color='black', label=f'Line {i + 1}')

        #plt.plot(range(len(task_delays_form_list[0])), task_delays_form_list[0], color='black', label=f'Line {i + 1}')

        #all_delays = [delay for sublist in task_delays_form_list for delay in sublist]
        #plt.hist(all_delays, bins=10, alpha=0.75, color='blue', edgecolor='black')

        # 添加标题和标题
        plt.xlabel('任务序号')
        plt.ylabel('单个任务从就绪到被执行完成的时间(ms)')
        plt.title('Local算法的一次隨机测试结果')
        plt.legend()
        plt.grid(True)
        plt.savefig('./Image/Local算法的一次隨机测试结果.png')
        plt.show()

        return total_response_times, avg_task_delays

    def local_efficiency_taskNum_sum_time(self, wd_count, mec_count):
        mecSystemGenerator = MECSystemGenerator()
        taskDAGGenerator = TaskDAGGenerator()

        local_total_application_execute_time = []  # wd应用的总执行时间
        efficiency_total_application_execute_time = [] #效率貪婪時應用的總執行時間
        avg_task_delays = []  # 存儲每次測試的平均任務時延
        task_delays_form_list = []
        taskGraphDict = {}
        print("#########生成MEC系統拓樸中#########")
        mecSystem = mecSystemGenerator.generateMEC(wd_count, mec_count)

        print("#########生成任務DAG圖中#########")
        taskGraphDict = {}

        for round_size in range(10, 81):
            for j in range(wd_count):
                print("#########生成任務DAG圖中#########")
                while True:
                    try:
                        nums, edges, into_degree, out_degree, position = taskDAGGenerator.DAG_generate(mode="size",
                                                                                                       size=round_size,
                                                                                                       alpha=1.0, beta=1.0)
                        taskGraph = taskDAGGenerator.transform_networkx_DAG(nums, position, edges)
                        wd_no = "WD" + str(j)
                        taskGraphDict[wd_no] = taskGraph
                        break  # 成功生成后跳出重试循环
                    except ValueError as e:
                        print(f"发生错误：{e}")
                        j -= 1

            print("##########本地執行仿真測試##########")
            localExecute = LocalExecute()
            total_task_complete_time, average_task_complete_time, average_task_delay_time, task_delay_form = localExecute.run(
                'WD0', mecSystem, taskGraphDict["WD0"])
            avg_task_delays.append(average_task_delay_time)
            local_total_application_execute_time.append(total_task_complete_time)
            task_delays_form_list.append(task_delay_form.values())

            # 輸出每次測試的結果
            print(f"本地算法測試 {round_size}:")
            print(f"總任務執行時間: {total_task_complete_time}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()




            print("##########效率貪婪仿真測試##########")
            greedyExecuter = EfficiencyGreedyExecute()
            total_task_execute_time, time_line, average_task_complete_time, total_task_delay_time, average_task_delay_time, task_delay_form = greedyExecuter.run(
                wd_count, mec_count, mecSystem, taskGraphDict)
            avg_task_delays.append(average_task_delay_time)
            efficiency_total_application_execute_time.append(time_line)
            task_delays_form_list.append(task_delay_form.values())

            # 輸出每次測試的結果
            print(f"測試DAG_size {round_size}:")
            print(f"所有任務執行需時: {total_task_execute_time}")
            print(f"系統執行完任務經過的實際時間: {time_line}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()

        plt.rcParams['font.family'] = 'SimHei'
        dag_nodes = list(range(10, 90, 10))

        local_interp_y = np.interp(dag_nodes, np.arange(1, len(local_total_application_execute_time) + 1),
                                   local_total_application_execute_time)
        efficiency_interp_y = np.interp(dag_nodes, np.arange(1, len(efficiency_total_application_execute_time) + 1),
                                        efficiency_total_application_execute_time)
        # 绘制折线图
        plt.figure(figsize=(10, 6))  # 设置图表大小
        plt.plot(dag_nodes, local_interp_y, 'b-', marker='o',
                 label='Local算法')  # 平均執行時間用藍色線表示
        plt.plot(dag_nodes, efficiency_interp_y, 'r-', marker='s', label='效率贪婪算法')  # 平均時延用紅色線表示

        # 添加图表标题和坐标轴标签
        plt.title('兩种算法下应用总完成时间隨任务节点数量的变化')
        plt.xlabel('任务节点数')
        plt.ylabel('时间 (ms)')

        # 显示图例
        plt.legend()

        # 显示网格
        plt.grid(True)

        # 保存图表到文件
        plt.savefig('./Image/Local_Efficiency_Performance_Analysis.png')

        # 显示图表
        plt.show()


    def local_efficiency_taskNum_average_delay(self, wd_count, mec_count):
        mecSystemGenerator = MECSystemGenerator()
        taskDAGGenerator = TaskDAGGenerator()

        local_total_application_average_execute_time = []  # wd应用的总执行时间
        efficiency_total_application_average_execute_time = [] #效率貪婪時應用的總執行時間
        avg_task_delays = []  # 存儲每次測試的平均任務時延
        task_delays_form_list = []
        taskGraphDict = {}
        print("#########生成MEC系統拓樸中#########")
        mecSystem = mecSystemGenerator.generateMEC(wd_count, mec_count)

        print("#########生成任務DAG圖中#########")
        taskGraphDict = {}

        for round_size in range(10, 90, 10):
            for j in range(wd_count):
                print("#########生成任務DAG圖中#########")
                nums, edges, into_degree, out_degree, position = taskDAGGenerator.DAG_generate(mode="size",
                                                                                               size=round_size,
                                                                                               alpha=1.0, beta=1.0)
                taskGraph = taskDAGGenerator.transform_networkx_DAG(nums, position, edges)
                wd_no = "WD" + str(j)
                taskGraphDict[wd_no] = taskGraph

            print("##########本地執行仿真測試##########")
            localExecute = LocalExecute()
            total_task_complete_time, average_task_complete_time, average_task_delay_time, task_delay_form = localExecute.run(
                'WD0', mecSystem, taskGraphDict["WD0"])
            avg_task_delays.append(average_task_delay_time)
            local_total_application_average_execute_time.append(average_task_delay_time)
            task_delays_form_list.append(task_delay_form.values())

            # 輸出每次測試的結果
            print(f"本地算法測試 {round_size}:")
            print(f"總任務執行時間: {total_task_complete_time}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()




            print("##########效率貪婪仿真測試##########")
            greedyExecuter = EfficiencyGreedyExecute()
            total_task_execute_time, time_line, average_task_complete_time, total_task_delay_time, average_task_delay_time, task_delay_form = greedyExecuter.run(
                wd_count, mec_count, mecSystem, taskGraphDict)
            avg_task_delays.append(average_task_delay_time)
            efficiency_total_application_average_execute_time.append(average_task_delay_time)
            task_delays_form_list.append(task_delay_form.values())

            # 輸出每次測試的結果
            print(f"測試DAG_size {round_size}:")
            print(f"所有任務執行需時: {total_task_execute_time}")
            print(f"系統執行完任務經過的實際時間: {time_line}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()

        plt.rcParams['font.family'] = 'SimHei'
        dag_nodes = list(range(10, 90, 10))
        # 绘制折线图
        plt.figure(figsize=(10, 6))  # 设置图表大小
        plt.plot(dag_nodes, local_total_application_average_execute_time, 'b-', marker='o',
                 label='Local算法')  # 平均執行時間用藍色線表示
        plt.plot(dag_nodes, efficiency_total_application_average_execute_time, 'r-', marker='s', label='效率贪婪算法')  # 平均時延用紅色線表示

        # 添加图表标题和坐标轴标签
        plt.title('兩种算法下任务平均时延隨任务节点数量的变化')
        plt.xlabel('任务节点数')
        plt.ylabel('时间 (ms)')

        # 显示图例
        plt.legend()

        # 显示网格
        plt.grid(True)

        # 保存图表到文件
        plt.savefig('./Image/Local_Efficiency_average_delay_Analysis.png')

        # 显示图表
        plt.show()

    def local_efficiency_DAG_density(self, wd_count, mec_count):
        mecSystemGenerator = MECSystemGenerator()
        taskDAGGenerator = TaskDAGGenerator()

        local_total_execute_time = []
        efficiency_total_execute_time = []
        local_total_application_average_execute_time = []  # wd任務平均执行时间
        efficiency_total_application_average_execute_time = [] #效率貪婪時應用的總執行時間
        avg_task_delays = []  # 存儲每次測試的平均任務時延
        task_delays_form_list = []
        taskGraphDict = {}
        print("#########生成MEC系統拓樸中#########")
        mecSystem = mecSystemGenerator.generateMEC(wd_count, mec_count)

        print("#########生成任務DAG圖中#########")
        taskGraphDict = {}

        for density in range(5,21):
            for j in range(wd_count):
                print("#########生成任務DAG圖中#########")
                nums, edges, into_degree, out_degree, position = taskDAGGenerator.DAG_generate(mode="size",
                                                                                               size= 60,
                                                                                               max_out= 4,
                                                                                               alpha= density/10.0 , beta=1.0)
                taskGraph = taskDAGGenerator.transform_networkx_DAG(nums, position, edges)
                wd_no = "WD" + str(j)
                taskGraphDict[wd_no] = taskGraph

            print("##########本地執行仿真測試##########")
            localExecute = LocalExecute()
            total_task_complete_time, average_task_complete_time, average_task_delay_time, task_delay_form = localExecute.run(
                'WD0', mecSystem, taskGraphDict["WD0"])
            avg_task_delays.append(average_task_delay_time)
            local_total_application_average_execute_time.append(average_task_delay_time)
            task_delays_form_list.append(task_delay_form.values())
            local_total_execute_time.append(total_task_complete_time)

            # 輸出每次測試的結果
            print(f"本地算法測試 {density/10.0}:")
            print(f"總任務執行時間: {total_task_complete_time}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()




            print("##########效率貪婪仿真測試##########")
            greedyExecuter = EfficiencyGreedyExecute()
            total_task_execute_time, time_line, average_task_complete_time, total_task_delay_time, average_task_delay_time, task_delay_form = greedyExecuter.run(
                wd_count, mec_count, mecSystem, taskGraphDict)
            avg_task_delays.append(average_task_delay_time)
            efficiency_total_application_average_execute_time.append(average_task_delay_time)
            task_delays_form_list.append(task_delay_form.values())
            efficiency_total_execute_time.append(time_line)

            # 輸出每次測試的結果
            print(f"測試DAG_size {density/10.0}:")
            print(f"所有任務執行需時: {total_task_execute_time}")
            print(f"系統執行完任務經過的實際時間: {time_line}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()

        plt.rcParams['font.family'] = 'SimHei'
        dag_nodes = list(i/10.0 for i in range(5, 21))
        # 绘制折线图
        plt.figure(figsize=(10, 6))  # 设置图表大小
        plt.plot(dag_nodes, local_total_application_average_execute_time, 'b-', marker='o',
                 label='Local算法')  # 平均執行時間用藍色線表示
        plt.plot(dag_nodes, efficiency_total_application_average_execute_time, 'r-', marker='s', label='效率贪婪算法')  # 平均時延用紅色線表示

        # 添加图表标题和坐标轴标签
        plt.title('兩种算法下任务平均时延隨任务图密度的变化')
        plt.xlabel('DAG图密度')
        plt.ylabel('时间 (ms)')

        # 显示图例
        plt.legend()

        # 显示网格
        plt.grid(True)

        # 保存图表到文件
        plt.savefig('./Image/Local_Efficiency_DAG_density_delay_Analysis.png')

        # 显示图表
        plt.show()

        time.sleep(5)
        plt.close()

        dag_nodes = list(i / 10.0 for i in range(5, 21))
        # 绘制折线图
        plt.figure(figsize=(10, 6))  # 设置图表大小
        plt.plot(dag_nodes, local_total_execute_time, 'b-', marker='o',
                 label='Local算法')  # 平均執行時間用藍色線表示
        plt.plot(dag_nodes, efficiency_total_execute_time, 'r-', marker='s',
                 label='效率贪婪算法')  # 平均時延用紅色線表示

        # 添加图表标题和坐标轴标签
        plt.title('兩种算法下应用完成时间隨任务图密度的变化')
        plt.xlabel('DAG图密度')
        plt.ylabel('时间 (ms)')

        # 显示图例
        plt.legend()

        # 显示网格
        plt.grid(True)

        # 保存图表到文件
        plt.savefig('./Image/Local_Efficiency_totalTime_DAG_density.png')

    def local_efficiency_channel_bandwidth(self, wd_count, mec_count):
        mecSystemGenerator = MECSystemGenerator()
        taskDAGGenerator = TaskDAGGenerator()

        local_total_application_average_execute_time = []  # wd应用的总执行时间
        efficiency_total_application_average_execute_time = [] #效率貪婪時應用的總執行時間
        avg_task_delays = []  # 存儲每次測試的平均任務時延
        task_delays_form_list = []
        taskGraphDict = {}


        print("#########生成任務DAG圖中#########")
        taskGraphDict = {}
        for j in range(wd_count):
            print("#########生成任務DAG圖中#########")
            nums, edges, into_degree, out_degree, position = taskDAGGenerator.DAG_generate(mode="size",
                                                                                           size=60,
                                                                                           alpha= 1.0,
                                                                                           beta=1.0)
            taskGraph = taskDAGGenerator.transform_networkx_DAG(nums, position, edges)
            wd_no = "WD" + str(j)
            taskGraphDict[wd_no] = taskGraph
            mecSystem = mecSystemGenerator.generateMEC(wd_count, mec_count)

        for transportSpeed in range(100,6 * 1024, 200):
            print("#########生成MEC系統拓樸中#########")
            mecSystemGenerator.change_MAX_SPEED(mecSystem,transportSpeed/1024)


            print("##########本地執行仿真測試##########")
            localExecute = LocalExecute()
            total_task_complete_time, average_task_complete_time, average_task_delay_time, task_delay_form = localExecute.run(
                'WD0', mecSystem, taskGraphDict["WD0"])
            avg_task_delays.append(average_task_delay_time)
            local_total_application_average_execute_time.append(total_task_complete_time)
            task_delays_form_list.append(task_delay_form.values())

            # 輸出每次測試的結果
            print(f"本地算法測試，帶寛: {transportSpeed}:")
            print(f"總任務執行時間: {total_task_complete_time}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()




            print("##########效率貪婪仿真測試##########")
            greedyExecuter = EfficiencyGreedyExecute()
            total_task_execute_time, time_line, average_task_complete_time, total_task_delay_time, average_task_delay_time, task_delay_form = greedyExecuter.run(
                wd_count, mec_count, mecSystem, taskGraphDict)
            avg_task_delays.append(average_task_delay_time)
            efficiency_total_application_average_execute_time.append(time_line)
            task_delays_form_list.append(task_delay_form.values())

            # 輸出每次測試的結果
            print(f"測試帶寛: {transportSpeed}:")
            print(f"所有任務執行需時: {total_task_execute_time}")
            print(f"系統執行完任務經過的實際時間: {time_line}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()

        plt.rcParams['font.family'] = 'SimHei'
        dag_nodes = list(range(100,6 * 1024, 200))

        local_interp_y = np.interp(dag_nodes, np.arange(1, len(local_total_application_average_execute_time) + 1),
                                   local_total_application_average_execute_time)
        efficiency_interp_y = np.interp(dag_nodes, np.arange(1, len(efficiency_total_application_average_execute_time) + 1),
                                        efficiency_total_application_average_execute_time)
        # 绘制折线图
        plt.figure(figsize=(10, 6))  # 设置图表大小
        plt.plot(dag_nodes, local_interp_y, 'b-', marker='o',
                 label='Local算法')  # 平均執行時間用藍色線表示
        plt.plot(dag_nodes, efficiency_total_application_average_execute_time, 'r-', marker='s', label='效率贪婪算法')  # 平均時延用紅色線表示

        # 添加图表标题和坐标轴标签
        plt.title('兩种算法下应用完成时间隨网络传输速率的变化')
        plt.xlabel('网络传输速率(KB/s)')
        plt.ylabel('时间 (ms)')

        # 显示图例
        plt.legend()

        # 显示网格
        plt.grid(True)

        # 保存图表到文件
        plt.savefig('./Image/Local_Efficiency_speed_delay_Analysis.png')

        # 显示图表
        plt.show()


    def efficiency_greedy_execute_taskNum_delay(self,  wd_count, mec_count):
        mecSystemGenerator = MECSystemGenerator()
        taskDAGGenerator = TaskDAGGenerator()

        total_average_execute_times = []  # 存儲每次測試的任務平均執行時間
        avg_task_delays = []  # 存儲每次測試的平均任務時延
        task_delays_form_list = []


        taskGraphDict = {}
        print("#########生成MEC系統拓樸中#########")
        mecSystem = mecSystemGenerator.generateMEC(wd_count, mec_count)
        for round_size in range(10,90,10):
            for j in range(wd_count):
                print("#########生成任務DAG圖中#########")
                nums, edges, into_degree, out_degree, position = taskDAGGenerator.DAG_generate(mode="size",size=round_size, alpha=1.0, beta=1.0)
                taskGraph = taskDAGGenerator.transform_networkx_DAG(nums,position, edges)
                wd_no = "WD" + str(j)
                taskGraphDict[wd_no] = taskGraph

            print("##########本地執行仿真測試##########")
            greedyExecuter = EfficiencyGreedyExecute()
            total_task_execute_time, time_line, average_task_complete_time, total_task_delay_time, average_task_delay_time, task_delay_form = greedyExecuter.run(
                wd_count, mec_count, mecSystem, taskGraphDict)
            avg_task_delays.append(average_task_delay_time)
            total_average_execute_times.append(average_task_complete_time)
            task_delays_form_list.append(task_delay_form.values())

            # 輸出每次測試的結果
            print(f"測試DAG_size {round_size}:")
            print(f"所有任務執行需時: {total_task_execute_time}")
            print(f"系統執行完任務經過的實際時間: {time_line}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()

        plt.rcParams['font.family'] = 'SimHei'
        dag_nodes = list(range(10,90,10))
        # 绘制折线图
        plt.figure(figsize=(10, 6))  # 设置图表大小
        plt.plot(dag_nodes, total_average_execute_times, 'b-', marker='o',
                 label='任务平均执行时间')  # 平均執行時間用藍色線表示
        plt.plot(dag_nodes, avg_task_delays, 'r-', marker='s', label='任务平均时延')  # 平均時延用紅色線表示

        # 添加图表标题和坐标轴标签
        plt.title("效率贪婪算法任务平均执行时间和时延隨任务节点数量的变化")
        plt.xlabel('任务节点数')
        plt.ylabel('时间 (ms)')

        # 显示图例
        plt.legend()

        # 显示网格
        plt.grid(True)

        # 保存图表到文件
        plt.savefig('./Image/DAG_Size_Performance_Analysis.png')

        # 显示图表
        plt.show()

        return total_average_execute_times, avg_task_delays


    def efficiency_greedy_execute(self, times):
        mecSystemGenerator = MECSystemGenerator()
        taskDAGGenerator = TaskDAGGenerator()

        total_response_times = []  # 存儲每次測試的總任務加權響應時間
        avg_task_delays = []  # 存儲每次測試的平均任務時延
        task_delays_form_list = []

        for i in range(times):
            taskGraphDict = {}
            print("#########生成MEC系統拓樸中#########")
            wd_count = random.randint(self.WD_count_scope[0], self.WD_count_scope[1])
            mec_count = random.randint(self.MEC_count_scope[0], self.MEC_count_scope[1])
            mecSystem = mecSystemGenerator.generateMEC(wd_count, mec_count)

            for j in range(wd_count):
                print("#########生成任務DAG圖中#########")
                nums, edges, into_degree, out_degree, position = taskDAGGenerator.DAG_generate()
                taskGraph = taskDAGGenerator.transform_networkx_DAG(nums,position, edges)
                wd_no = "WD" + str(j)
                taskGraphDict[wd_no] = taskGraph


            print("##########本地執行仿真測試##########")
            greedyExecuter = EfficiencyGreedyExecute()
            total_task_execute_time, time_line, average_task_complete_time, total_task_delay_time, average_task_delay_time, task_delay_form = greedyExecuter.run(

                wd_count, mec_count, mecSystem, taskGraphDict)
            avg_task_delays.append(average_task_delay_time)
            total_response_times.append(average_task_complete_time)
            task_delays_form_list.append(task_delay_form.values())

            # 輸出每次測試的結果
            print(f"測試 {i + 1}:")
            print(f"所有任務執行需時: {total_task_execute_time}")
            print(f"系統執行完任務經過的實際時間: {time_line}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()


        plt.figure(figsize=(12, 6))

        for i, line_data in enumerate(task_delays_form_list):
            x = range(len(line_data))
            y = line_data
            plt.plot(x, y, color='black', label=f'Line {i + 1}')
        # plt.plot(range(len(task_delays_form_list[0])), task_delays_form_list[0], color='black', label=f'Line {i + 1}')
        plt.xlabel('task')
        plt.ylabel('delay_time')
        plt.title('Multiple Lines Chart')
        plt.legend()
        plt.grid(True)
        plt.savefig('./Image/折線圖.png')
        plt.show()

        return total_response_times, avg_task_delays

    def execute_task(self, task_id, on_mec=True):
        # 根據任務ID和是否在MEC上執行來更新任務狀態
        pass

    def update_environment(self):
        # 根據當前任務狀態和MEC系統狀態更新環境
        pass



    def efficiency_greedy_execute_wdNum_effect(self, dagSize, max_wd, mec_count):
        mecSystemGenerator = MECSystemGenerator()
        taskDAGGenerator = TaskDAGGenerator()

        total_average_execute_times = []  # 存儲每次測試的任務平均執行時間
        avg_task_delays = []  # 存儲每次測試的平均任務時延
        task_delays_form_list = []


        taskGraphDict = {}




        print("#########生成MEC系統拓樸中#########")

        for wd_count in range(1,max_wd+1):
            mecSystem = mecSystemGenerator.generateMEC(wd_count, mec_count)
            for i in range(wd_count):
                print("#########生成任務DAG圖中#########")
                nums, edges, into_degree, out_degree, position = taskDAGGenerator.DAG_generate(mode="size",
                                                                                               size=dagSize,
                                                                                               alpha=1.0, beta=1.0)
                taskGraph = taskDAGGenerator.transform_networkx_DAG(nums, position, edges)
                taskGraphDict["WD" + str(i)] = taskGraph

            print("##########本地執行仿真測試##########")
            greedyExecuter = EfficiencyGreedyExecute()
            total_task_execute_time, time_line, average_task_complete_time, total_task_delay_time, average_task_delay_time, task_delay_form = greedyExecuter.run(
                wd_count, mec_count, mecSystem, taskGraphDict)
            avg_task_delays.append(average_task_delay_time)
            total_average_execute_times.append(average_task_complete_time)
            task_delays_form_list.append(task_delay_form.values())

            # 輸出每次測試的結果
            print(f"測試wd_num {wd_count}:")
            print(f"所有任務執行需時: {total_task_execute_time}")
            print(f"系統執行完任務經過的實際時間: {time_line}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()

        plt.rcParams['font.family'] = 'SimHei'
        dag_nodes = list(range(0, max_wd))
        # 设置柱状图的宽度
        bar_width = 0.3

        # 设置柱状图的位置
        bar_positions1 = np.arange(len(dag_nodes))
        bar_positions2 = [x + bar_width for x in bar_positions1]

        # 绘制柱状图
        plt.figure(figsize=(10, 6))  # 设置图表大小
        plt.bar(bar_positions1, total_average_execute_times, bar_width, color='b', label='任务平均被执行时间')
        plt.bar(bar_positions2, avg_task_delays, bar_width, color='r', label='任务平均时延')

        # 添加图表标题和坐标轴标签
        plt.title('任务平均被执行时间和时延随移动节点数量的变化')
        plt.xlabel('任务节点数')
        plt.ylabel('时间 (ms)')

        # 显示图例
        plt.legend()

        # 设置x轴刻度标签
        plt.xticks(bar_positions1 + bar_width / 2, dag_nodes)

        # 显示网格
        plt.grid(True)

        # 保存图表到文件
        plt.savefig('./Image/wd_count_Performance_Analysis.png')

        # 显示图表
        plt.show()

        return total_average_execute_times, avg_task_delays


    def efficiency_greedy_execute_wdNum_effect(self, dagSize, max_wd, mec_count):
        mecSystemGenerator = MECSystemGenerator()
        taskDAGGenerator = TaskDAGGenerator()

        total_average_execute_times = []  # 存儲每次測試的任務平均執行時間
        avg_task_delays = []  # 存儲每次測試的平均任務時延
        task_delays_form_list = []


        taskGraphDict = {}




        print("#########生成MEC系統拓樸中#########")

        for wd_count in range(1,max_wd+1):
            mecSystem = mecSystemGenerator.generateMEC(wd_count, mec_count)
            for i in range(wd_count):
                print("#########生成任務DAG圖中#########")
                nums, edges, into_degree, out_degree, position = taskDAGGenerator.DAG_generate(mode="size",
                                                                                               size=dagSize,
                                                                                               alpha=1.0, beta=1.0)
                taskGraph = taskDAGGenerator.transform_networkx_DAG(nums, position, edges)
                taskGraphDict["WD" + str(i)] = taskGraph

            print("##########本地執行仿真測試##########")
            greedyExecuter = EfficiencyGreedyExecute()
            total_task_execute_time, time_line, average_task_complete_time, total_task_delay_time, average_task_delay_time, task_delay_form = greedyExecuter.run(
                wd_count, mec_count, mecSystem, taskGraphDict)
            avg_task_delays.append(average_task_delay_time)
            total_average_execute_times.append(average_task_complete_time)
            task_delays_form_list.append(task_delay_form.values())

            # 輸出每次測試的結果
            print(f"測試wd_num {wd_count}:")
            print(f"所有任務執行需時: {total_task_execute_time}")
            print(f"系統執行完任務經過的實際時間: {time_line}")
            print(f"總任務平均執行時間: {average_task_complete_time}")
            print(f"平均任務時延: {average_task_delay_time}")
            print()

        plt.rcParams['font.family'] = 'SimHei'
        dag_nodes = list(range(0, max_wd))
        # 设置柱状图的宽度
        bar_width = 0.3

        # 设置柱状图的位置
        bar_positions1 = np.arange(len(dag_nodes))
        bar_positions2 = [x + bar_width for x in bar_positions1]

        # 绘制柱状图
        plt.figure(figsize=(10, 6))  # 设置图表大小
        plt.bar(bar_positions1, total_average_execute_times, bar_width, color='b', label='任务平均被执行时间')
        plt.bar(bar_positions2, avg_task_delays, bar_width, color='r', label='任务平均时延')

        # 添加图表标题和坐标轴标签
        plt.title('任务平均被执行时间和时延随移动节点数量的变化')
        plt.xlabel('任务节点数')
        plt.ylabel('时间 (ms)')

        # 显示图例
        plt.legend()

        # 设置x轴刻度标签
        plt.xticks(bar_positions1 + bar_width / 2, dag_nodes)

        # 显示网格
        plt.grid(True)

        # 保存图表到文件
        plt.savefig('./Image/wd_count_Performance_Analysis.png')

        # 显示图表
        plt.show()

        return total_average_execute_times, avg_task_delays


if __name__ == '__main__':
    testEnvironment = TestEnvironment()
    #testEnvironment.efficiency_greedy_execute(1)
    #testEnvironment.local_execute(1,taskDAG_nodes= 80)
    #testEnvironment.efficiency_greedy_execute_taskNum_delay(2,8)


    #testEnvironment.local_efficiency_taskNum_sum_time(2,5)
    #testEnvironment.local_efficiency_taskNum_average_delay(2,8)
    #testEnvironment.efficiency_greedy_execute_wdNum_effect(60, 16, 2)
    #testEnvironment.local_efficiency_DAG_density(3, 6)
    testEnvironment.local_efficiency_channel_bandwidth(2,6)

