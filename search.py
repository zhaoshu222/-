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
import pandas as pd
import time

#计算经纬度距离
def distance(stations_info,from_station,to_station):
    x=stations_info[from_station][0]-stations_info[to_station][0]
    y=stations_info[from_station][1]-stations_info[to_station][1]
    return (x**2+y**2)**0.5
    
def get_path_Astar(lines_info, neighbor_info, stations_info, from_station, to_station):
    # 搜索策略：以路径的站点间直线距离累加为cost，以当前站点到目标的直线距离为启发函数
    # 检查输入站点名称
    
    #预估每个点到终点的距离，放在字典中不用反复计算
    guessDic={}
    for station in neighbor_info.keys():
        guessDic[station]=distance(stations_info,station,to_station)
    #已确定的点
    reached={from_station:[0,0]}
    #备选的点、距离、上一个点
    neighbor={station:[distance(stations_info, from_station, station),from_station] for station in neighbor_info[from_station]}
    while to_station not in reached.keys():
        #找到去该点距离+预估距离最短的点
        bestItem=None
        bestDistance=10000
        for item in neighbor.items():
            if item[1][0]+guessDic[item[0]]<bestDistance:
                bestDistance=item[1][0]+guessDic[item[0]]
                bestItem=item
        reached[bestItem[0]]=bestItem[1]
        neighbor.pop(bestItem[0])
        for station in neighbor_info[bestItem[0]]:
            if station not in reached.keys():
                if station not in neighbor:
                    neighbor[station]=[bestItem[1][0]+distance(stations_info,bestItem[0],station),bestItem[0]]
                else:
                    curDistance=bestItem[1][0]+distance(stations_info,bestItem[0],station)
                    if curDistance<neighbor[station][0]:
                        neighbor[station]=[curDistance,bestItem[0]]
    #反向找路径
    path=[to_station]
    while path[-1]!=from_station:
        path.append(reached[path[-1]][-1])
    path.reverse()
    return path 
res=get_path_Astar(lines_info, neighbor_info, stations_info, '奥体中心', '天安门东')
print('Astar:',res)
