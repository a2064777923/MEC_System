import random, math, argparse
import numpy as np
from numpy.random.mtrand import sample
from matplotlib import pyplot as plt
import networkx as nx


class TaskDAGGenerator:
    def __init__(self):

        # 应用的數據量大小(KB)
        self.TASK_DATA_SIZE_SCOPE = [200, 400]
        # 任務的最大容忍時延范圍(s)
        self.TASK_MAX_DELAY_TIME_SCOPE = [0.5, 3]
        # 任務的平均計算密度(cycles/bits)
        self.TASK_CALCULATION_DENSITY_SCOPE = [400, 600]


    def DAG_generate(self, mode='default', size=20, max_out=2, alpha=1.0, beta=1.0):
        set_dag_size = [10, 20, 30, 40, 50, 60, 70, 80]  # 設定DAG集的大小
        set_max_out = [1, 2, 3, 4]  # 設定節點的最大出度，即該節點最多為多少個任務的前驅
        set_alpha = [0.5, 1.0, 2.0]  # 形狀參數，alpha越小，DAG越瘦長，反之相反。即alpha小會偏向線性單任務
        set_beta = [0.0, 0.5, 1.0, 2.0]  # 每層寛度的規則度，beta越大，DAG越不規則，模彷各種類型的任務場景
        DAG_argument = {"dag_size": 0, "max_out": 0, "alpha": 0, "beta": 0}
        # DAG的參數可以自行設定，也可以默認隨機
        if mode == 'default':
            DAG_argument["dag_size"] = random.sample(set_dag_size, 1)[0]
            DAG_argument["max_out"] = random.sample(set_max_out, 1)[0]
            DAG_argument["alpha"] = random.sample(set_alpha, 1)[0]
            DAG_argument["beta"] = random.sample(set_beta, 1)[0]
        else:

            if size != -1:
                DAG_argument["dag_size"] = size
            else:
                DAG_argument["dag_size"] = random.sample(set_dag_size, 1)[0]
            if max_out != -1:
                DAG_argument["max_out"] = max_out
            else:
                DAG_argument["max_out"] = random.sample(set_max_out, 1)[0]
            if alpha != -1:
                DAG_argument["alpha"] = alpha
            else:
                DAG_argument["alpha"] = random.sample(set_alpha, 1)[0]
            if beta != -1:
                DAG_argument["beta"] = beta
            else:
                DAG_argument["beta"] = random.sample(set_beta, 1)[0]

        # 圖的深度
        length = math.floor(math.sqrt(DAG_argument["dag_size"]) / DAG_argument["alpha"])
        # 每層的平均節點個數
        mean_value = DAG_argument["dag_size"] / length
        # 返回一個符合正太分布的數組，參數: loc-均值，scale-標准差(離散程度)，size-形狀(長度為length的一維數組)
        random_num = np.random.normal(loc=mean_value, scale=DAG_argument["beta"], size=(length, 1))
        ###############################################division############################################
        position = {'Start': (0, 4), 'Exit': (10, 4)}
        generate_num = 0
        dag_num = 1
        dag_list = []
        for i in range(len(random_num)):
            dag_list.append([])
            for j in range(math.ceil(random_num[i][0])):
                dag_list[i].append(j)
            generate_num += math.ceil(random_num[i][0])

        if generate_num != DAG_argument["dag_size"]:
            if generate_num < DAG_argument["dag_size"]:
                for i in range(DAG_argument["dag_size"] - generate_num):
                    index = random.randrange(0, length, 1)
                    dag_list[index].append(len(dag_list[index]))
            if generate_num > DAG_argument["dag_size"]:
                i = 0
                while i < generate_num - DAG_argument["dag_size"]:
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
        into_degree = [0] * DAG_argument["dag_size"]
        out_degree = [0] * DAG_argument["dag_size"]
        edges = []
        pred = 0

        for i in range(length - 1):
            sample_list = list(range(len(dag_list_update[i + 1])))
            for j in range(len(dag_list_update[i])):
                od = random.randrange(1, DAG_argument["max_out"] + 1, 1)
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

        return DAG_argument["dag_size"], edges, into_degree, out_degree, position


    def plot_DAG(self, edges, position):
        g1 = nx.DiGraph()
        g1.add_edges_from(edges)
        nx.draw_networkx(g1, arrows=True, pos=position)
        plt.savefig("DAG.png", format="PNG")
        return plt.clf


    def transform_networkx_DAG(self, size, position, edges):

        G = nx.DiGraph()
        G.add_nodes_from(position.keys())
        G.add_edges_from(edges)
        G.nodes["Start"]["Cycles"] = 0
        G.nodes["Start"]["DataIn"] = 0
        G.nodes["Exit"]["Cycles"] = 0
        G.nodes["Exit"]["DataIn"] = 0

        application_size = random.randint(self.TASK_DATA_SIZE_SCOPE[0] * 1024 * 8,
                                          self.TASK_DATA_SIZE_SCOPE[1] * 1024 * 8) * math.ceil(size/15)
        mean = application_size / size
        std_dev = mean / 3
        tasks_size = np.random.normal(mean, std_dev, size)  # 用np.random.normal生成符合正態分布的任務輸入數據大小
        i = 0

        for nodes in G.nodes:
            if nodes != "Start" and nodes != "Exit":
                G.nodes[nodes]["Cycles"] = random.randint(self.TASK_CALCULATION_DENSITY_SCOPE[0],
                                                          self.TASK_CALCULATION_DENSITY_SCOPE[1])

                G.nodes[nodes]["DataIn"] = round(tasks_size[i] /1024 / 8,2)
                i += 1

        predecessors = G.predecessors("Exit")
        for predecessor in predecessors:
            G.nodes[predecessor]["MaxDelayTime"] = random.randint(self.TASK_MAX_DELAY_TIME_SCOPE[0] * 1000,
                                                                  self.TASK_MAX_DELAY_TIME_SCOPE[1] * 1000)
        return G


def draw_graph(G):

    pos = nx.spring_layout(G, 2)  # 定義節點位置

    # 繪製節點
    node_labels = {node: f"{node}\n{G.nodes[node]['Cycles'], G.nodes[node]['DataIn']}" for node in G.nodes()}
    # edge_labels = {edge: G.edges[edge]['labels']['maxTransmissionSpeed'] for edge in G.edges()}

    nx.draw_networkx_nodes(G, pos, node_size=500, node_color='skyblue')
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)

    # 繪製邊
    nx.draw_networkx_edges(G, pos)
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)  # 顯示邊的標籤

    # 顯示圖形
    plt.axis('off')
    plt.show()


if __name__ == '__main__':
    task = TaskDAGGenerator()

    size, edges, into, out, position = task.DAG_generate(mode="size",size= 20,alpha= 0.5 , beta=1.0) #task.DAG_generate(mode="tt" ,size=10)


    G = task.transform_networkx_DAG(size, position, edges)
    draw_graph(G)
