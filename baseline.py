import csv
import numpy as np
import argparse
import json
import os
import time
import math
from openpyxl import load_workbook
import networkx as nx
from coverage_final_algo_combined import readGraph, run_BFS


def check_current_coverage(G, threshold, seed_set):
    graph_nodes = list(G.nodes)
    count_coverage = 0
    map_vertices_1 = {}
    covered_nodes = {}
    infected_nodes = []
    infected_queue = list(seed_set)
    for node in graph_nodes:
        if node not in infected_queue:
            map_vertices_1[node] = min(G.degree(node), threshold)
            covered_nodes[node] = 0
        else:
            map_vertices_1[node] = 0
            covered_nodes[node] = 1
            infected_nodes.append(node)
            count_coverage += 1

    (map_vertices_1, covered_nodes, infected_nodes, count_coverage) = \
        run_BFS(G, infected_queue, map_vertices_1,
                covered_nodes, infected_nodes, count_coverage)
    return len(infected_nodes)

def check_coverage_entire_graph(G, threshold, seed_set):
    graph_nodes = list(G.nodes)
    count_coverage = 0
    map_vertices = {}
    covered_nodes = {}
    infected_nodes = []
    infected_queue = list(seed_set)
    for node in graph_nodes:
        if node not in infected_queue:
            map_vertices[node] = min(G.degree(node), threshold)
            covered_nodes[node] = 0
        else:
            map_vertices[node] = 0
            covered_nodes[node] = 1
            infected_nodes.append(node)
            count_coverage += 1

    (map_vertices, covered_nodes, infected_nodes, count_coverage) = \
        run_BFS(G, infected_queue, map_vertices,
                covered_nodes, infected_nodes, count_coverage)
    assert set(graph_nodes) == set(infected_nodes)

def count_zero_threshold_vertices(map_vertices):
    vertices = 0
    for key, value in map_vertices.items():
        #print (key, value)
        if value == 0:
            vertices+=1
    return vertices

def minimal_coverage_set(G, threshold):
    # Graph nodes.
    graph_nodes = list(G.nodes)
    # Declare variables.
    seed_set = set([])
    map_vertices = {}
    map_vertices_coverage = {}
    neighbor_list_dict = {}
    neighbor_list_dict_coverage = {}
    degree_dict = {}
    degree_dict_coverage = {}
    visited_nodes = {}
    total_infected_queue = set([])
    for node in graph_nodes:
        map_vertices[node] = min(G.degree(node), threshold)
        map_vertices_coverage[node] =  min(G.degree(node), threshold) 
        degree_dict[node] = G.degree(node)
        degree_dict_coverage[node] = G.degree(node)
        neighbor_list_dict[node] = list(G.neighbors(node))
        neighbor_list_dict_coverage[node] = list(G.neighbors(node))
        visited_nodes[node] = 0

    total_nodes = len(graph_nodes)
    first_instance = 0
    count_coverage = 0
    while (graph_nodes):
        selected_node = None
        zero_node = False
        found_lower_degree_node = False
        max_node_value = -math.inf
        max_node = None
        for node in graph_nodes:
            node_degree = degree_dict[node]
            # If found Case 1, break
            if map_vertices[node] == 0:
                neighbor_list = neighbor_list_dict[node]
                for neighbor_node in neighbor_list:
                    map_vertices[neighbor_node] = \
                        max(map_vertices[neighbor_node]-1, 0)
                zero_node = True
                selected_node = node
                break
            # If found Case 2, store the node and keep going as we may
            # still find Case 1.
            if node_degree < map_vertices[node] and not found_lower_degree_node:
                lower_degree_node = node
                found_lower_degree_node = True

            # Calculate Case 3, in case we don't find Case 1 and Case 2.
            if node_degree > 0:
                node_value = (map_vertices[node])/(node_degree * (node_degree+1))
                if node_value > max_node_value:
                    max_node = node 
                    max_node_value = node_value

        if not zero_node and found_lower_degree_node:
            seed_set.add(lower_degree_node)
            neighbor_list = neighbor_list_dict[lower_degree_node]
            for neighbor_node in neighbor_list:
                map_vertices[neighbor_node] -= 1
            selected_node = lower_degree_node
        elif not zero_node and not found_lower_degree_node:
            selected_node = max_node
        selected_node_neighbor = neighbor_list_dict[selected_node]
        for neighbor_node in selected_node_neighbor:
            degree_dict[neighbor_node] -= 1
            neighbor_list_dict[neighbor_node].remove(selected_node)
        graph_nodes.remove(selected_node)
    print ('seed set nodes', seed_set)
    print ('seed set', len(seed_set))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create matrix")
    parser.add_argument('--filepath', help='Path for graph')
    parser.add_argument('--outputpath', help='Path for output graph')
    parser.add_argument('--allnodespath', help='Path for all seeds')
    parser.add_argument('--threshold', type=int, help='Threshold')
    parser.add_argument('--excelpath', help='Excel file Path')
    parser.add_argument('--rownum', help='Row number')
    args = parser.parse_args()
    minimal_coverage_set(args.filepath, args.outputpath, args.allnodespath,
                         float(args.threshold), args.excelpath, args.rownum)
