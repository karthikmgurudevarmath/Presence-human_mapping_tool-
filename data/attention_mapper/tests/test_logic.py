import unittest
import os
import sys
import time
import shutil

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from analyzer import DataAnalyzer

class TestAttentionLogic(unittest.TestCase):
    def setUp(self):
        self.test_db = "data/test_session.db"
        if not os.path.exists("data"):
            os.makedirs("data")
        self.db = Database(self.test_db)
        self.analyzer = DataAnalyzer(self.test_db)

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_database_logging(self):
        self.db.log_event("test_event", 100, 200, "Test Window")
        df = self.analyzer.get_session_data()
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['event_type'], "test_event")
        self.assertEqual(df.iloc[0]['window_title'], "Test Window")

    def test_batch_logging(self):
        events = [
            (time.time(), "move", 1, 1, "App1"),
            (time.time(), "move", 2, 2, "App1"),
            (time.time(), "click", 3, 3, "App2"),
        ]
        self.db.log_events_batch(events)
        df = self.analyzer.get_session_data()
        self.assertEqual(len(df), 3)

    def test_metrics_calculation(self):
        now = time.time()
        events = [
            (now, "start", 0, 0, "App"),
            (now + 10, "move", 1, 1, "App"),
            (now + 60, "idle", 0, 0, "App"), # 5s idle estimated
            (now + 120, "end", 0, 0, "App")
        ]
        self.db.log_events_batch(events)
        metrics = self.analyzer.calculate_metrics()
        
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics['total_time'], 2.0) # 120s / 60
        self.assertEqual(metrics['idle_time'], 0.08) # 5s / 60 = 0.0833
        self.assertEqual(metrics['focus_time'], 1.92) # 2.0 - 0.08 = 1.92

    def test_clear_data(self):
        self.db.log_event("test", 0, 0)
        self.db.clear_data()
        df = self.analyzer.get_session_data()
        self.assertTrue(df.empty)

if __name__ == '__main__':
    unittest.main()
