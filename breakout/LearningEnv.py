import tensorflow as tf
import tensorflow.keras.models as models
import tensorflow.keras.layers as layers
import tensorflow.keras.optimizers as optimizers
from tensorflow.keras import backend

from BreakoutEnv import BreakoutEnv

class LearningEnv(BreakoutEnv):
    def __init__(self):
        super().__init__()

        # Define ML Network and other training utilities here
        self.net_input_grid = self.grid[:][1:8]

        # Start training
        self.episode = 0
        while (self.episode < 1000):
            self.run()
            self.episode += 1

    def getInput(self):
        # Inference from network here
        return 0

    def observe(self):
        # Learn from state transition here
        pass