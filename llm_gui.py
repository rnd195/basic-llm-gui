from tkinter import Tk, Frame, Button, font
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
    main_fonts = ["Inter", "Courier"]


class BasicLLMChat:
    """
    A class for a basic Ollama Chat GUI

    Attributes:
        root (Tk): Top level tkinter widget
        main_font (str): Custom font used in the main parts of the GUI
        frame_messages (Frame): Frame for the messages between the user and LLM
        frame_buttons (Frame): Frame for buttons to interact with the GUI
        frame_chat (Frame): Frame for the user's queries
        messages (ScrolledText): Text widget for messages between the user and LLM with a scrollbar
        chat_box (ScrolledText): Text widget for the user's queries with a scrollbar
        user_input (str): Text input from the chat box
        is_msg_sent (bool): Flag whether a message has been sent by the user
        response_finished (bool): Flag whether a response from the LLM is completed
        cancel_response (bool): Flag whether a response from the LLM should be interrupted
        previous (str): String that stores the last query for retrieval
        msg_resp_history (list): List of dictionaries containing the queries and responses
        send_button (Button): Button to send the user's queries to the LLM
        previous_button (Button): Returns the user's previous query
        cancel_button (Button): Interrupts the response of the LLM
        reset_button (Button): Starts a new chat by clearing history
        exit_button (Button): Exits the GUI

                          root
    -------------------------------------------------
    |                frame_messages                 |
    |   -----------------------------------------   |
    |   |               messages                |   |
    |   -----------------------------------------   |
    |                 frame_buttons                 |
    |   -----------------------------------------   |
    |   |  send prev newchat cancel       exit  |   |
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

        # Set the main font or fallback to "Courier"
        if Settings.main_fonts[0] in font.families():
            self.main_font = Settings.main_fonts[0]
        else:
            self.main_font = Settings.main_fonts[1]

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
            height=32,
            background=Settings.light,
            padx=5,
            pady=5
        )
        self.messages.config(wrap="word")
        self.messages.pack()
        # Start in an uneditable mode
        self.messages.config(state="disabled")
        # Set a custom font in the message box or fallback to a default one
        self.font_setter(
            self.messages,
            self.main_font
        )

        # Actual user input widget
        self.chat_box = ScrolledText(
            self.frame_chat,
            width=76,
            height=11,
            background=Settings.light,
            padx=5,
            pady=5
        )
        self.chat_box.config(wrap="word")
        # Set a custom font in the chat box or fallback to a default one
        self.font_setter(
            self.chat_box,
            self.main_font
        )

        # Send messages using ctrl+enter
        self.chat_box.bind(Settings.send_keybind, self.send_message)
        # Clear the chat box completely (otherwise there would be a newline in the empty box)
        self.root.bind(Settings.send_keybind, self.clear_chat_box)
        self.chat_box.pack()

        # Used as input to the LLM
        self.user_input = str()
        # Track whether a message is sent, response is finished, or user wants to cancel the response
        self.is_msg_sent = False
        self.response_finished = False
        self.cancel_response = False

        # This is used for putting the previous message into the chat box.
        # For simplicity, this history list is independent of the context history below.
        self.previous = str()
        # This enables conversations with context
        self.msg_resp_history = []

        # Send messages from the chat box
        self.send_button = Button(
            self.frame_buttons,
            text="Send",
            command=self.send_message,
            background=Settings.blue,
            foreground=Settings.light,
            padx=10
        )
        # Get the last saved message
        self.previous_button = Button(
            self.frame_buttons,
            text="Previous",
            command=self.get_previous,
            background=Settings.light,
            foreground=Settings.dark,
            padx=5
        )
        # Interrupt the llm while it is generating an answer
        self.cancel_button = Button(
            self.frame_buttons,
            text="Cancel",
            command=self.cancel_request,
            background=Settings.light,
            foreground=Settings.dark,
            padx=5
        )
        # Start a new chat
        self.reset_button = Button(
            self.frame_buttons,
            text="New Chat",
            command=self.reset_chat,
            background=Settings.light,
            foreground=Settings.dark,
            padx=5
        )
        # Exit the program predictably
        self.exit_button = Button(
            self.frame_buttons,
            text="Exit",
            command=self.exit_gui,
            background=Settings.light,
            foreground=Settings.dark,
            padx=5
        )

        self.send_button.grid(row=0, column=0, padx=3)
        self.previous_button.grid(row=0, column=1, padx=3)
        self.cancel_button.grid(row=0, column=2, padx=3)
        self.reset_button.grid(row=0, column=3, padx=3)
        # Position the exit button all the way to the right
        self.exit_button.grid(row=0, column=4, sticky="E", padx=3)

        # Safe exit
        self.root.protocol("WM_DELETE_WINDOW", self.exit_gui)

        self.root.mainloop()

    def _insert_text(self, to_insert):
        """Make messages editable, insert text, and disable edits"""
        self.messages.config(state="normal")
        self.messages.insert("end", to_insert)
        self.messages.config(state="disabled")

    def font_setter(self, widget, new_font):
        """Set a custom font to a widget"""
        widget.config(
            font=(new_font, 10, "normal")
        )

    def send_message(self, event=None):
        """Send message to the LLM"""
        self.user_input = self.chat_box.get("1.0", "end-1c")
        if self.user_input == "":
            return None

        self._insert_text(f"USER:\n{self.user_input}\n\n")

        # Save the last sent message for possible retrieval
        self.previous = self.user_input
        # Clear chat box on send
        self.chat_box.delete("1.0", "end-1c")
        # Too many messages to fit the screen -> move to the last
        self.messages.see("end")

        # Let other parts of the code know that a message was sent
        self.is_msg_sent = True

        # Progressively generate answer in the GUI via threading; improves stability
        response_thread = threading.Thread(target=self.get_answer, daemon=True)

        # Run response thread after 1ms
        self.root.after(1, response_thread.start())

    def clear_chat_box(self, event=None):
        """Delete everything in the chat box"""
        self.chat_box.delete("1.0", "end-1c")

    def get_previous(self):
        """Get the last sent message back into the chat box"""
        if self.previous == "":
            return None

        self.chat_box.delete("1.0", "end")
        self.chat_box.insert("end", self.previous)

    def exit_gui(self):
        """Clean up and exit the program"""
        self.clear_chat_box()
        self.root.destroy()
        del self.previous
        del self.msg_resp_history
        print("Exiting program.")
        sys.exit(0)

    def reset_chat(self):
        """Clear all history and start a new chat"""
        if self.response_finished:
            self.msg_resp_history = []

            self.messages.config(state="normal")
            self.messages.delete("1.0", "end-1c")
            self.messages.config(state="disabled")
            self.messages.see("end")

    def cancel_request(self):
        """Used for cancelling the output of the LLM"""
        if self.is_msg_sent:
            self.cancel_response = True

    def get_answer(self):
        """Get answer from LLM"""
        # Probably not needed to check this 
        if not self.is_msg_sent:
            return None

        # Disable some buttons while getting an answer
        self.send_button["state"] = "disabled"
        self.reset_button["state"] = "disabled"
        self.send_button.configure(background = Settings.lightblue)

        # Check if ollama is running in the background
        try:
            r = requests.get("http://localhost:11434/")
        except requests.ConnectionError:
            explanation = """Failed to connect to localhost:11434
            \nIs Ollama running?
            \nTo continue, start Ollama and restart the GUI.
            """
            self._insert_text(f"SYSTEM:\n{explanation}\n\n")
            return None

        if r.status_code != 200:
            self._insert_text(
                f"SYSTEM:\nCouldn't connect to Ollama. Consider restarting Ollama and the GUI.\n\n"
            )
            return None

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
            
            # Append partial answer on a cancellation request
            if self.cancel_response:
                self.msg_resp_history.append(
                    {
                        "role": "assistant",
                        "content": full_response
                    }
                )
                self._insert_text("\n\n")
                # Reset message sent checker
                self.is_msg_sent = False
                self.response_finished = True

                # Re-enable the send button
                self.send_button["state"] = "normal"
                self.reset_button["state"] = "normal"
                self.send_button.configure(background = Settings.blue)
                self.cancel_response = False
                return None

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
        self.reset_button["state"] = "normal"
        self.send_button.configure(background = Settings.blue)


chat = BasicLLMChat()
