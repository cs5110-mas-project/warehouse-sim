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
            Finds the best available robot for the current job. This adds value to the robot the closer it is to the start or the finish
            of the job. Also adds value if they have a higher battery percentage and if they are not currently doing a job.  
        """
        best_robot = robots[0]
        best_score = 0
        for robot in robots:
            if robot.needCharge == False:
                sum = 0
                # Checks the distance from robot to start of job
                distanceToStart = math.sqrt(
                    (robot.x - job.startX)**2 + (robot.y - job.startY)**2)
                # Checks the distance from robot to end of job
                distanceToEnd = math.sqrt(
                    (robot.x - job.endX)**2 + (robot.y - job.endY)**2)
                if (distanceToStart > 0):
                    sum += 100 - distanceToStart
                if distanceToEnd > 0:
                    sum += (100 - distanceToEnd)
                sum += robot.batteryPercent
                if robot.currentJob == None:
                    sum += 500
                else:
                    # Checks the distance from end of robots current job to the start of new job.
                    distanceFromEndToStart = math.sqrt(
                        (robot.currentJob.endX - job.startX)**2 + (robot.currentJob.endY - job.startY)**2)
                    if distanceFromEndToStart > 0:
                        sum += (500 - distanceFromEndToStart)
                if sum > best_score:
                    best_robot = robot
                    best_score = sum
        if not best_robot.jobQueue:
            return best_robot

    def assignJobToRobot(self, robot, job):
        if robot:
            print(f'assigning {robot.x}')
            robot.assignJob(job)
            job.assigned = True
            robot.currentJob = job
