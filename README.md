# RansomShield-AI: GenAI-Augmented Ransomware Detection Framework

RansomShield-AI is an advanced, post-execution ransomware analysis and detection framework. It bridges the gap between traditional heuristic detection and deep semantic analysis by integrating a Local Large Language Model (Qwen2 0.5b via Ollama) to contextualize system telemetry, map behaviors to the MITRE ATT&CK framework, and detect evasion tactics like telemetry tampering.

## Core Architecture

The system is built on a modern, decoupled architecture:
1. **Hypervisor-Based Sandbox Orchestrator:** A Python-based orchestrator (`services/sandbox_orchestrator`) that interfaces directly with VirtualBox to automate the isolation, execution, and containment of malware samples. It ensures a sterile environment by actively restoring `clean_state` snapshots before every run.
2. **Out-of-Band Telemetry Agent:** A host-side network monitor (`agents/host_side`) built with `scapy` that captures network traffic (DNS, TCP connections) without relying on in-guest agents that malware could tamper with.
3. **GenAI Analysis Engine:** A backend service that ingests telemetry logs and feeds them through a locally hosted, highly quantized LLM to analyze semantic intent, eliminating false positives caused by benign system administration tasks.
4. **Interactive Web UI:** A Next.js dashboard for uploading samples, triggering sandbox runs, and visualizing the LLM's threat analysis and ATT&CK mappings in real-time.

## Evaluation and Performance

In a controlled benchmark using a synthetic dataset of 100 behavioral traces (50 benign, 50 malicious), the GenAI-augmented framework demonstrated significant advantages over passive baselines:
* **ATT&CK Mapping:** Successfully mapped 51% of malicious traces to exact MITRE ATT&CK techniques with a 0.00% unsupported-claim rate (zero hallucinations).
* **Tamper Detection:** Successfully detected 83% of simulated T1562 (Impair Defenses) events, such as event log clearing, which traditional baselines miss.
* **Overhead:** Added a negligible 0.28% CPU overhead, proving that small-parameter local LLMs can provide deep semantic analysis without requiring datacenter-scale GPU clusters.

## Setup Instructions

### Prerequisites
* **VirtualBox:** Installed on the host machine with a Windows 10/11 VM configured with a `clean_state` snapshot.
* **Ollama:** Installed and serving the `qwen2:0.5b` model locally.
* **Python 3.12+** & **Node.js**

### Quick Start
1. Download the repository from the anonymous link:
   `https://anonymous.4open.science/r/ransomware-detection-8432`
   (Unzip and navigate into the `ransomware-detection` directory).
2. Start the Ollama server:
   ```powershell
   .\start_ollama.ps1
   ```
3. Launch the API and Web Dashboard:
   ```powershell
   .\run.ps1
   ```

## Disclaimer
This project is for educational and research purposes only. Always execute malware in strictly isolated, host-only network environments. The authors are not responsible for accidental network escapes or data loss.
