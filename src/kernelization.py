import heapq
import networkx as nx
from utils import *

def reduction_dcmst(G:nx.Graph,degree_bounds):
    '''
    :param G: Grafo inicial
    :type G: nx.Graph
    :param degree_bounds: restricciones de grado para cada vértice

    Devuelve un grafo T_star candidato a conectar para hallar un DCST
    '''
    G = G.copy()
    if len(G) <= 2: return G,G
    # Inicialización
    T_star = nx.Graph()
    T_star.add_nodes_from(G)
    
    changed = True
    while changed:
        changed = False
        # Paso 1: Teorema 2
        to_remove = set()
        for u,v,_ in G.edges.data():
            if degree_bounds[u] == degree_bounds[v] == 1:
                to_remove.add((u,v))
                changed = True
        G.remove_edges_from(to_remove)
        to_remove.clear()
    
        # Paso 2: Teorema 1
        for u in G:
            if G.degree(u) == 1:
                v = list(G.neighbors(u))[0]
                T_star.add_edge(u,v,weight=G[u][v]['weight'])
                G.remove_edge(u,v)
                to_remove.add(u)
                changed = True
        G.remove_nodes_from(to_remove)
        to_remove.clear()

        # Paso 3: Teorema 3
        for vk in G:
            if G.degree(vk) != 2: continue
            vi,vj = G.neighbors(vk)
            G_prime = G.copy()
            G_prime.remove_node(vk)
            if not nx.has_path(G_prime,vi,vj):
                T_star.add_edge(vi,vk,weight=G[vi][vk]['weight'])
                T_star.add_edge(vj,vk,weight=G[vj][vk]['weight'])
                G.remove_edge(vi,vk)
                G.remove_edge(vj,vk)
                to_remove.add(vk)
                changed = True
        G.remove_nodes_from(to_remove)
    return G,T_star

def kruskal_dcst(G:nx.Graph,T_star:nx.Graph,degree_bounds):
    uf = {v:v for v in T_star}
    for u,v in T_star.edges:
        merge(u,v,uf)

    q = [(w['weight'],u,v) for u,v,w in G.edges.data()]
    heapq.heapify(q)

    while q and len(T_star.edges) < len(T_star) - 1:
        w,u,v = heapq.heappop(q)
        if set_of(u,uf) == set_of(v,uf): continue 
        if T_star.degree(u) + 1 > degree_bounds[u]: continue 
        if T_star.degree(v) + 1 > degree_bounds[v]: continue
        merge(u,v,uf)
        T_star.add_edge(u,v,weight=w)

    return T_star