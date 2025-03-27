import multiprocessing
import os
import threading
import time

import pytest

from src.task_1 import fibonacci

RESOURCE_FOLDER_PATH = os.path.join("artifacts", "task_1")
os.makedirs(RESOURCE_FOLDER_PATH, exist_ok=True)


def run_fib_n_times(n, times):
    for _ in range(times):
        fibonacci(n)


def measure_sync(n: int, runs: int):
    start = time.time()
    run_fib_n_times(n, runs)
    return time.time() - start


def measure_threading(n: int, threads_count: int):
    threads = []
    start = time.time()
    for _ in range(threads_count):
        t = threading.Thread(target=fibonacci, args=(n,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return time.time() - start


def measure_multiprocessing(n: int, proc_count: int):
    processes = []
    start = time.time()
    for _ in range(proc_count):
        p = multiprocessing.Process(target=fibonacci, args=(n,))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    return time.time() - start


@pytest.mark.parametrize(
    "n, concurrency_mode", [(int(10e4), "synchronous"), (int(10e4), "threading"), (int(10e4), "multiprocessing")]
)
def test_fibonacci_performance(n, concurrency_mode):
    runs = 10
    attempts = 3
    durations = []
    for i in range(attempts):
        if concurrency_mode == "synchronous":
            duration = measure_sync(n, runs)
        elif concurrency_mode == "threading":
            duration = measure_threading(n, runs)
        elif concurrency_mode == "multiprocessing":
            duration = measure_multiprocessing(n, runs)
        else:
            raise ValueError("Unknown concurrency mode")

        durations.append(duration)

        result_path = os.path.join(RESOURCE_FOLDER_PATH, f"{concurrency_mode}.txt")
        with open(result_path, "w") as f:
            f.write(
                f"Attempt {i + 1} {concurrency_mode} took {duration:.4f} seconds for {runs} runs of fibonacci({n})\n"
            )
    average = sum(durations) / attempts
    with open(result_path, "a") as f:
        f.write(f"\nAverage time for {concurrency_mode}: {average:.4f} seconds over {attempts} attemps\n")
