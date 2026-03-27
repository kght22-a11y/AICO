# Idle Topography Runner

`idle_topography_runner.py` is a long-running data collector for model topography work.

## What it does

- Rotates through available Ollama models continuously.
- Collects exactly `N` trajectories per model (`N=1000` by default).
- Logs every trajectory as append-only NDJSON with prompt, seed, model digest, response text, hashes, and timing.
- Generates map artifacts **only** when a model reaches the full target count.
- If interrupted early (Ctrl+C), raw logs are kept but no map is generated for the partial model.

## Run

```bash
python "prompt theator/research/idle_topography_runner.py"
```

Optional flags:

```bash
python "prompt theator/research/idle_topography_runner.py" \
  --models "qwen2.5:0.5b,qwen3-coder:30b" \
  --trajectories-per-model 1000 \
  --num-predict 96 \
  --temperature 0.8
```

## Output layout

- `idle_runs/<run_id>/run_manifest.json`
- `idle_runs/<run_id>/raw/<model>.ndjson`
- `idle_runs/<run_id>/models/<model>_manifest.json`
- `idle_runs/<run_id>/maps/<model>_map.csv`
- `idle_runs/<run_id>/maps/<model>_map_summary.json`
- `idle_runs/<run_id>/run_end.json`

## Notes

- Requires a local Ollama server (`http://localhost:11434` by default).
- Uses deterministic hash embeddings + PCA for dependency-light map generation.
