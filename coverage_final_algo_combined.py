import os
import pdb
import argparse
import numpy as np
import networkx as nx

#def readGraph(path):
#    G = nx.read_edgelist(path, delimiter=' ')
#    return G

def readGraph(path):
    G = nx.read_edgelist(path, data=(("weight", float),))
    return G

def run_BFS(G, infected_queue, map_vertices,
            covered_nodes, all_infected_nodes, count_coverage):
    while(infected_queue):
        node = infected_queue.pop(0)
        neighbor_list = G.neighbors(node)
        for neighbor_node in neighbor_list:
            if neighbor_node not in all_infected_nodes and covered_nodes[neighbor_node]==0:
                map_vertices[neighbor_node] -= 1
                if map_vertices[neighbor_node] == 0:
                    count_coverage += 1
                    covered_nodes[neighbor_node] = 1
                    infected_queue.append(neighbor_node)
                    all_infected_nodes.append(neighbor_node)
    return (map_vertices, covered_nodes, all_infected_nodes,
            count_coverage)
 
def coverage_final_algo(graph, source_node1,
                        threshold, covered_nodes=None,
                        map_vertices=None,
                        all_infected_nodes=None,
                        count_coverage=None,
                        neighbors_set=None):
    if isinstance(graph, str):
        G = readGraph(graph)
    else:
        G = graph
    graph_nodes = list(G.nodes)

    if map_vertices is None:
        map_vertices = {}
        single_node = True
        for g in graph_nodes:
            # uninfected
            map_vertices[g] = threshold
    else:
        single_node = False

    if all_infected_nodes is None:
        all_infected_nodes = []

    if covered_nodes is None:
        covered_nodes = {}
        for g in graph_nodes:
            covered_nodes[g] = 0
    
    if count_coverage is None:
        count_coverage = 0

    infected_queue = []
    if covered_nodes[source_node1] == 0:
        map_vertices[source_node1] = 0
        covered_nodes[source_node1] = 1
        infected_queue.append(source_node1)
        all_infected_nodes.append(source_node1)

    # Get BFS (S union source_node).
    (map_vertices, covered_nodes, all_infected_nodes, count_coverage) = \
        run_BFS(G, threshold, infected_queue, map_vertices, covered_nodes,
                all_infected_nodes, count_coverage)
    
    # Get source neighbors and sort them.
    source_neighbors = list(G.neighbors(source_node1))
    neighbors_degree_list = G.degree(source_neighbors)
    # dynamic maximum
    sorted_neighbors = sorted(neighbors_degree_list, key = lambda x: x[1], reverse=True)

    infected_queue = []
    count_activated_neighbors = 0
    neighbors_seed_set = []
    for neighbor in sorted_neighbors:
        neighbor_node = neighbor[0]
        if covered_nodes[neighbor_node] == 0:
            neighbor_node_neighbors = list(G.neighbors(neighbor_node))
            count_covered_nodes = 0
            for neighbor_node_neighbor in neighbor_node_neighbors:
                if covered_nodes[neighbor_node_neighbor] == 1:
                    count_covered_nodes += 1
            if count_covered_nodes == len(neighbor_node_neighbors):
                neighbors_seed_set.append(neighbor_node)
                all_infected_nodes.append(neighbor_node)
                covered_nodes[neighbor_node] = 1
                count_coverage += 1
                map_vertices[neighbor_node] = 0
            else:
                infected_queue.append(neighbor_node)
                neighbors_seed_set.append(neighbor_node)
                covered_nodes[neighbor_node] = 1
                count_coverage += 1
                map_vertices[neighbor_node] = 0
                all_infected_nodes.append(neighbor_node)
                (map_vertices, covered_nodes, all_infected_nodes, count_coverage) = \
                    run_BFS(G, threshold, infected_queue, map_vertices, covered_nodes,
                            all_infected_nodes, count_coverage)
                infected_queue = []

    #if (len(neighbors_seed_set) > 0):
    #    count_coverage /= len(neighbors_seed_set)
    return (all_infected_nodes, count_coverage, map_vertices, covered_nodes,
            neighbors_seed_set)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate coverage")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--path', help='Path for graph')
    group.add_argument('--graph', help='Networkx Graph')
    parser.add_argument('--source_node1', type=str, help='First infected node')
    parser.add_argument('--threshold', type=int, help='Threshold')
    args = parser.parse_args()
    if args.path:
        coverage(args.path, args.source_node1, args.threshold)
    if args.graph:
        coverage(args.graph, args.source_node1. args.threshold)
