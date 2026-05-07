import tkinter as tk
from tkinter import ttk, messagebox
import winsound

class PomodoroTimer:
    WORK_TIME = 25 * 60       # 25 minutes
    SHORT_BREAK = 5 * 60      # 5 minutes
    LONG_BREAK = 15 * 60      # 15 minutes
    SESSIONS_BEFORE_LONG = 4

    # Color palette
    BG = "#faf5f0"
    CARD_BG = "#ffffff"
    WORK_COLOR = "#c0392b"
    SHORT_BREAK_COLOR = "#27ae60"
    LONG_BREAK_COLOR = "#2980b9"
    TEXT = "#2c3e50"
    SUBTEXT = "#7f8c8d"
    PROGRESS_TROUGH = "#ecf0f1"

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Pomodoro Timer")
        self.window.geometry("380x440")
        self.window.resizable(False, False)
        self.window.configure(bg=self.BG)

        self.current_phase = "work"
        self.remaining = self.WORK_TIME
        self.duration = self.WORK_TIME
        self.running = False
        self._job = None
        self.pomodoros = 0
        self.sessions_in_cycle = 0

        self._build_ui()
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        self.window.mainloop()

    # ── UI construction ────────────────────────────────────────────

    def _build_ui(self):
        card = tk.Frame(self.window, bg=self.CARD_BG,
                        highlightbackground="#e0d6cc", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=350, height=410)

        tk.Label(card, text="Pomodoro Timer", font=("Segoe UI", 16, "bold"),
                 fg=self.TEXT, bg=self.CARD_BG).pack(pady=(25, 5))

        self.phase_lbl = tk.Label(card, font=("Segoe UI", 11),
                                  fg=self.WORK_COLOR, bg=self.CARD_BG)
        self.phase_lbl.pack()

        self.timer_lbl = tk.Label(card, font=("Segoe UI", 50, "bold"),
                                  fg=self.WORK_COLOR, bg=self.CARD_BG)
        self.timer_lbl.pack(pady=(8, 5))

        self.progress = ttk.Progressbar(card, length=290, mode="determinate",
                                        maximum=self.duration, value=0)
        self.progress.pack(pady=(0, 10))

        self.tomato_lbl = tk.Label(card, font=("Segoe UI", 10),
                                   fg=self.SUBTEXT, bg=self.CARD_BG)
        self.tomato_lbl.pack(pady=(0, 12))

        btn_frame = tk.Frame(card, bg=self.CARD_BG)
        btn_frame.pack(pady=(0, 8))

        self._make_button(btn_frame, "Start",  self._start,  self.WORK_COLOR, 0)
        self._make_button(btn_frame, "Pause",  self._pause,  "#e67e22",       1)
        self._make_button(btn_frame, "Reset",  self._reset,  self.SUBTEXT,     2)
        self._make_button(btn_frame, "Skip",   self._skip,   self.LONG_BREAK_COLOR, 3)

        self.top_var = tk.BooleanVar(value=False)
        tk.Checkbutton(card, text="Always on Top", variable=self.top_var,
                       command=self._toggle_top,
                       font=("Segoe UI", 9), fg=self.SUBTEXT, bg=self.CARD_BG,
                       selectcolor=self.CARD_BG,
                       activebackground=self.CARD_BG).pack(pady=(10, 0))

        self._sync_display()

    def _make_button(self, parent, text, cmd, color, col):
        btn = tk.Button(parent, text=text, command=cmd,
                        font=("Segoe UI", 10, "bold"),
                        bg=color, fg="white", activebackground=color,
                        activeforeground="white", relief="flat",
                        padx=10, pady=5, cursor="hand2", width=6)
        btn.grid(row=0, column=col, padx=2)
        return btn

    # ── Timer engine ────────────────────────────────────────────────

    def _start(self):
        if not self.running:
            self.running = True
            self._tick()

    def _pause(self):
        self.running = False
        if self._job is not None:
            self.window.after_cancel(self._job)
            self._job = None

    def _reset(self):
        self._pause()
        self.remaining = self.duration
        self._sync_display()

    def _skip(self):
        self._pause()
        self.remaining = 0
        self._finish_phase()

    def _tick(self):
        if not self.running:
            return
        if self.remaining > 0:
            self.remaining -= 1
            self._sync_display()
            self._job = self.window.after(1000, self._tick)
        else:
            self.running = False
            self._finish_phase()

    # ── Phase switching ─────────────────────────────────────────────

    def _finish_phase(self):
        self._alert()
        if self.current_phase == "work":
            self.pomodoros += 1
            self.sessions_in_cycle += 1
            if self.sessions_in_cycle >= self.SESSIONS_BEFORE_LONG:
                self._set_phase("long_break")
                self.sessions_in_cycle = 0
            else:
                self._set_phase("short_break")
        else:
            self._set_phase("work")

    def _set_phase(self, phase):
        self.current_phase = phase
        if phase == "work":
            self.duration = self.WORK_TIME
            color = self.WORK_COLOR
            text = "Focus Time"
        elif phase == "short_break":
            self.duration = self.SHORT_BREAK
            color = self.SHORT_BREAK_COLOR
            text = "Short Break"
        else:
            self.duration = self.LONG_BREAK
            color = self.LONG_BREAK_COLOR
            text = "Long Break"

        self.remaining = self.duration
        self.phase_lbl.config(text=text, fg=color)
        self.timer_lbl.config(fg=color)
        self.progress.config(maximum=self.duration)
        self._sync_display()

    # ── Helpers ─────────────────────────────────────────────────────

    def _sync_display(self):
        m, s = divmod(self.remaining, 60)
        self.timer_lbl.config(text=f"{m:02d}:{s:02d}")
        self.progress["value"] = self.duration - self.remaining
        self.tomato_lbl.config(text=f"{self.pomodoros} completed")

    def _alert(self):
        names = {"work": "Focus time", "short_break": "Short break",
                 "long_break": "Long break"}
        # Sound — winsound.Beep blocks but is short, run in after() is fine
        for _ in range(3):
            winsound.Beep(1000, 180)
            winsound.Beep(800, 180)
        messagebox.showinfo("Time's Up!",
                            f"{names[self.current_phase]} is over!")

    def _toggle_top(self):
        self.window.attributes("-topmost", self.top_var.get())

    def _on_close(self):
        if self.running:
            if not messagebox.askokcancel("Quit",
                                          "Timer is still running. Quit anyway?"):
                return
        self.window.destroy()


if __name__ == "__main__":
    PomodoroTimer()
