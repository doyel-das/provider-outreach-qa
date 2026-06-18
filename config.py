# Central configuration: model name, file paths, and numeric score thresholds used by main.py.
# ANTHROPIC_API_KEY is read automatically from the environment by anthropic.Anthropic().
MODEL = "claude-opus-4-8"

INPUT_CSV = "sample_tickets.csv"
OUTPUT_CSV = "scored_tickets.csv"
METRICS_LOG_CSV = "metrics_log.csv"

# AI-drafted responses scoring below any of these thresholds (on a 1-5 scale) get flagged for review.
TONE_THRESHOLD = 3
CLARITY_THRESHOLD = 3
ACCURACY_THRESHOLD = 3
