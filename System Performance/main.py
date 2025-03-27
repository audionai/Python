import psutil
import time
import threading
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import logging

class SystemMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Performance Monitor")
        self.root.geometry("800x600")

        # --- Variables ---
        self.cpu_data = []
        self.mem_data = []
        self.time_data = []
        self.max_data_points = 60
        self.update_interval = 1000
        self.is_running = True

        # --- Logging Configuration ---
        logging.basicConfig(filename='system_monitor.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("Application started.")

        # --- UI Elements ---
        self.cpu_label = tk.Label(root, text="CPU Usage: ", font=("Arial", 12))
        self.cpu_label.pack(pady=(10, 0))
        self.mem_label = tk.Label(root, text="Memory Usage: ", font=("Arial", 12))
        self.mem_label.pack()

        # --- Matplotlib Figure and Axes ---
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("CPU and Memory Usage", fontdict={'family': 'Arial', 'size': 14}) # Changed to fontdict
        self.ax.set_xlabel("Time (s)", fontdict={'family': 'Arial', 'size': 12}) # Changed to fontdict
        self.ax.set_ylabel("Usage (%)", fontdict={'family': 'Arial', 'size': 12}) # Changed to fontdict
        self.ax.set_xlim(0, self.max_data_points)
        self.ax.set_ylim(0, 100)
        self.line1, = self.ax.plot([], [], 'r-', label="CPU")
        self.line2, = self.ax.plot([], [], 'b-', label="Memory")
        self.ax.legend(loc="upper right")
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Stop Button ---
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_monitoring, font=("Arial", 12), bg="red", fg="white")
        self.stop_button.pack(pady=10)

        # --- Start Data Collection and Update ---
        self.thread = threading.Thread(target=self.fetch_data)
        self.thread.daemon = True
        self.thread.start()
        self.ani = animation.FuncAnimation(self.fig, self.update_graph, interval=self.update_interval, blit=False)

    def fetch_data(self):
        """Collects CPU and memory usage data in a loop."""
        while self.is_running:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                mem_percent = psutil.virtual_memory().percent
                timestamp = time.time()

                self.cpu_data.append(cpu_percent)
                self.mem_data.append(mem_percent)
                self.time_data.append(timestamp)

                self.cpu_data = self.cpu_data[-self.max_data_points:]
                self.mem_data = self.mem_data[-self.max_data_points:]
                self.time_data = self.time_data[-self.max_data_points:]

                self.root.after(0, lambda: self.cpu_label.config(text=f"CPU Usage: {cpu_percent}%"))
                self.root.after(0, lambda: self.mem_label.config(text=f"Memory Usage: {mem_percent}%"))
                logging.info(f"CPU Usage: {cpu_percent}%, Memory Usage: {mem_percent}%")

            except Exception as e:
                logging.error(f"Error fetching data: {e}")
                print(f"Error fetching data: {e}")
                self.is_running = False
                self.root.after(0, lambda: tk.messagebox.showerror("Error", f"Error fetching data: {e}"))
            time.sleep(1)

    def update_graph(self, frame):
        """Updates the Matplotlib graph with new data."""
        if not self.is_running:
            return

        start_time = self.time_data[0] if self.time_data else 0
        x_data = [t - start_time for t in self.time_data]

        self.line1.set_data(x_data, self.cpu_data)
        self.line2.set_data(x_data, self.mem_data)

        if len(x_data) > 0:
            self.ax.set_xlim(0, x_data[-1] + 1)

        return self.line1, self.line2,

    def stop_monitoring(self):
        """Stops the data collection and graph updates."""
        logging.info("Stopping application.")
        self.is_running = False
        if self.ani:
            self.ani.event_source.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.mainloop()
