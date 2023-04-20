# warehouse-sim
The warehouse simulator is a warehouse robot transportation system, with robots existing as autonomous agents which are tasked with transporting resources between points while having to manage power while maximizing their own reward. 


## Setup
- Make sure python 3 is installed on your device
- Install the necessary python packages with the command:

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
- Use the `-fps` option to control how fast the simulation runs in terms of frames per second.
- Use the `-c` option to switch the simulation to competitive mode instead of cooperative
- Use the `--help` to get help using the command
Example:
```bash
python main.py -fps 10 -c
```