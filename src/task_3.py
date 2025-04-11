from multiprocessing import Process, Queue, Event
import time
import codecs
from datetime import datetime


def log_message(process_name, message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_time}] {process_name}: {message}")


def process_a(input_queue, output_queue, stop_event):
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


def process_b(input_queue, output_queue, stop_event):
    while not stop_event.is_set():
        if not input_queue.empty():
            message = input_queue.get()
            if message == "STOP":
                output_queue.put("STOP")
                stop_event.set()
                break
            encoded_message = codecs.encode(message, 'rot_13')
            log_message("Процесс B", f"получил '{message}', закодировал в '{encoded_message}'")
            output_queue.put(encoded_message)
            time.sleep(5)


if __name__ == "__main__":
    queue_main_to_a = Queue()
    queue_a_to_b = Queue()
    queue_b_to_main = Queue()
    stop_event = Event()

    proc_a = Process(target=process_a, args=(queue_main_to_a, queue_a_to_b, stop_event))
    proc_b = Process(target=process_b, args=(queue_a_to_b, queue_b_to_main, stop_event))

    proc_a.start()
    proc_b.start()

    try:
        while not stop_event.is_set():
            user_input = input("Введите сообщение (или 'exit' для выхода): ")
            if user_input.lower() == 'exit':
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
