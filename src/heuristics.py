import networkx as nx
from utils import *

def dual_method(G:nx.Graph, T_star:nx.Graph, degree_bounds):
        for i in T_star.nodes:
            if T_star.degree(i) <= degree_bounds[i]: continue
            while T_star.degree(i) > degree_bounds[i]:
                p = {}
                ers_exists = False

                for j in T_star.neighbors(i):
                    w_eij = T_star[i][j]['weight']
                    ers,pj = get_replacement_edge(i,j,w_eij,T_star.copy(),G,degree_bounds)
                    if ers is not None:
                        ers_exists = True
                        p[j] = (ers,pj)
                
                if not ers_exists: return T_star # No existe solución factible
                
                j,ers,pj = get_best_replacement_edge(p)
                r,s = ers
                w_ers = pj + w_eij
                T_star.remove_edge(i,j)
                T_star.add_weighted_edges_from([(r,s,w_ers)])

        return T_star
            
def get_replacement_edge(i,j, w_eij: int, MST: nx.Graph, G: nx.Graph, degree_bounds):
    best = float('inf')
    deg_j = MST.degree(j)
    MST.remove_edge(i,j)
    cc1,cc2 = nx.connected_components(MST)
    ccj = cc1 if j in cc1 else cc2
    ers = None
    for s in ccj:
        for r in G.neighbors(s):
            if r in ccj: continue
            w_ers = G[r][s]['weight']
            pj = w_ers - w_eij
            
            r_is_valid = MST.degree(r) + 1 <= degree_bounds[r]
            s_is_valid = (s == j and deg_j <= degree_bounds[j]) or MST.degree(s) + 1 <= degree_bounds[s]
            
            if pj < best and r_is_valid and s_is_valid:
                best = pj
                ers = (r,s)
    return ers, best

def get_best_replacement_edge(p:dict[tuple,int]):
    if len(p) == 0:
        print('No hay ningún j válido.')
        return
    best = float('inf')
    j = None
    for k in p:
        _,pj = p[k]
        if pj < best:
            j = k
    ers,pj = p[j]
    return j,ers,pj