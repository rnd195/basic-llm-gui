@echo off

echo Starting Ollama and preparing the llama3.1 model
ollama run llama3.1 ""
echo Success

python.exe ".\llm_gui.py"
