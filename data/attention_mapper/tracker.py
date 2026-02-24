import time
import threading
from queue import Queue
from pynput import mouse, keyboard
import pygetwindow as gw
from database import Database

class AttentionTracker:
    def __init__(self, db_path="data/session.db", idle_threshold=10):
        self.db = Database(db_path)
        self.event_queue = Queue()
        self.stop_event = threading.Event()
        self.last_activity_time = time.time()
        self.idle_threshold = idle_threshold  # seconds
        
        # Batch logging thread
        self.db_thread = threading.Thread(target=self._process_queue, daemon=True)
        
    def _get_active_window(self):
        try:
            window = gw.getActiveWindow()
            return window.title if window else "Unknown"
        except:
            return "Unknown"

    def _log_event(self, event_type, x=0, y=0):
        current_time = time.time()
        window_title = self._get_active_window()
        self.event_queue.put((current_time, event_type, x, y, window_title))
        self.last_activity_time = current_time

    def _process_queue(self):
        while not self.stop_event.is_set() or not self.event_queue.empty():
            batch = []
            try:
                while not self.event_queue.empty() and len(batch) < 100:
                    batch.append(self.event_queue.get_nowait())
                
                if batch:
                    self.db.log_events_batch(batch)
            except Exception as e:
                print(f"Error processing queue: {e}")
            
            time.sleep(0.5) # Reduced sleep for better responsiveness

    def on_move(self, x, y):
        # Throttle mouse move events to avoid flooding
        if time.time() - self.last_activity_time > 0.1:
            self._log_event("move", x, y)

    def on_click(self, x, y, button, pressed):
        if pressed:
            self._log_event("click", x, y)

    def on_press(self, key):
        self._log_event("key")

    def stop(self):
        self.stop_event.set()
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
        
        if hasattr(self, 'db_thread') and self.db_thread.is_alive():
            self.db_thread.join(timeout=2)

    def start(self):
        self.stop_event.clear()
        self.db_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.db_thread.start()
        
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        # Idle detection loop
        threading.Thread(target=self._idle_check, daemon=True).start()

    def _idle_check(self):
        while not self.stop_event.is_set():
            if time.time() - self.last_activity_time > self.idle_threshold:
                # Log idle state
                self._log_event("idle")
            time.sleep(5)

if __name__ == "__main__":
    tracker = AttentionTracker()
    print("Tracker started. Press Ctrl+C to stop.")
    tracker.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tracker.stop()
        print("Tracker stopped.")
