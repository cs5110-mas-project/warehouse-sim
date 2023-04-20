class StatisticManager:
    def __init__(self, count, name="DEFAULT"):
        self.name = name
        self.stats = [StatsObject() for i in range(count)]

    def get(self, index):
        return self.stats[index]

    def getPowerConsumed(self):
        return sum([stat.powerConsumed for stat in self.stats])

    def getDistanceTraveled(self):
        return sum([stat.distanceTraveled for stat in self.stats])

    def getJobsCompleted(self):
        return sum([stat.jobsCompleted for stat in self.stats])

    def getTimeCharging(self):
        return sum([stat.timeCharging for stat in self.stats])

    def getConflicts(self):
        return sum([stat.conflicts for stat in self.stats])

    def getUtilityLost(self):
        return sum([stat.utilityLost for stat in self.stats])

    def printReport(self):
        title = f"REPORT FOR RUN {self.name}:"
        print(title)
        print("=" * len(title))
        print(f"    Power Consumed: {self.getPowerConsumed():.2f}")
        print(f"    Distance Traveled: {self.getDistanceTraveled():.2f}")
        print(f"    Jobs Completed: {self.getJobsCompleted()}")
        print(f"    Time Charging: {self.getTimeCharging():.2f}")
        print(f"    Conflicts: {self.getConflicts()}")
        print(f"    Utility Lost: {self.getUtilityLost():.2f}")



class StatsObject:
    def __init__(self):
        self.powerConsumed = 0
        self.distanceTraveled = 0
        self.jobsCompleted = 0
        self.timeCharging = 0
        self.conflicts = 0
        self.utilityLost = 0

