import random
import pygame
from pygame.locals import *
import constants
from robot import Robot
from jobStation import JobStation
from drawManager import DrawManager
from warehouseManager import WarehouseManager
from dataclasses import dataclass


@dataclass
class Job:
    startX: int
    startY: int
    endX: int
    endY: int
    activationTime: int
    assigned: bool


WAREHOUSE = constants.factory_given
FPS = 5
CELL_SIZE = 18
NUM_HORIZONTAL_CELLS = len(WAREHOUSE[0])
NUM_VERTICAL_CELLS = len(WAREHOUSE)
WINDOW_WIDTH = CELL_SIZE * NUM_HORIZONTAL_CELLS
WINDOW_HEIGHT = CELL_SIZE * NUM_VERTICAL_CELLS


def getCell(x, y):
    cellPosX = int(x/CELL_SIZE)
    cellPosY = int(y/CELL_SIZE)
    return cellPosX, cellPosY


def generateJobList(jobStations, totalJobs, numJobsAssignedAtATime):
    jobList = []
    activationTime = 1
    for i in range(totalJobs):
        start = random.choice(jobStations)
        end = random.choice(jobStations)
        while start == end:
            end = random.choice(jobStations)

        # Make it so 'x' jobs get assigned at a time
        if i > 0 and i % numJobsAssignedAtATime == 0:
            activationTime += 30
        jobList.append(Job(start.location[0], start.location[1],
                       end.location[0], end.location[1], activationTime, False))

    return jobList


def runSim(drawManager, warehouseManager, robots, jobList, totalTicks):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

    drawManager.update(robots)
    warehouseManager.update(robots, jobList, totalTicks)

    # There is a chance that all the jobs have been completed before the next round of jobs get assigned.
    # Make sure the simulation keeps running until all jobs have been assigned
    keepGoing = jobList[-1].activationTime > totalTicks

    # Update each robot and determine if all jobs have been completed
    for robot in robots:
        performingJob = robot.update()
        if performingJob:
            keepGoing = True

    pygame.display.update()
    clock.tick(FPS)

    return keepGoing


def main():
    """Main entrypoint for the simulation"""
    global clock, screen, font
    random.seed(1337)

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    font = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Warehouse Sim')

    # Get a list of the job stations in the simulation
    jobStations = []
    # List of Charging stations and their coordinates
    chargingStations = []
    for y in range(len(WAREHOUSE)):
        for x in range(len(WAREHOUSE[0])):
            if WAREHOUSE[y][x] == constants.JOB_STATION:
                newJobStation = JobStation((x, y), 100000)
                jobStations.append(newJobStation)
            elif WAREHOUSE[y][x] == constants.CHARGING_STATION:
                chargingStations.append([y, x])

    # Get a list of the robots in the simulation
    robots = [Robot(chargingStations[0], WAREHOUSE), Robot(chargingStations[1], WAREHOUSE), Robot(chargingStations[2], WAREHOUSE),
              Robot(chargingStations[3], WAREHOUSE), Robot(
                  chargingStations[4], WAREHOUSE), Robot(chargingStations[5], WAREHOUSE),
              Robot(chargingStations[6], WAREHOUSE), Robot(
                  chargingStations[7], WAREHOUSE), Robot(chargingStations[8], WAREHOUSE),
              Robot(chargingStations[9], WAREHOUSE)]

    # Generate a list of jobs to perform
    jobList = generateJobList(jobStations, 17, 5)

    drawManager = DrawManager(screen, WINDOW_WIDTH,
                              WINDOW_HEIGHT, CELL_SIZE, WAREHOUSE)
    warehouseManager = WarehouseManager()

    totalTicks = 1
    run = True
    while run:
        # print(f"window height is {WINDOW_HEIGHT}, window width is {WINDOW_WIDTH}")
        run = runSim(drawManager, warehouseManager,
                     robots, jobList, totalTicks)
        totalTicks += 1


if __name__ == '__main__':
    main()
