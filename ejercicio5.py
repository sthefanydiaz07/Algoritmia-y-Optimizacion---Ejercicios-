import itertools
import math
import random
import statistics

N_CITIES = 9
N_INSTANCES = 100
SA_ITERATIONS = 3000
T0, T_FINAL = 100.0, 0.01


def tour_length(points, tour) -> float:
    return sum(math.dist(points[tour[i]], points[tour[(i + 1) % len(tour)]]) for i in range(len(tour)))


def two_opt_move(route: list[int], i: int, k: int) -> list[int]:
    return route[:i] + route[i:k + 1][::-1] + route[k + 1:]


def optimal_length(points) -> float:
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


def mst_prim(points) -> dict[int, list[int]]:
    best = {v: (math.dist(points[0], points[v]), 0) for v in range(1, len(points))}
    children = {v: [] for v in range(len(points))}
    while best:
        v = min(best, key=lambda u: best[u][0])
        children[best.pop(v)[1]].append(v)          
        for u in best:
            d = math.dist(points[v], points[u])
            if d < best[u][0]:
                best[u] = (d, v)
    return children


def preorder(children: dict[int, list[int]], root: int = 0) -> list[int]:
    return [root] + [c for child in children[root] for c in preorder(children, child)]


def two_opt(points, route):
    n = len(route)
    best, best_len = route[:], tour_length(points, route)
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for k in range(i + 1, n):
                candidate = two_opt_move(best, i, k)
                cand_len = tour_length(points, candidate)
                if cand_len < best_len - 1e-9:
                    best, best_len = candidate, cand_len
                    improved = True
    return best


def nearest_neighbour(points, start: int) -> list[int]:
    route, pending = [start], set(range(len(points))) - {start}
    while pending:
        last = route[-1]
        nxt = min(pending, key=lambda c: math.dist(points[last], points[c]))
        route.append(nxt)
        pending.remove(nxt)
    return route


def simulated_annealing(points, initial, n_iter, seed):
    n = len(initial)
    rng = random.Random(seed)
    current, best = initial[:], initial[:]
    cur_len = best_len = tour_length(points, current)
    for t in range(1, n_iter + 1):
        T = T0 * (T_FINAL / T0) ** (t / n_iter)
        i = rng.randint(1, n - 2)
        k = rng.randint(i + 1, n - 1)
        nxt = two_opt_move(current, i, k)
        nxt_len = tour_length(points, nxt)
        delta_E = cur_len - nxt_len
        if delta_E > 0 or rng.random() < math.exp(delta_E / T):
            current, cur_len = nxt, nxt_len
        if cur_len < best_len:
            best, best_len = current[:], cur_len
    return best


if __name__ == "__main__":
    rng = random.Random(2024)                     
    METHODS = ["MST", "MST + 2-opt", "2-opt (inicio aleatorio)", "2-opt (vecino más cercano)",
               "Recocido simulado"]
    costs = {m: [] for m in METHODS}
    optimal = []

    for idx in range(N_INSTANCES):
        pts = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(N_CITIES)]
        optimal.append(optimal_length(pts))

        mst_tour = preorder(mst_prim(pts))
        costs["MST"].append(tour_length(pts, mst_tour))
        costs["MST + 2-opt"].append(tour_length(pts, two_opt(pts, mst_tour)))

        random_start = list(range(N_CITIES))
        rng.shuffle(random_start)
        costs["2-opt (inicio aleatorio)"].append(tour_length(pts, two_opt(pts, random_start)))
        nn_start = nearest_neighbour(pts, start=rng.randrange(N_CITIES))
        costs["2-opt (vecino más cercano)"].append(tour_length(pts, two_opt(pts, nn_start)))
        costs["Recocido simulado"].append(
            tour_length(pts, simulated_annealing(pts, random_start, SA_ITERATIONS, seed=idx)))

    ratios = {m: [c / o for c, o in zip(costs[m], optimal)] for m in METHODS}
    assert all(r <= 2 + 1e-9 for r in ratios["MST"]), "el recorrido del MST debe estar dentro del factor 2"

    print(f"{N_INSTANCES} instancias aleatorias de {N_CITIES} ciudades. razón = C_obtenido / C_óptimo\n")
    print(f"{'método':28s} {'costo medio':>11s} {'razón media':>12s} {'mínima':>7s} {'máxima':>7s} {'óptimo hallado':>15s}")
    print(f"{'Óptimo (fuerza bruta)':28s} {statistics.mean(optimal):>11.2f} {1:>12.3f} {1:>7.3f} {1:>7.3f}")
    for m in METHODS:
        found = sum(r < 1 + 1e-9 for r in ratios[m])
        print(f"{m:28s} {statistics.mean(costs[m]):>11.2f} {statistics.mean(ratios[m]):>12.3f} "
              f"{min(ratios[m]):>7.3f} {max(ratios[m]):>7.3f} {str(found) + ' de ' + str(N_INSTANCES):>15s}")
    worst = max(ratios["MST"])
    print(f"\nPeor razón del MST: {worst:.3f}  ({2 - worst:.3f} por debajo del límite teórico de 2)")
    print(f"Instancias donde el recorrido del MST pasa de 1.5: {sum(r > 1.5 for r in ratios['MST'])} de {N_INSTANCES}")

    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [2, 1]})
    x = range(1, N_INSTANCES + 1)
    ax1.plot(x, ratios["MST"], "o", color="#0072B2", markersize=4, label="MST")
    ax1.plot(x, ratios["MST + 2-opt"], "s", color="#009E73", markersize=4, label="MST + 2-opt")
    ax1.axhline(2, color="#c0392b", linestyle="--", label="Límite teórico (2)")
    ax1.axhline(1, color="k", linestyle=":", label="Óptimo (1)")
    ax1.set_ylim(0.95, 2.1)
    ax1.set_xlabel("Instancia")
    ax1.set_ylabel("Razón = C_obtenido / C_óptimo")
    ax1.set_title("Razón de aproximación por instancia")
    ax1.legend(loc="center right", fontsize=8)
    ax2.hist(ratios["MST"], bins=15, color="#0072B2", alpha=0.7, edgecolor="white", label="MST")
    ax2.axvline(2, color="#c0392b", linestyle="--", label="Límite teórico (2)")
    ax2.axvline(statistics.mean(ratios["MST"]), color="k", linestyle=":",
                label=f"Promedio = {statistics.mean(ratios['MST']):.3f}")
    ax2.set_xlim(0.95, 2.1)
    ax2.set_xlabel("Razón = C_obtenido / C_óptimo")
    ax2.set_ylabel("Número de instancias")
    ax2.set_title("Histograma (MST)")
    ax2.legend(fontsize=8)
    for a in (ax1, ax2):
        a.grid(alpha=0.25)
    fig.suptitle(f"Aproximación con MST en {N_INSTANCES} instancias aleatorias de {N_CITIES} ciudades", fontsize=12)
    plt.tight_layout()
    plt.savefig("mst_ratio.png", dpi=150)

    fig, ax = plt.subplots(figsize=(10, 5.2))
    palette = ["#0072B2", "#009E73", "#E69F00", "#D55E00", "#CC79A7"]
    box = ax.boxplot([ratios[m] for m in METHODS], tick_labels=[m.replace(" (", "\n(") for m in METHODS],
                     patch_artist=True, showmeans=True, widths=0.55,
                     medianprops=dict(color="black"),
                     meanprops=dict(marker="D", markerfacecolor="white", markeredgecolor="black"))
    for patch, color in zip(box["boxes"], palette):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax.axhline(1, color="k", linestyle=":", linewidth=1, label="Óptimo (1)")
    ax.set_ylabel("Costo obtenido / costo óptimo")
    ax.set_title(f"Costo obtenido por cada método ({N_INSTANCES} instancias de {N_CITIES} ciudades; rombo = promedio)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    plt.tight_layout()
    plt.savefig("method_comparison.png", dpi=150)
    print("\nGráficas guardadas en mst_ratio.png y method_comparison.png")
    plt.show()
