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
    GREEN = (100, 255, 100)
    PURPLE = (191, 66, 245)
    ROBOT_COLOR = (145, 202, 217)
    DARKGRAY  = (40, 40, 40)

    def __init__(self, screen, windowWidth, windowHeight, cellSize):
        self.screen = screen
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.cellSize = cellSize

    def update(self, robots):
        """Handles drawing everything on the screen"""
        self.screen.fill(self.WHITE)
        self.drawObjects(robots)
        self.drawGrid()

    def drawGrid(self):
        """Draws the grid over the warehouse. Shamelessly "borrowed" from program 1"""
        for x in range(0, self.windowWidth, self.cellSize): # draw vertical lines
            pygame.draw.line(self.screen, self.BLACK, (x, 0), (x, self.windowHeight))
        for y in range(0, self.windowHeight, self.cellSize): # draw horizontal lines
            pygame.draw.line(self.screen, self.BLACK, (0, y), (self.windowWidth, y))

    def drawObjects(self, robots):
        """Draws all the objects in the warehouse"""
        for x in range(len(constants.warehouse)):
            for y in range(len(constants.warehouse[0])):
                if constants.warehouse[x][y] == constants.WALL:
                    wallRect = pygame.Rect(y * self.cellSize, x * self.cellSize, self.cellSize, self.cellSize)
                    pygame.draw.rect(self.screen, self.DARKGRAY, wallRect)
                elif constants.warehouse[x][y] == constants.CHARGING_STATION:
                    wallRect = pygame.Rect(y * self.cellSize, x * self.cellSize, self.cellSize, self.cellSize)
                    pygame.draw.rect(self.screen, self.GREEN, wallRect)
                elif constants.warehouse[x][y] == constants.JOB_STATION:
                    wallRect = pygame.Rect(y * self.cellSize, x * self.cellSize, self.cellSize, self.cellSize)
                    pygame.draw.rect(self.screen, self.PURPLE, wallRect)
        
        for robot in robots:
            robotRect = pygame.Rect(robot.x * self.cellSize, robot.y * self.cellSize, self.cellSize, self.cellSize)
            pygame.draw.rect(self.screen, self.ROBOT_COLOR, robotRect)