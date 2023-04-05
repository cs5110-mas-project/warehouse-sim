from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


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

    def __init__(self, pos, warehouse):
        self.x = pos[0]
        self.y = pos[1]
        self.batteryPercent = 100
        self.grid = Grid(matrix=warehouse)
        self.path = []
        self.jobQueue = []
        self.jobStatus = self.JOB_UNASSIGNED

    def update(self):
        """
            Updates the state of the robot, i.e. updates battery percentage, evaluates job status and moves the robot.
            Returns true if the robot is currently performing a job, false otherwise
        """
        self.batteryPercent -= 1
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
        if self.jobStatus == self.JOB_UNASSIGNED and self.jobQueue:
            self.startNewJob()
        elif self.jobStatus == self.JOB_STARTED and not self.path:
            self.executePhaseTwo()
        else:
            return # TODO Maybe have the bot wander or charge?
    
    def startNewJob(self):
        """Grabs the next job in the job queue and starts a path to the starting job station"""
        self.grid.cleanup()
        job = self.jobQueue[0]
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
        print(f"Starting job from {job.startX}, {job.startY} to {job.endX}, {job.endY}")
    
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
                print(f"Removing job from {job.startX}, {job.startY} to {job.endX}, {job.endY}")
                self.jobStatus = self.JOB_UNASSIGNED
                
    
    def assignJob(self, job):
        self.jobQueue.append(job)
    
    def move(self):
        """Moves the robot happily along the path destroying all in its wake"""
        if self.path:
            x, y = self.path.pop(0)
            # print(f"moving self from {self.x}, {self.y} to {x}, {y}")
            self.x = x
            self.y = y

