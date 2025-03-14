import ollama

def chat_with_ollama(model="granite3-dense:8b"):
    print("Welcome to the Ollama Chatbot! Type 'exit' to quit.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        response = ollama.chat(model=model, messages=[{"role": "user", "content": user_input}])
        print("Bot:", response["message"]["content"])

if __name__ == "__main__":
    chat_with_ollama()
