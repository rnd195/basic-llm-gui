@echo off

echo Starting Ollama and preparing the llama3 model
ollama run llama3 ""
echo Success

python.exe ".\ui.py"
