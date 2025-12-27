# Analisis de resultados (DC-MST)

Este documento interpreta los resultados del notebook `DAA/src/DC-MST.ipynb` a la luz del
estado del arte en DC-MST: heuristicas constructivas (CH, AH), metodo dual, kernelizacion
con Kruskal modificado y lineas base (fuerza bruta y voraces capadas). Se resalta que las
heuristicas realizan cambios locales, por lo que un fallo no prueba inexistencia de solucion.

## Experimento 1: instancias pequenas con referencia optima

Resultados promedio:
- Kernel+Kruskal: factible 68.8%, brecha 0.00%, tiempo 0.0007s
- Dual method: factible 68.8%, brecha 6.82%, tiempo 0.0007s
- CH: factible 75.0%, brecha 7.12%, tiempo 0.0009s
- AH: factible 68.8%, brecha 0.00%, tiempo 0.0006s
- Bruteforce: factible 90.0%, brecha 0.00%, tiempo 0.0748s

Lectura desde el estado del arte:
- La fuerza bruta actua como optimo de referencia (solo en instancias muy pequenas). Su
  tiempo es mucho mayor, lo que confirma el caracter exponencial esperado.
- Kernel+Kruskal y AH con brecha 0.00% indican que, cuando encuentran solucion, suelen
  coincidir con el mejor costo hallado en el conjunto. Esto es coherente con la literatura:
  la kernelizacion fija aristas criticas y AH explota intercambios con buena estructura.
- CH muestra mayor tasa de factibilidad, pero mayor brecha promedio, consistente con que
  su construccion es mas flexible y puede terminar en soluciones suboptimas locales.

## Experimento 2: escalabilidad en n

Resultados promedio:
- Kernel+Kruskal: factible 72.2%, brecha 0.37%, tiempo 0.0057s
- Dual method: factible 83.3%, brecha 3.42%, tiempo 0.0188s
- CH: factible 88.9%, brecha 9.93%, tiempo 0.0095s
- AH: factible 38.9%, brecha 1.01%, tiempo 0.0110s

Lectura:
- CH mantiene alta factibilidad pero penaliza calidad (brecha mas alta), acorde a su
  naturaleza constructiva con pocos intercambios costosos.
- Dual method mejora factibilidad con costo moderado, coherente con su estrategia de
  reemplazos locales minimizando penalizacion.
- AH cae en factibilidad al crecer n, lo cual es esperable: su logica de intercambio
  estructural es sensible a combinaciones de restricciones de grado.
- Kernel+Kruskal se mantiene muy rapido y con brecha baja, lo que en la literatura se
  interpreta como un buen filtro inicial.

## Experimento 3: sensibilidad a densidad y restricciones

Se midieron heatmaps de factibilidad y brecha variando `edge_prob` y `violation_prob`.

Lectura:
- Con `edge_prob` bajo y `violation_prob` alto, la factibilidad cae en todos los metodos.
  Esto es consistente con el DC-MST: menos aristas y restricciones fuertes reducen el
  espacio factible.
- Con grafos mas densos, la factibilidad sube y las brechas bajan, porque los intercambios
  locales tienen mas alternativas de reemplazo.

## Experimento 4: robustez por semillas

Resultados (n=30):
- Kernel+Kruskal: gap media 0.20%, std 0.49
- Dual method: gap media 2.97%, std 3.58
- CH: gap media 9.10%, std 6.70
- AH: gap media 0.17%, std 0.47

Lectura:
- Kernel+Kruskal y AH son los mas estables (baja desviacion), lo que sugiere que su
  rendimiento depende menos del azar del generador.
- CH presenta alta variabilidad, algo tipico en heuristicas mas greedy en problemas con
  restricciones locales.

## Experimento 5: reinicios (CH y AH)

Resultados promedio (n=30):
- CH: single 79.00, restart 78.50
- AH: single 69.40, restart 71.50

Lectura:
- Los reinicios muestran mejoras marginales en CH y no mejoran AH.
- Esto sugiere que, en estas instancias, el punto de arranque no cambia demasiado el
  optimo local alcanzado, coherente con estructuras relativamente rigidas.

## Experimento 6: costo de restricciones (MST vs factible)

Resultados promedio (n=20):
- MST costo medio: 37.13
- Mejor factible medio: 50.36
- Violaciones promedio en MST: 3.47

Lectura:
- El incremento de costo refleja el ?precio? de respetar grados. El MST es una cota
  inferior que normalmente viola grados, como predice la teoria.
- El numero medio de violaciones indica que, aun en instancias moderadas, la restriccion
  de grado es relevante y no trivial.

## Experimento 7: restricciones muy estrictas

Resultados:
- Kernel+Kruskal: factible 50.0%
- Dual method: factible 90.0%
- CH: factible 100.0%
- AH: factible 40.0%

Lectura:
- Al forzar d(v) <= 2, el problema se acerca a un camino hamiltoniano. En ese escenario,
  CH y Dual method son mas efectivos en encontrar soluciones factibles.
- AH y Kernel+Kruskal fallan mas, lo cual es consistente con que dependen de estructuras
  del MST que ya no son compatibles con restricciones tan duras.

## Experimento 8: impacto de kernelizacion

Se midio el ratio de aristas fijadas por la reduccion y su evolucion con n.

Lectura:
- Ratios altos indican que el grafo queda muy reducido y la busqueda posterior es mas
  sencilla, lo que explica tiempos bajos en Kernel+Kruskal.
- En la literatura, esto se interpreta como una buena etapa de preprocesamiento para
  acotar el espacio combinatorio.

## Experimento 9: hibrido Kernel+Dual

Resultados:
- Dual method: factible 80.0%
- Kernel+Dual: factible 100.0%

Lectura:
- El hibrido mejora factibilidad, lo que respalda el enfoque por etapas del estado del
  arte: kernelizacion para reducir y luego heuristica local para ajustar grados.
- No se reporta brecha porque no se calculo gap_vs_best en este experimento, pero la
  mejora de factibilidad es clara.

## Experimento 10: exacto por fuerza bruta (muy pequeno)

Resultados:
- Kernel+Kruskal: gap medio vs exacto 0.00%
- Dual method: gap medio vs exacto 13.33%
- CH: gap medio vs exacto 0.00%
- AH: gap medio vs exacto 0.00%

Lectura:
- En instancias donde la fuerza bruta es viable, Kernel+Kruskal, CH y AH alcanzan el
  optimo exacto. Dual method queda mas lejos, lo que concuerda con su enfoque de
  minimizacion local de penalizacion.

## Experimento 11: sensibilidad al rango de pesos

Se vario w_max y se observo la brecha promedio.

Lectura:
- La tendencia esperada es que mayor dispersion de pesos dificulta la eleccion de
  intercambios locales y puede aumentar la brecha.
- Si la curva se mantiene plana, significa que el metodo es robusto a la escala de pesos.

## Experimento 12: cuellos de botella (nodos con d<=2)

Se midio la relacion entre ratio de nodos con d(v) <= 2 y factibilidad.

Lectura:
- Un ratio alto suele disminuir la factibilidad. Esto es coherente con la teoria: se
  restringen los grados y se reduce el numero de arboles factibles.
- El patron refleja la transicion hacia estructuras tipo camino.

## Experimento 13: Prim/Kruskal capados

Resultados:
- Capped Kruskal: factible 46.7%, brecha n/a
- Capped Prim: factible 80.0%, brecha n/a
- Kernel+Kruskal: factible 60.0%, brecha 2.85%
- Dual method: factible 73.3%, brecha 2.37%
- CH: factible 93.3%, brecha 4.72%
- AH: factible 40.0%, brecha 2.36%

Lectura:
- Los voraces capados son rapidos pero pierden factibilidad, como se anticipa en la
  literatura: impedir aristas por grados rompe la optimalidad local del MST.
- CH y Dual method se mantienen como mejores opciones en factibilidad, aunque con costo
  algo mayor.

## Experimento 14: conectividad residual cuando falla

Se midio el numero de componentes cuando una heuristica falla.

Lectura:
- Si el numero de componentes es alto, el metodo no logra conectar subarboles por falta
  de reemplazos validos.
- Si es bajo, el fallo se debe mas a violaciones de grado que a conectividad, lo que
  sugiere necesidad de intercambios mas sofisticados.

## Conclusiones globales

- Kernelizacion + Kruskal es un excelente preprocesamiento: muy rapido y con brechas
  bajas cuando encuentra solucion. Es consistente con la literatura sobre reduccion.
- CH maximiza factibilidad, pero con mayor costo relativo; es tipico de heuristicas
  constructivas que priorizan construir algo viable.
- AH ofrece soluciones muy cercanas al optimo cuando funciona, pero es mas fragil en
  instancias grandes o con restricciones severas.
- El metodo dual equilibra costo y factibilidad, aunque su brecha suele ser mayor que
  AH y Kernel+Kruskal.
- La evidencia respalda el enfoque por etapas: preprocesamiento (kernel) seguido de
  heuristicas locales o hibridos para mejorar factibilidad.
