# Algorithms & Optimization: Exercises 1 to 5

- **Repositorio:** https://github.com/sthefanydiaz07/Algoritmia-y-Optimizacion---Ejercicios-
- **Video (máx. 8 min):** `https://youtu.be/VsBMZDh1SHU?si=6BOw_Mz1McSyn5Ck`

Todos los scripts están basados en `p2.py`, son independientes entre sí y usan semillas fijas, así que los resultados se repiten en cada corrida (solo cambian los tiempos en milisegundos).

## Cómo ejecutar

Requisitos: Python 3.10 o superior y `matplotlib`.

```
pip install matplotlib
python ejercicio1.py
python ejercicio2.py
python ejercicio3.py
python ejercicio4.py
python ejercicio5.py
```

Cada script imprime sus resultados, guarda sus gráficas como `.png` en la carpeta donde se ejecuta y las muestra en pantalla.

| Ejercicio | Script | Gráficas generadas |
|---|---|---|
| 1. Parallel Speedup | `ejercicio1.py` | `speedup_pi.png` |
| 2. Greedy Knapsack | `ejercicio2.py` | `knapsack_comparison.png` |
| 3. 2-opt (búsqueda local) | `ejercicio3.py` | `two_opt_comparison.png` |
| 4. Simulated Annealing | `ejercicio4.py` | `sa_convergence.png`, `sa_time_vs_quality.png` |
| 5. MST Approximation | `ejercicio5.py` | `mst_ratio.png`, `method_comparison.png` |

---

## Ejercicio 1: Aceleración paralela

Se ejecuta `estimate_pi` (Monte Carlo, 8 tareas de 1,000,000 muestras) con 1, 2, 4 y 8 procesos. El tiempo es la mediana de 5 repeticiones, con el pool ya creado, y el speedup es `T(1) / T(p)`.

![speedup](speedup_pi.png)

Resultado en una máquina con 4 núcleos lógicos (en otra máquina los valores cambian; ver nota al final):

| Procesos | Tiempo (s) | Speedup | Ideal | Eficiencia |
|---|---|---|---|---|
| 1 | 3.627 | 1.00x | 1x | 100% |
| 2 | 2.223 | 1.63x | 2x | 82% |
| 4 | 1.753 | 2.07x | 4x | 52% |
| 8 | 1.586 | 2.29x | 8x | 29% |

**¿Por qué la aceleración no es lineal?**

1. **Número de núcleos.** Más procesos que núcleos no dan más trabajo en paralelo: los procesos extra solo se turnan. Por eso la curva se aplana cuando `p` pasa del número de núcleos (línea punteada de la gráfica). Además, los núcleos lógicos (hyperthreading) que comparten un núcleo físico rinden mucho menos que un núcleo real, así que el speedup puede aplanarse antes de llegar al número de núcleos lógicos que reporta el sistema.
2. **Sobrecostos de comunicación.** Crear los procesos, enviar a cada uno su semilla y recibir los resultados cuesta tiempo (serialización con pickle y comunicación entre procesos), y ese costo no existe en la ejecución secuencial.
3. **Parte secuencial (ley de Amdahl).** Si una fracción `f` del trabajo no se puede paralelizar (repartir tareas, juntar resultados y promediar), el speedup máximo con `p` procesos es `S(p) = 1 / (f + (1 - f) / p)`. Cuando `p` crece, el speedup se acerca a `1 / f` y nunca a `p`.
4. **Sincronización y balance de carga.** `pool.map` espera al proceso más lento. Con solo 8 tareas, repartirlas entre 4 u 8 procesos deja procesos esperando al final.

## Ejercicio 2: Mochila voraz (Greedy Knapsack)

Se modificó el algoritmo voraz para ordenar los objetos por **menor peso primero** (los que no caben se saltan y se sigue con el siguiente), y se compara con el voraz clásico de **mayor valor/peso**. El óptimo exacto sale de la tabla de programación dinámica `knapsack` de `p2.py`.

![knapsack](knapsack_comparison.png)

| Instancia | Método | Objetos | Capacidad usada | Valor |
|---|---|---|---|---|
| 1 (p2.py, W = 50) | Valor/peso | A, B | 30 / 50 | 160 |
| 1 | Menor peso | A, B | 30 / 50 | 160 |
| 1 | Óptimo (DP) | B, C | 50 / 50 | 220 |
| 2 (diseñada, W = 10) | Valor/peso | B, C | 10 / 10 | 75 |
| 2 | **Menor peso** | A, B | 3 / 10 | **7** |
| 2 | Óptimo (DP) | B, C | 10 / 10 | 75 |

**Instancia diseñada (entregable):** objetos `A (peso 1, valor 2)`, `B (peso 2, valor 5)`, `C (peso 8, valor 70)` con capacidad 10. Los dos objetos ligeros se toman primero y dejan solo 7 de capacidad, así que el objeto C (el de mejor valor por peso) ya no cabe. El criterio de menor peso termina con valor 7, contra 75 del método de valor/peso, que en este caso coincide con el óptimo. El criterio de peso ignora el valor, por eso puede llenar la mochila con objetos casi inútiles.

En la instancia 1 los dos criterios empatan en 160, y ninguno llega al óptimo de 220: los voraces no garantizan el óptimo.

## Ejercicio 3: Búsqueda local (2-opt para el TSP)

2-opt es subir colinas: se aplica un movimiento (invertir un tramo del recorrido) mientras acorte el recorrido, y se detiene en un óptimo local. Cada movimiento aceptado cuenta como una **mejora**. Se probó en 100 instancias aleatorias de 9 ciudades, desde dos soluciones iniciales: una ruta aleatoria y una ruta de Vecino Más Cercano que empieza en una ciudad aleatoria. La calidad se mide como `L(óptimo local) / L(óptimo real)`, con el óptimo real por fuerza bruta.

![2-opt](two_opt_comparison.png)

| | Inicio aleatorio | Vecino más cercano |
|---|---|---|
| Razón de la ruta inicial (promedio) | 1.686 | 1.098 |
| Mejoras (promedio / mediana / máximo) | 7.77 / 7.5 / 15 | 2.27 / 2 / 8 |
| Razón del óptimo local (promedio) | 1.006 | 1.009 |
| Instancias donde llega al óptimo real | 77 de 100 | 74 de 100 |

**¿El Vecino Más Cercano requiere menos mejoras?** Sí. Necesita en promedio 2.27 mejoras contra 7.77 del inicio aleatorio, y requirió menos mejoras en 93 de las 100 instancias (el mismo número en 4 y más en 3). El diagrama de caja de la izquierda lo muestra: la caja de Vecino Más Cercano queda por completo debajo de la del inicio aleatorio. La razón está en el diagrama de la derecha: la ruta de Vecino Más Cercano ya empieza a 1.10 veces el óptimo, mientras que la aleatoria empieza a 1.69, así que hay mucho menos que corregir.

**Calidad del óptimo alcanzado:** es prácticamente la misma (1.006 contra 1.009). Partir de una mejor ruta ahorra mejoras, pero no garantiza llegar a un mejor óptimo local.

## Ejercicio 4: Ajuste de parámetros (Simulated Annealing)

Recocido simulado del pseudocódigo de `p2.py`, con 2-opt como movimiento (`RANDOM_SUCCESSOR`), desde una solución inicial aleatoria, sobre 10 ciudades fijas (óptimo por fuerza bruta: L = 253.37). Se comparan dos esquemas de enfriamiento que van de `T0 = 100` a `T_final = 0.01` en el mismo número de iteraciones `N`, así que solo cambia la forma de la curva de enfriamiento:

- **Lineal:** `T(t) = T0 + (T_final - T0) · t / N`
- **Exponencial:** `T(t) = T0 · (T_final / T0)^(t / N)`

Un `N` pequeño equivale a un enfriamiento rápido y un `N` grande a uno lento.

**Curvas de convergencia** (costo contra iteraciones y contra temperatura, N = 3000):

![convergence](sa_convergence.png)

**Tiempo de ejecución contra calidad** (5 valores de `N`, 30 corridas por punto):

![time vs quality](sa_time_vs_quality.png)

| Esquema | Iteraciones | Tiempo mediano (ms) | Razón media | Peor razón | Óptimo encontrado |
|---|---|---|---|---|---|
| Lineal | 100 | 0.5 | 1.202 | 1.545 | 2 de 30 |
| Lineal | 300 | 1.4 | 1.072 | 1.200 | 4 de 30 |
| Lineal | 1000 | 4.5 | 1.008 | 1.042 | 23 de 30 |
| Lineal | 3000 | 13.6 | 1.000 | 1.000 | 30 de 30 |
| Lineal | 10000 | 47.7 | 1.000 | 1.000 | 30 de 30 |
| Exponencial | 100 | 0.5 | 1.059 | 1.300 | 11 de 30 |
| Exponencial | 300 | 1.4 | 1.018 | 1.098 | 18 de 30 |
| Exponencial | 1000 | 4.6 | 1.003 | 1.042 | 28 de 30 |
| Exponencial | 3000 | 14.0 | 1.000 | 1.000 | 30 de 30 |
| Exponencial | 10000 | 47.7 | 1.000 | 1.000 | 30 de 30 |

**¿Cómo impacta cada esquema en la calidad y el tiempo?**

- **Tiempo:** depende del número de iteraciones, no de la forma del enfriamiento. Con el mismo `N`, el lineal y el exponencial tardan lo mismo (por ejemplo, unos 4.5 ms con 1000 iteraciones); el tiempo crece de forma casi proporcional a `N`.
- **Calidad con pocas iteraciones:** el exponencial es claramente mejor. Con 100 iteraciones, la razón media es 1.059 contra 1.202 del lineal, y con 300 es 1.018 contra 1.072. El esquema exponencial baja rápido la temperatura y pasa más tiempo con temperaturas bajas, donde el algoritmo ya refina la solución. El lineal pasa la mayor parte de las iteraciones con temperatura alta, aceptando muchos cambios malos (se ve en la gráfica de convergencia: la solución actual sigue oscilando entre 300 y 600 hasta cerca del final), y le queda poco tiempo para asentarse.
- **Calidad con muchas iteraciones:** con 3000 o más iteraciones los dos esquemas encuentran el óptimo en las 30 corridas. Pasar de 3000 a 10000 iteraciones no mejora el resultado y cuesta unas 3.5 veces más tiempo.
- **Conclusión:** un enfriamiento más lento (más iteraciones) mejora la calidad con rendimientos decrecientes, y a igual tiempo el esquema exponencial da mejor calidad, sobre todo con presupuestos pequeños.

## Ejercicio 5: Razón de aproximación (MST)

Aproximación basada en el MST (Prim y recorrido en preorden con atajos, de `p2.py`) sobre 100 instancias aleatorias de 9 ciudades. La razón es `C_obtenido / C_óptimo`, con el óptimo real por fuerza bruta (8! = 40,320 recorridos por instancia). Además se aplica 2-opt al recorrido del MST y se compara con los métodos anteriores (2-opt desde inicio aleatorio y desde Vecino Más Cercano, y recocido simulado exponencial con 3000 iteraciones) sobre las mismas 100 instancias.

![ratio](mst_ratio.png)

![methods](method_comparison.png)

| Método | Costo medio | Razón media | Razón mínima | Razón máxima | Óptimo encontrado |
|---|---|---|---|---|---|
| Óptimo (fuerza bruta) | 277.00 | 1.000 | 1.000 | 1.000 | |
| MST | 312.57 | 1.128 | 1.000 | 1.389 | 7 de 100 |
| MST + 2-opt | 278.84 | 1.007 | 1.000 | 1.110 | 75 de 100 |
| 2-opt (inicio aleatorio) | 278.76 | 1.006 | 1.000 | 1.105 | 77 de 100 |
| 2-opt (vecino más cercano) | 279.44 | 1.009 | 1.000 | 1.137 | 74 de 100 |
| Recocido simulado | 277.04 | 1.000 | 1.000 | 1.012 | 98 de 100 |

**¿Qué tan cerca se mantiene la razón del límite teórico de 2?** Muy lejos. La razón media del MST es 1.128 y la peor de las 100 instancias es 1.389, a 0.611 del límite de 2; ninguna instancia pasa de 1.5. El límite de 2 es una garantía de peor caso que, en instancias aleatorias, casi nunca se acerca. La garantía sí se cumple siempre (el programa lo verifica).

**¿Qué impacto tiene 2-opt como post-procesamiento?** Muy grande: la razón media baja de 1.128 a 1.007, el peor caso baja de 1.389 a 1.110 y las instancias donde se llega al óptimo pasan de 7 a 75 de 100. El resultado de MST + 2-opt es prácticamente igual al de 2-opt desde un inicio aleatorio (1.007 contra 1.006) y mejor que 2-opt desde Vecino Más Cercano (1.009), es decir, en este experimento el MST no da una ventaja sobre un inicio aleatorio, y 2-opt hace casi todo el trabajo. El recocido simulado fue el mejor método (razón media 1.000, óptimo en 98 de 100), a cambio de más cómputo: 3000 iteraciones por instancia.

---

