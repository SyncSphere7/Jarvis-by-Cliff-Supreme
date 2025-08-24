import os
from core.cognitive.hybrid_intelligence import HybridIntelligenceSystem

# Set the API key for testing purposes
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCK9TgGvQsHoHcvwbT8JEKmxqAPZFRuQMU'

system = HybridIntelligenceSystem()
print("Knowledge Retrieval:")
print(system.knowledge_retrieval("What is Jarvis?"))
print("Content Generation:")
print(system.generate_content("Write a short description of Jarvis."))
print("Question Answering:")
print(system.answer_question("What can Jarvis do?"))
