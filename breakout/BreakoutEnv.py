import numpy as np
import copy
from abc import ABC, abstractmethod
from utils import Parametric, Vector

class BreakoutEnv(ABC):
    def __init__(self):
        # State variables
        self.grid = np.zeros((7, 8))    # Grid of blocks
        self.x = 0                      # x position of shooter at bottom of screen
        self.round = 1                  # Round number

        # Interstate variables
        self.blocksHit = 0              # Number of blocks hit after calling shoot()

        # Env init
        self.newGridRow()

    def newGridRow(self):
        # Populate top row randomly
        for x in range(7):
            self.grid[x][7] = 0

        rng = np.random.default_rng()
        blocks = rng.choice(7, size=np.random.randint(1, 7), replace=False)

        for block in blocks:
            # Blocks require the same number of hits as the current rount
            self.grid[block][7] = self.round

    def nextGrid(self):
        # Pull down the blocks from the row above
        for y in range(7):
            for x in range(7):
                self.grid[x][y] = self.grid[x][y+1]

        # Repopulate the top row
        self.newGridRow()

    def shoot(self, angle):
        # Action to compute the next state
        # Angle is -90 to 90 degrees, mapped to -1 and 1
        assert -1.0 <= angle and angle <= 1.0

        # 90 degree angle will loop forever, terminate early
        if angle == -1.0 or angle == 1.0:
            return

        # Convert input and starting x pos into a vector
        vy = np.cos(np.deg2rad(angle*90))
        vx = np.sin(np.deg2rad(angle*90))

        vec = Vector(Parametric(vx, self.x), Parametric(vy, -1.0 / 3.5))
        # Balls hit the same amount as the current round
        vec.balls = self.round

        vectors = [vec]

        t = -1
        x = 0

        while (len(vectors) > 0):
            # toRemove is added to when the vector hits the ground or does a complete bounce
            # Complete bounce is when a vector hits a wall or a block with points >= vector balls
            toRemove = []
            for idx, vector in enumerate(vectors):
                nextVector, hitsGround = self.nextCollision(vector)
                
                if (hitsGround):
                    # Track when and where ground is hit to determine next starting position
                    if ((t < 0 or vector.src_t < t) and vector.src_t > 0):
                        t = vector.src_t
                        x = vector.contact_x
                    toRemove.append(idx)
                    continue

                # If the current and next vectors balls don't match, the bounce is incomplete
                # Incomplete bounce splits the vector
                if (nextVector.balls != vector.balls):
                    vector.balls -= nextVector.balls
                    vector.rebaseX(nextVector.x.base)
                    vector.rebaseY(nextVector.y.base)
                    vectors[idx] = vector
                else:
                    toRemove.append(idx)

                vectors.append(nextVector)
            
            toRemove.reverse()

            for idx in toRemove:
                del vectors[idx]
        
        self.x = x

    def nextCollision(self, vector):
        # For a given vector on the current state, determine nearest collision and mutate state
        toRet = None
        t = -1
        min_coords = None

        # Iterate over every block in the grid
        for x in range(7):
            for y in range(7):
                if (self.grid[x][y+1] == 0):
                    continue
                
                # Convert grid coordinate to horizontal and vertical line dependent on vector
                # eg, if vector moving down, check collision with top of block

                # Horizontal check
                h_line = y + (0 if (vector.y.slope > 0) else 1)
                h_line = (h_line / 3.5)

                hit_x = vector.getX(h_line)
                min_x = x / 3.5 - 1
                max_x = (x + 1) / 3.5 - 1

                # Vertical check
                v_line = x + (0 if (vector.x.slope > 0) else 1)
                v_line = (v_line / 3.5) - 1

                hit_y = vector.getY(v_line)
                min_y = y / 3.5
                max_y = (y + 1) / 3.5

                # Verify that the collision is possible (ie, slope not opposite direction)
                possible = True
                if (min_x >= vector.x.base and vector.x.slope <= 0):
                    possible = False
                if (max_x <= vector.x.base and vector.x.slope >= 0):
                    possible = False
                if (min_y >= vector.y.base and vector.y.slope <= 0):
                    possible = False
                if (max_y <= vector.y.base and vector.y.slope >= 0):
                    possible = False

                # If collision detected, only update if occurs sooner than currently tracked collision
                if (possible and hit_x >= min_x and hit_x <= max_x):
                    new_t = vector.getTFromX(h_line)
                    if (t <= 0 or t > new_t):
                        t = new_t
                        min_coords = (x, y+1)
                        toRet = copy.deepcopy(vector)
                        toRet.bounceY(h_line)
                        toRet.rebaseX(hit_x)

                if (possible and hit_y >= min_y and hit_y <= max_y):
                    new_t = vector.getTFromY(v_line)
                    if (t <= 0 or t > new_t):
                        t = new_t
                        min_coords = (x, y+1)
                        toRet = copy.deepcopy(vector)
                        toRet.bounceX(v_line)
                        toRet.rebaseY(hit_y)

        # Mutate state and return if collision found
        if (t > 0):
            toRet.src_t += t
            vector.src_t += t
            toRet.balls = min(vector.balls, int(self.grid[min_coords[0]][min_coords[1]]))
            self.grid[min_coords[0]][min_coords[1]] -= toRet.balls
            self.blocksHit += toRet.balls
            min_x = min_coords[0] / 3.5 - 1
            max_x = (min_coords[0] + 1) / 3.5 - 1
            min_y = min_coords[1] / 3.5
            max_y = (min_coords[1] + 1) / 3.5
            return toRet, False

        # Repeat vertical and horizontal line checks with boundaries of game

        # Horizontal check for roof and ground
        h_line = (-1.0 / 3.5) if (vector.y.slope < 0) else (8.0 / 3.5)

        hit_x = vector.getX(h_line)
        if (hit_x >= -1 and hit_x <= 1):
            # If vector moving downwards, ground is hit
            if (vector.y.slope > 0):
                toRet = copy.deepcopy(vector)
                toRet.src_t += vector.getTFromX(hit_x)
                toRet.bounceY(h_line)
                toRet.rebaseX(hit_x)
            else:
                vector.src_t = vector.getTFromX(hit_x)
                vector.contact_x = hit_x
                return None, True

        # Vertical check for both walls
        v_line = -1 if (vector.x.slope < 0) else 1

        hit_y = vector.getY(v_line)
        if (hit_y >= (-1 / 3.5) and hit_y <= (8 / 3.5)):
            toRet = copy.deepcopy(vector)
            toRet.src_t += vector.getTFromY(hit_y)
            toRet.bounceX(v_line)
            toRet.rebaseY(hit_y)

        vector.src_t = toRet.src_t
        return toRet, False
        
    @abstractmethod
    def getInput(self):
        # Override to provide input to game (AI or manual)
        pass

    @abstractmethod
    def observe(self):
        # Override to train from state transition (AI)
        pass

    def step(self):
        # Play a single round of the game
        inp = self.getInput()
        self.shoot(inp)
        self.observe()

        # Update to next state and reset interstate variables
        self.round += 1
        self.nextGrid()
        self.blocksHit = 0

    def run(self):
        # Game loop
        gameOver = False
        while (not gameOver):
            self.step()
            # Game ends
            for x in range(7):
                if (self.grid[x][0] != 0):
                    gameOver = True
                    break