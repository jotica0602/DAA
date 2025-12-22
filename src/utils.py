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