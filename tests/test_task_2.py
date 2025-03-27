import math
import os
import time

import pytest

from src.task_2 import ExecutorType, integrate, integrate_synchonous

RESOURCE_FOLDER_PATH = os.path.join("artifacts", "task_2")
os.makedirs(RESOURCE_FOLDER_PATH, exist_ok=True)


@pytest.mark.parametrize("executor_type", [ExecutorType.Process, ExecutorType.Thread, "synchronous"])
def test_integration_performance(executor_type):
    a, b = 0, math.pi
    n_iter = 10_000_000
    n_jobs = os.cpu_count() if executor_type != "synchronous" else 1
    attempts = 3
    durations = []

    for _ in range(1, attempts + 1):
        start = time.time()

        if executor_type == "synchronous":
            res = integrate_synchonous(math.sin, a, b, n_iter=n_iter)
        else:
            res = integrate(math.sin, a, b, n_jobs=n_jobs, n_iter=n_iter, executor_type=executor_type)
        assert res == pytest.approx(2, 1e-6)
        end = time.time()
        duration = end - start
        durations.append(duration)

        mode_str = executor_type if isinstance(executor_type, str) else executor_type.name

    average = sum(durations) / attempts
    mode_str = executor_type if isinstance(executor_type, str) else executor_type.name
    filename = f"{mode_str.lower()}.txt"
    path = os.path.join(RESOURCE_FOLDER_PATH, filename)

    with open(path, "w") as f:
        for i, dur in enumerate(durations, 1):
            f.write(f"Attempt {i}: Params — a={a}, b={b:.2f}, iters={n_iter}, workers={n_jobs} → {dur:.4f} seconds\n")
        f.write(f"\nAverage time over {attempts} attempts: {average:.4f} seconds\n")
