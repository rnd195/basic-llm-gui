# Basic LLM GUI

A simple GUI written in Python for chatting with large language models locally using [Ollama](https://github.com/ollama/ollama).

Below is an example of a short chat with the 8B variant of [Meta Llama 3](https://ollama.com/library/llama3):

![screenshot](assets/screenshot.jpg)

# How to Install

Assuming you have Python 3.8+ installed:

1. Install the required Python packages
   - `pip install requests ollama`
   - The remaining packages should be part of the base library
2. Install and run [Ollama](https://ollama.com/)
3. Download [Llama 3](https://ollama.com/library/llama3) by opening the command line and running
   - `ollama pull llama3`
4. *Optional but recommended*: Download and install the [Inter font](https://fonts.google.com/specimen/Inter) (otherwise the default "Courier" font is displayed)
5. Make sure that Ollama is running, then start `llm_gui.py` and chat!

Lastly, Windows users may use the `Start GUI.bat` script, which first starts Ollama with the Llama 3 model and then runs `llm_gui.py` to start the GUI.



# How to Use

Write into the bottom text box and click **Send** (or `Ctrl + Enter`). The first prompt may take a while since the model will be loading in the background. After that, you should see a stream of answers from the LLM.

The **Previous** button returns the last message/query sent by the user.

The **Cancel** button interrupts the response of the LLM.

The **New Chat** button resets history and starts a brand new chat session.

The **Exit** button exits the GUI (or simply close out the window).

# To-do

- [x] Cancel / interrupt the LLM while an answer is being generated
- [x] Start a new chat / reset
- [x] Improve stability
- [ ] Add more fallback fonts
- [ ] Monospaced font for code
- [ ] Custom button design

# License

This project is licensed under the [MIT License](https://github.com/rnd195/basic-llm-gui/blob/main/LICENSE).

# Attribution & Acknowledgements

This project builds upon the concepts and ideas from several sources listed in [ATTRIBUTION.md](https://github.com/rnd195/basic-llm-gui/blob/main/ATTRIBUTION.md).

