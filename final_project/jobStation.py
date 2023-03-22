import random
import time

class Job:
    def __init__(self, start, end, removeJobCallback):
        self.start = start
        self.end = end
        self.removeJobCallback = removeJobCallback

class JobStation:
    """
      Represents a job station in the warehouse. These are meant to signal to robots when a job is
      available
    """
    def __init__(self, location, radius):
        self.location = location
        self.others = []
        self.radius = radius
        self.pendingJobs = []
        ## TEMPORARY ##
        self.lastCreatedJob = time.time()

    def update(self):
        if not self.pendingJobs:
            self.createJob()
        elif time.time() - self.lastCreatedJob > 300:
            self.createJob()
        

    def setOtherJobStations(self, others):
        self.others = [jobStation for jobStation in others if jobStation.location != self.location]

    def createJob(self):
        destination = random.choice(self.others)
        self.pendingJobs.append(Job(self.location, destination.location, self.removeJob))

    def removeJob(self):
        job = self.pendingJobs.pop(0)
        print(f"in callback for job from {job.start} to {job.end}")