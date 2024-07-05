import copy
import random
import threading
import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Tire:
    def __init__(self, name, max_laps, degradation_rate):
        self.name = name
        self.max_laps = max_laps
        self.degradation_rate = degradation_rate
        self.current_lap = 0

    def degrade(self):
        self.current_lap += 1
        wear_percentage = self.current_lap / self.max_laps
        if wear_percentage > 1:
            raise Exception(f"{self.name} tire is completely worn out!")
        additional_time = 0
        if wear_percentage >= 0.5:
            additional_time = (wear_percentage - 0.5) * 2 * self.degradation_rate
        return additional_time


class Driver:
    def __init__(self, name, available_tires):
        self.name = name
        self.strategy = []
        self.available_tires = available_tires
        self.current_tire = None
        self.lap_times = []
        self.total_time = 0
        self.pit_stop_count = 0
        self.points = 0
        self.laps_completed = 0

    def copy(self):
        return copy.deepcopy(self)

    def choose_strategy(self, strategy):
        if not strategy:
            raise ValueError(f"No strategy provided for {self.name}.")
        self.strategy = strategy
        starting_tire = strategy[0][0]
        if not isinstance(starting_tire, Tire):
            raise ValueError(f"The starting tire for {self.name} is not a valid Tire instance.")
        self.current_tire = starting_tire

    def race(self):
        if self.current_tire is None:
            raise ValueError(f"{self.name} has no current tire selected to race with.")

        if self.laps_completed in [pit[1] for pit in self.strategy if pit[1] == self.laps_completed]:
            self.pit_stop()
        elif self.current_tire.current_lap >= self.current_tire.max_laps:
            self.pit_stop(unscheduled=True)

        additional_time = self.current_tire.degrade()
        base_lap_time = 60
        lap_time = base_lap_time + additional_time
        self.lap_times.append(lap_time)
        self.total_time += lap_time
        self.laps_completed += 1

    def pit_stop(self, unscheduled=False):
        self.pit_stop_count += 1

        if not unscheduled:
            upcoming_tire_change = next(((tire, lap) for tire, lap in self.strategy if lap == self.laps_completed),
                                        None)
            if upcoming_tire_change:
                self.current_tire = upcoming_tire_change[0]

        if unscheduled or not upcoming_tire_change:
            self.current_tire = random.choice(self.available_tires)

        self.current_tire.current_lap = 0
        pit_time = 20
        self.total_time += pit_time


class Race:
    def __init__(self, race_num, drivers, total_laps):
        self.race_num = race_num
        self.drivers = drivers[:7]
        self.total_laps = total_laps

    def assign_points_based_on_position(self):
        points_distribution = [7, 8, 5, 4, 3, 2, 1] + [0] * (len(self.drivers) - 10)

        for index, driver in enumerate(self.drivers):
            driver.points += points_distribution[index] if index < len(points_distribution) else 0

    def run(self, update_gui_callback):
        print(f"Starting Race {self.race_num}")
        for lap in range(1, self.total_laps + 1):
            for driver in self.drivers:
                driver.race()
            sorted_drivers = sorted(self.drivers, key=lambda d: d.total_time)
            self.assign_points_based_on_position()
            for index, driver in enumerate(sorted_drivers):
                driver.position = index + 1
            update_gui_callback(self.race_num, self.compile_results(lap))
        print(f"Race {self.race_num} finished.")

    def compile_results(self, lap):
        return pd.DataFrame([{
            'Position': driver.position,
            'Driver': driver.name,
            'Total Time': driver.total_time,
            'Pit Stops': driver.pit_stop_count,
            'Points': driver.points,
            'Tire Used': f"{driver.current_tire.name} - Lap {driver.current_tire.current_lap}",
            'Lap': lap
        } for driver in self.drivers])


class F1SimulationGUI:
    def __init__(self, master, num_races=7, total_laps=50):
        self.master = master
        self.master.title("F1 Strategy Simulation")
        self.num_races = num_races
        self.total_laps = total_laps
        self.race_results_dataframes = []
        self.results_all = pd.DataFrame()
        self.tabControl = ttk.Notebook(master)
        self.race_results_tabs = [ttk.Frame(self.tabControl) for _ in range(num_races)]
        for i, tab in enumerate(self.race_results_tabs, start=1):
            self.tabControl.add(tab, text=f'Race {i}')
            self.create_race_table(tab, i)
        self.tabControl.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.season_standings_frame = ttk.LabelFrame(master, text="Season Standings")
        self.season_standings_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.season_standings_tree = self.create_treeview(self.season_standings_frame,
                                                          columns=("Position", "Driver", "Points"))

        self.lap_time_graph_frame = tk.Frame(master)
        self.lap_time_graph_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.setup_lap_time_graph()

        self.race_time_graph_frame = tk.Frame(master)
        self.race_time_graph_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        self.setup_race_time_graph()

        self.start_button = tk.Button(master, text="Start Simulation", command=self.start_simulation)
        self.start_button.grid(row=3, column=0, columnspan=2, pady=5)

        master.rowconfigure(1, weight=1)
        master.rowconfigure(2, weight=1)
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)

    def create_drivers(self):
        soft_tire = Tire("Soft", 10, 0.2)
        medium_tire = Tire("Medium", 20, 0.1)
        hard_tire = Tire("Hard", 30, 0.05)
        self.drivers = [
            Driver(f"Driver {i + 1}", [soft_tire, medium_tire, hard_tire])
            for i in range(10)
        ]
        for driver in self.drivers:
            driver.choose_strategy([
                (soft_tire, 10),
                (medium_tire, 20),
                (hard_tire, 30)
            ])

    def create_race_table(self, parent, race_number):
        columns = ('Position', 'Driver', 'Race Time', 'Tire Used', 'Pit Stops')
        tree = self.create_treeview(parent, columns)
        setattr(self, f'race_{race_number}_tree', tree)

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True)
        return tree

    def start_simulation(self):
        self.start_button.config(state="disabled")
        threading.Thread(target=self.simulate_season, daemon=True).start()

    def simulate_season(self):
        race_threads = []
        for race_number in range(1, self.num_races + 1):
            self.create_drivers()
            race_thread = threading.Thread(target=self.run_race, args=(race_number,))
            race_thread.daemon = True
            race_threads.append(race_thread)
            race_thread.start()
        for race_thread in race_threads:
            race_thread.join()
        self.start_button.config(state="normal")

    def run_race(self, race_number):
        race = Race(race_number, self.drivers, self.total_laps)
        race_result_df = race.run(self.update_gui_after_each_lap)
        self.race_results_dataframes.append(race_result_df)
        self.update_season_standings_with_cumulative_data()

    def update_gui_after_each_lap(self, race_num, lap_results_df):
        self.update_race_results(race_num, lap_results_df)
        self.update_lap_time_graph(lap_results_df)

    def update_season_standings_with_cumulative_data(self):
        if not self.race_results_dataframes:
            print("No race results available.")
            return

        # Concatenate all race results DataFrames into one DataFrame
        cumulative_results_df = pd.concat(self.race_results_dataframes)

        # Sum the points for each driver and reset index for sorting
        cumulative_points = cumulative_results_df.groupby('Driver')['Points'].sum().reset_index()

        # Sort the drivers based on their total points in descending order
        sorted_cumulative_points = cumulative_points.sort_values(by='Points', ascending=False)

        # Clear previous season standings and update with new data
        self.season_standings_tree.delete(*self.season_standings_tree.get_children())
        for position, (index, row) in enumerate(sorted_cumulative_points.iterrows(), start=1):
            # Insert the new standings into the Treeview
            self.season_standings_tree.insert('', 'end', values=(position, row['Driver'], row['Points']))

    def update_race_results(self, race_num, results_df):
        sorted_results_df = results_df.sort_values(by='Total Time')
        race_tree = getattr(self, f'race_{race_num}_tree')
        race_tree.delete(*race_tree.get_children())
        for index, row in sorted_results_df.iterrows():
            race_tree.insert('', 'end', values=(
            row['Position'], row['Driver'], row['Total Time'], row['Tire Used'], row['Pit Stops']))
        if self.results_all is None or self.results_all.empty:
            self.results_all = sorted_results_df
        else:
            self.results_all = pd.concat([self.results_all, sorted_results_df])
        self.results_all.to_csv('results.csv', index=False)
        print(sorted_results_df)

    def setup_lap_time_graph(self):
        self.lap_time_figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.lap_time_subplot = self.lap_time_figure.add_subplot(111)
        self.lap_time_canvas = FigureCanvasTkAgg(self.lap_time_figure, self.lap_time_graph_frame)
        self.lap_time_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update_lap_time_graph(self, lap_results_df):
        df = lap_results_df
        for driver in df['Lap'].unique():
            # driver_data = df[df['Driver'] == driver]
            self.lap_time_subplot.plot(df['Lap'], df['Total Time'])
        self.lap_time_subplot.set_xlabel("Lap")
        self.lap_time_subplot.set_ylabel("Total Time")
        self.lap_time_canvas.draw()

    def setup_race_time_graph(self):
        self.race_time_figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.race_time_subplot = self.race_time_figure.add_subplot(111)
        self.race_time_canvas = FigureCanvasTkAgg(self.race_time_figure, self.race_time_graph_frame)
        self.race_time_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update_race_time_graph(self, race_results_df):
        df = pd.read_csv('results.csv')
        df = df.groupby(['Driver'])['Total Time'].mean().sort_values(ascending=True).reset_index().head(5)

        self.race_time_subplot.plot(df['Driver'], df['Total Time'], label=df['Driver'])
        self.race_time_subplot.set_xlabel("Driver")
        self.race_time_subplot.set_ylabel("Total Time")
        self.race_time_subplot.legend()
        self.race_time_canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = F1SimulationGUI(root)
    root.mainloop()
