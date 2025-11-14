import json, os
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader, PdfWriter

os.makedirs("plots", exist_ok=True)

files = {
    "notejam": "./results/notejam_metrics_summary.json",
    "url": "./results/url_shortener_metrics_summary.json",
    "todo": "./results/todo_cli_metrics_summary.json"
}

data = {}
for k, p in files.items():
    with open(p) as f:
        data[k] = json.load(f)

projects = ["Notejam", "URL-Shortener", "Todo-CLI"]

# Set global font size
plt.rcParams.update({
    "font.size": 16,
    "axes.titlesize": 18,
    "axes.labelsize": 16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "legend.fontsize": 14,
})

def crop_pdf(in_path, out_path, margin=20):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages:
        box = page.mediabox
        box.lower_left = (box.lower_left[0] + margin, box.lower_left[1] + margin)
        box.upper_right = (box.upper_right[0] - margin, box.upper_right[1] - margin)
        page.mediabox = box
        writer.add_page(page)
    with open(out_path, "wb") as f:
        writer.write(f)

# =======================
# 1. SLOC
# =======================
sloc_vals = [
    data["notejam"]["sloc_summary"]["source_lines"],
    data["url"]["sloc_summary"]["source_lines"],
    data["todo"]["sloc_summary"]["source_lines"],
]

plt.figure(figsize=(7, 3.5))
plt.bar(projects, sloc_vals)
plt.ylabel("Source Lines of Code")
plt.title("SLOC Comparison Across Codebases")
plt.tight_layout()
path = "plots/sloc.pdf"
plt.savefig(path)
plt.close()

# =======================
# 2. Cyclomatic Complexity
# =======================
avg_cc = [
    data["notejam"]["cyclomatic_summary"]["average_complexity"],
    data["url"]["cyclomatic_summary"]["average_complexity"],
    data["todo"]["cyclomatic_summary"]["average_complexity"],
]
max_cc = [
    data["notejam"]["cyclomatic_summary"]["max_complexity"],
    data["url"]["cyclomatic_summary"]["max_complexity"],
    data["todo"]["cyclomatic_summary"]["max_complexity"],
]

plt.figure(figsize=(7, 3.5))
plt.plot(projects, avg_cc, marker='o', label="Average CC", linewidth=3)
plt.plot(projects, max_cc, marker='o', label="Max CC", linewidth=3)
plt.ylabel("Cyclomatic Complexity")
plt.title("Cyclomatic Complexity Comparison")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
path = "plots/cyclomatic.pdf"
plt.savefig(path)
plt.close()

# =======================
# 3. Halstead Volume + Effort
# =======================
vol = [
    data["notejam"]["halstead_summary"]["average_volume"],
    data["url"]["halstead_summary"]["average_volume"],
    data["todo"]["halstead_summary"]["average_volume"],
]
eff = [
    data["notejam"]["halstead_summary"]["total_effort"],
    data["url"]["halstead_summary"]["total_effort"],
    data["todo"]["halstead_summary"]["total_effort"],
]

plt.figure(figsize=(7, 3.5))
ax1 = plt.gca()

# Volume bar
bars = ax1.bar(projects, vol, alpha=0.7, label="Volume")
ax1.set_ylabel("Average Halstead Volume")
ax1.set_title("Halstead Volume and Effort")

# Effort line
ax2 = ax1.twinx()
line = ax2.plot(projects, eff, marker="o", linestyle="--", color="black", linewidth=3, label="Effort")
ax2.set_ylabel("Total Effort (log scale)")
ax2.set_yscale("log")

# Merge legends
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles1 + handles2, labels1 + labels2, loc="upper left")

plt.tight_layout()
path = "plots/halstead_volume_effort.pdf"
plt.savefig(path)
plt.close()

# =======================
# 4. Live Variables
# =======================
live = [
    data["notejam"]["dataflow_summary"]["average_live_variables"],
    data["url"]["dataflow_summary"]["average_live_variables"],
    data["todo"]["dataflow_summary"]["average_live_variables"],
]

plt.figure(figsize=(7, 3.5))
plt.bar(projects, live)
plt.ylabel("Average Live Variables")
plt.title("Live Variables Comparison")
plt.tight_layout()
path = "plots/live_vars.pdf"
plt.savefig(path)
plt.close()

print("Plots generated in ./plots")
