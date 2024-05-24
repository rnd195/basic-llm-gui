from tkinter import Tk, Frame, Button
from tkinter.scrolledtext import ScrolledText
import requests
import ollama
import sys
import threading


class Settings:
    dark = "#1f1f1f"
    light = "#dadada"
    blue = "#2654d3"
    lightblue = "#a2b3e1"
    send_keybind = "<Control-Return>"


class BasicLLMChat:
    """
    A class for a basic Ollama Chat GUI

    Attributes:
        root (Tk): Top level tkinter widget
        frame_messages (Frame): Frame for the messages between the user and LLM
        frame_buttons (Frame): Frame for buttons to interact with the GUI
        frame_chat (Frame): Frame for the user's queries
        messages (ScrolledText): Text widget for messages between the user and LLM with a scrollbar
        chat_box (ScrolledText): Text widget for the user's queries with a scrollbar
        user_input (str): Text input from the chat box
        is_msg_sent (bool): Flag whether a message has been sent by the user
        history (list): List that saves all user queries - used for retrieving the last query
        msg_resp_history (list): List of dictionaries containing the queries and responses
        send_button (Button): Button to send the user's queries to the LLM
        previous_button (Button): Returns the user's previous query
        delete_button (Button): Deletes everything currently written in the chat box
        exit_button (Button): Exits the GUI

                          root
    -------------------------------------------------
    |                frame_messages                 |
    |   -----------------------------------------   |
    |   |               messages                |   |
    |   -----------------------------------------   |
    |                 frame_buttons                 |
    |   -----------------------------------------   |
    |   |  send  delete  previous  reset  exit  |   |
    |   -----------------------------------------   |
    |                  frame_chat                   |
    |   -----------------------------------------   |
    |   |               chat_box                |   |
    |   -----------------------------------------   |
    -------------------------------------------------
    """

    def __init__(self):
        self.root = Tk()
        self.root.configure(background=Settings.dark)

        # Place to display messages between the user and the LLM
        self.frame_messages = Frame(
            self.root,
            background=Settings.dark,
            padx=10,
            pady=9
        )
        self.frame_messages.grid(row=0, column=0)

        # A layer for buttons
        self.frame_buttons = Frame(
            self.root,
            background=Settings.dark,
            padx=10,
            pady=0
        )
        # "EW" - ensure that the frame spans from left to right all the way
        self.frame_buttons.grid(row=1, column=0, sticky="EW")
        # Third button (third column) will be aligned to the right
        self.frame_buttons.columnconfigure(index=4, weight=1)

        # Frame for user input
        self.frame_chat = Frame(
            self.root,
            background=Settings.dark,
            padx=10,
            pady=9
        )
        self.frame_chat.grid(row=2, column=0)

        # Possibly add images instead of the default buttons
        # self.send_images = {
        #     "idle": PhotoImage(file="./assets/send.png"),
        #     "hover": "./assets/send_hover.png",
        #     "active": "./assets/send_active.png"
        # }

        # Actual messages widget
        self.messages = ScrolledText(
            self.frame_messages,
            width=76,
            height=30,
            background=Settings.light
        )
        self.messages.config(wrap="word")
        self.messages.pack()
        # Start in an uneditable mode
        self.messages.config(state="disabled")

        # Actual user input widget
        self.chat_box = ScrolledText(
            self.frame_chat,
            width=76,
            height=10,
            background=Settings.light
        )
        self.chat_box.config(wrap="word")
        # Send messages using ctrl+enter
        self.chat_box.bind(Settings.send_keybind, self._send_message)
        # Clear the chat box completely (otherwise there would be a newline in the empty box)
        self.root.bind(Settings.send_keybind, self._clear_chat_box)
        self.chat_box.pack()

        # Used as input to the LLM
        self.user_input = ""
        # Track the state of whether a message is sent
        self.is_msg_sent = True

        # This is used for putting the previous message into the chat box.
        # For simplicity, this history list is independent of the context history below.
        self.history = []
        # This enables conversations with context
        self.msg_resp_history = []

        # Send messages from the chat box
        self.send_button = Button(
            self.frame_buttons,
            text="Send",
            command=self._send_message,
            background=Settings.blue,
            foreground=Settings.light,
            padx=10
        )
        # Get the last item from history (implement longer history?)
        self.previous_button = Button(
            self.frame_buttons,
            text="Previous",
            command=self._history_previous,
            background=Settings.light,
            foreground=Settings.dark,
            padx=5
        )
        # Quickly delete everything in the chat box
        self.delete_button = Button(
            self.frame_buttons,
            text="Delete",
            command=self._clear_chat_box,
            background=Settings.light,
            foreground=Settings.dark,
            padx=5
        )
        # Start a new chat
        self.reset_button = Button(
            self.frame_buttons,
            text="Reset",
            command=self._reset_chat,
            background=Settings.light,
            foreground=Settings.dark,
            padx=5
        )
        # Exit the program predictably
        self.exit_button = Button(
            self.frame_buttons,
            text="Exit",
            command=self._exit_gui,
            background=Settings.light,
            foreground=Settings.dark,
            padx=5
        )

        self.send_button.grid(row=0, column=0, padx=3)
        self.delete_button.grid(row=0, column=1, padx=3)
        self.previous_button.grid(row=0, column=2, padx=3)
        self.reset_button.grid(row=0, column=3, padx=3)
        # Position the exit button all the way to the right
        self.exit_button.grid(row=0, column=4, sticky="E", padx=3)

        # Safe exit
        self.root.protocol("WM_DELETE_WINDOW", self._exit_gui)

        self.root.mainloop()

    def _insert_text(self, to_insert):
        """Make messages editable, insert text, and disable edits"""
        self.messages.config(state="normal")
        self.messages.insert("end", to_insert)
        self.messages.config(state="disabled")

    def _send_message(self, event=None):
        """Send message to the LLM"""
        self.user_input = self.chat_box.get("1.0", "end-1c")
        if self.user_input == "":
            return None

        self._insert_text(f"USER:\n{self.user_input}\n\n")

        # Save sent stuff to history
        self.history.append(self.user_input)
        # Clear chat box on send
        self.chat_box.delete("1.0", "end-1c")
        # Too many messages to fit the screen -> move to the last
        self.messages.see("end")

        # Let other parts of the code know that a message was sent / response was generated
        self.is_msg_sent = True
        self.response_finished = False

        # Progressively generate answer in the GUI via threading; improves stability
        response_thread = threading.Thread(target=self._get_answer, daemon=True)

        # Run response thread after 1ms
        self.root.after(1, response_thread.start())

    def _clear_chat_box(self, event=None):
        """Delete everything in the chat box"""
        self.chat_box.delete("1.0", "end-1c")

    def _history_previous(self):
        """Get previous sent message into the chat box"""
        n_items = len(self.history)

        if n_items == 0:
            return None

        # Get last saved message
        last_msg = self.history[n_items - 1]
        self.chat_box.delete("1.0", "end")
        self.chat_box.insert("end", last_msg)

    def _exit_gui(self):
        """Clean up and exit the program"""
        self._clear_chat_box()
        self.root.destroy()
        del self.history
        print("Exiting program.")
        sys.exit(0)

    def _reset_chat(self):
        """Clear all history and start a new chat"""
        if self.response_finished:
            self.msg_resp_history = []

            self.messages.config(state="normal")
            self.messages.delete("1.0", "end-1c")
            self.messages.config(state="disabled")
            self.messages.see("end")

    def _get_answer(self):
        """Get answer from LLM"""
        # Disable the send button while getting an answer
        self.send_button["state"] = "disabled"
        self.send_button.configure(background = Settings.lightblue)

        # Check if ollama is running in the background
        try:
            r = requests.get("http://localhost:11434/")
        except requests.ConnectionError:
            explanation = "Failed to connect to localhost:11434\nIs Ollama running?"
            self._insert_text(f"SYSTEM:\n{explanation}\n\n")
            return None

        if r.status_code != 200:
            self._insert_text(f"SYSTEM:\nOllama is not running.\n\n")
            return None

        if self.is_msg_sent:
            # Always save what the user asks and the response (further below)
            self.msg_resp_history.append(
                {
                    "role": "user",
                    "content": self.user_input,
                }
            )

            # Connect to the model to chat and get responses in a stream
            response_stream = ollama.chat(
                model="llama3",
                messages=self.msg_resp_history,
                stream=True
            )

            self._insert_text("LLM:\n")
            
            # Build the response by appending the generated text as it is generated
            self.response_finished = False
            full_response = str()
            for llm_output in response_stream:
                self._insert_text(llm_output["message"]["content"])
                self.messages.see("end")
                full_response = full_response + llm_output["message"]["content"]

            self.msg_resp_history.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )

            # Insert newlines after generated text
            self._insert_text("\n\n")

            # Reset message sent checker
            self.is_msg_sent = False
            self.response_finished = True

            # Re-enable the send button
            self.send_button["state"] = "normal"
            self.send_button.configure(background = Settings.blue)


chat = BasicLLMChat()
