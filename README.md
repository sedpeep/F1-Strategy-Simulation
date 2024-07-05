# F1 Strategy Simulation

## Overview

The F1 Strategy Simulation is a Python-based desktop application that simulates Formula 1 racing strategies. This simulation allows users to manage drivers, select tire strategies, and simulate race events, providing a detailed analysis of race results and season standings.

## Features

- **Simulated Race Environment:** Simulate multiple races with customizable tire strategies and lap counts.
- **Driver Management:** Create and manage drivers with different tire strategies.
- **Real-Time Updates:** Get real-time updates on race progress, lap times, and race standings.
- **Season Standings:** View cumulative points and positions of drivers throughout the season.
- **Interactive GUI:** User-friendly interface built with Tkinter, featuring tables and graphs to visualize race data.

## Requirements

- Python 3.x
- Required Libraries:
  - pandas
  - tkinter
  - matplotlib

You can install the required libraries using:

```bash
pip install pandas matplotlib
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/F1StrategySimulation.git
```

2. Navigate to the project directory:

```bash
cd F1StrategySimulation
```

3. Run the application:

```bash
python f1_simulation.py
```

## Usage

1. **Start the Application:** Run the script `f1_simulation.py` to start the simulation.
2. **Simulation Control:** Use the "Start Simulation" button to initiate the race simulation.
3. **Race Tabs:** View detailed results for each race in the respective tabs.
4. **Season Standings:** Check the season standings in the "Season Standings" frame.
5. **Graphs:** Analyze lap times and race times using the interactive graphs provided.

## Code Structure

- `Tire`: Class representing a tire with specific characteristics and degradation behavior.
- `Driver`: Class representing a driver with a tire strategy and race performance tracking.
- `Race`: Class representing a race event, managing drivers and lap progress.
- `F1SimulationGUI`: Class for the graphical user interface, handling user interactions and visualizations.

## GUI Overview

- **Race Results Tabs:** Each tab corresponds to a race, showing detailed results for that race.
- **Season Standings Frame:** Displays cumulative points and rankings for all drivers across the season.
- **Lap Time Graph:** Visual representation of lap times for each driver.
- **Race Time Graph:** Summary of race times for top drivers.

## Customization

- **Driver Creation:** Modify the `create_drivers` method in `F1SimulationGUI` to change driver and tire configurations.
- **Tire Strategies:** Adjust the `choose_strategy` method in the `Driver` class to implement different tire strategies.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

