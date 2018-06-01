from app.util import reddit_util
import requests
import json

# To run tests, do "python -m tests"

entries = reddit_util.parse_post("8n1cs0")

scores = reddit_util.score_entries(entries)

for event, results in scores.items():
    print(event, ": ", results)
