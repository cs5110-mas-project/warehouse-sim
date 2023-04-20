import argparse
import warehouseSimulator

def main():
    """Main entrypoint for the simulation"""
    # TODO add argument for selecting which factory to use, add functionality to WarhouseSimulator class
    parser = argparse.ArgumentParser()
    parser.add_argument("-fps", "--frames_per_sec", type=int, default=5, help="How many times per second the simulator runs at")
    parser.add_argument("-c", "--competitive", action="store_true", help="Whether to run the competitive simulation, default is cooperative")
    args = parser.parse_args()
    simulation = warehouseSimulator.WarehouseSimulator(args.frames_per_sec, args.competitive)
    simulation.run()


if __name__ == '__main__':
    main()