import openai

# from llama_cpp import Llama

# local_llm = Llama(model_path="tinyllama-1.1b-chat-v1.0.Q3_K_S.gguf", n_threads=4, n_gpu_layers=-1)

def think(prompt, legal=True):
    if legal:
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
    else:
        # Placeholder for local LLM thinking
        return "Local LLM is currently disabled."