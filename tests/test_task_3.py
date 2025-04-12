import codecs
from multiprocessing import Event, Process, Queue

import pytest

from src.task_3 import log_message, process_a, process_b


def test_full_pipeline():
    queue_main_to_a = Queue()
    queue_a_to_b = Queue()
    queue_b_to_main = Queue()
    stop_event = Event()

    proc_a = Process(target=process_a, args=(queue_main_to_a, queue_a_to_b, stop_event))
    proc_b = Process(target=process_b, args=(queue_a_to_b, queue_b_to_main, stop_event))
    proc_a.start()
    proc_b.start()

    messages = ["Hello World", "Python", "Multiprocessing", "Test"]
    # Ожидаемые преобразования:
    # process_a -> перевод в нижний регистр: "hello world"
    # process_b -> применение ROT13: "uryyb jbeyq"
    expected_results = [codecs.encode(msg.lower(), "rot_13") for msg in messages]

    for msg in messages:
        log_message("Главный процесс", f"Отправлено сообщение {msg} в процесс A")
        queue_main_to_a.put(msg)

    results = []
    for idx in range(len(messages)):
        try:
            result = queue_b_to_main.get()
            log_message("Главный процесс", f"Получено сообщение от B: {result}")
            results.append(result)
        except Exception:
            stop_event.set()
            proc_a.join()
            proc_b.join()
            pytest.fail(f"Не удалось получить ответ для сообщения {idx + 1} в заданное время.")

    assert results == expected_results, f"Ожидалось {expected_results}, получено {results}"

    queue_main_to_a.put("STOP")
    proc_a.join()
    proc_b.join()
