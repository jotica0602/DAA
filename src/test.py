import networkx as nx
from itertools import combinations
from collections import defaultdict
import random
import time

def find(x,parent):
    if parent[x] == x: return x
    parent[x] = find(parent[x],parent)
    return parent[x]

def merge(x,y,parent):
    px,py = find(x,parent),find(y,parent)
    if px == py: return False
    parent[py] = px
    return True

def generate_instance(n,
                      edge_prob=0.4,
                      w_min=1,
                      w_max=10,
                      violation_prob=0.4,
                      seed=None):
    '''
    :param n: cantidad de vértices del grafo
    :param edge_prob: probabilidad de que entre un par de vértices haya una arista
    :param w_min: costo mínimo de arista
    :param w_max: costo máximo de arista
    :param violation_prob: probabilidad de que un vértice viole su restricción de grado
    :param seed: semilla
    '''
    if seed is not None:
        random.seed(seed)

    # generamos una lista con n vértices
    vertices = list(range(n))
    # los regamos
    random.shuffle(vertices)
    # inicializamos la lista de aristas
    edges = []
    # diccionario de padres
    parent = {i:i for i in range(n)}

    used = set() # conjunto de aristas usadas para no crear un multigrafo
    # por cada vertice del arbol escogemos uno que se encuentre antes que el en la lista de forma aleatoria y los conectamos por una arista de bajo costo
    for i in range(1,n):
        u = vertices[i]
        v = vertices[random.randint(0,i-1)]
        w = random.randint(w_min,w_min+2)
        merge(u,v,parent)   # lo unimos al arbol
        edges.append([u,v,w])
        t = tuple(sorted([u,v]))
        used.add(t)
    
    # agregamos aristas extra
    for i in range(n):
        for j in range(i+1,n):
            # si el numero aleatorio generado es menor que la probabilidad de que exista una arista entre ellos, creamos una
            t = tuple(sorted([i,j]))
            if not t in used and random.random() < edge_prob:
                w = random.randint(w_min + 3, w_max)
                edges.append([i,j,w])
    
    deg = defaultdict(int)
    # tomamos las primeras n-1 aristas agregadas (las del árbol base generado) y calculamos el grado inicial de sus vértices extremos
    for u,v,_ in edges[:n-1]:
        deg[u] += 1
        deg[v] += 1

    degree_bounds = defaultdict(int)
    # agregamos las restricciones de grados
    for i in range(n):
        # si el numero aleatorio sale por debajo de la probabilidad de violacion la forzamos haciendo que su restriccion de grado este entre 1 y su grado actual menos 1
        if random.random() < violation_prob and deg[i] > 1:
            degree_bounds[i] = random.randint(1,deg[i] - 1)
        # si sale por encima le permitimos tener numeros entre deg[i] y deg[i] + 2
        else:
            degree_bounds[i] = random.randint(deg[i],deg[i] + 2)

    return edges,degree_bounds

def get_cost(T:nx.Graph):
    '''
    Calcula el costo de un árbol sumando los pesos de todas sus aristas.
    '''
    return sum(w['weight'] for _,_,w in T.edges.data())

def ok(degree_bound,T:nx.Graph):
    '''
    Verifica que cada nodo del árbol cumpla con la restricción de grado.
    '''
    return all(T.degree(node) <= degree_bound[node] for node in T)

def get_dcmst(G:nx.Graph,degree_bound) -> tuple[int,nx.Graph]: # O(2^m), m = |E|
    '''
    :param G: instancia a resolver
    :param degree_bound: mapeo de las restricciones de grado para cada vértice.
    
    Construye un grafo a partir del conjunto de aristas y obtiene el DC-MST.
    '''

    m = len(G.edges)
    min_cost = float('inf') # fijamos una cota superior para podas

    # probamos todas las combinaciones posibles a escoger del conjunto de aristas
    for k in range(1,m+1):
        for comb in combinations(G.edges.data(),k):
            # creamos un grafo por cada combinación
            T = nx.Graph()
            T.add_nodes_from(G)
            T.add_edges_from([(u,v,w) for u,v,w in comb])
            actual_cost = get_cost(T)                   # obtenemos el costo de aristas del grafo craedo con esta combinación
            if actual_cost >= min_cost: continue        # podamos aquellas soluciones que excedan nuestra mejor solución
            if nx.is_tree(T) and ok(degree_bound,T):    # si el costo es potencialmente mejor que el mejor costo obtenido, verificamos que sea un árbol y que se cumpla la restricción de grado 
                min_cost = get_cost(T)
    return min_cost,T

def dual_method(G:nx.Graph, MST:nx.Graph, degree_bounds):
    for i in list(MST.nodes):
        if MST.degree(i) <= degree_bounds[i]: continue
        while MST.degree(i) > degree_bounds[i]:
            p = {}
            erj_exists = False
            for j in list(MST.neighbors(i)):
                w_eij = MST[i][j]['weight']
                MST.remove_edge(i,j)
                erj,pj = get_replacement_edge(j,w_eij,MST,G,degree_bounds)
                if erj is not None:
                    erj_exists |= True
                    p[j] = [erj,pj]
                MST.add_weighted_edges_from([(i,j,w_eij)])
            
            if not erj_exists: # No existe una solución
                return float('inf'),MST
            erj,pj = get_best_replacement_edge(p)
            r,j = erj
            MST.remove_edge(i,j)
            w_erj = pj + w_eij
            print(f'PJ: {pj} WERJ:{w_erj}')
            MST.add_weighted_edges_from([(r,j,w_erj)])
    return get_cost(MST), MST
            
def get_replacement_edge(j, w_eij: int, MST: nx.Graph, G: nx.Graph, degree_bounds):
    best = float('inf')
    components = list(nx.connected_components(MST))
    ccj = next(c for c in components if j in c)
    erj = None
    for r_ in G.neighbors(j):
        if r_ in ccj:
            continue
        w_erj = G[r_][j]['weight']
        pj = w_erj - w_eij
        if pj < best and MST.degree(r_) + 1 <= degree_bounds[r_]:
            best = pj
            erj = (r_, j)
    return erj, best

def get_best_replacement_edge(p:dict[tuple,int]):
    erj,pj = sorted(p.values(),key=lambda x:x[1])[0]
    return erj,pj 

if __name__ == "__main__":
    # Código de prueba - solo se ejecuta si se corre este archivo directamente
    # for i in range(2,12):
    #     edges,degree_bounds = generate_instance(i,seed=time.time())
    #     # print(f'Test para {i} vértices y {len(edges)} aristas \n')
    #     # Construimos G
    #     G = nx.Graph()
    #     G.add_weighted_edges_from(edges)
    #
    #     # Aplicamos dual method
    #     T = nx.minimum_spanning_tree(G)
    #     s = time.time()
    #     min_cost,T = dual_method(G,T,degree_bounds)
    #     f = time.time()
    #     # print(f'Dual method: \n- costo: {min_cost}\n- tiempo: {f-s}')
    #
    #     # Hallamos el costo por fuerza bruta
    #     s = time.time()
    #     min_cost,T = get_dcmst(G,degree_bounds)
    #     f = time.time()
    #     # print(f'Fuerza bruta:\n- costo: {min_cost} \n- tiempo: {f-s}\n')
    pass