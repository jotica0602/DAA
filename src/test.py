import networkx as nx
from itertools import combinations
from collections import defaultdict
import heapq
import random
import time

def set_of(x,parent):
    if parent[x] == x: return x
    parent[x] = set_of(parent[x],parent)
    return parent[x]

def merge(x,y,parent):
    px,py = set_of(x,parent),set_of(y,parent)
    if px == py: return False
    parent[py] = px
    return True

# region Generador
def generate_instance(n,
                      edge_prob=0.4,
                      w_min=1,
                      w_max=10,
                      violation_prob=0.4,
                      seed=None) -> tuple[list[list[list[tuple]]],dict[int:int]]:
    '''
    :param n: cantidad de vértices del grafo
    :param edge_prob: probabilidad de que entre un par de vértices haya una arista
    :param w_min: costo mínimo de arista
    :param w_max: costo máximo de arista
    :param violation_prob: probabilidad de que un vértice viole su restricción de grado
    :param seed: semilla

    returns:
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

def is_feasable(degree_bound,T:nx.Graph):
    '''
    Verifica que cada nodo del árbol cumpla con la restricción de grado.
    '''
    return all(T.degree(node) <= degree_bound[node] for node in T)

# region Fuerza Bruta
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



# region Kernelización
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

# region Heurísticas    
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

# region Zona de Pruebas
G = nx.Graph()
G.add_weighted_edges_from([('a','b',5),('b','c',3),('c','e',1),('c','d',9),('c','f',4),('e','f',2),('f','d',17),('d','h',8),('h','g',3),('g','i',1),('g','j',5),('i','j',2)])
degree_bounds = {'e':1,'f':1,'a':2,'b':2,'d':2,'g':2,'h':2,'i':2,'j':2,'c':4}

G,T_star = reduction_dcmst(G,degree_bounds)
T_star = kruskal_dcst(G,T_star,degree_bounds)
print(nx.is_tree(T_star))
print(get_cost(T_star))


for _ in range(20):
    for i in range(2,100):
        edges,degree_bounds = generate_instance(i,seed=time.time())
        print(f'Test para {i} vértices y {len(edges)} aristas \n')
        # Construimos G
        G = nx.Graph()
        G.add_weighted_edges_from(edges)

        if len(G.edges) < len(G) - 1: 
            print('Hay menos aristas de las requeridas para que el grafo sea conexo.')
            continue 

        # Kernelización
        s = time.time()
        G_prime,T_star = reduction_dcmst(G,degree_bounds)
        T_star = kruskal_dcst(G_prime,T_star,degree_bounds)
        f = time.time()
        is_tree = nx.is_tree(T_star)
        is_ok = False
        if is_tree: is_ok = is_feasable(degree_bounds,T_star)
        kernelization_cost = get_cost(T_star)
        print(f'Kernelización: \n- costo: {kernelization_cost if is_tree and is_ok else float('inf')}\n- tiempo: {f-s}')

        # Dual Method
        T_star = nx.minimum_spanning_tree(G)
        s = time.time()
        T_star = dual_method(G,T_star,degree_bounds)
        f = time.time()
        is_tree = nx.is_tree(T_star)
        is_ok = False
        if is_tree: is_ok = is_feasable(degree_bounds,T_star)
        dual_cost = get_cost(T_star)
        print(f'Método Dual: \n- costo: {dual_cost if is_tree and is_ok else float('inf')}\n- tiempo: {f-s}')
        
        # Hallamos el costo por fuerza bruta
        # s = time.time()
        # bruteforce_cost,T2 = bruteforce(G,degree_bounds)
        # f = time.time()
        # print(f'Fuerza bruta:\n- costo: {bruteforce_cost} \n- tiempo: {f-s}\n')