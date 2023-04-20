import random
import pygame
import constants
import argparse
from pygame.locals import *
from robot import Robot
from jobStation import JobStation
from drawManager import DrawManager
from warehouseManager import WarehouseManager
from dataclasses import dataclass
from statisticManager import StatisticManager


@dataclass
class Job:
    startX: int
    startY: int
    endX: int
    endY: int
    activationTime: int
    assigned: bool

class WarehouseSimulator:

    
    def __init__(self, fps, competitive, gui, verbose) -> None:
        # TODO add functionality for competitive and cooperative
        self.gui = gui
        self.fps = fps
        self.verbose = verbose
        self.cell_size = 15
        self.competitive = competitive
        self.warehouse = constants.factory_given
        self.num_horizontal_cells = len(self.warehouse[0])
        self.num_vertical_cells = len(self.warehouse)
        self.window_width = self.cell_size * self.num_horizontal_cells
        self.window_height = self.cell_size * self.num_vertical_cells
        # Get a list of the job stations in the simulation
        self.jobStations = self.getJobStations()
        # List of Charging stations and their coordinates
        self.chargingStations = self.getChargingStations()
        # Generate a list of jobs to perform
        self.jobList = self.generateJobList(self.jobStations, 17, 5)
        # Create a Stats Object
        self.stats = StatisticManager(len(self.chargingStations))
        # Get a list of the robots in the simulation
        self.robots = self.getRobots()
        if self.gui:
            self.clock = pygame.time.Clock()
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            # self.font = pygame.font.Font('freesansbold.ttf', 18)
            self.drawManager = DrawManager(self.screen, self.window_width, self.window_height, self.cell_size, self.warehouse)
        self.warehouseManager = WarehouseManager(self.verbose)



    def getCell(self, x, y):
        cellPosX = int(x/self.cell_size)
        cellPosY = int(y/self.cell_size)
        return cellPosX, cellPosY


    def generateJobList(self, jobStations, totalJobs, numJobsAssignedAtATime):
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


    def getJobStations(self):
        jobStations = []
        for y in range(len(self.warehouse)):
            for x in range(len(self.warehouse[0])):
                if self.warehouse[y][x] == constants.JOB_STATION:
                    newJobStation = JobStation((x, y), 100000, self.verbose)
                    jobStations.append(newJobStation)

        return jobStations
    

    def getChargingStations(self):
        chargingStations = []
        for y in range(len(self.warehouse)):
            for x in range(len(self.warehouse[0])):
                if self.warehouse[y][x] == constants.CHARGING_STATION:
                    chargingStations.append([y, x])

        return chargingStations


    def getRobots(self):
        return [Robot(self.chargingStations[i], self.warehouse, self.jobList, self.stats.get(i), i, self.verbose) for i in range(len(self.chargingStations))]

        
    def update(self, totalTicks):
        if self.gui:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
        
            
        self.warehouseManager.update(self.robots, self.jobList, totalTicks)

        # There is a chance that all the jobs have been completed before the next round of jobs get assigned.
        # Make sure the simulation keeps running until all jobs have been assigned
        keepGoing = self.jobList[-1].activationTime > totalTicks

        # Update each robot and determine if all jobs have been completed
        for robot in self.robots:
            performingJob = robot.update()
            if performingJob:
                keepGoing = True
        if self.gui:
            self.drawManager.update(self.robots)
            pygame.display.update()
            self.clock.tick(self.fps)
        return keepGoing


    def run(self):

        if self.gui:
            pygame.init()
            pygame.display.set_caption('Warehouse Sim')

        totalTicks = 1
        keepGoing = True
        while keepGoing:   
            keepGoing = self.update(totalTicks)
            totalTicks += 1

        self.stats.printReport()