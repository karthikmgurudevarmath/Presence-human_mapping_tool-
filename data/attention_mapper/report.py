import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from analyzer import DataAnalyzer

class ReportGenerator:
    def __init__(self, db_path="data/session.db"):
        self.analyzer = DataAnalyzer(db_path)

    def generate_heatmap(self, filename="heatmap.png"):
        data = self.analyzer.get_heatmap_data()
        if data.empty:
            return None

        plt.style.use('dark_background')
        plt.figure(figsize=(10, 6))
        sns.kdeplot(data=data, x='x', y='y', cmap="magma", fill=True, thresh=0, levels=100)
        plt.title("Presence: Attention Heatmap", pad=20)
        plt.xlabel("Screen Width (px)")
        plt.ylabel("Screen Height (px)")
        plt.gca().invert_yaxis()
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"data/{timestamp}_{filename}"
        plt.savefig(report_path, bbox_inches='tight', dpi=150)
        plt.close()
        return report_path

    def generate_activity_graph(self, filename="activity_graph.png"):
        df = self.analyzer.get_session_data()
        if df.empty:
            return None

        plt.style.use('bmh')
        # Bucket activity by minute
        import pandas as pd
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        activity = df.resample('1Min', on='datetime').size()

        plt.figure(figsize=(12, 5))
        activity.plot(kind='line', marker='o', color='#3498db', linewidth=2)
        plt.fill_between(activity.index, activity.values, color='#3498db', alpha=0.3)
        plt.title("Presence: Interaction Pulse", pad=15)
        plt.xlabel("Time")
        plt.ylabel("Event Count")
        plt.grid(True, alpha=0.3)
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"data/{timestamp}_{filename}"
        plt.savefig(report_path, bbox_inches='tight', dpi=150)
        plt.close()
        return report_path

    def generate_window_report(self, filename="app_usage.png"):
        stats = self.analyzer.get_window_durations()
        if stats.empty:
            return None

        plt.style.use('ggplot')
        plt.figure(figsize=(12, 6))
        
        # Plot top 10 apps
        top_stats = stats.head(10).sort_values(ascending=True)
        top_stats.plot(kind='barh', color='#8e44ad')
        
        plt.title("Presence: App & Web Usage", pad=15)
        plt.xlabel("Duration (Minutes)")
        plt.ylabel("Application / Website Window Title")
        plt.grid(True, axis='x', alpha=0.3)
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"data/{timestamp}_{filename}"
        plt.savefig(report_path, bbox_inches='tight', dpi=150)
        plt.close()
        return report_path
