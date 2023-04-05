import math

class WarehouseManager:
    def __init__(self):
        self.efficiency = 0
    
    def update(self, robots, jobList, totalTicks):
        self.notifyRobotsOfJobs(robots, jobList, totalTicks)
    
    def notifyRobotsOfJobs(self, robots, jobList, totalTicks):
        for job in jobList:
            if totalTicks >= job.activationTime and not job.assigned:
                robotsInRange = self.robotsInRangeOfStation(robots, job)
                if robotsInRange:
                    assignedRobot = self.determineVotes(robotsInRange, job)
                    self.assignJobToRobot(assignedRobot, job)

                
    
    def robotsInRangeOfStation(self, robots, job):
        # This may or may not work...
        # x, y = jobStation.location
        # robotsInRange = []
        # for robot in robots:
        #     distance = math.hypot(x - robot.x, y - robot.y)
        #     if distance <= 1 + jobStation.radius: #Robot has a radius of 1
        #         robotsInRange.append(robot)
        # robotsInRange.append(robots[0])
        # return robotsInRange
        return robots

    def determineVotes(self, robots, job):
        # TODO do some voting or something...
        for robot in robots:
            if not robot.jobQueue:
                return robot
    
    def assignJobToRobot(self, robot, job):
        if robot:
            robot.assignJob(job)
            job.assigned = True
