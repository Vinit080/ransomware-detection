import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_box(ax, x, y, width, height, text, facecolor='white', edgecolor='black', linestyle='-'):
    rect = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor=edgecolor, facecolor=facecolor, linestyle=linestyle)
    ax.add_patch(rect)
    ax.text(x + width/2, y + height/2, text, horizontalalignment='center', verticalalignment='center', fontsize=11, fontweight='bold', wrap=True)

def draw_arrow(ax, x1, y1, x2, y2, text=""):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(facecolor='black', edgecolor='black', width=2, headwidth=10, shrink=0.05))
    if text:
        # calculate midpoint
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        ax.text(mx, my+0.2, text, horizontalalignment='center', fontsize=9, backgroundcolor='white')

fig, ax = plt.subplots(figsize=(12, 8))

# Orchestration
draw_box(ax, 0.5, 7, 3, 1.5, "Hypervisor\nOrchestrator\n(Kali Linux)", facecolor='#ffe6e6')
draw_box(ax, 0.5, 5, 3, 1.5, "Adversarial\nStimuli\n(Metasploit)", facecolor='#ffe6e6')

# Guest
draw_box(ax, 4.5, 6, 3, 2.5, "Windows Sandbox\nGuest\n(VirtualBox)", facecolor='#e6f2ff', linestyle='--')

# Host Collection
draw_box(ax, 4.5, 3, 3, 1.5, "Network Capture Agent\n(Scapy)", facecolor='#e6ffe6')
draw_box(ax, 4.5, 1, 3, 1.5, "Behavioral Event Collector\n(Python)", facecolor='#e6ffe6')

# Interpretation
draw_box(ax, 8.5, 3.5, 3, 1.5, "Telemetry Summarization\n& Formatting", facecolor='#f2e6ff')
draw_box(ax, 8.5, 6, 3, 1.5, "Qwen2 0.5B Local LLM\n(via Ollama)", facecolor='#f2e6ff')

# Reporting
draw_box(ax, 8.5, 1, 3, 1.5, "Next.js Dashboard\nNode.js Reporting", facecolor='#ffffe6')

# Arrows
draw_arrow(ax, 3.5, 7.75, 4.5, 7.75, "Controls / Snapshots")
draw_arrow(ax, 3.5, 5.75, 4.5, 7.25, "Injects Malware")

draw_arrow(ax, 6, 6, 6, 4.5, "Network Traffic")
draw_arrow(ax, 6, 6, 6, 2.5, "OS Events")

draw_arrow(ax, 7.5, 3.75, 8.5, 3.75, "")
draw_arrow(ax, 7.5, 1.75, 8.5, 3.75, "JSON Event Stream")

draw_arrow(ax, 10, 5, 10, 6, "Compressed Prompt")
draw_arrow(ax, 11.5, 6.75, 12, 6.75, "") # Dummy to connect back down
draw_arrow(ax, 10, 6, 10, 7.5, "")
draw_arrow(ax, 10, 6.75, 10, 2.5, "")
ax.annotate('', xy=(10, 2.5), xytext=(10, 6),
            arrowprops=dict(facecolor='black', edgecolor='black', width=2, headwidth=10, shrink=0.05))
# A bit messy, let's just do a direct arrow
# clear previous arrows for the last one
ax.cla()
ax.set_xlim(0, 12)
ax.set_ylim(0, 9)
ax.axis('off')

# Redraw clean
draw_box(ax, 0.5, 6.5, 3, 1.5, "Hypervisor\nOrchestrator\n(Kali Linux)", facecolor='#ffe6e6')
draw_box(ax, 0.5, 4.5, 3, 1.5, "Adversarial\nStimuli\n(Metasploit)", facecolor='#ffe6e6')

draw_box(ax, 4.5, 5.5, 3, 2.5, "Windows Sandbox\nGuest\n(VirtualBox)", facecolor='#e6f2ff', linestyle='--')

draw_box(ax, 4.5, 3, 3, 1.5, "Network Capture Agent\n(Scapy)", facecolor='#e6ffe6')
draw_box(ax, 4.5, 1, 3, 1.5, "Behavioral Event\nCollector (Python)", facecolor='#e6ffe6')

draw_box(ax, 8.5, 3, 3, 1.5, "Telemetry Summarization\n& Formatting", facecolor='#f2e6ff')
draw_box(ax, 8.5, 6, 3, 1.5, "Qwen2 0.5B Local LLM\n(via Ollama)", facecolor='#f2e6ff')
draw_box(ax, 8.5, 0.5, 3, 1.5, "Interactive Dashboard\n(Next.js / Node.js)", facecolor='#ffffe6')

draw_arrow(ax, 3.5, 7.25, 4.5, 7.25, "Controls")
draw_arrow(ax, 3.5, 5.25, 4.5, 6.75, "Injects")

draw_arrow(ax, 6, 5.5, 6, 4.5, "")
draw_arrow(ax, 5.5, 5.5, 5.5, 2.5, "")

draw_arrow(ax, 7.5, 3.75, 8.5, 3.75, "")
draw_arrow(ax, 7.5, 1.75, 8.5, 3.75, "JSON Stream")

draw_arrow(ax, 10, 4.5, 10, 6, "Prompt")
draw_arrow(ax, 10.5, 6, 10.5, 2, "ATT&CK Mappings")

plt.tight_layout()
plt.savefig(r'E:\Ransomware Det\Figure1_Architecture.png', dpi=300, bbox_inches='tight')
print("Saved Figure1_Architecture.png")
