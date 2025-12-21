import sys
import os
import time
import networkx as nx

# Agregar el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from test import generate_instance, get_cost, ok
from ah import AH_Heuristic


def calculate_c_max(G: nx.Graph):
    '''
    Calcula la cota superior como la suma de todos los costos de las aristas del grafo.
    '''
    return sum(w['weight'] for _, _, w in G.edges.data())


def test_ah_heuristic(n, edge_prob=0.4, w_min=1, w_max=10, violation_prob=0.4, seed=None):
    '''
    Prueba la heurística AH con un grafo generado.
    
    :param n: Número de vértices del grafo
    :param edge_prob: Probabilidad de que exista una arista entre un par de vértices
    :param w_min: Costo mínimo de arista
    :param w_max: Costo máximo de arista
    :param violation_prob: Probabilidad de que un vértice viole su restricción de grado
    :param seed: Semilla para reproducibilidad
    :return: Diccionario con los resultados de la prueba
    '''
    # Generar instancia
    edges, degree_bounds = generate_instance(n, edge_prob, w_min, w_max, violation_prob, seed)
    
    # Construir grafo G
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    
    # Calcular C_max como la suma de todos los costos de las aristas
    C_max = calculate_c_max(G)
    
    # Obtener MST inicial para comparación
    MST_initial = nx.minimum_spanning_tree(G)
    cost_initial = get_cost(MST_initial)
    
    # Verificar si el MST inicial cumple las restricciones
    initial_feasible = ok(degree_bounds, MST_initial)
    
    # Ejecutar heurística AH
    start_time = time.time()
    cost_ah, T_ah = AH_Heuristic(G, degree_bounds, C_max)
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Verificar si la solución es factible
    is_feasible = ok(degree_bounds, T_ah)
    
    # Verificar que T_ah es un árbol
    is_tree = nx.is_tree(T_ah)
    
    # Verificar que T_ah es conexo
    is_connected = nx.is_connected(T_ah)
    
    # Calcular estadísticas de grado
    degree_stats = {}
    for node in T_ah.nodes():
        degree = T_ah.degree(node)
        bound = degree_bounds[node]
        degree_stats[node] = {
            'degree': degree,
            'bound': bound,
            'violation': degree > bound
        }
    
    violations = sum(1 for stats in degree_stats.values() if stats['violation'])
    
    return {
        'n': n,
        'num_edges': len(G.edges()),
        'C_max': C_max,
        'cost_initial_mst': cost_initial,
        'initial_feasible': initial_feasible,
        'cost_ah': cost_ah,
        'is_feasible': is_feasible,
        'is_tree': is_tree,
        'is_connected': is_connected,
        'execution_time': execution_time,
        'violations': violations,
        'degree_stats': degree_stats,
        'seed': seed
    }


def print_test_results(results):
    '''
    Imprime los resultados de una prueba de forma legible.
    '''
    print(f"\n{'='*60}")
    print(f"Test para grafo con {results['n']} vértices y {results['num_edges']} aristas")
    print(f"{'='*60}")
    print(f"Semilla: {results['seed']}")
    print(f"\nCota superior (C_max): {results['C_max']}")
    print(f"\nMST inicial (sin restricciones):")
    print(f"  - Costo: {results['cost_initial_mst']}")
    print(f"  - Factible: {'Sí' if results['initial_feasible'] else 'No'}")
    print(f"\nHeurística AH:")
    print(f"  - Costo: {results['cost_ah']}")
    print(f"  - Tiempo de ejecución: {results['execution_time']:.6f} segundos")
    print(f"  - Es árbol: {'Sí' if results['is_tree'] else 'No'}")
    print(f"  - Es conexo: {'Sí' if results['is_connected'] else 'No'}")
    print(f"  - Es factible: {'Sí' if results['is_feasible'] else 'No'}")
    print(f"  - Violaciones de grado: {results['violations']}")
    
    if results['violations'] > 0:
        print(f"\n  Nodos con violaciones:")
        for node, stats in results['degree_stats'].items():
            if stats['violation']:
                print(f"    - Nodo {node}: grado={stats['degree']}, límite={stats['bound']}")
    
    print(f"\n  Mejora respecto al MST inicial: {results['cost_initial_mst'] - results['cost_ah']:.2f}")
    print(f"{'='*60}\n")


def run_multiple_tests(test_configs):
    '''
    Ejecuta múltiples pruebas con diferentes configuraciones.
    
    :param test_configs: Lista de diccionarios con configuraciones de prueba
    '''
    all_results = []
    
    for i, config in enumerate(test_configs):
        print(f"\nEjecutando prueba {i+1}/{len(test_configs)}...")
        seed = int(time.time() * 1000) % 1000000  # Semilla basada en tiempo
        results = test_ah_heuristic(seed=seed, **config)
        all_results.append(results)
        print_test_results(results)
    
    # Resumen estadístico
    print(f"\n{'='*60}")
    print("RESUMEN ESTADÍSTICO")
    print(f"{'='*60}")
    print(f"Total de pruebas: {len(all_results)}")
    print(f"Pruebas factibles: {sum(1 for r in all_results if r['is_feasible'])}")
    print(f"Pruebas con violaciones: {sum(1 for r in all_results if r['violations'] > 0)}")
    print(f"\nTiempo promedio: {sum(r['execution_time'] for r in all_results) / len(all_results):.6f} segundos")
    print(f"Costo promedio: {sum(r['cost_ah'] for r in all_results) / len(all_results):.2f}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Configuraciones de prueba
    test_configs = [
        {'n': 5, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 10, 'violation_prob': 0.4},
        {'n': 8, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 10, 'violation_prob': 0.4},
        {'n': 10, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 10, 'violation_prob': 0.4},
        {'n': 12, 'edge_prob': 0.5, 'w_min': 1, 'w_max': 15, 'violation_prob': 0.5},
        {'n': 15, 'edge_prob': 0.5, 'w_min': 1, 'w_max': 20, 'violation_prob': 0.5},
    ]
    
    run_multiple_tests(test_configs)

