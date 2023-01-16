import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import numpy as np
import sys
from BreakoutEnv import BreakoutEnv

class GraphicsEnv(BreakoutEnv):
    def __init__(self, screenLength, skipAnim = True):
        super().__init__()
        
        screenWidth = int(screenLength * 7 / 9)
        self.screenSize = (screenWidth, screenLength)
        self.blockLength = int(screenWidth / 7)
        self.skipAnim = skipAnim
        
        pygame.init()

        self.screen = pygame.display.set_mode(self.screenSize)
        self.font = pygame.font.SysFont(None, 96)
        pygame.display.set_caption("Breakout")

        self.run()

    def getInput(self):
        running = True

        mousePos = (0, self.screenSize[1])

        while (running):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()
            self.drawState()
            mousePos = pygame.mouse.get_pos()
            self.drawAim(mousePos)
            if (pygame.mouse.get_pressed()[0]):
                running = False
            pygame.display.flip()

        if (not self.skipAnim):
            pass

        return self.posToAngle(mousePos)

    def posToAngle(self, pos):
        midX = self.screenSize[0] / 2
        x_pos = midX + midX * self.x
        rise = self.screenSize[1] - pos[1]
        run = pos[0] - x_pos

        if (run == 0):
            return 0

        angle = np.rad2deg(np.arctan(float(rise)/run))/90

        return (1 - angle) if (angle > 0) else (-1 - angle)

    def drawState(self):
        self.screen.fill((0,0,0))
        for x in range(7):
            for y in range(7):
                if (self.grid[x][7-y] != 0):
                    self.drawBlock((x, y))

    def drawAim(self, pos):
        midX = self.screenSize[0] / 2
        x_pos = midX + midX * self.x

        pygame.draw.line(self.screen, (255, 0, 0), (x_pos, self.screenSize[1]), pos)

    def observe(self):
        pygame.time.wait(500)

    def drawBlock(self, coord):
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(coord[0]*self.blockLength, (coord[1] + 1)*self.blockLength, self.blockLength, self.blockLength))
        img = self.font.render(str(int(self.grid[coord[0], 7 - coord[1]])), True, (0, 0, 0))
        self.screen.blit(img, (coord[0]*self.blockLength + self.blockLength/2, (coord[1] + 1)*self.blockLength + self.blockLength/2))