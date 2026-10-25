import multiprocessing as mp
import os
import random
import statistics
import time

def estimate_pi(seed: int, samples: int = 1_000_000) -> float:
    """Monte Carlo: fracción de puntos aleatorios que caen dentro del cuarto de círculo unitario."""
    rng = random.Random(seed)
    inside = sum(rng.random()**2 + rng.random()**2 <= 1.0 for _ in range(samples))
    return 4 * inside / samples


def _noop(x):
    return x


def measure(seeds: list[int], processes: int, repeats: int = 5):
    """Tiempo real de pool.map(estimate_pi, seeds) con `processes` procesos.
    Devuelve (mediana del tiempo en `repeats` corridas, estimación de pi)."""
    with mp.Pool(processes=processes) as pool:
        pool.map(_noop, range(processes))            # calentamiento: arranca los procesos antes de medir
        times = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            results = pool.map(estimate_pi, seeds)
            times.append(time.perf_counter() - t0)
    return statistics.median(times), sum(results) / len(results)


if __name__ == "__main__":
    seeds = list(range(8))                           # 8 corridas independientes, una semilla cada una
    process_counts = [1, 2, 4, 8]
    cores = os.cpu_count()
    print(f"Núcleos de CPU disponibles: {cores}")
    print(f"Tareas: {len(seeds)} corridas de estimate_pi (1,000,000 de muestras cada una)\n")

    times, speedup = {}, {}
    for p in process_counts:
        times[p], pi_est = measure(seeds, p)
        print(f"procesos = {p}   tiempo = {times[p]:.3f} s   pi ~ {pi_est:.5f}")

    print(f"\n{'procesos':>8s} {'tiempo (s)':>11s} {'speedup':>8s} {'ideal':>6s} {'eficiencia':>11s}")
    for p in process_counts:
        speedup[p] = times[1] / times[p]
        print(f"{p:>8d} {times[p]:>11.3f} {speedup[p]:>7.2f}x {p:>5d}x {speedup[p] / p:>10.0%}")

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.plot(process_counts, process_counts, "--", color="#555555", label="Speedup ideal (= p)")
    ax.plot(process_counts, [min(p, cores) for p in process_counts], ":", color="#999999",
            label=f"Límite por {cores} núcleos de CPU")
    ax.plot(process_counts, [speedup[p] for p in process_counts], "o-", color="#0072B2",
            linewidth=2, markersize=7, label="Medido (multiprocessing)")
    for p in process_counts:
        ax.annotate(f"{speedup[p]:.2f}x", (p, speedup[p]), textcoords="offset points",
                    xytext=(0, -16), ha="center", fontsize=9, color="#0072B2")
    ax.set_ylim(0, max(process_counts) * 1.05)
    ax.set_xlabel("Número de procesos (p)")
    ax.set_ylabel("Speedup = T(1) / T(p)")
    ax.set_title("Aceleración paralela de estimate_pi")
    ax.set_xticks(process_counts)
    ax.grid(alpha=0.25)
    ax.legend()
    plt.tight_layout()
    plt.savefig("speedup_pi.png", dpi=150)
    print("\nGráfica guardada en speedup_pi.png")
    plt.show()
