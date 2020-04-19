import requests
import re
import numpy as np
import json
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
r = requests.get('http://map.amap.com/service/subway?_1469083453978&srhdata=1100_drw_beijing.json')
s1 = json.loads(r.text)
cities_list = []
#print(s1)
for l in s1.values():
    #print(type(l))
    if type(l) is str :continue
    cities_list = l
def get_lines_stations_info(text):
    lines_name_list=[] #线路名称列表
    station_name_list=[]#——站点名称列表
    lines_info = {} #‘线路’：‘所有站点’
    station_x_y_list = []#经纬度列表
    station_info = {}#经纬度字典
    for lines in range(0,len(cities_list)):
        lines_name = cities_list[lines]['ln']#取线路
        lines_name_list.append(lines_name)
        rightnow_station = []#临时储存每条线路的站点
        rightnow_station_x_y = []#临时储存经纬度
        right_x_y_dict = {}#临时储经纬度键值对
        for m in range(0,len(cities_list[lines]['st'])):
            station_x_y = cities_list[lines]['st'][m]['sl']#取经纬度
            x = re.findall('\d+.\d{0,6}',station_x_y)
            x[0] = float(x[0])
            x[1] = float(x[1])
            rightnow_station_x_y.append(x)
            stations_name = cities_list[lines]['st'][m]['n']#取站点名
            rightnow_station.append(stations_name)
        station_name_list.append(rightnow_station)
        station_x_y_list.append(rightnow_station_x_y)
    for idex in range(0,24):
        x_y_rightnow = {}#临时经纬度字典
        x_y_rightnow = dict(zip(station_name_list[idex],station_x_y_list[idex]))
        station_info.update(x_y_rightnow)
   # print(station_info)
    lines_info  = dict(map(lambda x,y:[x,y],lines_name_list,station_name_list))#‘线路名’：‘线路中所有站点名’
    #print(lines_info)
    return lines_info,station_info
lines_info, stations_info = get_lines_stations_info(cities_list)
#print(stations_info)
# 根据线路信息，建立站点邻接表dict
def get_neighbor_info(lines_info):
    neighbor_info = {}
    for sta in lines_info.values():
        # print(sta)
        for k, v in enumerate(sta):  # k,v分别为索引，值
            # print(k)
            # print(v)
            tmp_list = []
            if k == 0:
                if v in neighbor_info:
                    tmp_list = neighbor_info[v]
                    tmp_list.append(sta[k + 1])
                else:
                    tmp_list.append(sta[k + 1])
                neighbor_info[v] = tmp_list
            elif k == len(sta) - 1:
                if v in neighbor_info:
                    tmp_list = neighbor_info[v]
                    tmp_list.append(sta[k - 1])
                else:
                    tmp_list.append(sta[k - 1])
                neighbor_info[v] = tmp_list
            else:
                if v in neighbor_info:
                    tmp_list = neighbor_info[v]
                    tmp_list.append(sta[k + 1])
                    tmp_list.append(sta[k - 1])
                else:
                    tmp_list.append(sta[k + 1])
                    tmp_list.append(sta[k - 1])
                neighbor_info[v] = tmp_list

    return neighbor_info


neighbor_info = get_neighbor_info(lines_info)
neighbor_info

# 画地铁图
lines_info, stations_info = get_lines_stations_info(cities_list)
# 如果汉字无法显示，请参照
#matplotlib.rcParams['font.sans-serif'] = ['SimHei']
station_connection_graph = nx.Graph(neighbor_info)
#station_graph.add_nodes_from(list(station_info.keys()))
nx.draw(station_connection_graph,stations_info,with_labels=True, node_size=50,font_size=5)
plt.figure(figsize=(100, 50))#画布大小
plt.show()
# matplotlib.rcParams['font.family']='sans-serif'
# 你可以用递归查找所有路径
def get_path_DFS_ALL(lines_info, neighbor_info, from_station, to_station):
    # 递归算法，本质上是深度优先
    # 遍历所有路径
    # 这种情况下，站点间的坐标距离难以转化为可靠的启发函数，所以只用简单的BFS算法
    # 检查输入站点名称
    pathes = [[from_station]]
    visited = set()
    road = []
    while pathes:
        path = pathes.pop(0)
        froniter = path[-1]
        if froniter in visited: continue
        successors = neighbor_info[froniter]
        for station in successors:
            if station in path: continue
            new_path = path + [station]
            pathes = [new_path] + pathes
            if station == to_station:
                road.append(new_path)
        visited.add(froniter)

    return road


demo = get_path_DFS_ALL(lines_info, neighbor_info, from_station='石厂', to_station='苹果园')
print(demo)


#  你也可以使用第二种算法：没有启发函数的简单宽度优先

def get_path_BFS(lines_info, neighbor_info, from_station, to_station):
    # 搜索策略：以站点数量为cost（因为车票价格是按站算的）
    # 这种情况下，站点间的坐标距离难以转化为可靠的启发函数，所以只用简单的BFS算法
    # 由于每深一层就是cost加1，所以每层的cost都相同，算和不算没区别，所以省略
    # 检查输入站点名称
    pathes = [[from_station]]
    visited = set()
    road = []
    while pathes:
        path = pathes.pop(0)
        froniter = path[-1]

        if froniter in visited: continue
        successor = neighbor_info[froniter]
        for station in successor:
            if station in path: continue
            new_path = path + [station]
            pathes.append(new_path)
            if station == to_station:
                road.append(new_path)
        visited.add(froniter)
    return road


demo_1 = get_path_BFS(lines_info, neighbor_info, from_station='石厂', to_station='苹果园')
print(demo_1)
