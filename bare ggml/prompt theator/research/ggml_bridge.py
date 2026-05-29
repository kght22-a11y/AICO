import ctypes
import os
import sys

class GGMLBridge:
    def __init__(self, lib_path=None):
        if lib_path is None:
            # Try to auto-detect based on platform
            ext = ".dll" if sys.platform == "win32" else ".so"
            # Look in the ggml build directory or local dir
            possible_paths = [
                os.path.join(os.path.dirname(__file__), "..", "..", "ggml-master", "build", "bin", "Release", f"cdlss_engine{ext}"),
                os.path.join(os.path.dirname(__file__), "..", "..", "ggml-master", "build", "bin", f"cdlss_engine{ext}"),
                os.path.join(os.path.dirname(__file__), "..", "..", "ggml-master", "build", "examples", "cdlss_engine", "Release", f"cdlss_engine{ext}"),
                os.path.join(os.path.dirname(__file__), "..", "..", "ggml-master", "build", "examples", "cdlss_engine", f"libcdlss_engine{ext}"),
                os.path.join(os.path.dirname(__file__), f"cdlss_engine{ext}")
            ]
            for p in possible_paths:
                p = os.path.abspath(p)
                if os.path.exists(p):
                    lib_path = p
                    break
        
        self.lib_path = lib_path
        self.lib = None
        
        if self.lib_path and os.path.exists(self.lib_path):
            try:
                # On Windows with Python 3.8+, we must explicitly add the DLL directory 
                # so Windows can find dependent DLLs like ggml.dll, ggml-base.dll, etc.
                if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
                    os.add_dll_directory(os.path.dirname(self.lib_path))
                
                self.lib = ctypes.CDLL(self.lib_path)
                # Define signature: const char* run_cdlss_inference(const char*, const char*, int, float, float, int)
                self.lib.run_cdlss_inference.argtypes = [
                    ctypes.c_char_p, # model_path
                    ctypes.c_char_p, # prompt
                    ctypes.c_int,    # num_trajectories
                    ctypes.c_float,  # dcx_threshold
                    ctypes.c_float,  # temp
                    ctypes.c_int     # n_predict
                ]
                self.lib.run_cdlss_inference.restype = ctypes.c_char_p
            except Exception as e:
                print(f"Error loading GGML CDLSS library: {e}")
        else:
            print("Warning: GGML CDLSS library not found. It must be built via CMake first.")

    def run_inference(self, model_path, prompt, num_trajectories=10, dcx_threshold=0.85, temp=0.7, n_predict=256):
        if not self.lib:
            # Fallback mock for UI testing if lib isn't built yet
            return f"[MOCK GGML CDLSS RESULT]\nPrompt: {prompt[:50]}...\nTrajectories: {num_trajectories}\nDCX Thresh: {dcx_threshold}\n(Compile cdlss_engine shared library to see real output)"
            
        try:
            m_path_b = model_path.encode('utf-8')
            prompt_b = prompt.encode('utf-8')
            
            result_b = self.lib.run_cdlss_inference(
                m_path_b,
                prompt_b,
                num_trajectories,
                dcx_threshold,
                temp,
                n_predict
            )
            
            if result_b:
                return result_b.decode('utf-8')
            return ""
        except Exception as e:
            return f"ERROR in GGML C-Call: {e}"

if __name__ == "__main__":
    # Test
    bridge = GGMLBridge()
    res = bridge.run_inference("dummy_model.gguf", "Hello world")
    print("Result:", res)
