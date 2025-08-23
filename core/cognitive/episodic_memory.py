"""
Episodic Memory for Jarvis 2.0
This module allows Jarvis to remember past events and experiences.
"""

import networkx as nx
import numpy as np
from gensim.models import KeyedVectors
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import gensim.downloader as api

class EpisodicMemory:
    def __init__(self, similarity_threshold=0.7):
        self.graph = nx.Graph()
        self.similarity_threshold = similarity_threshold
        self.word_vectors = self._load_word_vectors()
        self.stop_words = set(stopwords.words('english'))

    def _load_word_vectors(self):
        """
        Loads pre-trained word vectors.
        """
        try:
            # Using a smaller, pre-trained model for demonstration purposes
            print("Loading word vectors... (this may take a while the first time)")
            word_vectors = api.load("glove-wiki-gigaword-50")
            print("Word vectors loaded successfully.")
            return word_vectors
        except Exception as e:
            print(f"Error loading word vectors: {e}")
            return None

    def _preprocess_text(self, text):
        """
        Tokenizes and removes stop words from text.
        """
        tokens = word_tokenize(text.lower())
        return [word for word in tokens if word.isalpha() and word not in self.stop_words]

    def _get_sentence_vector(self, tokens):
        """
        Calculates the sentence vector by averaging word vectors.
        """
        vectors = [self.word_vectors[word] for word in tokens if word in self.word_vectors]
        if not vectors:
            return np.zeros(self.word_vectors.vector_size)
        return np.mean(vectors, axis=0)

    def add_episode(self, episode):
        """
        Adds an episode to the memory.
        """
        self.graph.add_node(episode)
        for other_episode in self.graph.nodes():
            if episode != other_episode and self.are_related(episode, other_episode):
                self.graph.add_edge(episode, other_episode)

    def get_related_episodes(self, episode):
        """
        Returns all episodes related to the given episode.
        """
        if episode in self.graph:
            return list(self.graph.neighbors(episode))
        
        related = []
        for existing_episode in self.graph.nodes():
            if self.are_related(episode, existing_episode):
                related.append(existing_episode)
        return related

    def are_related(self, episode1, episode2):
        """
        Checks if two episodes are related based on semantic similarity.
        """
        if not self.word_vectors:
            return False

        tokens1 = self._preprocess_text(episode1)
        tokens2 = self._preprocess_text(episode2)

        if not tokens1 or not tokens2:
            return False

        vec1 = self._get_sentence_vector(tokens1)
        vec2 = self._get_sentence_vector(tokens2)

        # Cosine similarity
        cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        return cosine_sim > self.similarity_threshold
