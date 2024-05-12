import ollama


# Test out ollama response streaming
get_stream = ollama.chat(
    model="llama3",
    messages=[
        {
            "role": "user", 
            "content": "Write the words MAGICAL HOUSE and nothing else."
        }
    ],
    stream=True
)

for output in get_stream:
  print(output["message"]["content"], end="-", flush=True)
