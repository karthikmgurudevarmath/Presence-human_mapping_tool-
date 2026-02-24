import pandas as pd
import sqlite3
from database import Database

class DataAnalyzer:
    def __init__(self, db_path="data/session.db"):
        self.db_path = db_path

    def get_session_data(self):
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query("SELECT * FROM events", conn)
        finally:
            conn.close()
        return df

    def calculate_metrics(self):
        df = self.get_session_data()
        if df.empty:
            return None

        # total_time from first to last event
        total_seconds = df['timestamp'].max() - df['timestamp'].min()
        
        idle_events = df[df['event_type'] == 'idle']
        
        # Idle calculation: Estimate idle time based on idle events (logged every 5s)
        idle_seconds = len(idle_events) * 5 
        focus_seconds = max(0, total_seconds - idle_seconds)

        # Top 3 Windows
        top_windows = df[df['window_title'] != 'Unknown']['window_title'].value_counts().head(3).to_dict()

        return {
            "total_time": round(total_seconds / 60, 2),  # minutes
            "idle_time": round(idle_seconds / 60, 2),   # minutes
            "focus_time": round(focus_seconds / 60, 2), # minutes
            "activity_level": len(df[df['event_type'].isin(['click', 'key'])]),
            "top_windows": top_windows
        }

    def get_window_durations(self):
        df = self.get_session_data()
        if df.empty:
            return pd.Series(dtype=float)
        
        # Calculate duration as the difference between current and next event
        df = df.sort_values('timestamp')
        df['duration'] = df['timestamp'].diff().shift(-1).fillna(0)
        
        # Filter out gaps larger than 30 seconds (likely inactive or app switch gap)
        # to focus on 'attention' time
        df.loc[df['duration'] > 30, 'duration'] = 0
        
        # Group by window title and sum durations in minutes
        stats = df.groupby('window_title')['duration'].sum() / 60
        return stats.sort_values(ascending=False)

    def get_heatmap_data(self):
        df = self.get_session_data()
        # Filter mouse movements and clicks with valid coordinates
        data = df[df['event_type'].isin(['move', 'click'])][['x', 'y']].copy()
        return data.dropna()

