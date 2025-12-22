'''
Funciones de utilidad
- set_of(x,parent): devuelve el representante de la clase de equivalencia de x.
- merge(x,y,parent): une las clases de equivalencia de x e y si no son la misma.

- get_cost(G): calcula el costo de las aristas del grafo que recibe como parámetro.
- is_feasable(T,degree_bounds): devuelve True si todos los vértices del árbol respetan su restricción de grado.
'''

import networkx as nx

def set_of(x,parent):
    if parent[x] == x: return x
    parent[x] = set_of(parent[x],parent)
    return parent[x]

def merge(x,y,parent):
    px,py = set_of(x,parent),set_of(y,parent)
    if px == py: return False
    parent[py] = px
    return True

def get_cost(G:nx.Graph):
    '''
    Calcula el costo de un grafo sumando los pesos de todas sus aristas.
    '''
    return sum(w['weight'] for _,_,w in G.edges.data())

def is_feasable(degree_bound,T:nx.Graph):
    '''
    Verifica que cada nodo del árbol cumpla con la restricción de grado.
    '''
    return all(T.degree(node) <= degree_bound[node] for node in T)