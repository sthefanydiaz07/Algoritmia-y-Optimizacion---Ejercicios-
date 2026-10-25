import itertools
import math
import random
import statistics

N_CITIES = 9
N_INSTANCES = 100


def tour_length(points, route) -> float:
    return sum(math.dist(points[route[i]], points[route[(i + 1) % len(route)]])
               for i in range(len(route)))


def two_opt_move(route: list[int], i: int, k: int) -> list[int]:
    return route[:i] + route[i:k + 1][::-1] + route[k + 1:]


def two_opt(points, route):
    n = len(route)
    best = route[:]
    best_len = tour_length(points, best)
    improvements, improved = 0, True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for k in range(i + 1, n):
                candidate = two_opt_move(best, i, k)
                cand_len = tour_length(points, candidate)
                if cand_len < best_len - 1e-9:      
                    best, best_len = candidate, cand_len
                    improvements += 1
                    improved = True
    return best, improvements


def nearest_neighbour(points, start: int) -> list[int]:
    route, pending = [start], set(range(len(points))) - {start}
    while pending:
        last = route[-1]
        nxt = min(pending, key=lambda c: math.dist(points[last], points[c]))
        route.append(nxt)
        pending.remove(nxt)
    return route


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


if __name__ == "__main__":
    rng = random.Random(2024)                     
    rows = []
    for _ in range(N_INSTANCES):
        points = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(N_CITIES)]
        opt = optimal_length(points)

        random_start = list(range(N_CITIES))
        rng.shuffle(random_start)
        nn_start = nearest_neighbour(points, start=rng.randrange(N_CITIES))   

        row = {}
        for label, start in [("random", random_start), ("nn", nn_start)]:
            final, moves = two_opt(points, start)
            row[label] = dict(moves=moves,
                              start_ratio=tour_length(points, start) / opt,
                              final_ratio=tour_length(points, final) / opt)
        rows.append(row)

    def column(label, key):
        return [r[label][key] for r in rows]

    print(f"{N_INSTANCES} instancias aleatorias de {N_CITIES} ciudades. razón = longitud / longitud óptima\n")
    print(f"{'':32s} {'inicio aleatorio':>17s} {'vecino más cercano':>19s}")
    for title, key, fmt in [("Razón del recorrido inicial", "start_ratio", "{:.3f}"),
                            ("Mejoras (promedio)", "moves", "{:.2f}"),
                            ("Razón del óptimo local", "final_ratio", "{:.3f}")]:
        a, b = column("random", key), column("nn", key)
        print(f"{title:32s} {fmt.format(statistics.mean(a)):>17s} {fmt.format(statistics.mean(b)):>19s}")
    print(f"{'Mejoras (mediana)':32s} {statistics.median(column('random', 'moves')):>17.1f} "
          f"{statistics.median(column('nn', 'moves')):>19.1f}")
    print(f"{'Mejoras (máximo)':32s} {max(column('random', 'moves')):>17d} "
          f"{max(column('nn', 'moves')):>19d}")
    reached_random = sum(r["random"]["final_ratio"] < 1 + 1e-9 for r in rows)
    reached_nn = sum(r["nn"]["final_ratio"] < 1 + 1e-9 for r in rows)
    print(f"{'Llegó al recorrido óptimo':32s} {str(reached_random) + ' de ' + str(N_INSTANCES):>17s} "
          f"{str(reached_nn) + ' de ' + str(N_INSTANCES):>19s}")

    fewer = sum(r["nn"]["moves"] < r["random"]["moves"] for r in rows)
    equal = sum(r["nn"]["moves"] == r["random"]["moves"] for r in rows)
    more = N_INSTANCES - fewer - equal
    print(f"\nVecino más cercano necesitó menos mejoras en {fewer} instancias, "
          f"las mismas en {equal} y más en {more}.")

    import matplotlib.pyplot as plt

    colors = ["#0072B2", "#D55E00"]
    labels = ["Inicio aleatorio", "Inicio vecino\nmás cercano"]
    panels = [("Mejoras hasta el óptimo local", "moves", "Número de mejoras"),
              ("Calidad del óptimo local", "final_ratio", "L(óptimo local) / L(óptimo)"),
              ("Calidad del recorrido inicial", "start_ratio", "L(inicial) / L(óptimo)")]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8))
    for ax, (title, key, ylabel) in zip(axes, panels):
        box = ax.boxplot([column("random", key), column("nn", key)], tick_labels=labels,
                         patch_artist=True, showmeans=True, widths=0.55,
                         medianprops=dict(color="black"),
                         meanprops=dict(marker="D", markerfacecolor="white", markeredgecolor="black"))
        for patch, color in zip(box["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.55)
        ax.set_title(title, fontsize=10)
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.25)
    axes[1].axhline(1, color="k", linestyle=":", linewidth=1)
    fig.suptitle(f"2-opt desde dos recorridos iniciales ({N_INSTANCES} instancias de {N_CITIES} ciudades; "
                 f"rombo = promedio)", fontsize=12)
    plt.tight_layout()
    plt.savefig("two_opt_comparison.png", dpi=150)
    print("\nGráfica guardada en two_opt_comparison.png")
    plt.show()
