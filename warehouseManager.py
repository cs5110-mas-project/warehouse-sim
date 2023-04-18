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
                    assignedRobot = self.findOptimalRobot(robotsInRange, job)
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

    def findOptimalRobot(self, robots, job):
        """ 
            Finds the closest available robot to the current job. Could maybe add more options to this, like their battery percentage,
            if they do have a job, how close are they to being done. If the end is close to their charging station. ect. 
        """
        closest_robot = robots[0]
        closest_distance = math.sqrt(
            (closest_robot.x - job.startX)**2 + (closest_robot.y - job.startY)**2)
        for robot in robots:
            if robot.currentJob == None and robot.needCharge == False:
                distance = math.sqrt(
                    (robot.x - job.startX)**2 + (robot.y - job.startY)**2)
                if distance < closest_distance:
                    closest_robot = robot
                    closest_distance = distance
        if not closest_robot.jobQueue:
            return closest_robot

    def assignJobToRobot(self, robot, job):
        if robot:
            robot.assignJob(job)
            job.assigned = True
            robot.currentJob = job
