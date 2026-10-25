import itertools
import math
import random
import statistics
import time

N_CITIES = 10
T0, T_FINAL = 100.0, 0.01
BUDGETS = [100, 300, 1000, 3000, 10000]        # iteraciones: enfriamiento rápido ... lento
SEEDS = 30


def tour_length(points, route) -> float:
    return sum(math.dist(points[route[i]], points[route[(i + 1) % len(route)]])
               for i in range(len(route)))


def two_opt_move(route: list[int], i: int, k: int) -> list[int]:
    """Invierte route[i..k]: quita las aristas (i-1, i) y (k, k+1)."""
    return route[:i] + route[i:k + 1][::-1] + route[k + 1:]


def linear_schedule(t: int, n_iter: int) -> float:
    return T0 + (T_FINAL - T0) * t / n_iter


def exponential_schedule(t: int, n_iter: int) -> float:
    return T0 * (T_FINAL / T0) ** (t / n_iter)


SCHEDULES = {"Lineal": linear_schedule, "Exponencial": exponential_schedule}


def simulated_annealing(points, initial, schedule, n_iter, seed):
    """SA de p2.py. Devuelve (mejor recorrido, historial del costo actual, historial del
    mejor costo, historial de la temperatura)."""
    n = len(initial)
    rng = random.Random(seed)
    current, best = initial[:], initial[:]
    cur_len = best_len = tour_length(points, current)
    h_current, h_best, h_temp = [cur_len], [best_len], [schedule(0, n_iter)]
    for t in range(1, n_iter + 1):
        T = schedule(t, n_iter)
        i = rng.randint(1, n - 2)
        k = rng.randint(i + 1, n - 1)
        nxt = two_opt_move(current, i, k)               # RANDOM_SUCCESSOR (no el mejor)
        nxt_len = tour_length(points, nxt)
        delta_E = cur_len - nxt_len                     # next.VALUE - current.VALUE
        if delta_E > 0:
            current, cur_len = nxt, nxt_len             # mejora: siempre se acepta
        elif rng.random() < math.exp(delta_E / T):
            current, cur_len = nxt, nxt_len             # empeora: se acepta con probabilidad e^(dE/T)
        if cur_len < best_len:
            best, best_len = current[:], cur_len
        h_current.append(cur_len)
        h_best.append(best_len)
        h_temp.append(T)
    return best, h_current, h_best, h_temp


def optimal_length(points) -> float:
    """Fuerza bruta sobre todos los recorridos que empiezan en la ciudad 0 ((n-1)! recorridos)."""
    n = len(points)
    D = [[math.dist(a, b) for b in points] for a in points]
    best = float("inf")
    for p in itertools.permutations(range(1, n)):
        L = D[0][p[0]] + D[p[-1]][0]
        for i in range(n - 2):
            L += D[p[i]][p[i + 1]]
        if L < best:
            best = L
    return best


def random_tour(n: int, seed: int) -> list[int]:
    route = list(range(n))
    random.Random(seed).shuffle(route)
    return route


if __name__ == "__main__":
    rng = random.Random(7)
    points = [(rng.randint(0, 100), rng.randint(0, 100)) for _ in range(N_CITIES)]
    optimum = optimal_length(points)
    print(f"{N_CITIES} ciudades, recorrido óptimo (fuerza bruta): L = {optimum:.2f}")
    print(f"T0 = {T0}, T_final = {T_FINAL}\n")

    # ---------- 1. Curvas de convergencia (una corrida por esquema, mismo inicio) ----------
    CURVE_BUDGET = 3000
    initial = random_tour(N_CITIES, seed=1)
    print(f"Recorrido inicial aleatorio: L = {tour_length(points, initial):.2f}")
    curves = {}
    for name, schedule in SCHEDULES.items():
        best, h_cur, h_best, h_temp = simulated_annealing(points, initial, schedule, CURVE_BUDGET, seed=42)
        curves[name] = (h_cur, h_best, h_temp)
        print(f"{name:12s} N = {CURVE_BUDGET}  L final = {tour_length(points, best):.2f}")

    # ---------- 2. Tiempo contra calidad: presupuestos x semillas ----------
    # Los dos esquemas se alternan dentro de cada semilla, para que ninguno quede favorecido o
    # perjudicado por el orden de ejecución (calentamiento del procesador, otros programas...).
    runs = {(name, n_iter): ([], []) for name in SCHEDULES for n_iter in BUDGETS}   # (tiempos, razones)
    for n_iter in BUDGETS:
        for seed in range(SEEDS):
            start = random_tour(N_CITIES, seed=1000 + seed)              # solución inicial aleatoria
            for name, schedule in SCHEDULES.items():
                t0 = time.perf_counter()
                best, *_ = simulated_annealing(points, start, schedule, n_iter, seed)
                runs[(name, n_iter)][0].append((time.perf_counter() - t0) * 1000)
                runs[(name, n_iter)][1].append(tour_length(points, best) / optimum)

    print(f"\n{'esquema':12s} {'iteraciones':>11s} {'tiempo mediano (ms)':>20s} "
          f"{'razón media':>12s} {'peor razón':>11s} {'óptimo hallado':>15s}")
    summary = {name: [] for name in SCHEDULES}
    for name in SCHEDULES:
        for n_iter in BUDGETS:
            times, ratios = runs[(name, n_iter)]
            found = sum(r < 1 + 1e-9 for r in ratios)
            summary[name].append((n_iter, statistics.median(times), statistics.mean(ratios), max(ratios)))
            print(f"{name:12s} {n_iter:>11d} {statistics.median(times):>20.1f} "
                  f"{statistics.mean(ratios):>12.3f} {max(ratios):>11.3f} {f'{found} de {SEEDS}':>15s}")

    import matplotlib.pyplot as plt

    colors = {"Lineal": "#0072B2", "Exponencial": "#D55E00"}

    # ----- Figura 1: convergencia (filas: contra iteraciones / contra temperatura) -----
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharey=True, layout="constrained")
    for col, name in enumerate(SCHEDULES):
        h_cur, h_best, h_temp = curves[name]
        ax = axes[0][col]
        ax.plot(h_cur, color="#7fa8c9", linewidth=0.7, label="Solución actual")
        ax.plot(h_best, color="#c0392b", linewidth=1.8, label="Mejor encontrada")
        ax.axhline(optimum, color="k", linestyle="--", linewidth=1, label=f"Óptimo ({optimum:.2f})")
        ax.set_title(f"Enfriamiento {name.lower()}: costo vs iteraciones\nL final = {h_best[-1]:.2f}")
        ax.set_xlabel("Iteraciones")
        ax2 = axes[1][col]
        ax2.plot(h_temp, h_cur, color="#7fa8c9", linewidth=0.7, label="Solución actual")
        ax2.plot(h_temp, h_best, color="#c0392b", linewidth=1.8, label="Mejor encontrada")
        ax2.axhline(optimum, color="k", linestyle="--", linewidth=1)
        ax2.set_xscale("log")
        ax2.invert_xaxis()
        ax2.set_title(f"Enfriamiento {name.lower()}: costo vs temperatura")
        ax2.set_xlabel("Temperatura (escala logarítmica, se enfría hacia la derecha)")
        for a in (ax, ax2):
            a.set_ylabel("Objetivo: longitud del recorrido")
            a.grid(alpha=0.25)
    axes[0][0].legend()
    fig.suptitle(f"Convergencia del recocido simulado ({CURVE_BUDGET} iteraciones)", fontsize=13)
    plt.savefig("sa_convergence.png", dpi=150)

    # ----- Figura 2: tiempo de ejecución contra calidad -----
    fig, ax = plt.subplots(figsize=(8, 5.2), layout="constrained")
    for name in SCHEDULES:
        t = [s[1] for s in summary[name]]
        q = [s[2] for s in summary[name]]
        ax.plot(t, q, "o-", color=colors[name], linewidth=2, markersize=7, label=name)
        offset = (6, 8) if name == "Lineal" else (6, -14)      # separa las dos etiquetas
        for (n_iter, ms, ratio, _) in summary[name]:
            ax.annotate(f"{n_iter:,}", (ms, ratio), textcoords="offset points",
                        xytext=offset, fontsize=8, color=colors[name])
    ax.axhline(1, color="k", linestyle=":", linewidth=1, label="Óptimo (razón = 1)")
    ax.set_xscale("log")
    ax.margins(x=0.12, y=0.1)
    ax.set_xlabel("Tiempo mediano de ejecución (ms, escala logarítmica)")
    ax.set_ylabel(f"Promedio de L(final) / L(óptimo)  ({SEEDS} corridas por punto)")
    ax.set_title("Tiempo de ejecución vs calidad de la solución\n(etiquetas = iteraciones; abajo a la izquierda es mejor)")
    ax.grid(alpha=0.25)
    ax.legend()
    plt.savefig("sa_time_vs_quality.png", dpi=150)
    print("\nGráficas guardadas en sa_convergence.png y sa_time_vs_quality.png")
    plt.show()