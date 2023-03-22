from robot import Robot
from jobStation import Job, JobStation
import math

class WarehouseManager:
    def __init__(self):
        self.efficiency = 0
    
    def update(self, robots, jobStations):
        self.notifyRobotsOfJobs(robots, jobStations)
    
    def notifyRobotsOfJobs(self, robots, jobStations):
        for jobStation in jobStations:
            robotsInRange = self.robotsInRangeOfStation(robots, jobStation)
            if jobStation.pendingJobs and robotsInRange:
                for job in jobStation.pendingJobs:
                  assignedRobot = self.determineVotes(robotsInRange, job)
                  self.assignJobToRobot(assignedRobot, job)
                
    
    def robotsInRangeOfStation(self, robots, jobStation):
        # This may or may not work...
        # x, y = jobStation.location
        robotsInRange = []
        # for robot in robots:
        #     distance = math.hypot(x - robot.x, y - robot.y)
        #     if distance <= 1 + jobStation.radius: #Robot has a radius of 1
        #         robotsInRange.append(robot)
        robotsInRange.append(robots[0])
        return robotsInRange

    def determineVotes(self, robots, job):
        # TODO Write voting algorithms or something
        return robots[0]
    
    def assignJobToRobot(self, robot, job):
        if not robot.jobQueue: # remove this
          robot.assignJob(job)