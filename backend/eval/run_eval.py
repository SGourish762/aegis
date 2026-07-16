"""Evaluation harness: run the detection engine against a labeled attack/
benign corpus and report precision, recall, F1, and false-positive rate.

Usage:
    python eval/run_eval.py

Reads every *.jsonl file under eval/corpus/ (each line: {"text", "label",
"source"}, label in {"attack", "benign"}), runs each sample through
app.detection.engine.screen, and scores it. A sample counts as a positive
detection if the verdict is "flag" or "block" (i.e. the engine did not
silently allow it) — see the README for why flag counts as a detection
rather than only block.

Writes a JSON summary to eval/results.json and prints a table to stdout.
"""

import json
import sys
from collections import Counter
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.detection.engine import screen  # noqa: E402

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
RESULTS_PATH = Path(__file__).resolve().parent / "results.json"


def load_corpus() -> list[dict]:
    samples = []
    for path in sorted(CORPUS_DIR.glob("*.jsonl")):
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                samples.append(json.loads(line))
    return samples


def evaluate(samples: list[dict]) -> dict:
    tp = fp = tn = fn = 0
    verdict_by_label: dict[str, Counter] = {"attack": Counter(), "benign": Counter()}

    for sample in samples:
        label = sample["label"]
        result = screen(sample["text"])
        verdict_by_label[label][result.verdict] += 1
        detected = result.verdict in ("flag", "block")

        if label == "attack" and detected:
            tp += 1
        elif label == "attack" and not detected:
            fn += 1
        elif label == "benign" and detected:
            fp += 1
        elif label == "benign" and not detected:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0

    return {
        "total_samples": len(samples),
        "attack_samples": sum(1 for s in samples if s["label"] == "attack"),
        "benign_samples": sum(1 for s in samples if s["label"] == "benign"),
        "positive_definition": "verdict in {flag, block}",
        "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
        "verdict_breakdown": {
            "attack": dict(verdict_by_label["attack"]),
            "benign": dict(verdict_by_label["benign"]),
        },
    }


def print_summary(results: dict) -> None:
    print(f"Samples: {results['total_samples']} "
          f"({results['attack_samples']} attack, {results['benign_samples']} benign)")
    print(f"Positive definition: {results['positive_definition']}")
    print()
    print(f"{'Metric':<22}{'Value':>10}")
    print("-" * 32)
    print(f"{'Precision':<22}{results['precision']:>10.4f}")
    print(f"{'Recall':<22}{results['recall']:>10.4f}")
    print(f"{'F1':<22}{results['f1']:>10.4f}")
    print(f"{'False positive rate':<22}{results['false_positive_rate']:>10.4f}")
    print()
    c = results["confusion"]
    print(f"Confusion: TP={c['tp']} FP={c['fp']} TN={c['tn']} FN={c['fn']}")
    print()
    print("Verdict breakdown:")
    print(f"  attack: {results['verdict_breakdown']['attack']}")
    print(f"  benign: {results['verdict_breakdown']['benign']}")


def main() -> None:
    samples = load_corpus()
    if not samples:
        print(f"No corpus files found under {CORPUS_DIR}", file=sys.stderr)
        sys.exit(1)

    results = evaluate(samples)
    print_summary(results)
    RESULTS_PATH.write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nWrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()
