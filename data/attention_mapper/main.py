import tkinter as tk
from tkinter import ttk, messagebox
from tracker import AttentionTracker
from analyzer import DataAnalyzer
from report import ReportGenerator
import threading
import time

class AttentionMapperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Offline Human Attention Mapping Tool")
        self.root.geometry("400x450")
        
        self.tracker = AttentionTracker()
        self.analyzer = DataAnalyzer()
        self.reporter = ReportGenerator()
        
        self.is_tracking = False
        
        self.setup_ui()
        self.update_stats()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#2c3e50")
        style.configure("TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#3498db")
        style.configure("Status.TLabel", font=("Segoe UI", 9, "italic"))
        style.configure("TButton", padding=8, font=("Segoe UI", 10))
        style.configure("Action.TButton", background="#3498db", foreground="white")
        style.map("Action.TButton", background=[('active', '#2980b9')])
        
        # Main Layout
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Presence", style="Header.TLabel")
        title_label.pack(pady=(0, 10))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Status: Ready", foreground="#3498db", style="Status.TLabel")
        self.status_label.pack(pady=5)
        
        # Metrics Display
        metrics_frame = ttk.LabelFrame(main_frame, text=" Session Insights ", padding="15")
        metrics_frame.pack(fill=tk.BOTH, pady=10, expand=True)
        
        self.focus_label = ttk.Label(metrics_frame, text="Focus Time: 0.0 min")
        self.focus_label.pack(anchor=tk.W, pady=2)
        
        self.idle_label = ttk.Label(metrics_frame, text="Idle Time: 0.0 min")
        self.idle_label.pack(anchor=tk.W, pady=2)
        
        self.activity_label = ttk.Label(metrics_frame, text="Activity Events: 0")
        self.activity_label.pack(anchor=tk.W, pady=2)

        self.top_windows_label = ttk.Label(metrics_frame, text="Top Windows: N/A", wraplength=300, justify=tk.LEFT)
        self.top_windows_label.pack(anchor=tk.W, pady=(10, 0))
        
        # Controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=15)
        
        self.toggle_btn = ttk.Button(controls_frame, text="Start Tracking", command=self.toggle_tracking, style="Action.TButton")
        self.toggle_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.report_btn = ttk.Button(controls_frame, text="Generate Reports", command=self.generate_reports)
        self.report_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Secondary Actions
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X)

        self.clear_btn = ttk.Button(action_frame, text="Clear Data", command=self.clear_data)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)

    def toggle_tracking(self):
        if not self.is_tracking:
            self.tracker.start()
            self.is_tracking = True
            self.toggle_btn.config(text="Stop Tracking")
            self.status_label.config(text="Status: Tracking...", foreground="green")
            messagebox.showinfo("Started", "Tracking has started. Move your mouse or type to begin mapping!")
        else:
            self.tracker.stop()
            self.is_tracking = False
            self.toggle_btn.config(text="Start Tracking")
            self.status_label.config(text="Status: Stopped", foreground="red")
            messagebox.showinfo("Stopped", "Tracking stopped. You can now generate reports.")

    def update_stats(self):
        try:
            metrics = self.analyzer.calculate_metrics()
            if metrics:
                self.focus_label.config(text=f"Focus Time: {metrics['focus_time']} min")
                self.idle_label.config(text=f"Idle Time: {metrics['idle_time']} min")
                self.activity_label.config(text=f"Activity Events: {metrics['activity_level']}")
                
                # Display top 2 windows
                if metrics.get('top_windows'):
                    top_text = "Top Active Apps:\n" + "\n".join([f"- {k[:30]}..." for k in metrics['top_windows'].keys()])
                    self.top_windows_label.config(text=top_text)
        except Exception:
            pass
        self.root.after(3000, self.update_stats)

    def clear_data(self):
        if self.is_tracking:
            messagebox.showwarning("Busy", "Please stop tracking before clearing data.")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all recorded data?"):
            self.tracker.db.clear_data()
            self.update_stats()
            messagebox.showinfo("Success", "All session data has been cleared.")

    def generate_reports(self):
        if self.is_tracking:
            messagebox.showwarning("Warning", "Please stop tracking before generating reports.")
            return
            
        try:
            # Show a brief "processing" status
            self.status_label.config(text="Status: Generating reports...", foreground="#f1c40f")
            self.root.update()
            
            heatmap = self.reporter.generate_heatmap()
            graph = self.reporter.generate_activity_graph()
            usage = self.reporter.generate_window_report()
            
            self.status_label.config(text="Status: Ready", foreground="#3498db")
            
            if heatmap and graph:
                messagebox.showinfo("Success", f"Reports generated successfully!\n\nCheck 'data' folder for:\n- Heatmap\n- Activity Graph\n- App Usage Stats")
            else:
                messagebox.showwarning("Incomplete", "Not enough data to generate reports yet (need mouse/key activity).")
        except Exception as e:
            self.status_label.config(text="Status: Report Error", foreground="#e74c3c")
            messagebox.showerror("Error", f"Failed to generate reports: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AttentionMapperApp(root)
    root.mainloop()
