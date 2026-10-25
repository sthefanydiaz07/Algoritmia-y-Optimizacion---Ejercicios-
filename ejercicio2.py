def knapsack(values: list[int], weights: list[int], W: int):
    n = len(values)
    K = [[0] * (W + 1) for _ in range(n + 1)]   
    for i in range(1, n + 1):
        v, w = values[i - 1], weights[i - 1]
        for c in range(W + 1):
            K[i][c] = K[i - 1][c]                                  
            if w <= c:
                K[i][c] = max(K[i][c], v + K[i - 1][c - w])       
    chosen, c = [], W                           
    for i in range(n, 0, -1):
        if K[i][c] != K[i - 1][c]:
            chosen.append(i - 1)
            c -= weights[i - 1]
    return K, K[n][W], chosen[::-1]


def greedy(values: list[int], weights: list[int], W: int, key):
    order = sorted(range(len(values)), key=key)
    chosen, used, total = [], 0, 0
    for i in order:
        if used + weights[i] <= W:
            chosen.append(i)
            used += weights[i]
            total += values[i]
    return sorted(chosen), used, total


def greedy_ratio(values, weights, W):
    return greedy(values, weights, W, key=lambda i: -values[i] / weights[i])


def greedy_lowest_weight(values, weights, W):
    return greedy(values, weights, W, key=lambda i: weights[i])


def solve(title, items, values, weights, W):
    print(f"\n=== {title}  (capacidad W = {W}) ===")
    print(f"{'objeto':>6s} {'peso':>5s} {'valor':>6s} {'v/w':>6s}")
    for name, w, v in zip(items, weights, values):
        print(f"{name:>6s} {w:>5d} {v:>6d} {v / w:>6.2f}")

    _, opt_value, opt_idx = knapsack(values, weights, W)
    methods = {
        "Valor/peso": greedy_ratio(values, weights, W),
        "Menor peso": greedy_lowest_weight(values, weights, W),
        "Óptimo (PD)": (opt_idx, sum(weights[i] for i in opt_idx), opt_value),
    }
    print(f"\n{'método':12s} {'objetos elegidos':18s} {'capacidad usada':>16s} {'valor total':>12s}")
    for label, (idx, used, total) in methods.items():
        print(f"{label:12s} {str([items[i] for i in idx]):18s} {f'{used} / {W}':>16s} {total:>12d}")

    v_ratio, v_weight = methods["Valor/peso"][2], methods["Menor peso"][2]
    if v_weight < v_ratio:
        print(f"-> Menor peso es PEOR: {v_weight} contra {v_ratio} (pierde {v_ratio - v_weight}).")
    elif v_weight > v_ratio:
        print(f"-> Menor peso es MEJOR: {v_weight} contra {v_ratio}.")
    else:
        print(f"-> Los dos métodos voraces EMPATAN con valor {v_ratio}.")
    return methods


if __name__ == "__main__":
    names1, values1, weights1, W1 = ["A", "B", "C"], [60, 100, 120], [10, 20, 30], 50
    names2, values2, weights2, W2 = ["A", "B", "C"], [2, 5, 70], [1, 2, 8], 10

    instances = [
        ("Instancia 1", names1, values1, weights1, W1),
        ("Instancia 2 (diseñada: menor peso pierde)", names2, values2, weights2, W2),
    ]
    results = [solve(*inst) for inst in instances]

    import matplotlib.pyplot as plt

    colors = {"Valor/peso": "#0072B2", "Menor peso": "#D55E00", "Óptimo (PD)": "#999999"}
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    for row, ((title, names, values, weights, W), methods) in enumerate(zip(instances, results)):
        labels = list(methods)
        ax = axes[row][0]
        grid = [[1 if i in methods[m][0] else 0 for i in range(len(names))] for m in labels]
        ax.imshow(grid, cmap="Blues", vmin=0, vmax=1.6, aspect="auto")
        for r, m in enumerate(labels):
            for c, name in enumerate(names):
                ax.text(c, r, f"{name}\n(w={weights[c]}, v={values[c]})", ha="center", va="center",
                        fontsize=8, color="white" if grid[r][c] else "#777777")
        ax.set_xticks([])
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels)
        ax.set_title("Objetos elegidos (oscuro = tomado)")
        ax = axes[row][1]
        ax.bar(labels, [methods[m][1] for m in labels], color=[colors[m] for m in labels], width=0.6)
        ax.axhline(W, color="k", linestyle="--", linewidth=1, label=f"Capacidad W = {W}")
        for x, m in enumerate(labels):
            ax.text(x, methods[m][1] + W * 0.02, str(methods[m][1]), ha="center", fontsize=9)
        ax.set_ylim(0, W * 1.35)
        ax.set_title("Capacidad usada")
        ax.legend(loc="upper left", fontsize=8)
        # (3) valor total
        ax = axes[row][2]
        top = max(methods[m][2] for m in labels)
        ax.bar(labels, [methods[m][2] for m in labels], color=[colors[m] for m in labels], width=0.6)
        for x, m in enumerate(labels):
            ax.text(x, methods[m][2] + top * 0.02, str(methods[m][2]), ha="center", fontsize=9)
        ax.set_ylim(0, top * 1.15)
        ax.set_title("Valor total")
        for a in axes[row][1:]:
            a.grid(axis="y", alpha=0.25)
            a.tick_params(axis="x", labelsize=8)
        axes[row][0].set_ylabel(title, fontsize=9, labelpad=12)
    fig.suptitle("Mochila voraz: valor/peso contra menor peso primero", fontsize=13)
    plt.tight_layout()
    plt.savefig("knapsack_comparison.png", dpi=150)
    print("\nGráfica guardada en knapsack_comparison.png")
    plt.show()
