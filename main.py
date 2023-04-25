import argparse
import warehouseSimulator
import random
import constants

def main():
    """Main entrypoint for the simulation"""
    # TODO add argument for selecting which factory to use, add functionality to WarhouseSimulator class
    parser = argparse.ArgumentParser()
    parser.add_argument("-fps", "--frames-per-sec", type=int, default=5, help="How many times per second the simulator runs at")
    parser.add_argument("-m", "--mode", type=str, choices=['a', 'b', 'c', 'd', 'e'], default='a', help="Simulation mode. a-Agressive, b-Competative, c-Cooperative, d-Bad Actor, e-Fully Managed")
    parser.add_argument("-ng", "--no-gui", action="store_false", default=True, help="Whether to run with the GUI or not, default is true")
    parser.add_argument("-v", "--verbose", action="store_true", default=True, help="Prints extra info during simulation")
    parser.add_argument("-i", "--iterations", type=int, default=1, help="Number of times to run the simulation")
    parser.add_argument("-w", "--warehouse", type=int, default=0, help="Integer for which warehouse to run the simulator with (0-2)")
    args = parser.parse_args()
    random.seed(1337)

    simulation = warehouseSimulator.WarehouseSimulator(args.frames_per_sec, args.mode, args.no_gui, args.verbose, args.iterations, constants.warerhouses[args.warehouse])
    simulation.run()


if __name__ == '__main__':
    main()