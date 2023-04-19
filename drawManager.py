import pygame
from pygame.locals import *
import constants


class DrawManager:
    """
      Manager for drawing everything to the screen. This includes the background,
      all objects in the warehouse, and finally the grid overtop
    """
    # Pretend these are constants :)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    # GREEN = (100, 255, 100)
    # PURPLE = (191, 66, 245)
    # ROBOT_COLOR = (145, 202, 217)
    # ROBOT_BATTERY_LOW = (250, 100, 100)
    # ROBOT_CHARGING = (250, 247, 100)
    # DARKGRAY = (40, 40, 40)


    def __init__(self, screen, windowWidth, windowHeight, cellSize, warehouse):

        spritesheet           = pygame.image.load("resources/spritesheet.png").convert_alpha()
        self.JOB_STATION      = spritesheet.subsurface(pygame.Rect(0, 0, 15, 15))
        self.WALL             = spritesheet.subsurface(pygame.Rect(0, 15, 15, 15))
        self.FLOOR            = spritesheet.subsurface(pygame.Rect(0, 45, 15, 15))
        self.ROBOT_CHARGE     = spritesheet.subsurface(pygame.Rect(15, 0, 15, 15))
        self.ROBOT            = spritesheet.subsurface(pygame.Rect(15, 15, 15, 15))
        self.ROBOT_LOW        = spritesheet.subsurface(pygame.Rect(15, 30, 15, 15))
        self.CHARGING_STATION = spritesheet.subsurface(pygame.Rect(0, 30, 15, 15))
        self.screen = screen
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.cellSize = cellSize
        self.warehouse = warehouse

    def update(self, robots):
        """Handles drawing everything on the screen"""
        # self.screen.fill(self.WHITE)
        self.drawObjects(robots)
        self.drawGrid()

    def drawGrid(self):
        """Draws the grid over the warehouse. Shamelessly "borrowed" from program 1"""
        for x in range(0, self.windowWidth, self.cellSize):  # draw vertical lines
            pygame.draw.line(self.screen, self.BLACK,
                             (x, 0), (x, self.windowHeight))
        for y in range(0, self.windowHeight, self.cellSize):  # draw horizontal lines
            pygame.draw.line(self.screen, self.BLACK,
                             (0, y), (self.windowWidth, y))

    def drawObjects(self, robots):
        """Draws all the objects in the warehouse"""
        for y in range(len(self.warehouse)):
            for x in range(len(self.warehouse[0])):
                if self.warehouse[y][x] == constants.WALL:
                    # wallRect = pygame.Rect(
                    #     x * self.cellSize, y * self.cellSize, self.cellSize, self.cellSize)
                    # pygame.draw.rect(self.screen, self.DARKGRAY, wallRect)
                    self.screen.blit(self.WALL, (x * self.cellSize, y * self.cellSize))
                elif self.warehouse[y][x] == constants.CHARGING_STATION:
                    # wallRect = pygame.Rect(
                    #     x * self.cellSize, y * self.cellSize, self.cellSize, self.cellSize)
                    # pygame.draw.rect(self.screen, self.GREEN, wallRect)
                    self.screen.blit(self.FLOOR, (x * self.cellSize, y * self.cellSize))
                    self.screen.blit(self.CHARGING_STATION, (x * self.cellSize, y * self.cellSize))
                elif self.warehouse[y][x] == constants.JOB_STATION:
                    # wallRect = pygame.Rect(
                    #     x * self.cellSize, y * self.cellSize, self.cellSize, self.cellSize)
                    # pygame.draw.rect(self.screen, self.PURPLE, wallRect)
                    self.screen.blit(self.FLOOR, (x * self.cellSize, y * self.cellSize))
                    self.screen.blit(self.JOB_STATION, (x * self.cellSize, y * self.cellSize))
                else:
                    self.screen.blit(self.FLOOR, (x * self.cellSize, y * self.cellSize))

        for robot in robots:
            robotRect = (robot.x * self.cellSize, robot.y * self.cellSize)
            self.screen.blit(self.FLOOR, robotRect)
            if not robot.needCharge:
                self.screen.blit(self.ROBOT, robotRect)
            elif robot.y == robot.chargingPoint[0] and robot.x == robot.chargingPoint[1]:
                self.screen.blit(self.ROBOT_CHARGE, robotRect)
            else:
                self.screen.blit(self.ROBOT_LOW, robotRect)
