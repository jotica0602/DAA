import networkx as nx
from test import get_cost


def select_excess_edges(T: nx.Graph, v: int, limite: int):
    '''
    Retorna la lista de aristas incidentes de v que exceden 'limite'.
    Si el grado de v es mayor que limite, retorna las aristas que están "de más".
    Las aristas se ordenan por peso (de mayor a menor) para optimizar.
    '''
    grado_actual = T.degree(v)
    if grado_actual <= limite:
        return []
    
    # Calculamos cuántas aristas debemos remover
    exceso = grado_actual - limite
    
    # Obtenemos todas las aristas incidentes a v con sus pesos
    aristas_incidentes = []
    for neighbor in T.neighbors(v):
        peso = T[v][neighbor]['weight']
        # Guardamos como (v, neighbor, peso) para facilitar el manejo
        aristas_incidentes.append((v, neighbor, peso))
    
    # Ordenamos por peso descendente (las más pesadas primero) para optimizar
    aristas_incidentes.sort(key=lambda x: x[2], reverse=True)
    
    # Retornamos las primeras 'exceso' aristas (las más pesadas)
    return aristas_incidentes[:exceso]


def find_replacement_edge(T: nx.Graph, e: tuple, G: nx.Graph, degree_bounds: dict, violador: int = None):
    '''
    Busca una arista (x,y) en G \ T que:
    1. Conecte componentes separadas si quitamos e
    2. No haga que ningún nodo exceda su grado
    3. Si violador está especificado, garantiza que el reemplazo reduzca el grado del violador
    4. Preferiblemente, con costo mínimo
    Retorna None si no hay reemplazo seguro, o (x, y, peso) si lo encuentra.
    
    :param e: Tupla (u, v, peso) representando la arista a reemplazar
    :param violador: Nodo violador (opcional). Si se especifica, el reemplazo debe reducir su grado.
    '''
    u, v = e[0], e[1]
    
    # Removemos temporalmente la arista e del árbol
    T_temp = T.copy()
    if T_temp.has_edge(u, v):
        T_temp.remove_edge(u, v)
    else:
        return None
    
    # Obtenemos las componentes conexas después de remover e
    components = list(nx.connected_components(T_temp))
    if len(components) != 2:
        return None
    
    # Encontramos a qué componente pertenece cada nodo
    comp_u = next(c for c in components if u in c)
    comp_v = next(c for c in components if v in c)
    
    # Buscamos aristas en G que conecten las dos componentes
    best_candidate = None
    best_cost = float('inf')
    
    # Buscamos aristas que conecten nodos de comp_u con nodos de comp_v
    for node_u in comp_u:
        for node_v in comp_v:
            # Verificamos si existe una arista en G entre estos nodos
            # y que no esté ya en T_temp
            if G.has_edge(node_u, node_v) and not T_temp.has_edge(node_u, node_v):
                w_candidate = G[node_u][node_v]['weight']
                
                # Verificamos que al agregar esta arista, no se excedan los límites de grado
                # Para node_u: su grado actual en T_temp + 1 debe ser <= degree_bounds[node_u]
                # Para node_v: su grado actual en T_temp + 1 debe ser <= degree_bounds[node_v]
                grado_u_temp = T_temp.degree(node_u)
                grado_v_temp = T_temp.degree(node_v)
                
                if (grado_u_temp + 1 <= degree_bounds[node_u] and 
                    grado_v_temp + 1 <= degree_bounds[node_v]):
                    
                    # Si se especificó un violador, verificamos que el reemplazo reduzca su grado
                    if violador is not None:
                        # El violador debe ser u o v (uno de los extremos de la arista removida)
                        # Para que el grado del violador se reduzca, la nueva arista NO debe tener
                        # al violador como extremo (porque entonces su grado no cambiaría)
                        if violador == u:
                            # Si removemos (u, v) y u es el violador, la nueva arista (node_u, node_v)
                            # no debe tener a u como extremo. Como u está en comp_u, verificamos node_u
                            if node_u == violador or node_v == violador:
                                continue
                        elif violador == v:
                            # Si removemos (u, v) y v es el violador, la nueva arista (node_u, node_v)
                            # no debe tener a v como extremo. Como v está en comp_v, verificamos node_v
                            if node_u == violador or node_v == violador:
                                continue
                    
                    # Preferimos la arista de menor costo
                    if w_candidate < best_cost:
                        best_cost = w_candidate
                        best_candidate = (node_u, node_v, w_candidate)
    
    return best_candidate


def AH_Heuristic(G: nx.Graph, degree_bounds: dict, C_max: float = None):
    '''
    Implementa la heurística AH para árbol abarcador de costo mínimo con restricción de grados.
    
    :param G: Grafo con nodos V y aristas E con pesos
    :param degree_bounds: Diccionario que mapea cada vértice v a su límite máximo de grado d(v)
    :param C_max: Cota superior de costo (opcional). Si se proporciona, se revierten cambios que excedan esta cota.
    :return: Tupla (costo, árbol generador mínimo factible T)
    '''
    # 1. Construir árbol generador mínimo inicial (sin restricción de grado)
    T = nx.minimum_spanning_tree(G)
    
    # 2. Detectar nodos que violan la restricción de grado
    violadores = {v for v in T.nodes() if T.degree(v) > degree_bounds[v]}
    
    # 3. Ajustar el árbol para cumplir restricciones de grado
    max_iterations = len(G.nodes()) * len(G.edges())  # Límite para evitar loops infinitos
    iteration = 0
    cambios_en_iteracion = False
    
    while violadores and iteration < max_iterations:
        iteration += 1
        violadores_previo = violadores.copy()
        cambios_en_iteracion = False
        
        for v in list(violadores):
            # Seleccionar aristas incidentes que exceden el límite
            exceso = select_excess_edges(T, v, degree_bounds[v])
            
            # Intentar reemplazar todas las aristas excedentes, no solo la primera
            reemplazo_exitoso = False
            for edge_tuple in exceso:
                # edge_tuple es (u, v_node, peso)
                u, v_node, w_e = edge_tuple
                e = (u, v_node, w_e)
                
                # Buscar arista alternativa para reemplazar
                # Pasamos v como violador para asegurar que el reemplazo reduzca su grado
                candidate = find_replacement_edge(T, e, G, degree_bounds, violador=v)
                
                if candidate is not None:
                    x, y, w_candidate = candidate
                    
                    # Verificar que el reemplazo realmente reduzca el grado del violador
                    grado_antes = T.degree(v)
                    
                    # Reemplazar arista en el árbol
                    T.remove_edge(u, v_node)
                    T.add_weighted_edges_from([(x, y, w_candidate)])
                    
                    # Verificar que el grado del violador se redujo
                    grado_despues = T.degree(v)
                    
                    if grado_despues < grado_antes:
                        # El reemplazo fue exitoso y redujo el grado del violador
                        cambios_en_iteracion = True
                        reemplazo_exitoso = True
                        
                        # Revisar costo total
                        costo_despues = get_cost(T)
                        
                        # Si C_max está definido, NO debemos excederlo nunca
                        # El objetivo es encontrar un árbol factible con costo menor que C_max
                        # Si un cambio excede C_max, lo revertimos inmediatamente
                        if C_max is not None and costo_despues > C_max:
                            # Revertir cambio si excede la cota superior
                            T.remove_edge(x, y)
                            T.add_weighted_edges_from([(u, v_node, w_e)])
                            cambios_en_iteracion = False
                            reemplazo_exitoso = False
                        else:
                            # Reemplazo exitoso, continuar con la siguiente arista excedente
                            # si el violador aún viola las restricciones
                            if T.degree(v) <= degree_bounds[v]:
                                # El violador ya no viola, salir del loop de exceso
                                break
                    else:
                        # El reemplazo no redujo el grado del violador, revertir
                        T.remove_edge(x, y)
                        T.add_weighted_edges_from([(u, v_node, w_e)])
            
            # Si no se hizo ningún reemplazo exitoso para este violador, continuar con el siguiente
        
        # Actualizar lista de violadores
        violadores = {v for v in T.nodes() if T.degree(v) > degree_bounds[v]}
        
        # Si no hay cambios en los violadores Y no hubo cambios en esta iteración
        # Intentar una iteración más con una estrategia diferente: permitir reemplazos
        # que no reduzcan el grado del violador pero que puedan abrir nuevas posibilidades
        if violadores == violadores_previo and not cambios_en_iteracion:
            # Último intento: intentar reemplazos sin la restricción del violador
            # para ver si podemos encontrar una solución
            cambios_ultimo_intento = False
            for v in list(violadores):
                exceso = select_excess_edges(T, v, degree_bounds[v])
                for edge_tuple in exceso:
                    u, v_node, w_e = edge_tuple
                    e = (u, v_node, w_e)
                    # Intentar sin pasar el violador para ser menos restrictivo
                    candidate = find_replacement_edge(T, e, G, degree_bounds, violador=None)
                    if candidate is not None:
                        x, y, w_candidate = candidate
                        grado_antes = T.degree(v)
                        T.remove_edge(u, v_node)
                        T.add_weighted_edges_from([(x, y, w_candidate)])
                        grado_despues = T.degree(v)
                        # Aceptar si reduce el grado o si no lo aumenta mucho
                        if grado_despues <= grado_antes:
                            cambios_ultimo_intento = True
                            break
                if cambios_ultimo_intento:
                    break
            
            if not cambios_ultimo_intento:
                break
    
    # Retornar árbol factible
    costo_final = get_cost(T)
    return costo_final, T

