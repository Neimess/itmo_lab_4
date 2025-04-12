import codecs
import os
import time
from datetime import datetime, timezone
from multiprocessing import Process, get_context
from multiprocessing.queues import Queue as MPQueue
from multiprocessing.synchronize import Event as SyncEvent
from typing import Any

RESOURCE_FOLDER_PATH = os.path.join("artifacts", "task_3")
os.makedirs(RESOURCE_FOLDER_PATH, exist_ok=True)
LOG_FILE = os.path.join(RESOURCE_FOLDER_PATH, "multiprocessing.txt")


def log_message(process_name: str, message: str) -> None:
    """
    Логирует сообщение в консоль и в лог-файл с таймштампом.

    :param process_name: Имя процесса, отправившего сообщение
    :param message: Содержимое сообщения, которое требуется залогировать
    """
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    text = f"[{current_time}] {process_name}: {message}"
    print(text)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")


def process_a(input_queue: MPQueue[Any], output_queue: MPQueue[Any], stop_event: SyncEvent) -> None:
    """
    Процесс A: принимает строки из очереди input_queue,
    преобразует их в нижний регистр и отправляет в output_queue.
    После каждой отправки ждёт 5 секунд.

    :param input_queue: Очередь, из которой приходят исходные сообщения
    :param output_queue: Очередь, в которую отправляются преобразованные сообщения
    :param stop_event: Событие, сигнализирующее о необходимости остановки
    """
    while not stop_event.is_set():
        if not input_queue.empty():
            message = input_queue.get()
            if message == "STOP":
                output_queue.put("STOP")
                stop_event.set()
                break
            processed_message = message.lower()
            log_message("Процесс A", f"обработал '{message}' -> '{processed_message}'")
            output_queue.put(processed_message)
            time.sleep(5)


def process_b(input_queue: MPQueue[Any], output_queue: MPQueue[Any], stop_event: SyncEvent) -> None:
    """
    Процесс B: принимает строки из очереди input_queue,
    кодирует их в ROT13 и отправляет в output_queue.

    :param input_queue: Очередь, из которой приходят сообщения от A
    :param output_queue: Очередь, в которую отправляются закодированные сообщения
    :param stop_event: Событие, сигнализирующее о необходимости остановки
    """
    while not stop_event.is_set():
        if not input_queue.empty():
            message = input_queue.get()
            if message == "STOP":
                output_queue.put("STOP")
                stop_event.set()
                break
            encoded_message = codecs.encode(message, "rot_13")
            log_message("Процесс B", f"получил '{message}', закодировал в '{encoded_message}'")
            output_queue.put(encoded_message)


def process_main() -> None:
    queue_main_to_a: MPQueue[str] = MPQueue()
    queue_a_to_b: MPQueue[str] = MPQueue()
    queue_b_to_main: MPQueue[str] = MPQueue()
    ctx = get_context("spawn")
    stop_event: SyncEvent = ctx.Event()

    proc_a = Process(target=process_a, args=(queue_main_to_a, queue_a_to_b, stop_event))
    proc_b = Process(target=process_b, args=(queue_a_to_b, queue_b_to_main, stop_event))

    proc_a.start()
    proc_b.start()

    try:
        while not stop_event.is_set():
            user_input = input("Введите сообщение (или 'exit' для выхода): ")
            if user_input.lower() == "exit":
                queue_main_to_a.put("STOP")
                stop_event.set()
                break
            queue_main_to_a.put(user_input)

            if not queue_b_to_main.empty():
                encoded_response = queue_b_to_main.get()
                if encoded_response == "STOP":
                    break
                log_message("Главный процесс", f"получил от процесса B: '{encoded_response}'")

    except KeyboardInterrupt:
        queue_main_to_a.put("STOP")
        stop_event.set()

    proc_a.join()
    proc_b.join()

    log_message("Главный процесс", "завершён.")


if __name__ == "__main__":
    process_main()
