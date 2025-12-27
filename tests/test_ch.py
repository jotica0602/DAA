import sys
import os
import time
import networkx as nx

# Agregar el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from instance_generator import generate_instance
from heuristics import dual_method
from utils import get_cost, is_feasable
from ch import CH_Heuristic


def test_ch_heuristic(n, edge_prob=0.4, w_min=1, w_max=10, violation_prob=0.4, seed=None):
    '''
    Prueba la heurística CH con un grafo generado.
    
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
    
    # Obtener MST inicial para comparación
    MST_initial = nx.minimum_spanning_tree(G)
    cost_initial = get_cost(MST_initial)
    
    # Verificar si el MST inicial cumple las restricciones
    initial_feasible = is_feasable(degree_bounds, MST_initial)
    
    # Ejecutar método dual partiendo del MST inicial
    print(f"  Ejecutando método dual (partiendo del MST inicial)...")
    start_time_dual = time.time()
    T_dual = dual_method(G.copy(), MST_initial.copy(), degree_bounds)
    end_time_dual = time.time()
    execution_time_dual = end_time_dual - start_time_dual
    cost_dual = get_cost(T_dual)
    dual_feasible = is_feasable(degree_bounds, T_dual)
    dual_is_tree = nx.is_tree(T_dual)
    dual_is_connected = nx.is_connected(T_dual)
    
    # Usar el costo del método dual como cota superior (ub) para CH
    ub = cost_dual if cost_dual != float('inf') else get_cost(G)
    
    # Ejecutar heurística CH con cota superior (resultado del método dual)
    print(f"  Ejecutando heurística CH (ub={ub:.2f}, del método dual)...")
    start_time_ch = time.time()
    cost_ch, T_ch = CH_Heuristic(G, degree_bounds, ub=ub)
    end_time_ch = time.time()
    execution_time_ch = end_time_ch - start_time_ch
    
    # Verificar si la solución CH es factible
    ch_feasible = is_feasable(degree_bounds, T_ch)
    
    # Verificar que T_ch es un árbol
    ch_is_tree = nx.is_tree(T_ch)
    
    # Verificar que T_ch es conexo
    ch_is_connected = nx.is_connected(T_ch)
    
    # Calcular estadísticas de grado para CH
    ch_degree_stats = {}
    for node in T_ch.nodes():
        degree = T_ch.degree(node)
        bound = degree_bounds[node]
        ch_degree_stats[node] = {
            'degree': degree,
            'bound': bound,
            'violation': degree > bound
        }
    
    ch_violations = sum(1 for stats in ch_degree_stats.values() if stats['violation'])
    
    # Calcular estadísticas de grado para método dual
    dual_degree_stats = {}
    for node in T_dual.nodes():
        degree = T_dual.degree(node)
        bound = degree_bounds[node]
        dual_degree_stats[node] = {
            'degree': degree,
            'bound': bound,
            'violation': degree > bound
        }
    
    dual_violations = sum(1 for stats in dual_degree_stats.values() if stats['violation'])
    
    return {
        'n': n,
        'num_edges': len(G.edges()),
        'cost_initial_mst': cost_initial,
        'initial_feasible': initial_feasible,
        'cost_dual': cost_dual,
        'execution_time_dual': execution_time_dual,
        'dual_feasible': dual_feasible,
        'dual_is_tree': dual_is_tree,
        'dual_is_connected': dual_is_connected,
        'dual_violations': dual_violations,
        'dual_degree_stats': dual_degree_stats,
        'ub': ub,  # Cota superior usada (costo del método dual)
        'cost_ch': cost_ch,
        'ch_feasible': ch_feasible,
        'ch_is_tree': ch_is_tree,
        'ch_is_connected': ch_is_connected,
        'execution_time_ch': execution_time_ch,
        'ch_violations': ch_violations,
        'ch_degree_stats': ch_degree_stats,
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
    print(f"\nMST inicial (sin restricciones):")
    print(f"  - Costo: {results['cost_initial_mst']}")
    print(f"  - Factible: {'Sí' if results['initial_feasible'] else 'No'}")
    
    print(f"\n{'─'*60}")
    print(f"MÉTODO DUAL:")
    print(f"{'─'*60}")
    print(f"  - Costo: {results['cost_dual']}")
    print(f"  - Tiempo de ejecución: {results['execution_time_dual']:.6f} segundos")
    print(f"  - Es árbol: {'Sí' if results['dual_is_tree'] else 'No'}")
    print(f"  - Es conexo: {'Sí' if results['dual_is_connected'] else 'No'}")
    print(f"  - Es factible: {'Sí' if results['dual_feasible'] else 'No'}")
    print(f"  - Violaciones de grado: {results['dual_violations']}")
    
    if results['dual_violations'] > 0:
        print(f"\n  Nodos con violaciones:")
        for node, stats in results['dual_degree_stats'].items():
            if stats['violation']:
                print(f"    - Nodo {node}: grado={stats['degree']}, límite={stats['bound']}")
    
    print(f"\n{'─'*60}")
    print(f"HEURÍSTICA CH (ub = costo método dual = {results['ub']:.2f}):")
    print(f"{'─'*60}")
    print(f"  - Costo: {results['cost_ch']}")
    print(f"  - Tiempo de ejecución: {results['execution_time_ch']:.6f} segundos")
    print(f"  - Es árbol: {'Sí' if results['ch_is_tree'] else 'No'}")
    print(f"  - Es conexo: {'Sí' if results['ch_is_connected'] else 'No'}")
    print(f"  - Es factible: {'Sí' if results['ch_feasible'] else 'No'}")
    print(f"  - Violaciones de grado: {results['ch_violations']}")
    
    if results['ch_violations'] > 0:
        print(f"\n  Nodos con violaciones:")
        for node, stats in results['ch_degree_stats'].items():
            if stats['violation']:
                print(f"    - Nodo {node}: grado={stats['degree']}, límite={stats['bound']}")
    
    print(f"\n{'─'*60}")
    print(f"COMPARACIÓN:")
    print(f"{'─'*60}")
    print(f"  - Mejora respecto al MST inicial:")
    print(f"    * Método Dual: {results['cost_initial_mst'] - results['cost_dual']:.2f}")
    print(f"    * Heurística CH: {results['cost_initial_mst'] - results['cost_ch']:.2f}")
    
    diferencia_ch_dual = results['cost_ch'] - results['cost_dual']
    porcentaje_ch_dual = (diferencia_ch_dual / results['cost_dual']) * 100 if results['cost_dual'] > 0 else 0
    print(f"\n  - Diferencia de costo (CH - Dual): {diferencia_ch_dual:.2f} ({porcentaje_ch_dual:+.2f}%)")
    
    speedup_dual_ch = results['execution_time_dual'] / results['execution_time_ch'] if results['execution_time_ch'] > 0 else float('inf')
    print(f"  - Speedup (tiempo Dual / tiempo CH): {speedup_dual_ch:.2f}x")
    
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
        results = test_ch_heuristic(seed=seed, **config)
        all_results.append(results)
        print_test_results(results)
    
    # Resumen estadístico
    print(f"\n{'='*60}")
    print("RESUMEN ESTADÍSTICO")
    print(f"{'='*60}")
    print(f"Total de pruebas: {len(all_results)}")
    
    # Estadísticas de método dual
    print(f"\nMétodo Dual:")
    print(f"  - Pruebas factibles: {sum(1 for r in all_results if r['dual_feasible'])}")
    print(f"  - Pruebas con violaciones: {sum(1 for r in all_results if r['dual_violations'] > 0)}")
    print(f"  - Tiempo promedio: {sum(r['execution_time_dual'] for r in all_results) / len(all_results):.6f} segundos")
    print(f"  - Costo promedio: {sum(r['cost_dual'] for r in all_results) / len(all_results):.2f}")
    
    # Estadísticas de heurística CH
    print(f"\nHeurística CH:")
    print(f"  - Pruebas factibles: {sum(1 for r in all_results if r['ch_feasible'])}")
    print(f"  - Pruebas con violaciones: {sum(1 for r in all_results if r['ch_violations'] > 0)}")
    print(f"  - Tiempo promedio: {sum(r['execution_time_ch'] for r in all_results) / len(all_results):.6f} segundos")
    print(f"  - Costo promedio: {sum(r['cost_ch'] for r in all_results) / len(all_results):.2f}")
    
    # Comparación
    avg_speedup_dual_ch = sum(r['execution_time_dual'] / r['execution_time_ch'] for r in all_results if r['execution_time_ch'] > 0) / len(all_results)
    avg_cost_diff_ch_dual = sum(r['cost_ch'] - r['cost_dual'] for r in all_results) / len(all_results)
    avg_cost_diff_ch_dual_pct = sum((r['cost_ch'] - r['cost_dual']) / r['cost_dual'] * 100 for r in all_results if r['cost_dual'] > 0) / len(all_results)
    print(f"\nComparación:")
    print(f"  - Speedup promedio (Dual / CH): {avg_speedup_dual_ch:.2f}x")
    print(f"  - Diferencia de costo promedio (CH - Dual): {avg_cost_diff_ch_dual:.2f} ({avg_cost_diff_ch_dual_pct:+.2f}%)")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Configuraciones de prueba - Más casos para mejor evaluación
    test_configs = [
        # Grafos pequeños
        {'n': 5, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 10, 'violation_prob': 0.4},
        {'n': 6, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 10, 'violation_prob': 0.4},
        {'n': 7, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 10, 'violation_prob': 0.4},
        {'n': 8, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 10, 'violation_prob': 0.4},
        
        # Grafos medianos
        {'n': 10, 'edge_prob': 0.3, 'w_min': 1, 'w_max': 10, 'violation_prob': 0.4},
        {'n': 10, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 15, 'violation_prob': 0.5},
        {'n': 12, 'edge_prob': 0.3, 'w_min': 1, 'w_max': 15, 'violation_prob': 0.5},
        {'n': 12, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 20, 'violation_prob': 0.4},
        
        # Grafos más grandes
        {'n': 15, 'edge_prob': 0.3, 'w_min': 1, 'w_max': 20, 'violation_prob': 0.5},
        {'n': 15, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 15, 'violation_prob': 0.4},
        {'n': 18, 'edge_prob': 0.3, 'w_min': 1, 'w_max': 25, 'violation_prob': 0.5},
        {'n': 20, 'edge_prob': 0.3, 'w_min': 1, 'w_max': 20, 'violation_prob': 0.4},
        
        # Casos con diferentes probabilidades de violación
        {'n': 10, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 10, 'violation_prob': 0.3},
        {'n': 10, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 10, 'violation_prob': 0.6},
        {'n': 15, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 15, 'violation_prob': 0.3},
        {'n': 15, 'edge_prob': 0.4, 'w_min': 1, 'w_max': 15, 'violation_prob': 0.6},
    ]
    
    run_multiple_tests(test_configs)

