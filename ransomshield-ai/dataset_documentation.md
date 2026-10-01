# Benchmark Dataset Documentation

## Overview
This dataset (`benchmark_dataset.json`) contains synthetic, controlled OS-level telemetry traces designed to evaluate the semantic contextualization capabilities of Large Language Models (LLMs) and heuristic engines in detecting ransomware behaviors. 

It was constructed to isolate the analysis engine from the hypervisor layer, ensuring that the evaluation strictly measures analytical capabilities (precision, recall, MITRE ATT&CK mapping accuracy, and telemetry tamper detection) without introducing execution noise or variable boot times from physical sandbox infrastructure.

## Dataset Structure
The dataset consists of 100 behavioral traces:
*   **50 Benign Traces:** Normal administrative and user activities (e.g., file management, benign software execution).
*   **50 Malicious Traces:** Simulated ransomware behaviors explicitly designed around specific MITRE ATT&CK techniques:
    *   **T1490:** Inhibit System Recovery (e.g., `vssadmin delete shadows`)
    *   **T1486:** Data Encrypted for Impact
    *   **T1562:** Impair Defenses (e.g., clearing Windows Event Logs via `wevtutil`)

## JSON Schema Dictionary
The `benchmark_dataset.json` file contains a root `samples` array. Each object in the array represents a single execution trace with the following schema:

*   **`id`** *(string)*: A unique identifier for the simulated run.
*   **`ground_truth`** *(string)*: The true label of the trace, either `"BENIGN"` or `"MALICIOUS"`.
*   **`true_attck_techniques`** *(array of strings)*: For malicious traces, the exact MITRE ATT&CK technique IDs present in the events (e.g., `["T1490", "T1486", "T1562"]`). For benign traces, this is an empty array `[]`.
*   **`telemetry_tampered_ground_truth`** *(boolean)*: Indicates if the trace contains attempts to impair defenses or clear logs (T1562).
*   **`events`** *(array of objects)*: The chronological sequence of simulated OS telemetry events.
    *   **`event_type`** *(string)*: The category of the event (e.g., `"process_creation"`, `"file_modification"`).
    *   **`timestamp`** *(float)*: Epoch timestamp of the event.
    *   **`data`** *(object)*: Key-value pairs detailing the event (e.g., `command_line`, `file_path`, `process_name`).

## Usage
This dataset is intended to be injected directly into an analysis pipeline's ingestion layer. Systems can be evaluated on their ability to:
1. Perform binary classification (`BENIGN` vs `MALICIOUS`).
2. Correctly map the telemetry to the `true_attck_techniques` without hallucinating unsupported claims.
3. Successfully identify `telemetry_tampered_ground_truth` conditions where secondary evasion tactics are disguised among primary IOCs.
