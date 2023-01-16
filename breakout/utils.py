class Parametric():
    # Class represents a single variable parameterization of a 2D line [x(t) or y(t)]
    def __init__(self, slope, base):
        self.slope = slope
        self.base = base

    def getT(self, val):
        # Get t value of given position
        return (val - self.base)/self.slope

    def func(self, t):
        # Get position from given t value
        return t*self.slope + self.base

class Vector():
    # 2D vector implementation from two Parametric equations
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.balls = 0
        # Total t traveled, used for ground tracking
        self.src_t = 0
        # Where on the ground this vector inevitably hits
        self.contact_x = 0

    def getTFromX(self, x):
        # Get t from x pos
        return abs(self.x.getT(x))
    
    def getTFromY(self, y):
        # Get t from y pos
        return abs(self.y.getT(y))

    def getY(self, x):
        # Get y pos from x pos
        return self.y.func(self.getTFromX(x))

    def getX(self, y):
        # Get x pos from y pos
        return self.x.func(self.getTFromY(y))

    def bounceX(self, base):
        # Negate the slope of x and rebase
        self.x.slope *= -1
        self.x.base = base

    def bounceY(self, base):
        # Negate the slope of y and rebase
        self.y.slope *= -1
        self.y.base = base

    def rebaseX(self, base):
        # Update base of x equation
        self.x.base = base
    
    def rebaseY(self, base):
        # Update base of y equation
        self.y.base = base