"""
Writing Prep - Minimum Word Counter and Exam Assistant
For IELTS / TOEFL / Proficiency writing exams:
a distraction-free, dark-mode desktop text editor.
 
To run: python writing_prep.py   (Python 3.8+, no additional libraries required)
"""

# 1. IMPORTING MODULES ------------------------------------------
import tkinter as tk
from tkinter import messagebox,filedialog
from datetime import datetime


# Colors

BG = "#16141a"
PANEL = "#231f2b"
ENTRY_BG = "#312c3b"
MAIN_ACCENT = "#5c5470"
FG = "#dbd8e3"
MUTED = "#8d8796"
RED = "#d32f2f"  
ORANGE = "#e65100"
GREEN = "#2e7d32"


class WritingPrepApp:
      # 2. APPLICATION CLASS AND INTERFACE SETUP --------------------------------
      def __init__(self, root):
          self.root=root
          self.root.title("Writing Prep")
          self.root.geometry("1050x650")
          self.root.minsize(800, 500)
          self.root.configure(bg=BG)

          self.remaining_seconds = 0 
          self.timer_id = None
          self.timer_running = False
          self.goal_reached = False

          self._build_left_panel()
          self._build_right_panel()
          self.update_stats()

      def _build_left_panel(self):
          left = tk.Frame(self.root,bg = PANEL, width=270)
          left.pack(side="left", fill="y")
          left.pack_propagate(False)

          tk.Label(left, text="WritingPrep", bg=PANEL, fg=FG,
                   font=("Poppins Bold", 18, "bold")).pack(pady=(20, 15))

          # Settings
          tk.Label(left, text="Minimum Word Target", bg=PANEL, fg=MUTED,
                   font=("Poppins", 10)).pack(anchor="w", padx=20)
          self.goal_var = tk.StringVar(value="250")
          self.goal_var.trace_add("write", lambda *_: self.update_stats())
          tk.Entry(left, textvariable=self.goal_var, bg=ENTRY_BG, fg=FG,
                   insertbackground=FG, relief="flat",
                   font=("Poppins", 12)).pack(fill="x", padx=20, pady=(2,12), ipady=4)

          tk.Label(left, text="Time (Minute)", bg=PANEL, fg=MUTED,
                   font=("Poppins", 10)).pack(anchor="w", padx=20)
          self.minutes_var = tk.StringVar(value="40")
          tk.Entry(left, textvariable=self.minutes_var, bg=ENTRY_BG, fg=FG,
                   insertbackground=FG, relief="flat", 
                   font=("Poppins", 12)).pack(fill="x", padx=20, pady=(2,12), ipady=4)

          self.start_btn = tk.Button(left, text="Start the Timer", command=self.toggle_timer,
                                     bg=GREEN, fg="white", relief="flat", font=("Poppins", 11, "bold"), cursor="hand2")
          self.start_btn.pack(fill="x", padx=20, pady=(5, 5), ipady=5)

          tk.Button(left, text="Reset", command=self.reset_timer,
                    bg=ENTRY_BG, fg=FG, relief="flat",
                    font=("Poppins", 10), cursor="hand2").pack(fill="x", padx=20, ipady=3)

          # Countdown 
          self.timer_label = tk.Label(left, text="40:00", bg=PANEL, fg=FG,
                                      font=("Poppins", 34, "bold"))         
          self.timer_label.pack(pady=(20, 10))

          # Statics
          self.count_label = tk.Label(left, text="0 words", bg=PANEL, fg=FG,
                                      font=("Poppins", 14, "bold"))
          self.count_label.pack(pady=(10, 5))

          self.progress = tk.Canvas(left, height=18, bg=ENTRY_BG, highlightthickness=0)
          self.progress.pack(fill="x", padx=20)
          self.progress_rect = self.progress.create_rectangle(0, 0, 0, 18, fill=RED, width=0)

          self.status_label = tk.Label(left, text="", bg=PANEL, fg=MUTED,
                                       font=("Poppins", 10), wraplength=230)
          self.status_label.pack(pady=8)

          # Save
          tk.Button(left, text="Save (.txt)", command=self.save_text,
                    bg=MAIN_ACCENT, fg="white", relief="flat",
                    font=("Poppins", 11, "bold"), cursor="hand2"
                    ).pack(side="bottom", fill="x", padx=20, pady=20, ipady=5)

      def _build_right_panel(self):
          right = tk.Frame(self.root, bg=BG)
          right.pack(side="right", fill="both", expand=True) 

          self.text = tk.Text(right, bg=BG, fg=FG, insertbackground=FG,
                              font=("Poppins", 13), wrap="word", relief="flat",
                              padx=30, pady=25, undo=True, spacing2=4,
                              selectbackground=MAIN_ACCENT)
          scroll = tk.Scrollbar(right, command=self.text.yview)
          self.text.configure(yscrollcommand=scroll.set)
          scroll.pack(side="right", fill="y")
          self.text.pack(side="left", fill="both", expand=True)

          self.text.bind("<KeyRelease>", lambda e: self.update_stats())
          self.text.bind("<<Paste>>", lambda e: self.root.after(10, self.update_status))
          self.progress.bind("<Configure>", lambda e: self.update_stats())
          self.text.focus_set()

# 3. LOGIC FUNCTIONS --------------------------------
      def get_goal(self):
           try:
                return max (1, int(self.goal_var.get()))
           except ValueError:
                return 250

      def count_words(self):
           return len(self.text.get("1.0", "end-1c").split())

      def update_stats(self):
           words = self.count_words()
           goal = self.get_goal()
           ratio = min(words / goal, 1.0)

           self.count_label.config(text=f"{words} / {goal} words")

           width = self.progress.winfo_width()
           self.progress.coords(self.progress_rect, 0, 0, width * ratio, 18)

           if words >= goal:
                color = GREEN
                self.status_label.config(text=" Target Reached!", fg=GREEN)
                self.goal_reached = True
           else:
                color = RED if ratio < 0.6 else ORANGE
                self.status_label.config(text=f"{goal - words} words left", fg=MUTED)
           self.progress.itemconfig(self.progress_rect, fill=color)

      def format_time(self, seconds):
           return f"{seconds // 60:02d} : {seconds % 60:02d}"

      def toggle_timer(self):
           if self.timer_running:
                self.pause_timer()
           else:
                self.start_timer()

      def start_timer(self):
           if self.remaining_seconds <= 0:
                try:
                     minutes = int(self.minutes_var.get())
                     if minutes <= 0:
                          raise ValueError
                except ValueError:
                     messagebox.showwarning("Error", "Please enter a valid number of minutes.")
                     
                     return
                self.remaining_seconds = minutes * 60
           self.timer_running = True
           self.start_btn.config(text="Pause", bg=ORANGE)
           self.text.focus_set()
           self.tick()

           
