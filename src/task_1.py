# from functools import wraps

# def timer(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         start_time: float = time.time()
#         res = func(*args, **kwargs)
#         end_time: float = time.time()
#         return res, end_time - start_time
#     return wrapper


def fibonacci(n: int) -> int:
    if n < 0:
        raise NotImplementedError("This function can't calculate fibonacci at negative numbers")
    if n <= 1:
        return n
    fst, snd = 0, 1
    for _ in range(2, n + 1):
        fst, snd = snd, fst + snd
    return snd


if __name__ == "__main__":
    n = int(5)
    print(fibonacci(n))
