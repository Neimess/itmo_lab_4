import concurrent.futures as ft
import os
from enum import Enum
from typing import Callable, Optional, Union


class ExecutorType(Enum):
    Process = 1
    Thread = 2


def integrate_range(f: Callable[[float], float], a: float, step: float, start_i: int, end_i: int) -> float:
    acc = 0.0
    for i in range(start_i, end_i):
        acc += f(a + i * step) * step
    return acc


def integrate(
    f: Callable[[float], float],
    a: float,
    b: float,
    n_jobs: int | None = os.cpu_count(),
    n_iter: int = 10_000_000,
    executor_type: ExecutorType = ExecutorType.Process,
) -> float:
    if n_jobs is None:
        n_jobs = os.cpu_count() or 1

    step = (b - a) / n_iter
    chunk_size = n_iter // n_jobs

    ranges = [(f, a, step, i * chunk_size, (i + 1) * chunk_size) for i in range(n_jobs)]

    if n_iter % n_jobs != 0:
        ranges[-1] = (f, a, step, ranges[-1][3], n_iter)

    executor_class: Optional[Union[type[ft.ThreadPoolExecutor], type[ft.ProcessPoolExecutor]]] = {
        ExecutorType.Process: ft.ProcessPoolExecutor,
        ExecutorType.Thread: ft.ThreadPoolExecutor,
    }.get(executor_type)

    if executor_class is None:
        raise ValueError("Uknown executor type")

    with executor_class(max_workers=n_jobs) as executor:
        futures = [executor.submit(integrate_range, *args) for args in ranges]
        results = [f.result() for f in futures]

    return sum(results)


def integrate_synchonous(f: Callable[[float], float], a: float, b: float, n_iter: int = 10_000_000) -> float:
    acc = 0.0
    step = (b - a) / n_iter
    for i in range(n_iter):
        acc += f(a + i * step) * step
    return acc
