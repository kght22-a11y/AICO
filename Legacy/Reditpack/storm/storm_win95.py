#!/usr/bin/env python3
# storm_win95.py — AICO GUI
# Updated: Synced "n_paths" with "num_trajectories" and added "Insanity" control.

import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import storm_backend as backend

WIN_GREY = "#C0C0C0"
WIN_WHITE = "#FFFFFF"
WIN_BLUE = "#000080"
COMIC_FONT = ("Comic Sans MS", 10, "bold")

class RetroSplash(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        width = 400; height = 250
        x = (self.winfo_screenwidth()//2)-(width//2)
        y = (self.winfo_screenheight()//2)-(height//2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.configure(bg=WIN_BLUE, bd=5, relief="raised")
        tk.Label(self, text="AICO", font=("Comic Sans MS", 48, "bold"), bg=WIN_BLUE, fg="yellow").pack(pady=(20,0))
        tk.Label(self, text="STORM CONTROLLER", font=("Comic Sans MS", 16, "bold"), bg=WIN_BLUE, fg="white").pack()
        tk.Label(self, text="v0.99 [Registered]", font=("Comic Sans MS", 10), bg=WIN_BLUE, fg=WIN_GREY).pack(pady=10)
        self.lbl = tk.Label(self, text="Syncing Quantized States...", font=("Courier New", 9), bg=WIN_BLUE, fg="white")
        self.lbl.pack(side="bottom", pady=5)

class StormWin95App:
    def __init__(self, root):
        self.root = root
        self.root.title("AICO STORM CONTROLLER")
        self.root.configure(bg=WIN_GREY)
        self.root.geometry("850x680") # Made slightly taller for new options
        self.config = backend.load_config()
        
        main = tk.Frame(root, bg=WIN_GREY, bd=3, relief="raised")
        main.pack(fill="both", expand=True, padx=4, pady=4)
        
        tk.Label(main, text=" AICO SYSTEM CONTROL v0.98 ", bg=WIN_BLUE, fg=WIN_WHITE, font=("Comic Sans MS", 12, "bold"), anchor="w", bd=2, relief="raised").pack(fill="x", padx=2, pady=2)
        
        content = tk.Frame(main, bg=WIN_GREY)
        content.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- LEFT CONFIG PANEL ---
        left = tk.LabelFrame(content, text=" Parameters ", bg=WIN_GREY, fg="blue", font=COMIC_FONT, bd=2, relief="groove")
        left.pack(side="left", fill="y", padx=5, ipadx=5)
        
        # 1. Model
        self.ent_model = self.mk_entry(left, "Model:", "model", "qwen2.5:0.5b")
        
        # 2. Trajectories (The Fix: We will sync this to n_paths)
        self.ent_traj = self.mk_entry(left, "Trajectories (N):", "n_paths", "10")
        
        # 3. Insanity / Temperature (New)
        self.ent_temp = self.mk_entry(left, "Insanity (Temp):", "temperature", "0.1")
        
        # 4. Variant Dropdown
        tk.Label(left, text="Variant:", bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w", pady=(10,0))
        self.var_var = tk.StringVar(value=self.config.get("frontend", {}).get("storm_variant", "No Enhancements"))
        tk.OptionMenu(left, self.var_var, *backend.STORM_OPTIONS.keys()).pack(fill="x")
        
        # 5. Buttons
        tk.Button(left, text="Save Config", command=self.save, font=COMIC_FONT, bg=WIN_GREY, bd=3, relief="raised").pack(side="bottom", fill="x", pady=10)
        tk.Button(left, text="Clear Memory", command=self.reset_mem, font=COMIC_FONT, bg=WIN_GREY, bd=3, relief="raised", fg="red").pack(side="bottom", fill="x", pady=(0, 10))
        
        # --- RIGHT OUTPUT PANEL ---
        right = tk.LabelFrame(content, text=" Stream ", bg=WIN_GREY, fg="red", font=COMIC_FONT, bd=2, relief="groove")
        right.pack(side="right", fill="both", expand=True, padx=5)
        self.out = scrolledtext.ScrolledText(right, bg=WIN_WHITE, font=("Comic Sans MS", 10), bd=2, relief="sunken")
        self.out.pack(fill="both", expand=True)
        
        # --- BOTTOM INPUT ---
        bot = tk.Frame(main, bg=WIN_GREY, bd=2, relief="raised")
        bot.pack(fill="x", pady=5)
        tk.Label(bot, text=" INTENT > ", bg=WIN_GREY, font=("Comic Sans MS", 11, "bold")).pack(side="left")
        self.prompt = tk.Entry(bot, font=("Comic Sans MS", 11), bd=2, relief="sunken")
        self.prompt.pack(side="left", fill="x", expand=True, padx=5)
        self.prompt.bind("<Return>", self.run)
        self.btn = tk.Button(bot, text=" EXECUTE ", command=self.run, font=("Comic Sans MS", 10, "bold"), bg=WIN_GREY, bd=3, relief="raised")
        self.btn.pack(side="right", padx=5)

    def mk_entry(self, p, lbl, key, d):
        tk.Label(p, text=lbl, bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w")
        e = tk.Entry(p, font=("Comic Sans MS", 11), bg=WIN_WHITE, bd=2, relief="sunken")
        # Try to find key in root, then frontend, then default
        val = str(self.config.get(key, self.config.get("frontend", {}).get(key, d)))
        e.insert(0, val)
        e.pack(fill="x", padx=2)
        return e

    def log(self, t): self.out.insert(tk.END, t+"\n"); self.out.see(tk.END)
    
    def save(self):
        # --- THE FIX ---
        # Sync the UI values to the Root JSON keys used by the worker scripts
        self.config["model"] = self.ent_model.get()
        
        try:
            # Sync Trajectories to BOTH locations to be safe
            val_traj = int(self.ent_traj.get())
            self.config["n_paths"] = val_traj 
            self.config["frontend"]["num_trajectories"] = val_traj
            
            # Sync Temperature
            val_temp = float(self.ent_temp.get())
            self.config["temperature"] = val_temp
            
        except ValueError:
            messagebox.showerror("Error", "Trajectories must be Int, Insanity must be Float!")
            return

        self.config["frontend"]["storm_variant"] = self.var_var.get()
        
        backend.save_config(self.config)
        self.log(f">> CONFIG SAVED. (Traj: {val_traj}, Temp: {val_temp})")

    def run(self, e=None):
        p = self.prompt.get(); self.prompt.delete(0, tk.END)
        if not p: return
        self.btn.config(state="disabled", text=" BUSY ")
        self.log(f"\n>> USER: {p}")
        threading.Thread(target=self.proc, args=(p,)).start()

    def proc(self, p):
        self.save() # Auto-save ensures the worker script sees the new Temp/Traj
        cfg = backend.load_config() 
        out, err = backend.run_storm_process(cfg, p)
        self.root.after(0, lambda: self.done(out, err, p))

    def done(self, out, err, p):
        if err: self.log(f"ERROR: {err}")
        else:
            self.log("-"*40); self.log(out); self.log("-"*40)
            backend.commit_result(p, out)
            self.log(">> MEMORY UPDATED.")
        self.btn.config(state="normal", text=" EXECUTE ")

    def reset_mem(self):
        backend.clear_context()
        self.log("\n>> *** NEURALYZER FLASH ***")
        self.log(">> Short-term context wiped.")
        self.log(">> Long-term summary wiped.")

if __name__ == "__main__":
    r = tk.Tk(); r.withdraw()
    s = RetroSplash(r)
    r.after(3000, lambda: [s.destroy(), r.deiconify(), StormWin95App(r)])
    r.mainloop()