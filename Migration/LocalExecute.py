import heapq
import random

from Calculator import Calculator


class LocalExecute:

    def run(self, wd_node, mecSystem, taskGraph):
        calculator = Calculator(mecSystem, taskGraph)  # 初始化計算器
        time_line = 0
        total_task_completion_time = 0
        total_task_delay_time = 0
        task_delay_form = {}


        # 初始化任務執行狀態
        task_status = {task: False for task in taskGraph.nodes if task not in ["Start", "Exit"]}
        total_tasks = len(task_status)

        task_priority_queue = []

        # 將起始任務加入優先級隊列
        start_successors = list(taskGraph.successors("Start"))
        for successor in start_successors:
            # heapq用于实現堆排序算法
            heapq.heappush(task_priority_queue, (calculator.MAX_TOLERANCE_DELAY(successor, wd_node), successor))

        while task_priority_queue:
            _, current_task = heapq.heappop(task_priority_queue)
            if current_task == "Exit":
                continue

            # 隨機選擇一個WD執行當前任務
            # selected_WD = random.choice([node for node in mecSystem.nodes if mecSystem.nodes[node]['labels']['type'] == 'WD'])

            task_execute_time = calculator.LOCAL_CALCULATION_DELAY(current_task,wd_node)  # 計算任務執行時延
            total_task_completion_time += task_execute_time
            # 時間線
            time_line += task_execute_time
            # 更新任務的實際完成時間
            calculator.updateActualFinishTime(current_task,time_line)
            # 任務的完成時間減去任務的就緒時間，為任務延迟了多久才被執行
            task_delay_time = time_line - calculator.TASK_READY_TIME(current_task)
            total_task_delay_time += task_delay_time
            task_delay_form[current_task] = task_delay_time

            # 標記當前任務為已執行
            task_status[current_task] = True

            # 更新後繼任務的優先級並加入隊列
            for successor in taskGraph.successors(current_task):
                if successor not in task_status:  # 避免將Exit加入隊列
                    continue
                # 判斷是否這一後繼任務的所有前置任務都為已執行狀態，若是的話就加入優先隊列作排序
                if all(task_status[predecessor] for predecessor in taskGraph.predecessors(successor)):
                    heapq.heappush(task_priority_queue, (calculator.MAX_TOLERANCE_DELAY(successor, wd_node), successor))

        # 當所有任務完成後，標記Exit任務為已執行
        #task_status["Exit"] = True

        # 檢查是否所有任務都已成功執行
        assert all(status == True for status in task_status.values()), "有任務未能成功執行"

        # 計算平均執行時間
        average_task_complete_time = total_task_completion_time / total_tasks
        average_task_delay_time = total_task_delay_time / total_tasks

        return total_task_completion_time, average_task_complete_time, average_task_delay_time, task_delay_form

