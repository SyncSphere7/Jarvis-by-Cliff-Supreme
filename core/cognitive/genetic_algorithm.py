"""
Genetic Algorithm for Jarvis 2.0
This module allows Jarvis to evolve a population of neural networks.
"""

import numpy as np

class GeneticAlgorithm:
    def __init__(self, population_size, gene_length):
        self.population_size = population_size
        self.gene_length = gene_length
        self.population = self.initialize_population()

    def initialize_population(self):
        """
        Initializes a population of random genes.
        """
        return [np.random.rand(self.gene_length) for _ in range(self.population_size)]

    def evolve(self, fitness_function):
        """
        Evolves the population for one generation.
        """
        fitness_scores = [fitness_function(gene) for gene in self.population]
        self.population = self.selection(fitness_scores)
        self.population = self.crossover()
        self.population = self.mutation()

    def selection(self, fitness_scores):
        """
        Selects the fittest individuals from the population.
        """
        sorted_population = [x for _, x in sorted(zip(fitness_scores, self.population), key=lambda pair: pair[0], reverse=True)]
        return sorted_population[:self.population_size]

    def crossover(self):
        """
        Creates a new population by crossing over the fittest individuals.
        """
        new_population = []
        for i in range(0, self.population_size, 2):
            parent1 = self.population[i]
            parent2 = self.population[i+1]
            crossover_point = np.random.randint(0, self.gene_length)
            child1 = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
            child2 = np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))
            new_population.extend([child1, child2])
        return new_population

    def mutation(self):
        """
        Mutates the population by randomly changing genes.
        """
        for i in range(self.population_size):
            if np.random.rand() < 0.1:
                mutation_point = np.random.randint(0, self.gene_length)
                self.population[i][mutation_point] = np.random.rand()
        return self.population
