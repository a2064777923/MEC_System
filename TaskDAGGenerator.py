import random, math, argparse
import numpy as np
from numpy.random.mtrand import sample
from matplotlib import pyplot as plt
import networkx as nx



class TaskDAGGenerator:
    def __init__(self):
        # 任務的數據量大小(kB)
        self.TASK_DATA_SIZE_SCOPE = [200, 400]
        # 任務的最大容忍時延范圍
        self.TASK_MAX_DELAY_TIME_SCOPE = [0.5, 3]
        # 任務的平均計算密度(cycles)
        self.TASK_CALCULATION_DENSITY_SCOPE = [400, 600]


    def DAG_generate(self, mode='default', size =20, max_out=2, alpha=1.0, beta=1.0):
        set_dag_size = [20, 30, 40, 50, 60, 70, 80, 90]  # 設定DAG集的大小
        set_max_out = [1, 2, 3, 4, 5]  # 設定節點的最大出度，即該節點最多為多少個任務的前驅
        set_alpha = [0.5, 1.0, 2.0]  # 形狀參數，alpha越小，DAG越瘦長，反之相反。即alpha小會偏向線性單任務
        set_beta = [0.0, 0.5, 1.0, 2.0]  # 每層寛度的規則度，beta越大，DAG越不規則，模彷各種類型的任務場景
        DAG_argument={"dag_size":0, "max_out": 0, "alpha": 0 ,"beta": 0}
        if mode == 'default':
            DAG_argument["dag_size"] = random.sample(set_dag_size, 1)[0]
            DAG_argument["max_out"] = random.sample(set_max_out, 1)[0]
            DAG_argument["alpha"] = random.sample(set_alpha, 1)[0]
            DAG_argument["beta"] = random.sample(set_beta, 1)[0]
        else:
            DAG_argument["dag_size"] = size
            DAG_argument["max_out"] = max_out
            DAG_argument["alpha"] = alpha
            DAG_argument["beta"] = beta

        length = math.floor(math.sqrt(DAG_argument["dag_size"]) / DAG_argument["alpha"])
        mean_value = args.n / length
        random_num = np.random.normal(loc=mean_value, scale=args.beta, size=(length, 1))
        ###############################################division############################################
        position = {'Start': (0, 4), 'Exit': (10, 4)}
        generate_num = 0
        dag_num = 1
        dag_list = []
        for i in range(len(random_num)):
            dag_list.append([])
            for j in range(math.ceil(random_num[i])):
                dag_list[i].append(j)
            generate_num += math.ceil(random_num[i])

        if generate_num != args.n:
            if generate_num < args.n:
                for i in range(args.n - generate_num):
                    index = random.randrange(0, length, 1)
                    dag_list[index].append(len(dag_list[index]))
            if generate_num > args.n:
                i = 0
                while i < generate_num - args.n:
                    index = random.randrange(0, length, 1)
                    if len(dag_list[index]) == 1:
                        i = i - 1 if i != 0 else 0
                    else:
                        del dag_list[index][-1]
                    i += 1

        dag_list_update = []
        pos = 1
        max_pos = 0
        for i in range(length):
            dag_list_update.append(list(range(dag_num, dag_num + len(dag_list[i]))))
            dag_num += len(dag_list_update[i])
            pos = 1
            for j in dag_list_update[i]:
                position[j] = (3 * (i + 1), pos)
                pos += 5
            max_pos = pos if pos > max_pos else max_pos
            position['Start'] = (0, max_pos / 2)
            position['Exit'] = (3 * (length + 1), max_pos / 2)

        ############################################link###################################################
        into_degree = [0] * args.n
        out_degree = [0] * args.n
        edges = []
        pred = 0

        for i in range(length - 1):
            sample_list = list(range(len(dag_list_update[i + 1])))
            for j in range(len(dag_list_update[i])):
                od = random.randrange(1, args.max_out + 1, 1)
                od = len(dag_list_update[i + 1]) if len(dag_list_update[i + 1]) < od else od
                bridge = random.sample(sample_list, od)
                for k in bridge:
                    edges.append((dag_list_update[i][j], dag_list_update[i + 1][k]))
                    into_degree[pred + len(dag_list_update[i]) + k] += 1
                    out_degree[pred + j] += 1
            pred += len(dag_list_update[i])

        ######################################create start node and exit node################################
        for node, id in enumerate(into_degree):  # 给所有没有入边的节点添加入口节点作父亲
            if id == 0:
                edges.append(('Start', node + 1))
                into_degree[node] += 1

        for node, od in enumerate(out_degree):  # 给所有没有出边的节点添加出口节点作儿子
            if od == 0:
                edges.append((node + 1, 'Exit'))
                out_degree[node] += 1

        #############################################plot##################################################
        return edges, into_degree, out_degree, position

    def plot_DAG(edges, postion):
        g1 = nx.DiGraph()
        g1.add_edges_from(edges)
        nx.draw_networkx(g1, arrows=True, pos=postion)
        plt.savefig("DAG.png", format="PNG")
        return plt.clf