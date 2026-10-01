import sys
import argparse
import statistics
from evaluation_benchmark import run_evaluation

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="../benchmark_dataset.json", help="Path to dataset")
    parser.add_argument("--runs", type=int, default=3, help="Number of runs")
    args = parser.parse_args()

    print(f"Executing {args.runs} runs for variance calculation...")
    sys.stdout.flush()

    metrics_keys = [
        "precision", "recall", "f1", "attck_acc", 
        "unsupported_claim_rate", "telemetry_tamper_detection", 
        "latency_ms", "cpu_overhead_percent", "memory_overhead_mb"
    ]

    base_results_list = {k: [] for k in metrics_keys}
    prop_results_list = {k: [] for k in metrics_keys}

    for i in range(args.runs):
        print(f"Run {i+1}/{args.runs}...")
        sys.stdout.flush()
        baseline = run_evaluation(args.dataset, use_genai=False, active_simulation=False)
        proposed = run_evaluation(args.dataset, use_genai=True, active_simulation=False)
        
        print(f"  -> Run {i+1} Proposed Metrics: ATT&CK Mapping={proposed['attck_acc']:.4f}, Tamper Detection={proposed['telemetry_tamper_detection']:.4f}, Latency={proposed['latency_ms']:.2f}ms, CPU={proposed['cpu_overhead_percent']:.4f}%")
        sys.stdout.flush()
        
        for k in metrics_keys:
            base_results_list[k].append(baseline[k])
            prop_results_list[k].append(proposed[k])

    print("\n" + "="*80)
    print("TABLE III: RESULT STRUCTURE (MEAN ± STD DEV)")
    print("="*80)
    print(f"{'Metric':<25} | {'Passive / Baseline':<25} | {'Proposed':<25}")
    print("-" * 80)

    display_map = [
        ("Detection precision", "precision"),
        ("Detection recall", "recall"),
        ("F1 score", "f1"),
        ("ATT&CK mapping accuracy", "attck_acc"),
        ("Unsupported-claim rate", "unsupported_claim_rate"),
        ("Telemetry tamper detection", "telemetry_tamper_detection"),
        ("Median latency (ms)", "latency_ms"),
        ("CPU overhead (%)", "cpu_overhead_percent"),
        ("Memory overhead (MB)", "memory_overhead_mb")
    ]

    for display_name, key in display_map:
        b_vals = base_results_list[key]
        p_vals = prop_results_list[key]

        b_mean = statistics.mean(b_vals)
        p_mean = statistics.mean(p_vals)
        
        b_std = statistics.stdev(b_vals) if len(b_vals) > 1 else 0.0
        p_std = statistics.stdev(p_vals) if len(p_vals) > 1 else 0.0

        b_str = f"{b_mean:.2f} ± {b_std:.2f}"
        p_str = f"{p_mean:.2f} ± {p_std:.2f}"

        print(f"{display_name:<25} | {b_str:<25} | {p_str:<25}")

if __name__ == '__main__':
    main()
