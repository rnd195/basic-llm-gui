import ollama

# Message-response history
msg_resp_history = [
    {
        "role": "user",
        "content": "Write the words MAGICAL HOUSE ADVENTURE and nothing else.",
    }
]

# Test out ollama response streaming
response_stream = ollama.chat(model="llama3", messages=msg_resp_history, stream=True)

full_response = ""
for llm_output in response_stream:
    full_response = full_response + llm_output["message"]["content"]

msg_resp_history.append({"role": "assistant", "content": full_response})
