import asyncio
import os

class AsyncEngineV3:
    """
    Iteration 3: Async/Event-Driven Core.
    Focus: Responsiveness and Token Streaming.
    """
    def __init__(self):
        self.model = "qwen2.5:0.5b"

    async def list_models(self):
        """Async model listing."""
        print("[v3] Scanning models (async)...")
        proc = await asyncio.create_subprocess_exec(
            "ollama", "list",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        if proc.returncode == 0:
            return [l.split()[0] for l in stdout.decode().splitlines()[1:] if l.strip()]
        return []

    async def generate_stream(self, prompt, model=None):
        """Streams output from the inference engine."""
        target_model = model or self.model
        print(f"[v3] Opening stream: {target_model}")
        
        # Agnostic: In Phase 2, this would be a lookup for the specific CLI pattern
        proc = await asyncio.create_subprocess_exec(
            "ollama", "run", target_model, prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            # Yield tokens/lines as they arrive
            yield line.decode('utf-8').strip()

        await proc.wait()

async def main():
    eng = AsyncEngineV3()
    models = await eng.list_models()
    print("Models:", models)
    if models:
        prefix = f"[{models[0]}] "
        async for chunk in eng.generate_stream("Tell a 1-sentence joke.", models[0]):
            print(prefix + chunk)

if __name__ == "__main__":
    asyncio.run(main())
