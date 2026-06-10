import csv
import matplotlib.pyplot as plt
import argparse
import os

def render_map(csv_path):
    print(f"Reading {csv_path}...")
    x, y, c = [], [], []
    model_name = "Unknown"
    
    prompts = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            x.append(float(row['x']))
            y.append(float(row['y']))
            prompt_idx = int(row['prompt_index'])
            c.append(prompt_idx)
            if prompt_idx not in prompts:
                prompts[prompt_idx] = row['prompt_text']
            
            if model_name == "Unknown" and row.get('model'):
                model_name = row['model']
                
    if not x:
        print("No data found in CSV.")
        return None
        
    fig, ax = plt.subplots(figsize=(15, 10))
    s_val = 15 if len(x) < 1000 else 8
    alpha_val = 0.6 if len(x) < 1000 else 0.4
    
    scatter = ax.scatter(x, y, c=c, cmap='tab20', alpha=alpha_val, s=s_val)
    ax.set_title(f"Idle Topography (Model: {model_name}, Trajectories: {len(x)})")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("PCA Dimension 1")
    ax.set_ylabel("PCA Dimension 2")
    
    # Legend
    sorted_prompt_indices = sorted(prompts.keys())
    labels_str = [f"P{idx}: {prompts[idx][:30]}..." for idx in sorted_prompt_indices]
    
    handles, _ = scatter.legend_elements()
    num_items = min(len(handles), len(labels_str))
    
    fig.subplots_adjust(bottom=0.2) 
    fig.legend(handles[:num_items], labels_str[:num_items], loc="lower center", ncol=min(4, len(sorted_prompt_indices)), fontsize='small')
    
    out_file = csv_path.replace(".csv", "_rendered.png")
    plt.savefig(out_file, dpi=150)
    print(f"Plot saved to {out_file}")
    
    return out_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render map picture from idle mapper CSV coordinates")
    parser.add_argument("csv_path", help="Path to the map CSV file")
    args = parser.parse_args()
    
    if os.path.exists(args.csv_path):
        out = render_map(args.csv_path)
        if out and os.name == 'nt':
            os.startfile(out)  # Auto-open on Windows
    else:
        print(f"File not found: {args.csv_path}")
