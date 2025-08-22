"""
Generative Models for Jarvis 2.0
This module allows Jarvis to generate new and original ideas.
"""

import numpy as np

class GenerativeModels:
    def __init__(self, vocab_size, hidden_size):
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.Wxh = np.random.randn(hidden_size, vocab_size) * 0.01
        self.Whh = np.random.randn(hidden_size, hidden_size) * 0.01
        self.Why = np.random.randn(vocab_size, hidden_size) * 0.01
        self.bh = np.zeros((hidden_size, 1))
        self.by = np.zeros((vocab_size, 1))

    def generate(self, seed, length):
        """
        Generates new data based on the input data.
        """
        h = np.zeros((self.hidden_size, 1))
        x = np.zeros((self.vocab_size, 1))
        x[seed] = 1
        output = [seed]
        for _ in range(length):
            h = np.tanh(np.dot(self.Wxh, x) + np.dot(self.Whh, h) + self.bh)
            y = np.dot(self.Why, h) + self.by
            p = np.exp(y) / np.sum(np.exp(y))
            ix = np.random.choice(range(self.vocab_size), p=p.ravel())
            x = np.zeros((self.vocab_size, 1))
            x[ix] = 1
            output.append(ix)
        return output
