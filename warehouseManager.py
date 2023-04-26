import math
from itertools import permutations


MIN_UTIL = -1000
class WarehouseManager:
    def __init__(self, mode, verbose):
        self.verbose = verbose
        self.mode = mode
        self.efficiency = 0
        # Aggressive Mode, Robots Go for Closest Job
        if mode == 'a':
            self.updater = lambda x, y, z: self.fightForJobs(x, y, z)

        # Competitive Mode, Robots Bid for Jobs
        elif mode == 'b':
            pass

        # Cooperative Mode, Robots Try and Maximize Utility
        elif mode == 'c':
            self.updater = lambda x, y, z: self.voteOnJobs(x, y, z, honest=True)

        # Bad Actor Mode, Robots Try and Maximize Their Utility in Cooperative System
        elif mode == 'd':
            self.updater = lambda x, y, z: self.voteOnJobs(x, y, z, honest=False)

        # Fully Managed Mode, Warehouse Manager Determines Optimal Assignments
        elif mode == 'e':
            self.updater = lambda x, y, z: self.assignOptimalJobs(x, y, z)
        else:
            self.updater = lambda x, y, z: self.notifyRobotsOfJobs(x, y, z)

    def update(self, robots, jobList, totalTicks):
        jobs = [job for job in jobList if totalTicks >= job.activationTime and not job.assigned]
        freeRobots = [robot for robot in robots if robot.jobStatus == robot.JOB_UNASSIGNED and not robot.needCharge]
        self.updater(freeRobots, jobs, totalTicks)

    def voteOnJobs(self, robots, jobs, ticks, honest):
        votes = []
        for robot in robots:
            votes.append(robot.getVotes(robots=robots, jobs=jobs, tick=ticks, numVotes=3, honest=honest))
        results = self.resolveVotes(votes, len(robots), len(jobs))
        winners = [-1 for i in range(len(jobs))]
        for i in range(len(jobs)):
            winner = -1
            mostVotes = 0
            for j in range(len(robots)):
                if results[i][j] > mostVotes:
                    if j not in winners:
                        winner = j
                        mostVotes = results[i][j]
            winners[i] = winner

        for i in range(len(winners)):
            robotIndex = winners[i]
            if robotIndex >= 0:
                self.assignJobToRobot(robots[robotIndex], jobs[i])



    def resolveVotes(self, votes, numRobots, numJobs):
        results = [[0 for _ in range(numRobots)] for _ in range(numJobs)]
        scheme = [2, 1, 0]
        for voter in votes:
            for jobVote in voter.jobVotes:
                for pos, robot in enumerate(jobVote["vote"]):

                    if robot == -1:
                        continue
                    results[jobVote["job"]][robot] += scheme[pos]
        return results


    def assignOptimalJobs(self, robots, jobs, ticks):
        if len(jobs) <= 0 or len(robots) <= 0:
            return

        # Calcuates Utilities of all Jobs for All Robots
        utilities = self.getUtils(robots, jobs, ticks)
        if len(utilities) < len(jobs):
            for i in range(len(jobs) - len(robots)):
                utilities.append([MIN_UTIL for _ in range(len(jobs))])

        # Generates all Possible Permutations of Assignments
        perms = permutations([i for i in range(max(len(robots), len(jobs)))], len(jobs))

        # Finds the Permutation which Optimizes total Utility



        bestAssignment = max(perms, key=lambda x: sum([utilities[j][i] for i, j in enumerate(x)]))

        # Assigns Based on Results
        for job, robot in enumerate(bestAssignment):
            if robot >= len(robots):
                continue
            self.assignJobToRobot(robots[robot], jobs[job])


    def getUtils(self, robots, jobs, ticks):
        utils = [[MIN_UTIL for _ in range(len(jobs))] for _ in range(len(robots))]
        for i, robot in enumerate(robots):
            if robot.jobStatus == robot.JOB_UNASSIGNED:
                utils[i] = robot.getUtils(jobs, ticks)
        return utils

    def fightForJobs(self, robots, jobs, ticks):
        assignments = [[] for i in range(len(jobs))]
        for i, robot in enumerate(robots):
            closest, dist = robot.getClosest(jobs, ticks)
            if closest != -1:
                assignments[closest].append((i, dist))
        for i, job in enumerate(assignments):
            if len(job) == 1:
                self.assignJobToRobot(robots[job[0][0]], jobs[i])
            elif len(job) > 1:
                proximity = sorted(job, key=lambda x: x[1], reverse=True)
                self.assignJobToRobot(robots[proximity[0][0]], jobs[i])
                for j in range(1, len(proximity)):
                    self.assignFakeJobToRobot(robots[proximity[j][0]], jobs[i], proximity[j][1])
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

    def assignFakeJobToRobot(self, robot, job, dist):
        if robot:
            if self.verbose:
                print(f"assigning fake job to {robot.name}")
            robot.assignFakeJob(job, dist)
