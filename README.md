# warehouse-sim

The warehouse simulator is a warehouse robot transportation system, with robots existing as autonomous agents which are tasked with transporting resources between points while having to manage power while maximizing their own reward.

## Setup

- Make sure python 3 is installed on your device
- From the project's root directory install the necessary python packages with the command:

```bash
pip install -r requirements.txt
```

---

## Run

Run the warehouse simulator with:

<!-- add command options to run competitive or cooperative, fps, etc.-->

```bash
python main.py
```

### Options

- Use the `-fps NUM` option to control how fast the simulation runs in terms of frames per second.
- Use the `-m` option to switch the simulation's various modes
  - a: Aggressive (naive)
  - b: Competitive Range
  - c: Cooperative
  - d: Bad Actors
  - e: True Optimal
  - f: Competitive Borda
- Use the `-v` option to run in verbose
- Use the `-ng` option to run without the GUI
- Use the `-i NUM` option to run simulation NUM amount of times
- Use the `--help` to get help a full list of command options

Examples:

```bash
python main.py -fps 10 -m c
python main.py --help
```
