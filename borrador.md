##### Abstract

El presente informe se confecciona con el objetivo de hacer un análisis detallado de la problemática en cuestión, utilizando como cimiento los contenidos recibidos a lo largo del curso para proveer una solución lo suficientemente buena para lidiar con la complejidad de la misma.

# El problema

**Conectando la UH**

La Universidad de La Habana (UH), en su constante búsqueda de la excelencia académica y la innovación, se ha embarcado en un proyecto crucial para modernizar y expandir su infraestructura de red. Nuestro objetivo es dotar a todas nuestras facultades, centros de investigación y edificios administrativos con conectividad de fibra óptica de alta velocidad. Para este fin, contamos con el valioso apoyo técnico y logístico de ETECSA (Empresa de Telecomunicaciones de Cuba S.A.).

Nos enfrentamos a un desafío de diseño de red que requiere una solución óptima. Necesitamos interconectar todos los edificios principales de la UH con fibra óptica, creando una red robusta y eficiente. Cada posible conexión de fibra entre dos edificios tiene un costo de instalación asociado, que incluye desde los permisos internos y la mano de obra especializada de ETECSA hasta los materiales y las obras civiles necesarias.

Sin embargo, ETECSA ha establecido una restricción técnica fundamental que debemos respetar:  

En cada edificio, la conexión de la fibra óptica se gestionará a través de un equipo de red central (un router o switch principal) que ellos nos proporcionan. Estos equipos tienen una capacidad limitada de puertos. Esto significa que un equipo en un edificio específico solo puede manejar un número máximo de conexiones de fibra óptica directas a otros edificios. Exceder este límite implicaría la necesidad de instalar equipos adicionales mucho más caros y complejos, o la implementación de soluciones de red alternativas que ETECSA no puede garantizar o que dispararían drásticamente el presupuesto del proyecto.

Nuestro objetivo principal es diseñar la red de fibra óptica que conecte todos nuestros edificios principales de la manera más económica posible. Esto implica seleccionar las rutas de fibra de tal forma que:

1. Todos los edificios estén interconectados a la red principal de la universidad, sin crear bucles innecesarios (buscamos una estructura de red eficiente).
2. Ningún equipo de red en ningún edificio exceda su capacidad máxima de conexiones directas (es decir, el número de cables de fibra que llegan o salen de un edificio no puede superar el límite de puertos del equipo de ETECSA).
3. El costo total de instalación de toda la red sea el mínimo posible.

Una planificación subóptima podría resultar en un sobrecosto significativo para la universidad, la necesidad de adquirir hardware de red adicional no previsto, o en una red ineficiente que no cumpla con las especificaciones técnicas y presupuestarias acordadas con ETECSA.

## Comentarios

El problema en cuestión es clásico en el diseño y montaje de redes físicas, siendo un caso digno de estudio por más de cuarenta años para los matemáticos, con enfoque especial en ramas como la optimización y la teoría de grafos.

# Modelación del problema

Sea un grafo no dirigido y conexo $G = \langle V,E \rangle$ donde:
- Cada vértice $v \in V$ representa un edificio principal de la Universidad de la Habana
- Cada arista $e = \langle u,v \rangle \in E$ representa la posibilidad de instalar un enlace de fibra óptica directo entre los edificios u y v.
- A cada arista $e \in E$ se le asocia un peso $w(e) > 0$, que representa el costo de instalación
del enlace correspondiente.

Adicionalmente a cada vértice $v \in V$ se le asocia un entero positivo $d(v)$ que representa el número máximo de conexiones de fibra óptica (grado máximo) que puede soportar el equipo de red instalado en dicho edificio. 

### Estructura de red deseada

Para garantizar conectividad total sin bucles innecesarios se busca una subestructura $G$ que:

1. Conecte todos los vértices de $V$.
2. Sea acíclica.

Estas propiedades caracterizan a un *árbol abarcador* del grafo $G$.

## Formalización como Árbol Abarcador de Costo Mínimo con Restricción de Grado

**Definición (Árbol Abarcador de Costo Mínimo con Restricción de Grados)**: Dado un grafo no dirigido y conexo $G = \langle V,E \rangle$ con una función de costo para las aristas $w : E \rightarrow \R^+$ y una función de cotas de grado $d : V \rightarrow \N$, el problema del Árbol Abarcador de Costo Mínimo con Restricción de Grado consiste en encontrar un árbol generador $T = \langle V,E_T \rangle$ tal que:

1. $deg_T(v) \leq d(v), \forall v \in V$
2. La suma de los pesos $\sum_{e \in E_T} w(e)$ sea mínima.

> En lo adelante todas las referencias al nombre de este problema se harán por su nombre en inglés: Degree Constrained Minimum Spanning Tree (DCMST).

### Propiedades y Observaciones Iniciales

- Si $d(v) = |V| - 1$ para todo $v \in V$, el problema se reduce al clásico Árbol Generador de Costo Mínimo (Minimum Spanning Tree en inglés o MST), resoluble en tiempo polinomial mediante algoritmos como Kruskal o Prim.

- La introducción de restricciones de grado rompe las propiedades de optimalidad local que permiten dichos algoritmos voraces.

- En contextos reales, las cotas de grados suelen ser pequeñas, lo incrementa la dificultad computacional del problema.

## Complejidad Computacional

Para analizar la complejidad computacional del problema, consideramos su versión de decisión.

**Definición (DCMST-DEC):** Dado un grafo no dirigido y conexo $G = \langle V, E \rangle$, una función de pesos $w: E \to \R^+$, una función de cotas de grado $d: V \to N$ y un entero $k$, ¿existe un árbol abarcador $T$ de $G$ tal que:
1. $\deg_T(v) \leq d(v)$, $\forall v \in V$ y 
2. $\sum_{e \in E_T} w(e) \leq k$?

**Lema 1:** DCMST-DEC pertenece a la clase NP.

**Demostración:** Dado un certificado consistente en un conjunto de aristas $E_T \subseteq E$, es posible verificar en tiempo polinomial que $T = \langle V, E_T \rangle$ es un árbol abarcador que satisface las restricciones de grado para cada vértice y que el costo total no excede $k$. Por tanto, DCMST-DEC pertenece a NP.

**Lema 2:** DCMST-DEC es NP-Hard

**Demostración:**
Hagamos una reducción del problema *Camino Hamiltoniano (Hamiltonian Path)* en grafos no dirigidos, el cual es NP-completo y probemos que $Hamiltonian \, Path \leq_P DCMST-DEC$.

Sea $G_H = \langle V_H, E_H \rangle$ una instancia del problema del Camino Hamiltoniano. Construimos una instancia $G = \langle V, E \rangle$ de DCMST-DEC de la siguiente manera:

1. $V = V_H$.
2. $E = E_H$.
3. Para toda arista $e \in E$, definamos $w(e) = 1$.
4. Para todo vértice $v \in V$, definamos $d(v) = 2$.
5. Definamos $k = |V| - 1$.

Observemos que cualquier árbol abarcador de $G$ tiene exactamente $|V| - 1$ aristas y por la restricción de costo todas las aristas del árbol deben tener peso 1, por lo que el costo de cualquier árbol es $|V| - 1$.

Supongamos que $G_H$ admite un camino Hamiltoniano. Dicho camino es un árbol abarcador de $G$ en el cual cada vértice tiene grado a lo sumo 2. Por tanto, cumplen todas las restricciones de la instancia construida de DCMST-DEC, y su costo total es exactamente $|V| - 1 \leq k$.

Recíprocamente, supongamos que existe un árbol abarcador $T$ de $G$ que satisface las restricciones de grado y costo. Dado que todos los pesos son iguales a 1 y el costo total es $|V| - 1$, $T$ debe contener exactamente $|V| - 1$ aristas. Además, la restricción $\deg_T(v) \leq 2$ para todo $v$ implica que $T$ es un camino que visita todos los vértices exactamente una vez. Por lo tanto, $T$ corresponde a un camino Hamiltoniano en $G_H$.

La transformación descrita es realizable en tiempo polinomial y correcta en ambos sentidos. En consecuencia, DCMST-DEC es NP-Hard.

**Teorema:** DCMST-DC es NP-Completo

**Demostración:** En orden para probar esta afirmación debemos mostrar que:
1. DCMST-DC pertenece a la clase NP (Demostrado en **Lema 1**).
2. DCMST-DC es NP-Hard (Demostrado en **Lema 2**).