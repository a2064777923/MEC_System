import networkx as nx
import random
import matplotlib.pyplot as plt
import math


class WD:
    def __init__(self, calculation, transmission):
        # CPU計算能力(GHz),1-3
        self.calculation = calculation
        # 傳輸功率(mW)
        self.transmission = transmission


class MEC:
    def __init__(self, calculation, transmission):
        # CPU計算能力(GHz),2-4
        self.calculation = calculation
        # 傳輸功率(mW)
        self.transmission = transmission


class MECSystemGenerator:
    MECSystem = None

    def __init__(self):
        # 信道帶寬(Mhz)，通常超五類信息道的帶寛為100Mhz
        self.CHANNEL_BANDWIDTHS = 100
        # 信道增益，計算較為複雜，先設為1
        self.CHANNEL_GAIN = 1
        # 背景噪聲功率(dBm)
        self.BACKGROUND_NOISE = -100
        # 移動設備CPU計算能力范圍(Ghz)
        self.WD_CALCULATION_SCOPE = [1, 3]
        # MEC服務器CPU計算能力范圍(Ghz)
        self.MEC_CALCULATION_SCOPE = [2, 4]
        # 傳輸功率(mW)
        self.WD_TRANSMISSION = 100
        self.MEC_TRANSMISSION = 1000
        self.UPLINK_SIGNAL_FREQUENCY = [825, 954]
        # WD和MEC的距離的范圍
        self.WD_MEC_DISTANCE_SCOPE = [10, 1000]

    # 輸入參數: 需要的WD和MEC數量
    def generateMEC(self, WDNumber, MECNumber):
        self.MECSystem = nx.DiGraph()
        for i in range(WDNumber):
            # WDi = WD(round(random.uniform(1, 3), 2), 100)
            self.MECSystem.add_node("WD" + str(i), labels={
                "type": "WD",
                "calculation": round(random.uniform(self.WD_CALCULATION_SCOPE[0], self.WD_CALCULATION_SCOPE[1]), 2),
                "transmission": self.WD_TRANSMISSION,
                "signal_frequency": random.randint(self.UPLINK_SIGNAL_FREQUENCY[0], self.UPLINK_SIGNAL_FREQUENCY[1])})
        for i in range(MECNumber):
            # MECi = MEC(round(random.uniform(2, 4), 2), 1000)
            self.MECSystem.add_node("MEC" + str(i), labels={
                "type": "MEC",
                "calculation": round(random.uniform(self.MEC_CALCULATION_SCOPE[0], self.MEC_CALCULATION_SCOPE[1]), 2),
                "transmission": self.MEC_TRANSMISSION})
        # 每台WD和每台MEC間都有信道連接
        for nodeI in self.MECSystem.nodes:
            if self.MECSystem.nodes[nodeI]['labels']['type'] == 'WD':
                # 添加邊，權重先設為1
                for nodeJ in self.MECSystem.nodes:
                    if self.MECSystem.nodes[nodeJ]['labels']['type'] == 'MEC':
                        distance = random.randint(self.WD_MEC_DISTANCE_SCOPE[0], self.WD_MEC_DISTANCE_SCOPE[1])
                        self.MECSystem.add_edge(nodeI, nodeJ, weight=1, labels={
                            "distance": distance,
                            "maxTransmissionSpeed": MAX_TRANSMISSION_SPEED(self.CHANNEL_BANDWIDTHS, self.CHANNEL_GAIN,
                                                                           self.MECSystem.nodes[nodeI]['labels'][
                                                                               'transmission'],
                                                                           self.BACKGROUND_NOISE,
                                                                           self.MECSystem.nodes[nodeI]['labels'][
                                                                               'signal_frequency'],
                                                                           distance)
                        })

        return self.MECSystem
    

'''
計算信道的最大傳輸速率
B: 信道帶寬
Hi: 信道增益
Pi: 平均功率
N0: 高斯白噪聲
distance: 端到端距離
f: 信號頻率
'''


def MAX_TRANSMISSION_SPEED(B, Hi, Pi, N0, f, distance):
    # 自由空間路徑損失模型
    Lpath = 20 * math.log10(distance / 1000) + 20 * math.log10(f) + 32.4

    Pi_dBm = 10 * math.log10(Pi)
    N0_mW = math.pow(10, N0 / 10)
    # 接收功率
    Prx = Pi_dBm - Lpath
    Prx_mW = math.pow(10, Prx / 10)
    # 信道增益
    HPi = Hi * Prx_mW / Pi
    result = round(B * math.log2(1 + (HPi * Pi / N0_mW)), 2)
    return result


def draw_graph(G):
    pos = nx.spring_layout(G)  # 定義節點位置
    # 繪製節點
    node_labels = {node: f"{node}\n{G.nodes[node]['labels']['calculation']}" for node in G.nodes()}
    edge_labels = {edge: G.edges[edge]['labels']['maxTransmissionSpeed'] for edge in G.edges()}

    nx.draw_networkx_nodes(G, pos, node_size=1000, node_color='skyblue')
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)

    # 繪製邊
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)  # 顯示邊的標籤

    # 顯示圖形
    plt.axis('off')
    plt.show()


if __name__ == '__main__':
    mec = MECSystemGenerator()
    G = mec.generateMEC(1, 10)
    WD1 = WD(1, 1)
    print(WD1.calculation)
    # 顯示圖形
    draw_graph(G)
