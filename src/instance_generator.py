import random
from collections import defaultdict
from utils import *

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