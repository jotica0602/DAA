import networkx as nx
from utils import get_cost


def seleccionar_raiz(T: nx.Graph):
    '''
    Selecciona una raíz para el árbol, preferiblemente una hoja.
    Retorna un vértice hoja si existe, o cualquier vértice.
    '''
    # Buscar hojas (vértices con grado 1)
    hojas = [v for v in T.nodes() if T.degree(v) == 1]
    if hojas:
        return hojas[0]
    # Si no hay hojas, retornar cualquier vértice
    return next(iter(T.nodes()))


def camino_fundamental(T: nx.Graph, v: int, u: int):
    '''
    Retorna el único camino entre v y u en el árbol T.
    '''
    try:
        return nx.shortest_path(T, v, u)
    except nx.NetworkXNoPath:
        return []


def arista_mas_costosa(T: nx.Graph, camino: list):
    '''
    Retorna la arista más costosa en el camino dado.
    Retorna (u, v, peso) de la arista más costosa.
    '''
    if len(camino) < 2:
        return None
    
    max_weight = -float('inf')
    max_edge = None
    
    for i in range(len(camino) - 1):
        u, v = camino[i], camino[i + 1]
        if T.has_edge(u, v):
            weight = T[u][v]['weight']
            if weight > max_weight:
                max_weight = weight
                max_edge = (u, v, weight)
    
    return max_edge


def CH_Heuristic(G: nx.Graph, degree_bounds: dict):
    '''
    Implementa la heurística CH (Camerini-Heuristic) para árbol abarcador de costo mínimo 
    con restricción de grados.
    
    :param G: Grafo con nodos V y aristas E con pesos
    :param degree_bounds: Diccionario que mapea cada vértice v a su límite máximo de grado b(v)
    :return: Tupla (costo, árbol generador mínimo factible T)
    '''
    # 1. Construcción inicial
    T = nx.minimum_spanning_tree(G)
    
    # 2. Seleccionar raíz (preferiblemente una hoja)
    r = seleccionar_raiz(T)
    
    # 3. Marcar todos los vértices como NO_PROCESADOS
    procesados = set()
    
    # 4. Recorrido del árbol (DFS)
    orden = list(nx.dfs_preorder_nodes(T, source=r))
    
    # 5. Ajuste de grados
    for v in orden:
        # Marcar v como PROCESADO
        procesados.add(v)
        
        # Mientras el grado de v exceda su límite
        while T.degree(v) > degree_bounds[v]:
            mejor_intercambio = None
            mejor_delta = float('inf')
            
            # Evaluar cuerdas incidentes (aristas en G \ T que inciden en v)
            for u in G.neighbors(v):
                # Verificar que la arista (v, u) no esté en T
                if T.has_edge(v, u):
                    continue
                
                # Si u ya está en su límite de grado, no podemos agregar más aristas
                if T.degree(u) >= degree_bounds[u]:
                    continue
                
                # Obtener el camino fundamental entre v y u en T
                camino = camino_fundamental(T, v, u)
                if not camino or len(camino) < 2:
                    continue
                
                # Encontrar la arista más costosa en el camino
                e_max = arista_mas_costosa(T, camino)
                if e_max is None:
                    continue
                
                e_max_u, e_max_v, w_e_max = e_max
                
                # Si e_max incide en v, continuar (no queremos remover aristas incidentes a v)
                if e_max_u == v or e_max_v == v:
                    continue
                
                # Verificar que al remover e_max, el extremo no quede por debajo de su límite mínimo
                # En el contexto de nuestro problema, esto verifica que al remover e_max,
                # el extremo mantenga grado >= 1 (mínimo para mantener conectividad)
                extremo_e_max = e_max_u if e_max_u != v else e_max_v
                
                # Verificar que al remover e_max, el extremo mantenga grado >= 1
                if T.degree(extremo_e_max) - 1 < 1:
                    continue
                
                # Calcular el delta (cambio en el costo)
                w_vu = G[v][u]['weight']
                delta = w_vu - w_e_max
                
                # Si este intercambio es mejor, actualizar
                if delta < mejor_delta:
                    mejor_delta = delta
                    mejor_intercambio = (e_max, (v, u, w_vu))
            
            # Si no se encontró un intercambio válido, salir del loop
            if mejor_intercambio is None:
                break
            
            # Aplicar el intercambio
            e_max, nueva_arista = mejor_intercambio
            e_max_u, e_max_v, _ = e_max
            v_nuevo, u_nuevo, w_nuevo = nueva_arista
            
            # Remover la arista más costosa y agregar la nueva
            T.remove_edge(e_max_u, e_max_v)
            T.add_weighted_edges_from([(v_nuevo, u_nuevo, w_nuevo)])
    
    # Retornar el árbol resultante
    costo_final = get_cost(T)
    return costo_final, T

