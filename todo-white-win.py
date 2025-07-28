from tkinter import *
from tkinter import filedialog, messagebox
import pickle
import os
# import time
import random
import sys # for command line args
import ctypes # make app not blurry on high DPI screens for Windows users


class TodoApp:
    def __init__(self, master):
        self.master = master
        # self.master.iconbitmap("GDR.ico") # have in in main function
        # self.different_shapes = ['☺', '☻', '♥', '♦', '♣', '♠', '•', '◘', '○', '◙', '♂', '♀', '♪', '♫', '☼', '►', '◄', '▲', '▼'] 
        self.different_shapes = ['☻', '♥', '▲', '◄', '▲', '▼', '■', '♫', '☼']
        self.last_shape = None
        
        self.default_title = "Arbeiten Kurwa"
        self.current_file = ""     # path of the open/save‑as file
        self.master.title(self.default_title)
        # master.title("Arbeiten Kurwa")
        # master.resizable(width=False, height=True)

        # Configuration
        self.window_size      = 10    # Number of visible checkboxes
        self.scroll_threshold = 3     # Checked-in-a-row before scrolling

        # State
        self.all_tasks      = []      # List of (main_title, [subtasks])
        self.current_main   = 0       # Index of currently displayed main task
        self.tasks          = []      # Current main’s subtasks
        self.varTasks       = {}      # Maps subtask -> BooleanVar
        self.window_start   = 0
        self.saved_states   = {}      # main_title -> { subtask: bool }

        # === UI SETUP ===
        self.textFrame = Frame(master)
        self.textFrame.pack(side=LEFT, fill=Y)

        self.taskFrame = Frame(master)
        self.taskFrame.pack(side=LEFT, fill=Y)

        # Navigation (Prev / Main Label / Next)
        navFrame = Frame(self.taskFrame)
        navFrame.pack(side=TOP, fill=X, pady=5)

        self.btnPrev = Button(navFrame, text="← Prev", command=self.prev_main)
        self.btnPrev.pack(side=LEFT, padx=5)
        self.lblMainTask = Label(navFrame, font=("Arial bold", 16), width=36)
        self.lblMainTask.pack(side=LEFT, expand=True)
        self.btnNext = Button(navFrame, text="Next →", command=self.next_main)
        self.btnNext.pack(side=RIGHT, padx=5)

        # Save / Open / Load / Help
        toolFrame = Frame(self.textFrame)
        toolFrame.pack(side=TOP, fill=X, pady=5)
        Button(toolFrame, text="New", command=self.new_project)\
            .grid(row=0, column=0, padx=5)
        self.btnSave = Button(toolFrame, text="Save", command=self.save, state=DISABLED)
        self.btnSave.grid(row=0, column=1, padx=5)
        self.btnSaveAs = Button(toolFrame, text="Save As", command=self.save_as)
        self.btnSaveAs.grid(row=0, column=2, padx=5)
        # Button(toolFrame, text="Save", command=self.save_project)\ # Old Save
        #     .grid(row=0, column=2, padx=5)
        Button(toolFrame, text="Open", command=self.open_project)\
            .grid(row=0, column=3, padx=5)
        Button(toolFrame, text="Help", command=self.show_help_window)\
            .grid(row=0, column=4, padx=(5, 0))
        # Always on top checkbox for poor windows users
        self.isOnTopVar = BooleanVar(value=False)
        self.cbIsOnTop = Checkbutton(toolFrame, text='Pin',
                            wraplength=700, justify=LEFT,
                            variable=self.isOnTopVar,
                            command=lambda: self.master.attributes("-topmost", self.isOnTopVar.get()))
        self.cbIsOnTop.grid(row=0, column=5, padx=0)

        Button(toolFrame, text="Load Text → UI", command=self.load_all_tasks, width=16)\
            .grid(row=0, column=6, sticky='e', padx=0)


        self.textBox = Text(self.textFrame, height=12, width=70, font=("Arial", 10), wrap="word")
        self.textBox.pack(fill=BOTH, expand=True, pady=(0,5), padx=(5,0))

        # Keyboard shortcut for saving
        master.bind_all("<Control-s>", lambda e: self.save())

        # Initial load
        self.load_all_tasks()

    # --- NEW HELP WINDOW FUNCTION ---
    def show_help_window(self):
        # Create a new Toplevel window
        help_window = Toplevel(self.master)
        help_window.title("Help - Arbeiten Kurwa")
        help_window.geometry("600x760") # Set a reasonable size
        help_window.transient(self.master) # Make it appear on top of the main window
        help_window.grab_set() # Make it modal (user must interact with it before main window)

        # Define the help text
        help_text_content = """
Welcome to Arbeiten Kurwa - Tkinter To-Do application 💀💀💀💀💀

HOW TO USE:

1. EDIT YOUR TASKS (Left Panel)
- Type tasks in the text box
- MAIN TASKS: Write in ALL CAPS or use "----" lines.
- SUBTASKS: Write normal text below a main task
- Click "Load Text → UI" to apply changes

2. MANAGE TASKS (Right Panel)
- Check completed subtasks
- Use ← Prev / Next → buttons to switch between main tasks
- The app automatically scrolls when you complete tasks

3. SAVE YOUR WORK
- Save As: Save to a new .todo file
- Save: or Ctrl+S to Save changes to the current file
- Open: Load saved todo lists (.todo file)
- New: Clears everything (after confirmation)

4. TIPS
- It's time to remember about CapsLock key
- Don't forget to spam Ctrl+S after every change
- After saving, the app updates the title with a random shape
- You shouldn't have two same subtasks in one task
- You absolutely shouldn't have two same main tasks, they will conflict
- 'Pin' is for poor Windows users who can't just 'Always on Top' the window 
- Better use notepad and copy-paste to save your sanity
- You should explore example.todo file from gitgub page. 
- You can find this app and example of .todo file on github page:
  https://github.com/Matreddit/awful-tk-todo-app
- App updates may exist, but you should not expect them
        """

        # Create a Text widget for the help content
        help_text_widget = Text(help_window, wrap="word", padx=10, pady=10,font=("Arial", 10))
        help_text_widget.pack(expand=True, fill=BOTH, padx=10, pady=10)
        help_text_widget.insert(END, help_text_content.strip())
        help_text_widget.config(state=DISABLED) # Make it read-only

        # Create the "Close" button
        close_button = Button(help_window, text="Close This Window",
                              command=help_window.destroy, # This destroys the Toplevel window
                              width=30) # Make it wider
        close_button.pack(pady=10)

        # shit, it's nice in the middle of the screen
        # # Center the new window (optional, but nice for dialogs)
        # help_window.update_idletasks() # Update to get actual window size
        # x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (help_window.winfo_width() // 2)
        # y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (help_window.winfo_height() // 2)
        # help_window.geometry(f"+{int(x)}+{int(y)}")


    # ——————————————————————————————
    # Parsing helpers
    # ——————————————————————————————
    def isDelimiter(self, s):
        return all(c in ('-', ' ') for c in s) and '-' in s

    def split_into_mains(self, lines):
        """Return list of (main_title, [subtasks]) from non-empty stripped lines."""
        groups = []
        current = None
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            if line.isupper() or self.isDelimiter(line):
                current = [line, []]
                groups.append(current)
            else:
                if current is None:
                    current = ["UNTITLED", []]
                    groups.append(current)
                current[1].append(line)
        return groups

    # ——————————————————————————————
    # (Re)load everything from the text box
    # ——————————————————————————————
    def load_all_tasks(self):
        # 1) Snapshot current before we lose it
        self.snapshot_current_state()

        # 2) Read raw lines
        raw = self.textBox.get("1.0", END).splitlines()
        lines = [ln.strip() for ln in raw if ln.strip()]

        # 3) Split into main+subs
        self.all_tasks = self.split_into_mains(lines)
        if not self.all_tasks:
            self.all_tasks = [["DO SOMETHING!", ["Think about life", "Go to sleep", "Wake up", "Repeat"]]]

        # 4) Reset index & load
        self.current_main = 0
        self.load_current_main()

    # ——————————————————————————————
    # Load a single main + its subtasks into the UI
    # ——————————————————————————————
    def load_current_main(self):
        title, subtasks = self.all_tasks[self.current_main]
        # Title formatting (Title Case if uppercase)
        display_title = title
        if title.isupper():
            display_title = " ".join(w.capitalize() for w in title.split())
        self.lblMainTask.config(text=display_title)

        # replaced ~~~      replaced so that same subtasks would not conflict
        """
        # Build / preserve BooleanVars,
        # initializing using any previously saved state
        old = self.varTasks.copy()
        self.varTasks.clear()
        saved_for_this = self.saved_states.get(title, {})

        for t in subtasks:
            if t in old:
                var = old[t]
            else:
                # pull from saved_states or default False
                init = saved_for_this.get(t, False)
                var = BooleanVar(master=self.master, value=init)
            self.varTasks[t] = var
        """
        # Build BooleanVars, one per subtask, seeded from saved_states
        self.varTasks.clear()
        saved_for_this = self.saved_states.get(title, {})

        for t in subtasks:
            init = saved_for_this.get(t, False)
            self.varTasks[t] = BooleanVar(master=self.master, value=init)
        # ~~~ replaced

        # Set up for display
        self.tasks        = subtasks
        self.window_start = 0
        self.refresh_ui()
        self.update_nav_buttons()
        # auto‑scroll into place if many items are already checked
        self.on_var_changed()

    # ——————————————————————————————
    # Snapshot the current main’s check states into saved_states
    # ——————————————————————————————
    def snapshot_current_state(self):
        if not self.tasks:
            return
        title = self.all_tasks[self.current_main][0]
        state_map = { t: self.varTasks[t].get() for t in self.tasks }
        self.saved_states[title] = state_map

    # ——————————————————————————————
    # Prev / Next main
    # ——————————————————————————————
    def prev_main(self):
        if self.current_main > 0:
            self.snapshot_current_state()
            self.current_main -= 1
            self.load_current_main()

    def next_main(self):
        if self.current_main < len(self.all_tasks) - 1:
            self.snapshot_current_state()
            self.current_main += 1
            self.load_current_main()

    def update_nav_buttons(self):
        self.btnPrev.config(state=(NORMAL if self.current_main > 0 else DISABLED))
        self.btnNext.config(state=(NORMAL if self.current_main < len(self.all_tasks)-1 else DISABLED))

    # ——————————————————————————————
    # Autoscroll logic
    # ——————————————————————————————
    def on_var_changed(self):
        # Count checked in a row from top
        prefix = 0
        for t in self.tasks:
            if self.varTasks[t].get():
                prefix += 1
            else:
                break

        if prefix >= self.scroll_threshold:
            new_start = prefix - (self.scroll_threshold - 1)
        else:
            new_start = 0

        max_start = max(0, len(self.tasks) - self.window_size)
        self.window_start = min(new_start, max_start)
        self.refresh_ui()

    def refresh_ui(self):
        # Remove old checkbuttons
        for w in self.taskFrame.winfo_children():
            if w not in (self.lblMainTask, self.btnPrev, self.btnNext) and not isinstance(w, Frame):
                w.destroy()

        # Add current window of subtasks
        end = self.window_start + self.window_size
        for t in self.tasks[self.window_start:end]:
            cb = Checkbutton(self.taskFrame, text=t,
                             wraplength=700, justify=LEFT,
                             variable=self.varTasks[t],
                             command=self.on_var_changed)
            cb.pack(anchor=W)

    # ———————————————————————————————————
    # Clear, Save & Open project (pickle)
    # ———————————————————————————————————
    def new_project(self):
        confirm = messagebox.askyesno("Clear UI?", "Make sure everything is saved. This will clear all content.")
        if confirm:
            # for new Save feature
            self.current_file = ""
            self.btnSave.config(state=DISABLED)
            self.master.title(self.default_title)
            self.last_shape = None
            # Clear all state
            self.textBox.delete("1.0", END)
            self.saved_states.clear()
            self.all_tasks.clear()
            self.tasks.clear()
            self.varTasks.clear()
            self.window_start = 0
            self.current_main = 0
            self.lblMainTask.config(text="New Project")
            self.refresh_ui()
            self.update_nav_buttons()

    def save(self):
        """Save to current_file; if none, delegate to save_as."""
        if not self.current_file:
            return self.save_as()
        self.snapshot_current_state()
        try:
            with open(self.current_file, 'wb') as f:
                pickle.dump({
                    'text':   self.textBox.get("1.0", END),
                    'states': self.saved_states,
                    'current_main': self.current_main # to open on the same task next time
                }, f)
        except Exception as e:
            messagebox.showerror("Save failed", str(e))
            return

        # update timestamp in title
        # ts = time.strftime("%H:%M:%S")                    # OLD
        # self.master.title(f"Arbeiten Kurwa • ({ts})")     # OLD

        # Pick a random shape and append it
        fname = os.path.basename(self.current_file)
        available_shapes = [s for s in self.different_shapes if s != self.last_shape]
        shape = random.choice(available_shapes)
        self.last_shape = shape
        self.master.title(f"{fname} {shape}")

    def save_as(self):
        """Prompt for file, then save."""
        path = filedialog.asksaveasfilename(
            defaultextension=".todo",
            filetypes=[("Todo Projects","*.todo"),("All files","*.*")]
        )
        if not path:
            return
        self.current_file = path
        # now that we have a path, enable the Save button
        self.btnSave.config(state=NORMAL)

        # set title to filename only
        fname = os.path.basename(self.current_file)
        self.master.title(fname)

        # and perform the actual save
        self.save()
    

    # old method for single Save button
    # def save_project(self):
    #     # Snapshot one last time
    #     self.snapshot_current_state()

    #     path = filedialog.asksaveasfilename(
    #         defaultextension=".todo",
    #         filetypes=[("Todo Projects","*.todo"),("All files","*.*")]
    #     )
    #     if not path:
    #         return

    #     data = {
    #         'text': self.textBox.get("1.0", END),
    #         'states': self.saved_states
    #     }
    #     try:
    #         with open(path, 'wb') as f:
    #             pickle.dump(data, f)
    #     except Exception as e:
    #         messagebox.showerror("Save failed", str(e))

    def open_project(self, path=None):
        if path is None:
            path = filedialog.askopenfilename(
                defaultextension=".todo",
                filetypes=[("Todo Projects","*.todo"),("All files","*.*")]
            )
            if not path or not os.path.exists(path):
                return

        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
        except Exception as e:
            messagebox.showerror("Load failed", str(e))
            return

        # Restore text + saved_states, then reload UI
        self.textBox.delete("1.0", END)
        self.textBox.insert("1.0", data.get('text',''))
        self.saved_states = data.get('states', {})
        # after loading data and before load_all_tasks():
        self.current_file = path            # for new Save
        self.btnSave.config(state=NORMAL)   # for new Save
        # Show filename only
        fname = os.path.basename(self.current_file)
        self.master.title(fname)
        self.last_shape = None # reset last_shape for new file

        self.load_all_tasks()
        self.current_main = data.get('current_main', 0) # for saving current task
        self.load_current_main()                        # for saving current task

if __name__ == '__main__':
    # ————————————————————————————————————————————————————————————
    # make app not blurry on high DPI screens for Windows users
    # ————————————————————————————————————————————————————————————
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # For Windows 8.1+
    except:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # For Windows 7+
        except:
            pass
    # ————————————————————————————————————————————————————————————
    root = Tk()
    app = TodoApp(root)

    # ————————————————————————————————————————————————————————————
    # Set the icon for the main window
    # ————————————————————————————————————————————————————————————
    # Determine the folder where data files live:
    if getattr(sys, 'frozen', False):
        # running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # running in normal Python
        base_path = os.path.dirname(__file__)

    icon_path = os.path.join(base_path, 'GDR.png')
    img = PhotoImage(file=icon_path)
    root.iconphoto(False, img)
    # ————————————————————————————————————————————————————————————


    # If program was launched with a .todo filename, open it immediately
    if len(sys.argv) > 1:
        incoming = sys.argv[1]
        app.open_project(incoming)

    root.mainloop()
