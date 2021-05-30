import cvxpy as cp
import numpy as np
import networkx as nx
from baseline import minimal_coverage_set 
from coverage_final_algo_combined import readGraph, run_BFS


def cardinality(G, threshold, S):
    return len(S)

def influence(G, threshold, seed_set):
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
    return len(infected_nodes)

def lovasz_function(G, w, func, nodes, threshold):
    lambda_val =  np.random.rand(1)

    w_sort = np.sort(w.value, axis=None)
    w_indices = np.argsort(w.value, axis=None)
    w_indices = w_indices[::-1]
    w_sort = w_sort[::-1]
    x = np.zeros((len(nodes),1))
    F_prev = func(G, threshold, [])
    S = [];
    w_final = np.zeros((len(nodes), 1))
    for i in range(len(nodes)):
        if not S:
            S_new = [nodes[w_indices[i]]]
        else:
            S_new = S + [nodes[w_indices[i]]]
        #neighbors = list(G.neighbors(nodes[w_indices[i]]))
        #S_new = S_new + neighbors
        x[w_indices[i]] = func(G, threshold, set(S_new)) - F_prev
        S = S_new
        F_prev = F_prev + x[w_indices[i]]
        if w.value[i] > lambda_val:
            w.value[i] = 1
        else:
            w.value[i] = 0
    return cp.matmul(w.T, x)
V = 500
threshold = 8

G = nx.barabasi_albert_graph(500, 480)
nodes = list(G.nodes)
w1 = cp.Variable((len(nodes),1))
w1.value = np.random.rand(len(nodes),1)
w2 = cp.Variable((len(nodes),1))
w2.value = np.random.rand(len(nodes),1)
constraint_list = []
for i in range(len(nodes)):
    constraint_list.append(w1[i] >= 0)
    constraint_list.append(w1[i] <= 1)

objective = cp.Minimize(-lovasz_function(G, w1, influence, nodes, threshold)+lovasz_function(G, w1, cardinality, nodes, threshold))
#objective = cp.Minimize(lovasz_function(G, w1, cardinality, nodes, threshold))
constraint_list.append(lovasz_function(G, w1, influence, nodes, threshold) == len(nodes))
prob = cp.Problem(objective, constraint_list)
prob.solve(verbose=True)
print (prob.value)
b = w1.value
seed_set_cvx1, _ = np.where(b>=0.5)
minimal_coverage_set(G, threshold)

ss_check = []
print ("seed set cvx1", seed_set_cvx1)
for node in seed_set_cvx1:
    ss_check.append(node)
    #neighbors = list(G.neighbors(node))
    #ss_check = ss_check + neighbors
print ("ss check", len(ss_check))
print ("influence", influence(G, threshold, ss_check))
