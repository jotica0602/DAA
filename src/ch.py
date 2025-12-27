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


def encontrar_y_aplicar_reemplazo(T, violador, vecino, G, degree_bounds):
    """
    Intenta encontrar y aplicar un reemplazo de arista que reduzca
    el grado del violador. Similar a get_replacement_edge del método dual.
    
    :param T: Árbol actual
    :param violador: Nodo que viola la restricción de grado
    :param vecino: Vecino del violador cuya arista se considera remover
    :param G: Grafo original completo
    :param degree_bounds: Restricciones de grado
    :return: True si se encontró y aplicó un reemplazo, False en caso contrario
    """
    if not T.has_edge(violador, vecino):
        return False
    
    w_eij = T[violador][vecino]['weight']
    deg_vecino = T.degree(vecino)
    
    # Crear copia temporal para probar el reemplazo
    T_temp = T.copy()
    T_temp.remove_edge(violador, vecino)
    
    # Obtener componentes conexas después de remover la arista
    componentes = list(nx.connected_components(T_temp))
    if len(componentes) != 2:
        return False
    
    cc_violador = componentes[0] if violador in componentes[0] else componentes[1]
    cc_vecino = componentes[1] if violador in componentes[0] else componentes[0]
    
    mejor_reemplazo = None
    mejor_delta = float('inf')
    
    # Buscar arista de reemplazo válida
    for s in cc_vecino:
        for r in G.neighbors(s):
            if r in cc_vecino:
                continue
            if not G.has_edge(r, s):
                continue
            if T.has_edge(r, s):
                continue
            
            w_ers = G[r][s]['weight']
            delta = w_ers - w_eij
            
            # Verificar que no cause nuevas violaciones
            r_is_valid = T.degree(r) + 1 <= degree_bounds[r]
            s_is_valid = (s == vecino and deg_vecino <= degree_bounds[vecino]) or (T.degree(s) + 1 <= degree_bounds[s])
            
            if r_is_valid and s_is_valid and delta < mejor_delta:
                mejor_delta = delta
                mejor_reemplazo = (r, s, w_ers)
    
    # Aplicar el mejor reemplazo si existe
    if mejor_reemplazo is not None:
        r, s, w_ers = mejor_reemplazo
        T.remove_edge(violador, vecino)
        T.add_weighted_edges_from([(r, s, w_ers)])
        return True
    
    return False


def CH_Heuristic(G: nx.Graph, degree_bounds: dict, ub: float = None):
    '''
    Implementa la heurística CH (Camerini-Heuristic) para árbol abarcador de costo mínimo 
    con restricción de grados.
    
    :param G: Grafo con nodos V y aristas E con pesos
    :param degree_bounds: Diccionario que mapea cada vértice v a su límite máximo de grado b(v)
    :param ub: Cota superior opcional. Si se proporciona, la búsqueda puede terminar cuando el costo excede esta cota.
    :return: Tupla (costo, árbol generador mínimo factible T)
    '''
    # 1. Construcción inicial
    T = nx.minimum_spanning_tree(G)
    
    # Inicializar peso de construcción actual (omega)
    omega = get_cost(T)
    
    # 2. Seleccionar raíz (preferiblemente una hoja)
    r = seleccionar_raiz(T)
    
    # 3. Marcar todos los vértices como NO_PROCESADOS
    procesados = set()

    # Marcar la raíz como procesada
    procesados.add(r)
    
    # Seleccionar una hoja distinta de la raíz que no esté marcada
    hojas = [v for v in T.nodes() if T.degree(v) == 1 and v != r and v not in procesados]
    if hojas:
        hoja_inicial = hojas[0]
    else:
        hoja_inicial = None
    
    # Recorrer desde la hoja inicial hasta la raíz y marcar todos los vértices del camino
    if hoja_inicial is not None:
        camino_hoja_raiz = camino_fundamental(T, hoja_inicial, r)
        if camino_hoja_raiz:
            # Marcar todos los vértices del camino como procesados
            for v_camino in camino_hoja_raiz:
                procesados.add(v_camino)
    
    # 4. Ajuste de grados - bucle principal que continúa hasta resolver todas las violaciones
    # Después de cada intercambio, el árbol cambia y pueden aparecer nuevas hojas no marcadas
    max_iterations = len(G.nodes()) * len(G.nodes())  # Límite para evitar loops infinitos
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Verificar si hay violaciones
        violadores = {v for v in T.nodes() if T.degree(v) > degree_bounds[v]}
        if not violadores:
            # No hay más violaciones, terminar
            break
        
        # Crear cola con vértices de grado 1 no marcados
        cola_hojas = [v for v in T.nodes() if T.degree(v) == 1 and v not in procesados]
        
        # Si no hay más hojas no marcadas, verificar condiciones de terminación
        if not cola_hojas:
            # Verificar si todos los vértices están marcados Y no hay violaciones
            todos_marcados = len(procesados) == len(T.nodes())
            if todos_marcados and not violadores:
                # Todos visitados y sin violaciones, terminar correctamente
                break
            
            # Si aún hay violaciones, cambiar a estrategia alternativa
            # (procesamiento directo de violadores, similar al método dual)
            if violadores:
                cambio_estategia = True
                cambio_realizado_estrategia = False
                
                while cambio_estategia and violadores:
                    cambio_estategia = False
                    for violador in list(violadores):
                        if T.degree(violador) > degree_bounds[violador]:
                            # Intentar reducir grado del violador
                            for vecino in list(T.neighbors(violador)):
                                if encontrar_y_aplicar_reemplazo(T, violador, vecino, G, degree_bounds):
                                    cambio_estategia = True
                                    cambio_realizado_estrategia = True
                                    # Marcar el violador y sus vecinos si se resolvió
                                    if T.degree(violador) <= degree_bounds[violador]:
                                        procesados.add(violador)
                                    break
                    
                    # Actualizar lista de violadores
                    violadores = {v for v in T.nodes() if T.degree(v) > degree_bounds[v]}
                
                # Si se realizaron cambios con la estrategia alternativa, continuar
                if cambio_realizado_estrategia:
                    cambio_realizado = True
                    continue
                else:
                    # No se pudo hacer más cambios, terminar
                    break
            else:
                # No hay violaciones pero no todos están marcados
                # Marcar los vértices restantes
                for v in T.nodes():
                    if v not in procesados:
                        procesados.add(v)
                break
        
        # 5. Ajuste de grados - iterar sobre vértices de grado 1 no marcados
        cambio_realizado = False
        terminar_busqueda = False
        for v in cola_hojas:
            # Buscar el camino entre v y la raíz
            camino_v_raiz = camino_fundamental(T, v, r)
            
            # Recorrer el camino desde v hacia la raíz hasta encontrar el primer nodo marcado
            nodo_marcado = None
            nodo_anterior_marcado = None
            indice_nodo_marcado = None
            for i, nodo in enumerate(camino_v_raiz):
                if nodo in procesados:
                    nodo_marcado = nodo
                    indice_nodo_marcado = i
                    # Guardar el último nodo antes del nodo marcado
                    if i > 0:
                        nodo_anterior_marcado = camino_v_raiz[i - 1]
                    break
            
            # Si no se encontró ningún nodo marcado, marcar todos los nodos del camino hasta la raíz
            if nodo_marcado is None:
                # Marcar todos los nodos del camino desde v hasta la raíz
                for nodo_camino in camino_v_raiz:
                    procesados.add(nodo_camino)
                continue
            
            # Revisar el grado actual del nodo marcado
            if T.degree(nodo_marcado) <= degree_bounds[nodo_marcado]:
                # Si el grado es menor o igual a la restricción, marcar todos los nodos desde v hasta el nodo marcado
                # Usar el subcamino del camino_v_raiz desde v hasta nodo_marcado (incluyendo ambos)
                subcamino = camino_v_raiz[:indice_nodo_marcado + 1]
                # Marcar todos los nodos del subcamino (incluyendo v y nodo_marcado)
                for nodo_camino in subcamino:
                    procesados.add(nodo_camino)
                continue  # Continuar con el siguiente vértice de la cola
            
            
            # Si el grado del nodo marcado viola la restricción, proceder con el intercambio
            # p1 = v (vértice no marcado con grado 1, ya seleccionado)
            # p3 = nodo_marcado (vértice previamente marcado alcanzado desde p1)
            
            # Marcar p1 y todos los nodos del camino desde p1 hasta p3
            subcamino_p1_p3 = camino_v_raiz[:indice_nodo_marcado + 1]
            nodos_marcados_iteracion = set()
            for nodo_camino in subcamino_p1_p3:
                procesados.add(nodo_camino)
                nodos_marcados_iteracion.add(nodo_camino)
            
            # Obtener TODOS los vértices marcados adyacentes a p3
            vecinos_marcados = [vecino for vecino in T.neighbors(nodo_marcado) if vecino in procesados]
            
            # Verificar que tenemos al menos un vecino marcado
            if len(vecinos_marcados) < 1:
                continue  # Si no hay vecinos marcados, continuar
            
            p3 = nodo_marcado
            p1 = v
            
            # Verificar que existe el nodo anterior a p3 en el camino
            if nodo_anterior_marcado is None:
                continue
            
            # p es el nodo que viene justo antes de p3 en el camino desde p1 hasta la raíz
            p = nodo_anterior_marcado
            
            # Si p3 viola la restricción de grado, realizar UN intercambio
            # Se considera remover ⟨vecino, p3⟩ para cada vecino marcado de p3
            # y reemplazar por ⟨vecino, p⟩ donde p es el nodo anterior a p3
            # Se elige el mejor intercambio entre todas las opciones
            # Cada iteración del bucle externo reduce el grado de p3 en 1
            
            if T.degree(p3) > degree_bounds[p3]:
                mejor_intercambio = None
                mejor_delta = float('inf')
                
                # Considerar TODOS los vecinos marcados de p3
                # Para cada vecino marcado, considerar remover ⟨vecino, p3⟩ y reemplazar por ⟨vecino, p⟩
                for vecino in vecinos_marcados:
                    # Verificar que existe la arista ⟨vecino, p3⟩
                    if not T.has_edge(vecino, p3):
                        continue
                    
                    w_remover = T[vecino][p3]['weight']
                    
                    # Considerar ⟨vecino, p⟩ donde p es el nodo anterior a p3
                    if not G.has_edge(vecino, p):
                        continue
                    if T.has_edge(vecino, p):
                        continue
                    
                    # Verificar que agregar la arista no cause violación de grado
                    if T.degree(vecino) >= degree_bounds[vecino]:
                        continue
                    if T.degree(p) >= degree_bounds[p]:
                        continue
                    
                    # Verificar que el intercambio mantenga la conectividad del árbol
                    # (remover ⟨vecino, p3⟩ y agregar ⟨vecino, p⟩ debe resultar en un árbol)
                    T_temp = T.copy()
                    T_temp.remove_edge(vecino, p3)
                    T_temp.add_weighted_edges_from([(vecino, p, G[vecino][p]['weight'])])
                    
                    # Verificar que sigue siendo conexo (árbol)
                    if not nx.is_connected(T_temp):
                        continue
                    
                    # Calcular el delta (cambio en el costo)
                    w_nueva = G[vecino][p]['weight']
                    delta = w_nueva - w_remover
                    
                    # Si este intercambio es mejor, actualizar
                    if delta < mejor_delta:
                        mejor_delta = delta
                        mejor_intercambio = ((vecino, p3), (vecino, p, w_nueva))
                
                # Si se encontró un intercambio válido, aplicarlo
                if mejor_intercambio is not None:
                    # Aplicar el intercambio
                    arista_remover, nueva_arista = mejor_intercambio
                    origen_rem, destino_rem = arista_remover
                    origen_nuevo, destino_nuevo, w_nuevo = nueva_arista
                    
                    # Remover la arista antigua y agregar la nueva
                    T.remove_edge(origen_rem, destino_rem)
                    T.add_weighted_edges_from([(origen_nuevo, destino_nuevo, w_nuevo)])
                    
                    # Actualizar omega (peso de construcción actual)
                    omega += mejor_delta
                    cambio_realizado = True
                    
                    # Verificar criterio de parada con ub
                    if ub is not None and omega > ub:
                        # Verificar si hay violaciones en todo el árbol
                        # Si hay violaciones, continuar porque la próxima iteración podría disminuir omega
                        violadores_actuales = {v for v in T.nodes() if T.degree(v) > degree_bounds[v]}
                        if not violadores_actuales:
                            # No hay violaciones, terminar búsqueda: salir del bucle externo
                            terminar_busqueda = True
                            break
        
        # Si se debe terminar la búsqueda, salir
        if terminar_busqueda:
            break
        
        # Si no se realizó ningún cambio en esta iteración, verificar condiciones
        if not cambio_realizado:
            # Verificar si aún hay violaciones
            violadores_restantes = {v for v in T.nodes() if T.degree(v) > degree_bounds[v]}
            todos_marcados = len(procesados) == len(T.nodes())
            
            if violadores_restantes:
                # Aún hay violaciones pero no se pudo hacer ningún cambio con hojas
                # Intentar estrategia alternativa (procesamiento directo de violadores)
                cambio_estategia = True
                cambio_realizado_estrategia = False
                
                while cambio_estategia and violadores_restantes:
                    cambio_estategia = False
                    for violador in list(violadores_restantes):
                        if T.degree(violador) > degree_bounds[violador]:
                            for vecino in list(T.neighbors(violador)):
                                if encontrar_y_aplicar_reemplazo(T, violador, vecino, G, degree_bounds):
                                    cambio_estategia = True
                                    cambio_realizado_estrategia = True
                                    if T.degree(violador) <= degree_bounds[violador]:
                                        procesados.add(violador)
                                    break
                    
                    violadores_restantes = {v for v in T.nodes() if T.degree(v) > degree_bounds[v]}
                
                # Si se realizaron cambios, continuar en la siguiente iteración
                if cambio_realizado_estrategia:
                    continue
                else:
                    # No se puede hacer más cambios, terminar
                    break
            elif todos_marcados:
                # No hay violaciones y todos están marcados, terminar correctamente
                break
            else:
                # No hay violaciones pero no todos están marcados, marcar los restantes
                for v in T.nodes():
                    if v not in procesados:
                        procesados.add(v)
                break
    
    # Retornar el árbol resultante
    # Calcular el costo final para asegurar precisión (omega puede tener errores de redondeo acumulados)
    costo_final = get_cost(T)
    return costo_final, T

