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
        # 信道帶寬(MhH)，802.11n支持20/40/80/160 Mhz帶寛
        self.CHANNEL_BANDWIDTHS = 20
        # 信道增益，計算較為複雜，先設為1
        self.CHANNEL_GAIN = 1
        # 背景噪聲功率(dBm)
        self.BACKGROUND_NOISE = -100
        # 移動設備CPU計算能力范圍(Ghz)
        self.WD_CALCULATION_SCOPE = [0.5, 2]
        # MEC服務器CPU計算能力范圍(Ghz)
        self.MEC_CALCULATION_SCOPE = [2, 4]
        # 傳輸功率(mW)
        self.WD_TRANSMISSION = 100
        self.MEC_TRANSMISSION = 1000
        self.UPLINK_SIGNAL_FREQUENCY = [825, 954]
        # WD和MEC的距離的范圍
        # self.WD_MEC_DISTANCE_SCOPE = [10, 5000]
        # 方形区域边长
        self.AREA_SIZE = 1000
        # 最小连接距离
        self.MIN_CONNECTION_DISTANCE = 200
        self.MIN_DISTANCE_BETWEEN_DEVICES = 0.1  # meters


     # 计算两点间距离
    def calculate_distance(self, x1, y1, x2, y2):
            return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def generate_position(self):
        x = random.randint(0, self.AREA_SIZE)
        y = random.randint(0, self.AREA_SIZE)
        return x, y

    def is_valid_position(self, x, y):
        for node in self.MECSystem.nodes:
            pos = self.MECSystem.nodes[node]['labels']['position']
            if self.calculate_distance(x, y, pos[0], pos[1]) < self.MIN_DISTANCE_BETWEEN_DEVICES:
                return False
        return True

    def change_MAX_SPEED(self, MECSystem, transport_speed):
        for node in MECSystem.nodes:
            if "WD" in node:
                for mec in MECSystem.neighbors(node):
                    edge_data = MECSystem.get_edge_data(node, mec)
                    edge_data['labels']['maxTransmissionSpeed'] = transport_speed
            if "MEC" in node:
                for mec in MECSystem.neighbors(node):
                    edge_data = MECSystem.get_edge_data(node, mec)
                    edge_data['labels']['maxTransmissionSpeed'] = transport_speed


    # 輸入參數: 需要的WD和MEC數量
    def generateMEC(self, WDNumber, MECNumber,channel_bandwidths = -1):
        if channel_bandwidths == -1:
            self.CHANNEL_BANDWIDTHS = random.choice([20,40,80,160])
        else:
            self.CHANNEL_BANDWIDTHS = channel_bandwidths
        self.MECSystem = nx.DiGraph()
        for i in range(WDNumber):
            # WDi = WD(round(random.uniform(1, 3), 2), 100)
            x,y = 0,0
            valid = False
            while not valid:
                x, y = self.generate_position()
                if self.is_valid_position(x, y):
                    valid = True
            self.MECSystem.add_node("WD" + str(i), labels={
                "type": "WD",
                "calculation": round(random.uniform(self.WD_CALCULATION_SCOPE[0], self.WD_CALCULATION_SCOPE[1]), 2),
                "transmission": self.WD_TRANSMISSION,
                "signal_frequency": random.randint(self.UPLINK_SIGNAL_FREQUENCY[0], self.UPLINK_SIGNAL_FREQUENCY[1]),
                "position" : (x,y)
            })
        for i in range(MECNumber):
            # MECi = MEC(round(random.uniform(2, 4), 2), 1000)
            x, y = 0,0
            valid = False
            while not valid:
                x, y = self.generate_position()
                if self.is_valid_position(x, y):
                    valid = True
            self.MECSystem.add_node("MEC" + str(i), labels={
                "type": "MEC",
                "calculation": round(random.uniform(self.MEC_CALCULATION_SCOPE[0], self.MEC_CALCULATION_SCOPE[1]), 2),
                "transmission": self.MEC_TRANSMISSION,
                "position" : (x,y),

            })

            # 建立连接，考虑最小距离限制
            for nodeI in self.MECSystem.nodes:
                nodeI_type = self.MECSystem.nodes[nodeI]['labels']['type']
                if nodeI_type == 'WD':
                    connected = False
                    for nodeJ in self.MECSystem.nodes:
                        if self.MECSystem.nodes[nodeJ]['labels']['type'] == 'MEC':
                            distance = self.calculate_distance(
                                *self.MECSystem.nodes[nodeI]['labels']['position'],
                                *self.MECSystem.nodes[nodeJ]['labels']['position']
                            )
                            if distance <= self.MIN_CONNECTION_DISTANCE:
                                self.MECSystem.add_edge(nodeI, nodeJ, weight=1, labels={
                                    "distance": distance,
                                    "maxTransmissionSpeed": MAX_TRANSMISSION_SPEED(self.CHANNEL_BANDWIDTHS,
                                                                                   self.CHANNEL_GAIN,
                                                                                   self.MECSystem.nodes[nodeI][
                                                                                       'labels'][
                                                                                       'transmission'],
                                                                                   self.BACKGROUND_NOISE,
                                                                                   self.MECSystem.nodes[nodeI][
                                                                                       'labels'][
                                                                                       'signal_frequency'],
                                                                                   distance)
                                })
                                connected = True
                            if not connected:
                                # 如果WD没有连接到任何MEC，尝试重新生成位置

                                while not connected:
                                    x, y = self.generate_position()
                                    if self.is_valid_position(x, y):

                                        self.MECSystem.nodes[nodeI]['labels']['position'] = (x, y)
                                        for nodeJ in self.MECSystem.nodes:
                                            if 'MEC' in nodeJ:
                                                distance = self.calculate_distance(
                                                    *self.MECSystem.nodes[nodeI]['labels']['position'],
                                                    *self.MECSystem.nodes[nodeJ]['labels']['position']
                                                )
                                                if distance <= self.MIN_CONNECTION_DISTANCE:
                                                    self.MECSystem.add_edge(nodeI, nodeJ, weight=1, labels={
                                                        "distance": distance,
                                                        "maxTransmissionSpeed": MAX_TRANSMISSION_SPEED(
                                                            random.choice([20,40,80,160]),
                                                            self.CHANNEL_GAIN,
                                                            self.MECSystem.nodes[nodeI][
                                                                'labels'][
                                                                'transmission'],
                                                            self.BACKGROUND_NOISE,
                                                            self.MECSystem.nodes[nodeI][
                                                                'labels'][
                                                                'signal_frequency'],
                                                            distance)
                                                    })
                                                    connected = True

        # MEC之间的虚拟链路，同样考虑最小距离限制
        for i in range(MECNumber):
            for j in range(i + 1, MECNumber):
                distance = self.calculate_distance(
                    *self.MECSystem.nodes["MEC" + str(i)]['labels']['position'],
                    *self.MECSystem.nodes["MEC" + str(j)]['labels']['position']
                )
                self.MECSystem.add_edge("MEC" + str(i), "MEC" + str(j), weight=1, labels={
                    "distance": distance,
                    "maxTransmissionSpeed": 128 # MB/s
                })

        # # 每台WD和每台MEC間都有信道連接
        # for nodeI in self.MECSystem.nodes:
        #     if self.MECSystem.nodes[nodeI]['labels']['type'] == 'WD':
        #         # 添加邊，權重先設為1
        #         for nodeJ in self.MECSystem.nodes:
        #             if self.MECSystem.nodes[nodeJ]['labels']['type'] == 'MEC':
        #                 distance = random.randint(self.WD_MEC_DISTANCE_SCOPE[0], self.WD_MEC_DISTANCE_SCOPE[1])
        #                 self.MECSystem.add_edge(nodeI, nodeJ, weight=1, labels={
        #                     "distance": distance,
        #                     "maxTransmissionSpeed": MAX_TRANSMISSION_SPEED(self.CHANNEL_BANDWIDTHS, self.CHANNEL_GAIN,
        #                                                                    self.MECSystem.nodes[nodeI]['labels'][
        #                                                                        'transmission'],
        #                                                                    self.BACKGROUND_NOISE,
        #                                                                    self.MECSystem.nodes[nodeI]['labels'][
        #                                                                        'signal_frequency'],
        #                                                                    distance)
        #                 })


        return self.MECSystem




'''
計算信道的最大傳輸速率
B: 信道帶寬(MHz)
Hi: 信道增益
Pi: 平均功率(mW)
N0: 高斯白噪聲(dBm)
distance: 端到端距離 (m)
f: 信號頻率(Mhz)
'''


def MAX_TRANSMISSION_SPEED(B, Hi, Pi, N0, f, distance):
    # 自由空間路徑損失模型
    Lpath = 20 * math.log10(distance/1000) + 20 * math.log10(f) + 32.4

    Pi_dBm = 10 * math.log10(Pi)
    N0_mW = math.pow(10, N0 / 10)
    # 接收功率
    Prx = Pi_dBm - Lpath
    Prx_mW = math.pow(10, Prx / 10)
    # 信道增益
    HPi = Hi * Prx_mW  # / Pi
    # 香農公式中B單位是Hz，雖然Prx和N0的單位應該是W，但它們相除了，所以可以不改
    result = round(B * math.pow(10, 6) * math.log2(1 + (HPi * Pi / N0_mW)), 2)
    return round(result / 8 / 1024 / 1024, 2)  # MB/s


def draw_graph(G):

    pos = {node: (G.nodes[node]["labels"]['position'][0], G.nodes[node]["labels"]['position'][1]) for node in G.nodes()}  # 定義節點位置


    # 繪製節點
    node_labels = {node: f"{node}\n{G.nodes[node]['labels']['calculation']}" for node in G.nodes()}
    edge_labels = {edge: G.edges[edge]['labels']['maxTransmissionSpeed'] for edge in G.edges()}

    wd_node = {node for node in G.nodes() if "WD" in node}
    mec_node = {node for node in G.nodes() if"MEC" in node}
    nx.draw_networkx_nodes(wd_node, pos, node_size=800, node_color='skyblue')
    nx.draw_networkx_nodes(mec_node, pos, node_size=800, node_color='red')

    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)

    # 繪製邊
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)  # 顯示邊的標籤

    # 顯示圖形
    plt.axis('off')
    plt.show()


if __name__ == '__main__':
    mec = MECSystemGenerator()
    G = mec.generateMEC(6, 3)

    WD1 = WD(1, 1)
    print(WD1.calculation)
    # 顯示圖形
    draw_graph(G)
