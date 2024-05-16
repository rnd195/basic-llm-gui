# Basic LLM GUI

A simple GUI written in Python for chatting with large language models locally using [Ollama](https://github.com/ollama/ollama).

Below is an example of a short chat with the 8B variant of [Meta Llama 3](https://ollama.com/library/llama3):

![screenshot](assets/screenshot.jpg)

# How to Use

Assuming you have Python 3.8+ installed:

1. Install the required Python packages
   - `pip install requests ollama`
   - The remaining packages should be part of the base library
2. Install and run [Ollama](https://ollama.com/)
3. Download [Llama 3](https://ollama.com/library/llama3) by opening the command line and running
   - `ollama pull llama3`

4. Start `ui.py` and chat!


# License

This project is licensed under the [MIT License](https://github.com/rnd195/basic-llm-gui/blob/main/LICENSE).

# Attribution

This project builds upon the concepts and ideas from the following sources:

`https://realpython.com/python-gui-tkinter/`
`https://tkdocs.com/tutorial/`

- General sources of `tkinter` tutorials and documentation

`https://stackoverflow.com/questions/42062391/how-to-create-a-chat-window-with-tkinter`
`https://www.youtube.com/watch?v=sopNW98CRag`

- Specific sources for chat GUIs in `tkinter`

`https://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only`
`https://github.com/ollama/ollama-python/issues/70`

- Other helpful resources worth mentioning
