from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import math
import random


class Robot:
    """
        Class that represents a robot in the warehouse. Robots are capable of bidding and voting when it comes
        to jobs that are requested from job stations. When robots have a job, they will find the shortest path
        to the nodes required to finish a job
    """
    # Psuedo enum...
    JOB_UNASSIGNED = 0
    JOB_STARTED = 1
    JOB_IN_PROGRESS = 2

    def __init__(self, pos, warehouse, jobList):
        self.x = pos[1]
        self.y = pos[0]
        self.chargingPoint = pos
        self.batteryPercent = random.randint(100, 150)
        self.grid = Grid(matrix=warehouse)
        self.path = []
        self.jobQueue = []
        self.jobStatus = self.JOB_UNASSIGNED
        self.currentJob = None
        self.needCharge = False
        self.chargingPath = False
        self.jobList = jobList

    def update(self):
        """
            Updates the state of the robot, i.e. updates battery percentage, evaluates job status and moves the robot.
            Returns true if the robot is currently performing a job, false otherwise
        """
        self.updateCharging()
        self.evaluateJobProgress()
        self.getPath()
        self.move()
        return len(self.jobQueue) > 0

    def getPath(self):
        """ 
            Tries to start a new job if there is one waiting and not currently doing a job. If the robot
            is currently on a job and has reached the starting job node, the path will be updated to point
            the robot to the final destination job node
        """

        # If it needs to be charged, go to charging station and don't do job.
        if self.needCharge:
            self.chargeRobot()
        elif self.jobStatus == self.JOB_UNASSIGNED and self.jobQueue:
            self.startNewJob()
        elif self.jobStatus == self.JOB_STARTED and not self.path:
            self.executePhaseTwo()
        else:
            return  # TODO Maybe have the bot wander or charge?

    def updateCharging(self):
        """ 
            Updates the battery percentage based on the situation
        """
        # If it's at the charging station, then charge
        if self.y == self.chargingPoint[0] and self.x == self.chargingPoint[1] and self.batteryPercent < 300:
            self.batteryPercent += 5
        # If it's moving the decrease battery
        elif self.path:
            self.batteryPercent -= 1
        # If it's dead, go to charger
        if self.batteryPercent <= 0:
            self.needCharge = True
        # If it's done charging, run the function
        elif self.batteryPercent >= 100 and self.needCharge:
            self.needCharge = False
            self.chargingPath = False
            self.endCharging()

    def chargeRobot(self):
        """ 
            Get the path from the robot to their charging station and if they have not started the job yet, returns the job
            to the job queue for another robot to be able to pick it up
        """

        if self.y != self.chargingPoint[0] and self.x != self.chargingPoint[1] and not self.chargingPath:
            if self.currentJob:
                print(
                    f"Robot needs charging, pausing job {self.currentJob.startX}, {self.currentJob.startY} to {self.currentJob.endX}, {self.currentJob.endY}")
            self.path = []
            self.grid.cleanup()
            start = self.grid.node(self.x, self.y)
            end = self.grid.node(self.chargingPoint[1], self.chargingPoint[0])
            finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
            path, _ = finder.find_path(start, end, self.grid)
            self.path = path
            self.chargingPath = True
            if self.jobStatus == self.JOB_STARTED:
                print(
                    f"Job not in progress, returning job {self.currentJob.startX}, {self.currentJob.startY} to {self.currentJob.endX}, {self.currentJob.endY}")
                self.jobStatus == self.JOB_UNASSIGNED
                self.currentJob.assigned = False
                self.jobList.append(self.currentJob)
                self.currentJob = None

    def endCharging(self):
        """ 
            Function used when charging is over, checks if they have a job that they are working on, if so it finds the path to complete that job
            If it doesn't have a job then it tries to get one. 
        """

        if self.jobStatus != self.JOB_UNASSIGNED and self.currentJob:
            # If robot was currently working on a job, then return to that job
            self.grid.cleanup()
            start = None
            end = None
            job = self.currentJob
            # If they have not started the job, go to the start
            start = self.grid.node(self.x, self.y)
            end = self.grid.node(job.endX, job.endY)
            self.jobStatus = self.JOB_IN_PROGRESS
            finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
            path, _ = finder.find_path(start, end, self.grid)
            self.path = path
            print(
                f"Returning to job from {job.startX}, {job.startY} to {job.endX}, {job.endY}")
        elif self.jobQueue:
            self.startNewJob()

    def startNewJob(self):
        """Grabs the next job in the job queue and starts a path to the starting job station"""
        self.grid.cleanup()
        job = self.jobQueue[0]
        self.currentJob = job
        start = None
        end = None
        # Check and see if we are already on top of the job station that is the starting point. If not, we need
        # to first navigate to the starting node before the job can be in progress
        if self.x == job.startX and self.y == job.startY:
            start = self.grid.node(job.startX, job.startY)
            end = self.grid.node(job.endX, job.endY)
            self.jobStatus = self.JOB_IN_PROGRESS
        else:
            start = self.grid.node(self.x, self.y)
            end = self.grid.node(job.startX, job.startY)
            self.jobStatus = self.JOB_STARTED

        finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
        path, _ = finder.find_path(start, end, self.grid)
        self.path = path
        print(
            f"Starting job from {job.startX}, {job.startY} to {job.endX}, {job.endY}")

    def executePhaseTwo(self):
        """Plots a path from the current location (starting job node) to the destination job node"""
        self.grid.cleanup()
        self.jobStatus = self.JOB_IN_PROGRESS
        job = self.jobQueue[0]
        start = self.grid.node(job.startX, job.startY)
        end = self.grid.node(job.endX, job.endY)
        finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
        path, _ = finder.find_path(start, end, self.grid)
        self.path = path

    def evaluateJobProgress(self):
        """ 
            Determines if the current job in progress has been finished and removes that job from the job
            queue if so. No-op in all other cases
        """
        if self.jobStatus == self.JOB_IN_PROGRESS:
            job = self.jobQueue[0]
            if self.x == job.endX and self.y == job.endY:
                job = self.jobQueue.pop(0)
                print(
                    f"Removing job from {job.startX}, {job.startY} to {job.endX}, {job.endY}")
                self.jobStatus = self.JOB_UNASSIGNED
                self.currentJob = None

    def assignJob(self, job):
        self.jobQueue.append(job)

    def move(self):
        """Moves the robot happily along the path destroying all in its wake"""
        if self.path:
            x, y = self.path.pop(0)
            # print(f"moving self from {self.x}, {self.y} to {x}, {y}")
            self.x = x
            self.y = y
