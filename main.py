import threading
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext
import time

class Peterson:
    def __init__(self, num_processes):
        self.num_processes = num_processes
        self.flag = [False] * num_processes
        self.turn = 0

    def lock(self, pid):
        other = (pid + 1) % self.num_processes
        self.flag[pid] = True
        self.turn = other
        while self.flag[other] and self.turn == other:
            time.sleep(0.001)

    def unlock(self, pid):
        self.flag[pid] = False


class Main(tk.Tk):
    FILE_NAME = 'first_thread_output.txt'
    SYSTEM_FILE_NAME = 'second_thread_output.txt'
    counter = 0

    def __init__(self):
        super().__init__()

        self.peterson = Peterson(2)

        self.title("Алгоритм Питерсона")
        self.geometry("1000x620")

        # Поле для ввода текста
        self.textBox1 = scrolledtext.ScrolledText(self, width=55, height=10)
        self.textBox1.pack(pady=10)

        # Поле для вывода текста
        self.textBox2 = scrolledtext.ScrolledText(self, width=55, height=10)
        self.textBox2.pack(pady=10)

        # Поле для системного вывода
        self.textBox3 = scrolledtext.ScrolledText(self, width=55, height=10)
        self.textBox3.pack(pady=10)

        self.control_frame = tk.Frame(self)
        self.control_frame.pack(pady=10)

        # Кнопка "Старт"
        self.startButton = tk.Button(self.control_frame, text="Старт", command=self.start_processes, bg="lightgreen", fg="black")
        self.startButton.pack(side=tk.LEFT, padx=10)

        # Кнопка "Выход"
        self.stopButton = tk.Button(self.control_frame, text="Выход", command=self.quit, bg="red", fg="white")
        self.stopButton.pack(side=tk.LEFT, padx=10)

        # Кнопка "Справка"
        self.helpButton = tk.Button(self.control_frame, text="Справка", command=self.show_help, bg="lightblue", fg="black")
        self.helpButton.pack(side=tk.LEFT, padx=10)

        # Скорость работы потоков
        self.producer_speed = tk.DoubleVar(value=1.0)
        self.consumer_speed = tk.DoubleVar(value=1.0)

        tk.Label(self.control_frame, text="Скорость продюсера (сек):").pack(side=tk.LEFT, padx=5)
        self.producer_speed_slider = tk.Scale(self.control_frame, from_=1, to=5, orient=tk.HORIZONTAL, variable=self.producer_speed)
        self.producer_speed_slider.pack(side=tk.LEFT, padx=5)

        tk.Label(self.control_frame, text="Скорость потребителя (сек):").pack(side=tk.LEFT, padx=5)
        self.consumer_speed_slider = tk.Scale(self.control_frame, from_=1, to=5, orient=tk.HORIZONTAL, variable=self.consumer_speed)
        self.consumer_speed_slider.pack(side=tk.LEFT, padx=5)

        self.system_output_accumulated = """"""

        # Используем Event для синхронизации потоков
        self.producer_event = threading.Event()
        self.consumer_event = threading.Event()
        self.consumer_event.set()  # Начнем с продюсера

    def show_help(self):
        help_window = tk.Toplevel(self)
        help_window.title("Справка")
        help_window.geometry("400x300")

        help_text = """
        С помощью алгоритма Питерсона организовать работу параллельных вычислительных потоков.
        Первый поток записывает в файл введенные пользователем символы, кроме первого и последнего.
        Второй поток записывает в файл текущее время и количество символов в файле.
        """

        text_widget = scrolledtext.ScrolledText(help_window, width=100, height=30)
        text_widget.pack(padx=30, pady=30)
        text_widget.insert(tk.END, help_text)
        text_widget.configure(state='disabled')

    @classmethod
    def static_counter(cls):
        cls.counter += 1
        return cls.counter

    def producer(self):
        while True:
            input_text = self.textBox1.get("1.0", tk.END).strip()
            if input_text:
                lines = input_text.split('\n')
                for line in lines:
                    time.sleep(self.producer_speed.get())
                    self.peterson.lock(0)
                    try:
                        time.sleep(0.3)
                        if len(line) > 2:
                            modified_text = line[1:-1]
                            with open(self.FILE_NAME, 'a') as writer:
                                writer.write(modified_text + '\n')
                            self.textBox2.insert(tk.END, modified_text + '\n')
                    finally:
                        self.peterson.unlock(0)
                        self.producer_event.set()

    def consumer(self):
        consumer_str: int = 0
        consumer_acummulate:int = 0
        while True:
            time.sleep(self.consumer_speed.get())
            if len(self.textBox2.get("1.0", tk.END).strip().split('\n')) <= consumer_str:
                continue
            self.peterson.lock(1)
            try:
                time.sleep(0.3)
                system_output_text = self.textBox2.get("1.0", tk.END).strip()
                if system_output_text:
                    self.system_output_accumulated += system_output_text.split('\n')[consumer_str]
                    consumer_acummulate += len(self.system_output_accumulated)
                    consumer_str += 1
                if self.system_output_accumulated:
                    with open(self.SYSTEM_FILE_NAME, 'a') as writer:
                        time_and_length = f"{datetime.now()}: Длина файла - {consumer_acummulate} символов"
                        writer.write(time_and_length + '\n')
                        self.textBox3.insert(tk.END, time_and_length + '\n')
                    self.system_output_accumulated = ""
            finally:
                self.peterson.unlock(1)
                self.consumer_event.set()

    def start_processes(self):
        self.producer_thread = threading.Thread(target=self.producer, daemon=True)
        self.consumer_thread = threading.Thread(target=self.consumer, daemon=True)
        self.producer_thread.start()
        self.consumer_thread.start()

    def quit(self):
        self.destroy()


if __name__ == '__main__':
    main = Main()
    main.mainloop()
