
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import math
import random
from itertools import permutations
from dataclasses import dataclass


MIN_UTIL = -1000


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
    MAX_CHARGE = 600
    BATTERY_MOVE_COST = 2
    BATTERY_IDLE_COST = 1

    def __init__(self, pos, warehouse, jobList, statisticManager, name, verbose):
        self.verbose = verbose
        self.x = pos[1]
        self.y = pos[0]
        self.chargingPoint = pos
        self.batteryPercent = random.randint(math.floor(
            (self.MAX_CHARGE / 3)), math.floor(self.MAX_CHARGE * 2 / 3))
        self.grid = Grid(matrix=warehouse)
        self.path = []
        self.jobQueue = []
        self.jobStatus = self.JOB_UNASSIGNED
        self.currentJob = None
        self.needCharge = False
        self.chargingPath = False
        self.jobList = jobList
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
        self.stats = statisticManager
        self.name = name
        self.utils = {}
        self.neighbors = {}

    def update(self, chargingStations=None, statManager=None):
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
        self.grid.cleanup()
        costToChargeStation = len(self.finder.find_path(self.grid.node(self.x, self.y), self.grid.node(
            self.chargingPoint[1], self.chargingPoint[0]), self.grid)[0]) * self.BATTERY_MOVE_COST + self.BATTERY_MOVE_COST
        # If it's at the charging station, then charge
        if self.y == self.chargingPoint[0] and self.x == self.chargingPoint[1] and self.batteryPercent < self.MAX_CHARGE:
            self.batteryPercent = min(
                self.batteryPercent + 15, self.MAX_CHARGE)
            self.stats.timeCharging += 1
        # If it's moving the decrease battery
        elif self.path:
            self.batteryPercent -= self.BATTERY_MOVE_COST
            self.stats.powerConsumed += self.BATTERY_MOVE_COST
        # Passively Move Battery Over Time
        else:
            self.batteryPercent -= self.BATTERY_IDLE_COST
            self.stats.powerConsumed += self.BATTERY_IDLE_COST
        # If it's dead, go to charger
        if self.batteryPercent <= costToChargeStation:
            self.needCharge = True
        # If it's done charging, run the function
        elif self.batteryPercent >= self.MAX_CHARGE and self.needCharge:
            self.needCharge = False
            self.chargingPath = False
            self.endCharging()

    def chargeRobot(self):
        """ 
            Get the path from the robot to their charging station and if they have not started the job yet, returns the job
            to the job queue for another robot to be able to pick it up
        """

        if (self.y != self.chargingPoint[0] or self.x != self.chargingPoint[1]) and not self.chargingPath:
            if self.currentJob and self.verbose:
                print(
                    f"Robot needs charging, pausing job ({self.currentJob.startX}, {self.currentJob.startY}) to ({self.currentJob.endX}, {self.currentJob.endY})")
            self.path = []
            self.grid.cleanup()
            start = self.grid.node(self.x, self.y)
            end = self.grid.node(self.chargingPoint[1], self.chargingPoint[0])
            path, _ = self.finder.find_path(start, end, self.grid)
            self.path = path
            self.chargingPath = True
            if self.jobStatus == self.JOB_STARTED:
                if self.verbose:
                    print(
                        f"Job not in progress, returning job ({self.currentJob.startX}, {self.currentJob.startY}) to ({self.currentJob.endX}, {self.currentJob.endY})")
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
            path, _ = self.finder.find_path(start, end, self.grid)
            self.path = path
            if self.verbose:
                print(
                    f"Returning to job from ({job.startX}, {job.startY}) to ({job.endX}, {job.endY})")
        elif self.jobQueue:
            self.startNewJob()

    def checkChargeBeforeJob(self, job):
        self.grid.cleanup()
        needsCharge = False
        jobCost = 0

        # Calculate the number of steps to be able to start the job if we need to
        if self.x != job.startX and self.y != job.startY:
            start = self.grid.node(self.x, self.y)
            end = self.grid.node(job.startX, job.startY)
            path, _ = self.finder.find_path(start, end, self.grid)
            jobCost += len(path) * self.BATTERY_MOVE_COST

        # Calculate the number of steps to complete the job once it's started
        self.grid.cleanup()
        start = self.grid.node(job.startX, job.startY)
        end = self.grid.node(job.endX, job.endY)
        path, _ = self.finder.find_path(start, end, self.grid)
        jobCost += len(path) * self.BATTERY_MOVE_COST

        # Calculate the number of steps to make it to the charging station after the job is completed
        self.grid.cleanup()
        start = self.grid.node(job.endX, job.endY)
        end = self.grid.node(self.chargingPoint[1], self.chargingPoint[0])
        path, _ = self.finder.find_path(start, end, self.grid)
        jobCost += len(path) * self.BATTERY_MOVE_COST

        if self.batteryPercent < jobCost:
            needsCharge = True

        return needsCharge

    def startNewJob(self):
        """Grabs the next job in the job queue and starts a path to the starting job station"""
        job = self.jobQueue[0]
        self.currentJob = job
        start = None
        end = None

        # If the robot won't have enough battery to finish the job, send it to charge before starting the job
        if self.checkChargeBeforeJob(job):
            self.needCharge = True
            self.chargeRobot()
            if self.verbose:
                print(
                    f"robot '{self.name}' needs to charge before starting job ({job.startX}, {job.startY}) to ({job.endX}, {job.endY})")
        else:
            # Check and see if we are already on top of the job station that is the starting point. If not, we need
            # to first navigate to the starting node before the job can be in progress
            self.grid.cleanup()
            if self.x == job.startX and self.y == job.startY:
                if job.fake:
                    self.jobStatus = self.JOB_UNASSIGNED
                    self.currentJob = None
                    self.jobQueue.pop(0)
                    if self.verbose:
                        print(
                            f"robot {self.name} arrives at {job.startX}, {job.startY} to find the job already started")
                    return
                else:
                    start = self.grid.node(job.startX, job.startY)
                    end = self.grid.node(job.endX, job.endY)
                    self.jobStatus = self.JOB_IN_PROGRESS
            else:
                start = self.grid.node(self.x, self.y)
                end = self.grid.node(job.startX, job.startY)
                self.jobStatus = self.JOB_STARTED

            path, _ = self.finder.find_path(start, end, self.grid)
            self.path = path
            if self.verbose:
                print(
                    f"robot '{self.name}' is starting job from ({job.startX}, {job.startY}) to ({job.endX}, {job.endY})")

    def executePhaseTwo(self):
        """Plots a path from the current location (starting job node) to the destination job node"""
        job = self.jobQueue[0]
        if job.fake:
            self.jobStatus = self.JOB_UNASSIGNED
            self.currentJob = None
            if self.verbose:
                print(
                    f"robot {self.name} arrives at {job.startX}, {job.startY} to find the job already started")
            self.jobQueue.pop(0)
            return
        self.grid.cleanup()
        self.jobStatus = self.JOB_IN_PROGRESS
        start = self.grid.node(job.startX, job.startY)
        end = self.grid.node(job.endX, job.endY)
        path, _ = self.finder.find_path(start, end, self.grid)
        self.path = path

    def evaluateJobProgress(self):
        """ 
            Determines if the current job in progress has been finished and removes that job from the job
            queue if so. No-op in all other cases
        """
        if self.jobStatus == self.JOB_IN_PROGRESS:
            job = self.jobQueue[0]
            if self.x == job.endX and self.y == job.endY:
                self.stats.jobsCompleted += 1
                job = self.jobQueue.pop(0)
                if self.verbose:
                    print(
                        f"Removing job from {job.startX}, {job.startY} to {job.endX}, {job.endY}")
                self.jobStatus = self.JOB_UNASSIGNED
                self.currentJob = None

    def updateUtils(self, jobs, tick):
        if self.jobStatus == self.JOB_UNASSIGNED:
            start = self.grid.node(self.x, self.y)
        else:
            start = self.grid.node(self.currentJob.endX, self.currentJob.endY)
        for job in jobs:
            end = self.grid.node(job.endX, job.endY)
            self.grid.cleanup()
            self.utils[job] = (-len(self.finder.find_path(start,
                               end, self.grid)[0]), tick)

    def getUtils(self, jobs, tick):
        utils = []
        toUpdate = [
            job for job in jobs if job not in self.utils or self.utils[job][1] < tick]
        self.updateUtils(toUpdate, tick)
        for job in jobs:
            utils.append(self.utils[job][0])
        return utils

    def updateNeighbors(self, robots, tick):
        start = self.grid.node(self.x, self.y)
        for robot in robots:
            end = self.grid.node(robot.x, robot.y)
            self.grid.cleanup()
            self.neighbors[robot] = (len(self.finder.find_path(start, end, self.grid)[
                                     0]), tick) if robot != self else (0, tick)

    def getNeighbors(self, robots, tick):
        neighbors = []
        toUpdate = [
            robot for robot in robots if robot not in self.neighbors or self.neighbors[robot][1] < tick]
        self.updateNeighbors(robots, tick)
        for robot in robots:
            neighbors.append(self.neighbors[robot][0])
        return neighbors

    def getVotes(self, robots, jobs, tick, numVotes, honest):
        if len(jobs) <= 0:
            return Vote()
        # Find Numerical ID of Self
        selfIndex = robots.index(self)

        # Get Distance to Neighbors, and Find Closes
        neighbors = self.getNeighbors(robots, tick)
        neighbors = [(i, neighbors[i]) for i in range(len(neighbors))]
        neighbors = sorted(neighbors, reverse=False, key=lambda x: x[1])
        closestRobots = neighbors[:min(len(neighbors), numVotes)]

        # Find Distance to Jobs, and Get Closest (Utility is Negative Dist)
        dist = self.getUtils(jobs, tick)
        dist = [(i, dist[i]) for i in range(len(dist))]
        dist = sorted(dist, reverse=True, key=lambda x: x[1])
        closestJobs = dist[:min(len(dist), numVotes)]

        # Find Location of Numerical ID in Robot List
        selfNumber = max([i for i in range(len(closestRobots))],
                         key=lambda x: selfIndex == closestRobots[x][0])

        # Extract Job ID's from the Closest Job List
        jobIds = [job[0] for job in closestJobs]
        jobActuals = [jobs[i] for i in jobIds]

        # Calculate Utility Matrix
        utils = [robots[rob[0]].getUtils(jobActuals, tick)
                 for rob in closestRobots]
        if len(utils) < len(closestJobs):
            for i in range(len(closestJobs) - len(utils)):
                utils.append([MIN_UTIL for _ in range(len(closestJobs))])

        # Find all Possible Assignments
        perms = [perm for perm in permutations([i for i in range(
            max(len(closestRobots), len(closestJobs)))], len(closestJobs))]

        # Voting Matrix votes[i][j] Equals jth Preference for ith Job
        votes = [[-1 for _ in range(max(len(closestRobots), len(closestJobs)))]
                 for _ in range(len(closestJobs))]

        if honest:
            # Honest Robots Vote to Maximize total Utility
            def maximizer(x): return sum([utils[j][i]
                                          for i, j in enumerate(x)])
        else:
            # Dishonest Robots Vote to Maximize Own Utility
            # print(selfNumber)
            # print(len(closestRobots))
            # print(len(closestJobs))
            # print([i for i in range(
            #     max(len(closestRobots), len(closestJobs)))])

            def maximizer(x): return utils[selfNumber][x.index(selfNumber)]

        for i in range(min(numVotes, len(jobs))):
            # Find Best Remaining Valid Permutaiton

            best = max(perms, key=maximizer)

            # Assign Best Permutation to First Place votes
            for j in range(len(votes)):
                votes[j][i] = best[j]

            # Remove All Permutations which Overlap with Best
            newPerms = []
            for perm in perms:
                toAdd = True
                for k, assign in enumerate(best):
                    if perm[k] == assign:
                        toAdd = False
                if toAdd:
                    newPerms.append(perm)
            perms = newPerms

        # Package Votes into vote Object
        retVote = Vote()
        for job, finalVote in enumerate(votes):
            pref = []
            for vote in finalVote:
                if vote >= len(closestRobots):
                    pref.append(-1)
                else:
                    pref.append(closestRobots[vote][0])
            retVote.addVote(closestJobs[job][0], pref)

        return retVote

    def getClosest(self, jobs, tick):
        # Find Distance to Jobs, and Get Closest (Utility is Negative Dist)
        dist = self.getUtils(jobs, tick)
        dist = [(i, dist[i]) for i in range(len(dist))]
        dist = sorted(dist, reverse=True, key=lambda x: x[1])
        if len(dist) > 0:
            return dist[-1]
        else:
            return -1, MIN_UTIL

    def assignJob(self, job):
        self.jobQueue.append(job)

    def assignFakeJob(self, job, dist):
        fakeJob = Job(job.startX, job.startY, job.endX, job.endY,
                      job.activationTime, job.assigned, True)
        self.jobQueue.append(fakeJob)
        self.stats.conflicts += 1
        self.stats.utilityLost += dist

    def move(self):
        """Moves the robot happily along the path destroying all in its wake"""
        if self.path:
            x, y = self.path.pop(0)
            self.stats.distanceTraveled += 1
            self.x = x
            self.y = y

    def getRobotRankedVotes(self, jobList):
        votes = [0 for i in range(len(jobList))]
        numCount = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
        }
        votingWeights = []
        for job in jobList:
            # get distance to job
            distanceToStart = math.sqrt(
                (self.x - job.startX)**2 + (self.y - job.startY)**2)
            # Check if distance is closer than X
            if distanceToStart < 50:
                # Check if distance is very close
                if distanceToStart < 25:
                    # Check to see if can finish the job without having to charge
                    if self.batteryPercent > distanceToStart:
                        votingWeights.append(3)
                        numCount[3] += 1
                    else:
                        votingWeights.append(2)
                        numCount[2] += 1
                else:
                    votingWeights.append(1)
                    numCount[1] += 1
            else:
                votingWeights.append(0)
        if (numCount[1] == len(jobList)):
            return [1 for i in range(len(jobList))]

        for idx, vote in enumerate(votingWeights):
            if vote == 3:
                if numCount[3] > 1:
                    votes[idx] = len(jobList)/numCount[3]
                else:
                    votes[idx] = len(jobList)

                    return votes
            elif vote == 2 and numCount[3] == 0:
                if numCount[2] > 1:
                    votes[idx] = len(jobList)/numCount[2]
                else:
                    votes[idx] = len(jobList)

                    return votes
            elif vote == 1 and numCount[3] == 0 and numCount[2] == 0:
                if numCount[1] > 1:
                    votes[idx] = len(jobList)/numCount[1]
                else:
                    votes[idx] = len(jobList)

                    return votes

        return votes

    def getBordaStyleVotes(self, jobList):
        votes = [0 for i in range(len(jobList))]
        distances = []
        sorted = []
        for job in jobList:
            distances.append(math.sqrt(
                (self.x - job.startX)**2 + (self.y - job.startY)**2))
            sorted.append(math.sqrt(
                (self.x - job.startX)**2 + (self.y - job.startY)**2))
        sorted.sort()
        for i, num in enumerate(sorted):
            idx = distances.index(num)
            votes[idx] = len(jobList) - i
            distances[idx] = 100000

        return votes


class Vote:
    def __init__(self):
        self.jobVotes = []

    def addVote(self, job, vote):
        self.jobVotes.append({"job": job, "vote": vote})


@dataclass
class Job:
    startX: int
    startY: int
    endX: int
    endY: int
    activationTime: int
    assigned: bool
    fake: bool

    def __hash__(self):
        return hash(self.startX) * 7 + hash(self.startY) * 13 + 7 * hash(self.fake)
