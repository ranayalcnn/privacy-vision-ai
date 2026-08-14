import cv2
import queue
import time
import threading

from config import SOURCE, QUEUE_SIZE, WINDOW_NAME, AUDIT_LOG_PATH
from capture import Capture
from processor import Processor, draw_info


def main():
    input_queue = queue.Queue(maxsize=QUEUE_SIZE)
    output_queue = queue.Queue(maxsize=1)

    capture = Capture(SOURCE, input_queue)
    processor = Processor(AUDIT_LOG_PATH)

    capture.start()

    stop_event = threading.Event()

    def process_frames():
        while not stop_event.is_set():
            try:
                item = input_queue.get(timeout=0.05)
            except queue.Empty:
                if not capture.running:
                    break
                continue

            frame_id, captured_at, frame = item

            processed, face_count = processor.process(frame)

            result = (
                frame_id,
                captured_at,
                processed,
                face_count,
            )

            if output_queue.full():
                try:
                    output_queue.get_nowait()
                except queue.Empty:
                    pass

            try:
                output_queue.put_nowait(result)
            except queue.Full:
                pass

    processing_thread = threading.Thread(
        target=process_frames,
        daemon=True,
    )

    processing_thread.start()

    last_time = time.perf_counter()
    fps = 0.0

    try:
        while (
            capture.running
            or not input_queue.empty()
            or not output_queue.empty()
        ):
            try:
                _, captured_at, frame, face_count = (
                    output_queue.get(timeout=0.05)
                )
            except queue.Empty:
                continue

            now = time.perf_counter()

            instant_fps = 1 / max(
                now - last_time,
                0.0001,
            )

            fps = (
                instant_fps
                if fps == 0
                else fps * 0.9 + instant_fps * 0.1
            )

            last_time = now
            latency = (now - captured_at) * 1000

            draw_info(
                frame,
                fps,
                latency,
                input_queue.qsize(),
                capture.dropped,
                face_count,
            )

            cv2.imshow(WINDOW_NAME, frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        stop_event.set()
        capture.release()
        processing_thread.join(timeout=1)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
