from tkinter import Tk, Frame, Button
from tkinter.scrolledtext import ScrolledText
import sys


class Settings:
    dark = "#1f1f1f"
    light = "#dadada"
    blue = "#2654d3"
    send_keybind = "<Control-Return>"


class BasicLLMChat:
    """
            root
    ---------------------
    |   frame_messages  |
    |   frame_buttons   |
    |   frame_chat_box  |
    ---------------------
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
        self.frame_buttons.columnconfigure(index=3, weight=1)

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
        # Send messages using ctrl+enter
        self.chat_box.bind(Settings.send_keybind, self._send_message)
        # Clear the chat box completely (otherwise there would be a newline in the empty box)
        self.root.bind(Settings.send_keybind, self._clear_chat_box)
        self.chat_box.pack()

        # This is used for putting the previous message into the chat box
        self.history = []

        # Send messages from the chat box
        self.send_button = Button(
            self.frame_buttons,
            text="Send",
            command=self._send_message,
            background=Settings.blue,
            foreground=Settings.light,
            padx=10,
        )
        # Get the last item from history (implement longer history?)
        self.previous_button = Button(
            self.frame_buttons,
            text="Previous",
            command=self._history_previous,
            background=Settings.light,
            foreground=Settings.dark,
            padx=5,
        )
        # Quickly delete everything in the chat box
        self.delete_button = Button(
            self.frame_buttons,
            text="Delete",
            command=lambda: self._clear_chat_box(),
            background=Settings.light,
            foreground=Settings.dark,
            padx=5,
        )
        # Exit the program predictably
        self.exit_button = Button(
            self.frame_buttons,
            text="Exit",
            command=lambda: self._exit_gui(),
            background=Settings.light,
            foreground=Settings.dark,
            padx=5,
        )

        self.send_button.grid(row=0, column=0, padx=3)
        self.delete_button.grid(row=0, column=1, padx=3)
        self.previous_button.grid(row=0, column=2, padx=3)
        # Position the exit button all the way to the right
        self.exit_button.grid(row=0, column=3, sticky="E", padx=3)
        
        # Safe exit
        self.root.protocol("WM_DELETE_WINDOW", self._exit_gui)

        self.root.mainloop()

    def _send_message(self, event=None):
        """Send message to the LLM"""
        text = self.chat_box.get("1.0", "end-1c")
        if text == "":
            return None

        # Make messages editable, insert text, and disable edits
        self.messages.config(state="normal")
        self.messages.insert("end", f"USER:\n{text}\n\n")
        self.messages.config(state="disabled")

        # Save sent stuff to history
        self.history.append(text)
        # Clear chat box on send
        self.chat_box.delete("1.0", "end-1c")
        # Too many messages to fit the screen -> move to the last
        self.messages.see("end")

    def _clear_chat_box(self, event=None):
        """Delete everything in the chat box"""
        self.chat_box.delete("1.0", "end-1c")

    def _history_previous(self):
        """Get previous sent message into the chat box"""
        n_items = len(self.history)

        if n_items == 0:
            return None

        # Get last saved message
        text = self.history[n_items - 1]
        self.chat_box.delete("1.0", "end")
        self.chat_box.insert("end", text)

    def _exit_gui(self):
        """Clean up and exit the program"""
        self._clear_chat_box()
        self.root.destroy()
        del self.history
        sys.exit(0)
    
    # def _get_answer(self, event=None):
    #     """Get answer from LLM"""
        
    #     self.messages.config(state="normal")
    #     self.messages.insert("end", f"test insert ")
    #     self.messages.config(state="disabled")

    #     self.messages.see("end")


chat = BasicLLMChat()
