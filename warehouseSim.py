import pygame
from pygame.locals import *
import constants
from robot import Robot
from jobStation import JobStation
from drawManager import DrawManager
from warehouseManager import WarehouseManager

FPS = 5
CELL_SIZE = 24
NUM_HORIZONTAL_CELLS = len(constants.warehouse[0])
NUM_VERTICAL_CELLS = len(constants.warehouse)
WINDOW_WIDTH = CELL_SIZE * NUM_HORIZONTAL_CELLS
WINDOW_HEIGHT = CELL_SIZE * NUM_VERTICAL_CELLS

def getCell(x, y):
    cellPosX = int(x/CELL_SIZE)
    cellPosY = int(y/CELL_SIZE)
    return cellPosX, cellPosY

def runSim(drawManager, warehouseManager, robots, jobStations):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
  
    drawManager.update(robots)
    warehouseManager.update(robots, jobStations)
    
    for jobStation in jobStations:
        jobStation.update()
  
    for robot in robots:
        robot.update()

    pygame.display.update()
    clock.tick(FPS)

    return True

def main():
    """Main entrypoint for the simulation"""
    global clock, screen, font

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    font = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Warehouse Sim')

    # Get a list of the robots in the simulation
    robot = Robot((1, 1))
    robots = [robot]

    # Get a list of the job stations in the simulation
    jobStations = []
    for y in range(len(constants.warehouse)):
        for x in range(len(constants.warehouse[0])):
            if constants.warehouse[y][x] == constants.JOB_STATION:
                newJobStation = JobStation((x,y), 100000)
                jobStations.append(newJobStation)
  
    for jobStation in jobStations:
        jobStation.setOtherJobStations(jobStations)

    drawManager = DrawManager(screen, WINDOW_WIDTH, WINDOW_HEIGHT, CELL_SIZE)
    warehouseManager = WarehouseManager()

    run = True
    while run:
        # print(f"window height is {WINDOW_HEIGHT}, window width is {WINDOW_WIDTH}")
        run = runSim(drawManager, warehouseManager, robots, jobStations)
        


if __name__ == '__main__':
    main()