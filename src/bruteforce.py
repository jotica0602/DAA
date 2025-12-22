import networkx as nx
from itertools import combinations
from utils import *

def bruteforce(G:nx.Graph,degree_bound) -> tuple[int,nx.Graph]: # O(2^m), m = |E|
    '''
    :param G: instancia a resolver
    :param degree_bound: mapeo de las restricciones de grado para cada vértice.
    
    Construye un grafo a partir del conjunto de aristas y obtiene el DC-MST.
    '''

    n = len(G.nodes)
    m = len(G.edges)
    min_cost = float('inf') # fijamos una cota superior para podas
    best_edges = None  # Guardamos solo las aristas de la mejor solución, no el árbol completo

    # probamos todas las combinaciones posibles a escoger del conjunto de aristas
    for k in range(1,m+1):
        for comb in combinations(G.edges.data(),k):
            # creamos un grafo por cada combinación
            T = nx.Graph()
            T.add_nodes_from(G)
            T.add_edges_from([(u,v,w) for u,v,w in comb])
            actual_cost = get_cost(T)                   # obtenemos el costo de aristas del grafo craedo con esta combinación
            if len(T.edges) < n - 1: continue           # las combinaciones de aristas con menos de n-1 las descartamos
            if actual_cost >= min_cost: continue        # podamos aquellas soluciones que excedan nuestra mejor solución
            if nx.is_tree(T) and is_feasable(degree_bound,T):    # si el costo es potencialmente mejor que el mejor costo obtenido, verificamos que sea un árbol y que se cumpla la restricción de grado 
                min_cost = get_cost(T)
    return min_cost,T