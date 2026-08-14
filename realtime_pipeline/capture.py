import cv2
import time
import threading
import queue


class Capture:
    def __init__(self, source, input_queue):
        self.source = source
        self.input_queue = input_queue
        self.running = False
        self.frame_id = 0
        self.dropped = 0

        self.cap = cv2.VideoCapture(
            source,
            cv2.CAP_DSHOW,
        )

        if not self.cap.isOpened():
            self.cap.release()

            self.cap = cv2.VideoCapture(
                source,
                cv2.CAP_MSMF,
            )

        if not self.cap.isOpened():
            self.cap.release()

            self.cap = cv2.VideoCapture(
                source,
                cv2.CAP_ANY,
            )

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Kamera açılamadı. SOURCE değerini değiştir: {source}"
            )

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        print(f"Kamera açıldı: SOURCE = {source}")

    def start(self):
        self.running = True

        self.thread = threading.Thread(
            target=self.run,
            daemon=True,
        )

        self.thread.start()

    def run(self):
        while self.running:
            success, frame = self.cap.read()

            if not success or frame is None:
                print("Kameradan görüntü okunamadı.")
                time.sleep(0.1)
                continue

            item = (
                self.frame_id,
                time.perf_counter(),
                frame,
            )

            self.frame_id += 1

            if self.input_queue.full():
                try:
                    self.input_queue.get_nowait()
                    self.dropped += 1
                except queue.Empty:
                    pass

            try:
                self.input_queue.put_nowait(item)
            except queue.Full:
                self.dropped += 1

    def release(self):
        self.running = False

        if hasattr(self, "thread"):
            self.thread.join(timeout=1)

        self.cap.release()