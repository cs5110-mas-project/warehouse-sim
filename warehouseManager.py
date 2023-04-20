import math


class WarehouseManager:
    def __init__(self, verbose):
        self.verbose = verbose
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
        best_score = -math.inf
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
                if len(robot.jobQueue) == 0:
                    sum += 500
                else:
                    # The robot has jobs to do. Figure out roughly how much distance is required to complete each job.
                    # Note that this does not compute travel time from the end of one job to the start of another
                    totalRemainingDistance = 0
                    for j in robot.jobQueue:   
                        if j == robot.currentJob: 
                            totalRemainingDistance += math.sqrt((robot.currentJob.endX - job.startX)**2 + (robot.currentJob.endY - job.startY)**2)
                        else:
                            totalRemainingDistance += math.sqrt((job.endX - job.startX)**2 + (job.endY - job.startY)**2)
                    sum -= totalRemainingDistance
                if sum > best_score:
                    best_robot = robot
                    best_score = sum
        return best_robot

    def assignJobToRobot(self, robot, job):
        if robot:
            if self.verbose:
                print(f'assigning job to {robot.name}')
            robot.assignJob(job)
            job.assigned = True
