# Entry point: reads support tickets from sample_tickets.csv, calls the scorer for each one,
# writes scored output to scored_tickets.csv, and appends a run summary to metrics_log.csv.
import csv
import os
from datetime import datetime, timezone
from statistics import mean

from config import (
    ACCURACY_THRESHOLD,
    CLARITY_THRESHOLD,
    INPUT_CSV,
    METRICS_LOG_CSV,
    OUTPUT_CSV,
    TONE_THRESHOLD,
)
from scorer import score_response


def load_tickets(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_scored_tickets(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def append_metrics_log(path, summary):
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(summary)


def flag_reasons_for(score):
    reasons = []
    if score.tone < TONE_THRESHOLD:
        reasons.append("low_tone")
    if score.clarity < CLARITY_THRESHOLD:
        reasons.append("low_clarity")
    if score.accuracy < ACCURACY_THRESHOLD:
        reasons.append("low_accuracy")
    if score.safety_concern:
        reasons.append("safety_concern")
    if not score.action_appropriate:
        reasons.append("action_mismatch")
    return reasons


def main():
    rows = load_tickets(INPUT_CSV)

    scored_rows = []
    for row in rows:
        score = score_response(row)
        reasons = flag_reasons_for(score)
        scored_rows.append({
            **row,
            "tone_score": score.tone,
            "clarity_score": score.clarity,
            "accuracy_score": score.accuracy,
            "safety_concern": score.safety_concern,
            "action_appropriate": score.action_appropriate,
            "rationale": score.rationale,
            "flagged": bool(reasons),
            "flag_reasons": ", ".join(reasons),
        })

    fieldnames = list(rows[0].keys()) + [
        "tone_score",
        "clarity_score",
        "accuracy_score",
        "safety_concern",
        "action_appropriate",
        "rationale",
        "flagged",
        "flag_reasons",
    ]
    write_scored_tickets(OUTPUT_CSV, scored_rows, fieldnames)

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_tickets": len(scored_rows),
        "flagged_count": sum(1 for r in scored_rows if r["flagged"]),
        "safety_concern_count": sum(1 for r in scored_rows if r["safety_concern"]),
        "action_mismatch_count": sum(1 for r in scored_rows if not r["action_appropriate"]),
        "avg_tone": round(mean(r["tone_score"] for r in scored_rows), 2),
        "avg_clarity": round(mean(r["clarity_score"] for r in scored_rows), 2),
        "avg_accuracy": round(mean(r["accuracy_score"] for r in scored_rows), 2),
    }
    append_metrics_log(METRICS_LOG_CSV, summary)

    print(f"Scored {summary['total_tickets']} tickets -> {OUTPUT_CSV}")
    print(
        f"Flagged for review: {summary['flagged_count']} "
        f"(safety concerns: {summary['safety_concern_count']}, "
        f"action mismatches: {summary['action_mismatch_count']})"
    )
    print(
        f"Averages - tone: {summary['avg_tone']}, "
        f"clarity: {summary['avg_clarity']}, "
        f"accuracy: {summary['avg_accuracy']}"
    )


if __name__ == "__main__":
    main()
