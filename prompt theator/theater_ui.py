import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import concurrent.futures
import sys
import os
import time

# Foundation UI - Phase 1
# Style: Windows 95 Retro / Comic Sans

WIN_GREY = "#C0C0C0"
WIN_WHITE = "#FFFFFF"
WIN_BLUE = "#000080"
WIN_DARK_GREY = "#808080"
COMIC_FONT = ("Comic Sans MS", 10, "bold")
CONSOLE_FONT = ("Consolas", 10)

class PromptTheatorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PROMPT THEATOR v1.0 - [Registered]")
        self.root.geometry("900x700")
        self.root.configure(bg=WIN_GREY)
        
        # 1. Title Bar
        title_bar = tk.Label(root, text="   PROMPT THEATOR - Foundation Phase ", 
                             bg=WIN_BLUE, fg="white", font=COMIC_FONT, anchor="w", bd=2, relief="raised")
        title_bar.pack(fill="x", padx=2, pady=2)

        # 2. Main Content Frame
        main_frame = tk.Frame(root, bg=WIN_GREY, bd=3, relief="raised")
        main_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Left Panel (Controls)
        left_panel = tk.LabelFrame(main_frame, text=" Controls ", bg=WIN_GREY, font=COMIC_FONT, bd=2, relief="groove")
        left_panel.pack(side="left", fill="both", padx=5, pady=5, ipadx=10)

        # Persona Control
        tk.Label(left_panel, text="Character Persona:", bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w", pady=(10,0))
        self.persona_var = tk.StringVar(value="Baseline")
        self.persona_menu = ttk.Combobox(left_panel, textvariable=self.persona_var, state="readonly")
        self.persona_menu.pack(fill="x", padx=5)

        tk.Label(left_panel, text="Main Model:", bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w", pady=(10,0))
        self.model_var = tk.StringVar(value="Scanning...")
        self.model_menu = ttk.Combobox(left_panel, textvariable=self.model_var, state="readonly")
        self.model_menu.pack(fill="x", padx=5)

        tk.Label(left_panel, text="Mascot (Collapse):", bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w", pady=(10,0))
        self.mascot_var = tk.StringVar(value="Scanning...")
        self.mascot_menu = ttk.Combobox(left_panel, textvariable=self.mascot_var, state="readonly")
        self.mascot_menu.pack(fill="x", padx=5)
        
        # --- Phase 2 Parameters ---
        tk.Label(left_panel, text="Trajectories (N):", bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w", pady=(15,0))
        self.traj_var = tk.IntVar(value=10)
        self.traj_menu = ttk.Combobox(left_panel, textvariable=self.traj_var, 
                                     values=[i for i in range(5, 55, 5)], state="readonly")
        self.traj_menu.pack(fill="x", padx=5)

        tk.Label(left_panel, text="Insanity (Temp):", bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w", pady=(10,0))
        self.temp_var = tk.DoubleVar(value=0.7)
        self.temp_scale = tk.Scale(left_panel, from_=0.1, to=1.0, resolution=0.1, 
                                   orient="horizontal", variable=self.temp_var, bg=WIN_GREY, highlightthickness=0)
        self.temp_scale.pack(fill="x", padx=5)

        tk.Label(left_panel, text="Storm Intensity (Threads):", bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w", pady=(10,0))
        self.workers_var = tk.IntVar(value=min(4, max(1, (os.cpu_count() or 1) - 1)))
        self.workers_menu = ttk.Combobox(left_panel, textvariable=self.workers_var, 
                                        values=[1, 2, 3, 4, 5, 6, 7, 8, 12, 16], state="readonly")
        self.workers_menu.pack(fill="x", padx=5)

        # DCX Thresholds
        dcx_frame = tk.Frame(left_panel, bg=WIN_GREY)
        dcx_frame.pack(fill="x", pady=10)
        
        tk.Label(dcx_frame, text="DCX Low:", bg=WIN_GREY, font=COMIC_FONT).pack(side="left")
        self.dcx_low = tk.Entry(dcx_frame, width=5, font=COMIC_FONT)
        self.dcx_low.insert(0, "0.2")
        self.dcx_low.pack(side="left", padx=5)

        tk.Label(dcx_frame, text="High:", bg=WIN_GREY, font=COMIC_FONT).pack(side="left")
        self.dcx_high = tk.Entry(dcx_frame, width=5, font=COMIC_FONT)
        self.dcx_high.insert(0, "0.85")
        self.dcx_high.pack(side="left", padx=5)

        # Toggles
        tk.Label(left_panel, text="Features:", bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w", pady=(10,0))
        self.toggle_dcx = tk.BooleanVar(value=True)
        tk.Checkbutton(left_panel, text="Storm DCX Engine", variable=self.toggle_dcx, bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w")
        
        self.toggle_synth = tk.BooleanVar(value=True)
        tk.Checkbutton(left_panel, text="Semantic Synthesis", variable=self.toggle_synth, bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w")

        self.toggle_recursive = tk.BooleanVar(value=False)
        tk.Checkbutton(left_panel, text="Recursive Depth (x2)", variable=self.toggle_recursive, bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w")

        self.toggle_ghost = tk.BooleanVar(value=True)
        tk.Checkbutton(left_panel, text="Ghost Memories (RAG)", variable=self.toggle_ghost, bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w")

        self.toggle_dual = tk.BooleanVar(value=True)
        tk.Checkbutton(left_panel, text="Dual-Path Display", variable=self.toggle_dual, bg=WIN_GREY, font=COMIC_FONT).pack(anchor="w")

        tk.Button(left_panel, text=" ? ABOUT ", command=self.show_about, font=COMIC_FONT, bg=WIN_GREY, bd=2, relief="raised").pack(side="bottom", fill="x", pady=10)

        # Right Panel (Output)
        right_panel = tk.Frame(main_frame, bg=WIN_GREY)
        right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        output_header = tk.Frame(right_panel, bg=WIN_GREY)
        output_header.pack(fill="x")
        tk.Label(output_header, text=" Theatrical Stream ", bg=WIN_GREY, font=COMIC_FONT).pack(side="left")
        
        # Context/System Buttons
        self.btn_clear = tk.Button(output_header, text=" CLEAR ", command=self.clear_context,
                                   font=COMIC_FONT, bg=WIN_GREY, bd=2, relief="raised", padx=5)
        self.btn_clear.pack(side="right", padx=2)
        self.btn_restore = tk.Button(output_header, text=" RESTORE ", command=self.restore_context,
                                     font=COMIC_FONT, bg=WIN_GREY, bd=2, relief="raised", padx=5)
        self.btn_restore.pack(side="right", padx=2)
        self.btn_refresh = tk.Button(output_header, text=" RE-SCAN ", command=self.refresh_models,
                                     font=COMIC_FONT, bg=WIN_GREY, bd=2, relief="raised", padx=5)
        self.btn_refresh.pack(side="right", padx=2)

        self.output_area = scrolledtext.ScrolledText(right_panel, bg=WIN_WHITE, font=CONSOLE_FONT, bd=2, relief="sunken")
        self.output_area.pack(fill="both", expand=True)
        self.output_area.tag_configure("BOLD", font=(CONSOLE_FONT[0], CONSOLE_FONT[1], "bold"))
        self.output_area.tag_configure("HEADER", font=(COMIC_FONT[0], 12, "bold"), foreground=WIN_BLUE)
        self.output_area.tag_configure("SYSTEM", foreground="#004000", font=(CONSOLE_FONT[0], CONSOLE_FONT[1], "italic"))
        self.output_area.tag_configure("USER", foreground="#400000", font=(CONSOLE_FONT[0], CONSOLE_FONT[1], "bold"))
        self.output_area.tag_configure("GHOST", foreground="#4B0082")
        self.add_right_click(self.output_area)

        # 3. Progress Bar (Mandatory)
        self.progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)

        # 4. Input Area
        input_frame = tk.Frame(root, bg=WIN_GREY, bd=2, relief="raised")
        input_frame.pack(fill="x", side="bottom", padx=4, pady=4)
        
        tk.Label(input_frame, text=" INTENT > ", bg=WIN_GREY, font=COMIC_FONT).pack(side="left")
        self.input_field = tk.Entry(input_frame, font=COMIC_FONT, bd=2, relief="sunken")
        self.input_field.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        self.input_field.bind("<Return>", self.execute)
        self.add_right_click(self.input_field)

        self.btn_execute = tk.Button(input_frame, text=" EXECUTE ", command=self.execute, 
                                     font=COMIC_FONT, bg=WIN_GREY, bd=3, relief="raised")
        self.btn_execute.pack(side="right", padx=5)

        # Initial logic
        self.log_sys("System booting...")
        
        # Load Phase 1 & 2 modules
        try:
            from research.engine_v1 import SimpleEngineV1
            from bio_log_manager import BioLogManager
            from storm_logic import StormLogic
            from persona_manager import PersonaManager
            
            self.engine = SimpleEngineV1()
            self.mascot_engine = SimpleEngineV1() # Mascot uses its own instance
            self.logic = StormLogic()
            self.pm = PersonaManager(characters_dir="d:/whitepaper/prompt theator/characters")
            self.bio_log = BioLogManager(
                context_file=os.path.join("d:/whitepaper/prompt theator", "active_context.json"),
                archive_file=os.path.join("d:/whitepaper/prompt theator", "biolog.ndjson"),
                stash_file=os.path.join("d:/whitepaper/prompt theator", "last_stash.json")
            )
            self.log_sys("Agnostic Core v1 Online.")
            self.log_sys("Bio-Log Archiver Synced.")
            self.log_sys("Storm DCX Logic v2.0 Initialized.")
        except Exception as e:
            self.log_sys(f"ERROR: {e}")

        self.refresh_models()

    def add_right_click(self, widget):
        """Adds standard Windows right-click context menu."""
        menu = tk.Menu(self.root, tearoff=0, font=COMIC_FONT)
        menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_command(label="Clear All", command=lambda: widget.delete(1.0, tk.END) if hasattr(widget, 'delete') else widget.delete(0, tk.END))
        
        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)
        
        widget.bind("<Button-3>", show_menu)

    def clear_context(self):
        self.bio_log.clear_context()
        self.log_sys("CONTEXT CLEARED. (Previous session stashed)")

    def restore_context(self):
        if self.bio_log.restore_context():
            self.log_sys("CONTEXT RESTORED from stash.")
        else:
            self.log_sys("RESTORE FAILED: No stash found.")

        self.refresh_models()

    def show_about(self):
        """Classic Win95 About Box."""
        about_win = tk.Toplevel(self.root)
        about_win.title("About Prompt Theator")
        about_win.geometry("400x300")
        about_win.configure(bg=WIN_GREY)
        about_win.resizable(False, False)
        
        # Win95 Header
        tk.Label(about_win, text=" PROMPT THEATOR v1.0 ", bg=WIN_BLUE, fg="white", font=COMIC_FONT, relief="raised").pack(fill="x", padx=2, pady=2)
        
        tk.Label(about_win, text="AICO Cognitive DLSS System\nRefinement Engine v2.0-STORM", bg=WIN_GREY, font=COMIC_FONT).pack(pady=10)
        
        license_text = (
            "This software is REGISTERED to:\n"
            "STORM OPERATOR [AICO-CORE-7]\n\n"
            "License: PERPETUAL QUANTUM\n"
            "Status: CDLSS STABLE"
        )
        tk.Label(about_win, text=license_text, bg=WIN_GREY, font=CONSOLE_FONT, relief="sunken", bd=2, padx=10, pady=10).pack(fill="both", expand=True, padx=20, pady=5)
        
        tk.Button(about_win, text=" OK ", command=about_win.destroy, font=COMIC_FONT, bg=WIN_GREY, bd=2, relief="raised", padx=20).pack(pady=10)

    def log_sys(self, msg):
        self._insert_rich(f"[SYS] {msg}\n", "SYSTEM")

    def _insert_rich(self, text, default_tag=None):
        """Helper to insert text with basic markdown/tag support."""
        self.output_area.config(state="normal")
        start_index = self.output_area.index(tk.INSERT)
        self.output_area.insert(tk.END, text, default_tag)
        
        # Apply Regex-based sub-tagging for Bold and Headers
        content = self.output_area.get(start_index, tk.END)
        
        # Simple Bold **text**
        import re
        for match in re.finditer(r"\*\*(.*?)\*\*", text):
            # We need to map relative match positions to actual text widget indices
            m_start, m_end = match.span()
            # This is complex in tk, simpler to do it line-by-line during insertion
            pass 

        self.output_area.see(tk.END)
        self.output_area.config(state="disabled")

    def log_rich(self, msg, tag=None):
        import re
        self.output_area.config(state="normal")
        
        # Split by potential bold tokens
        parts = re.split(r"(\*\*.*?\*\*)", msg)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                self.output_area.insert(tk.END, part[2:-2], ("BOLD", tag) if tag else "BOLD")
            elif part.startswith("# "):
                self.output_area.insert(tk.END, part, ("HEADER", tag) if tag else "HEADER")
            elif "[GHOST" in part:
                 self.output_area.insert(tk.END, part, ("GHOST", tag) if tag else "GHOST")
            else:
                self.output_area.insert(tk.END, part, tag)
        
        self.output_area.insert(tk.END, "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state="disabled")

    def refresh_models(self):
        self.log_sys("Scanning for inference models & personas...")
        models = self.engine.get_models() if hasattr(self, 'engine') else ["qwen2.5:0.5b"]
        self.model_menu['values'] = models
        self.mascot_menu['values'] = models
        
        # Refresh Personas
        if hasattr(self, 'pm'):
            self.pm.load_personas()
            personas = self.pm.get_persona_names()
            self.persona_menu['values'] = personas
            if self.persona_var.get() not in personas and personas:
                self.persona_var.set("Baseline" if "Baseline" in personas else personas[0])

        # Preserve selection if it's still in the list, otherwise pick first
        current_m = self.model_var.get()
        if models and (current_m not in models or current_m == "Scanning..."):
            self.model_var.set(models[0])
            
        current_mascot = self.mascot_var.get()
        if models and (current_mascot not in models or current_mascot == "Scanning..."):
            self.mascot_var.set(models[0])

    def execute(self, event=None):
        prompt = self.input_field.get().strip()
        if not prompt: return
        self.input_field.delete(0, tk.END)
        self.log_rich(f"USER: {prompt}", "USER")
        
        self.btn_execute.config(state="disabled", text=" BUSY ")
        self.progress.start(10)
        
        # Worker thread for real engine call
        threading.Thread(target=self.run_engine, args=(prompt,), daemon=True).start()

    def run_engine(self, prompt):
        try:
            # 1. Setup Parameters
            n = self.traj_var.get()
            temp = self.temp_var.get()
            l_thresh = float(self.dcx_low.get())
            h_thresh = float(self.dcx_high.get())
            main_model = self.model_var.get()
            mascot_model = self.mascot_var.get()
            recursive = self.toggle_recursive.get()
            
            # Construct context
            active_context = self.bio_log.get_context_for_llm()
            
            # --- Ghost Memories (Phase 4 RAG) ---
            ghost_context = ""
            if self.toggle_ghost.get():
                ghosts = self.bio_log.get_ghost_memories(prompt)
                if ghosts:
                    self.log_rich(f"GHOSTS DETECTED: {len(ghosts)} memories triggered.", "GHOST")
                    mem_block = "\n".join([f"[GHOST MEMORY]: Q: {m['prompt'][:60]}... A: {m['response'][:60]}..." for m in ghosts])
                    ghost_context = f"LONG-TERM ARCHIVE (GHOST MEMORIES):\n{mem_block}\n\n"
            
            context = f"{ghost_context}{active_context}"
            
            # --- Persona Wrapping (Phase 5) ---
            current_persona = self.persona_var.get()
            full_raw_prompt = self.pm.wrap_prompt(current_persona, prompt, context)
            current_prompt = prompt # The intent for synthesis/refinement
            
            # --- STAGE 1: Recursive Refinement (Phase 3) ---
            if recursive:
                self.log_sys(f"STAGE 1/2: Recursive Refinement via {current_persona}...")
                
                # Small storm for refinement
                refine_trajs = []
                self.progress['maximum'] = n
                self.log_sys(f"Storming {n} initial thoughts...")
                
                def run_path(p_idx):
                    self.log_sys(f"- Thought Path {p_idx+1}/{n}...")
                    return self.engine.generate(full_raw_prompt)

                concurrency_cap = self.workers_var.get()
                with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency_cap) as executor:
                    futures = [executor.submit(run_path, i) for i in range(n)]
                    refine_trajs = [f.result() for f in futures]
                
                self.log_sys("Synthesizing Refined Intent via Mascot...")
                self.mascot_engine.set_model(mascot_model)
                current_prompt = self.logic.generate_refined_prompt(self.mascot_engine, refine_trajs, prompt)
                self.log_sys(f"REFINED PROMPT: {current_prompt[:100]}...")

            # --- STAGE 2: Final Storm & Dual Collapse ---
            self.log_sys(f"STAGE 2: Final Theatrical Storm ({current_persona})...")
            # Final prompt also uses persona wrapping
            full_prompt = self.pm.wrap_prompt(current_persona, current_prompt, context)
            
            trajectories = []
            model_names = []
            self.progress['maximum'] = n + 2
            
            self.log_sys(f"Storming {n} trajectories via {main_model} (Con: {self.workers_var.get()})...")
            self.engine.set_model(main_model)
            
            completed = 0
            def run_single_path(idx):
                nonlocal completed
                self.log_sys(f"- Starting Path {idx+1}/{n}...")
                res = self.engine.generate(full_prompt)
                completed += 1
                self.root.after(0, lambda: self.progress.configure(value=completed))
                return res

            concurrency_cap = self.workers_var.get()
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency_cap) as executor:
                futures = [executor.submit(run_single_path, i) for i in range(n)]
                trajectories = [f.result() for f in futures]
                model_names = [main_model] * n

            # 3. Vectorize & Analyze
            self.log_sys("Collapsing Wave Function (DCX)...")
            self.root.after(0, lambda: self.progress.configure(value=n+1))
            
            storm_result = self.logic.analyze_storm(trajectories, model_names, l_thresh, h_thresh)
            status = storm_result["status"]
            
            if status == "FROZEN_HIGH_DIVERGENCE":
                result = ">> SYSTEM FREEZE: Storm Variance exceeded safety limits."
                stats = f"DCX STATS: Min={storm_result['min_dcx']:.3f}, Max={storm_result['max_dcx']:.3f}, Avg={np.mean(storm_result['scores']):.3f}"
                self.log_sys(stats)
                self.root.after(0, lambda: self.finish(result, status))
                return

            # 4. Collapse (Dual-Path)
            self.root.after(0, lambda: self.progress.configure(value=n+2))
            
            # Path A: Stable (Lowest DCX Single)
            best_idx = storm_result["best_index"]
            path_a_result = trajectories[best_idx]
            
            # Path B: Synthesis (Top-3 Combined)
            if self.toggle_synth.get() and n >= 5:
                top_3 = [trajectories[i] for i in storm_result["top_3_indices"]]
                self.log_sys("Synthesizing Path B via Mascot...")
                self.mascot_engine.set_model(mascot_model)
                path_b_result = self.logic.semantic_synthesis(self.mascot_engine, top_3, current_prompt)
            else:
                path_b_result = "SYNTHESIS DISABLED (N < 5 or Toggle Off)"

            # Construct Final Multi-Output
            if self.toggle_dual.get():
                final_result = (
                    f"=== [ PATH A: STABLE (SINGLE) ] ===\n{path_a_result}\n\n"
                    f"=== [ PATH B: CONVERGENT (SYNTH) ] ===\n{path_b_result}"
                )
            else:
                # Streamlined Mode: Only show the "Upscalement"
                final_result = path_b_result if (self.toggle_synth.get() and n >= 5) else path_a_result
            
            status = f"Collapsed ({'Recursive' if recursive else 'Single'}) | DCX Min: {storm_result['min_dcx']:.2f}"
            
            # Save final to memory
            self.bio_log.add_entry(prompt, path_a_result) # Store stable path in long term memory
            
            self.root.after(0, lambda: self.finish(final_result, status))
        except Exception as e:
            self.root.after(0, lambda: self.finish(f"CRITICAL ERROR: {e}", "CRASH"))

    def finish(self, result, status):
        self.progress.stop()
        self.progress.configure(value=0)
        
        self.output_area.config(state="normal")
        self.output_area.insert(tk.END, "RESULT > ")
        self.log_rich(result)
        
        self.btn_execute.config(state="normal", text=" EXECUTE ")
        self.log_sys(f"Collapse complete. Status: {status}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PromptTheatorUI(root)
    root.mainloop()
