import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import numpy as np
import sys
from BreakoutEnv import BreakoutEnv
from utils import Vector, Parametric

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
            debug = pygame.mouse.get_pressed()[1]
            self.drawAim(mousePos, debug)
            if (debug):
                print(" ")
                pygame.time.wait(500)
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

    def drawAim(self, pos, debug=False):
        if (debug):
            print(pos)
        angle = self.posToAngle(pos)

        # Angle is -90 to 90 degrees, mapped to -1 and 1
        assert -1.0 <= angle and angle <= 1.0

        # 90 degree angle will loop forever, terminate early
        if angle == -1.0 or angle == 1.0:
            return

        if (debug):
            print(angle)

        # Convert input and starting x pos into a vector
        vy = np.cos(np.deg2rad(angle*90))
        vx = np.sin(np.deg2rad(angle*90))

        vec = Vector(Parametric(vx, self.x), Parametric(vy, -1.0 / 3.5))

        self.drawVectorPath(vec, debug)

    def drawVectorPath(self, vec, debug=False):
        hitsGround = False
        vector = vec

        i = 0

        while (not hitsGround and i < 1000):
            nextVector, hitsGround = self.nextCollision(vector, False, debug)

            start_x = int((vector.x.base + 1) * self.screenSize[0] / 2)
            start_y = self.screenSize[1] - int(((vector.y.base + 1 / 3.5) * 3.5 / 9)*self.screenSize[1])

            if (hitsGround):
                end_x = int((vector.getX(-1.0 / 3.5) + 1) * self.screenSize[0] / 2)
                end_y = self.screenSize[1]
            else:
                end_x = int((nextVector.x.base + 1) * self.screenSize[0] / 2)
                end_y = self.screenSize[1] - int(((nextVector.y.base + 1 / 3.5) * 3.5 / 9)*self.screenSize[1])
                vector = nextVector

            if (debug):
                print("Draw line: ", (start_x, start_y), (end_x, end_y))
                print(" ")
            pygame.draw.line(self.screen, (255, 0, 0), (start_x, start_y), (end_x, end_y))
            i += 1

    def observe(self):
        pygame.time.wait(500)

    def drawBlock(self, coord):
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(coord[0]*self.blockLength, (coord[1] + 1)*self.blockLength, self.blockLength, self.blockLength))
        img = self.font.render(str(int(self.grid[coord[0], 7 - coord[1]])), True, (0, 0, 0))
        self.screen.blit(img, (coord[0]*self.blockLength + self.blockLength / 2 - img.get_width() / 2, (coord[1] + 1)*self.blockLength + self.blockLength / 2 - img.get_height() / 2))