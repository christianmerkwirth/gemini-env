# Prompt Optimization Challenge: Strict JSON Extraction for Small Models

Small models (e.g., Gemma-7B, Llama-3-8B) frequently struggle with strict formatting constraints. While they are often capable of understanding the content, they tend to include conversational filler like "Sure, here's the JSON you requested:" or "I hope this information is helpful!", which immediately breaks automated JSON parsers.

## The Goal
Your objective is to optimize a **single prompt** that forces a small model (specifically Gemma 3 4B) to extract structured data from "messy" unstructured text and output **ONLY** a valid, parseable JSON object.

## The Task
Given a messy text snippet (e.g., an incident report, product review, or customer feedback), extract the following entities:
1. **Name**: The name of the person involved (String).
2. **Date**: The date mentioned (String, formatted as YYYY-MM-DD).
3. **Severity Level**: One of: `Low`, `Medium`, `High`, `Critical`.
4. **Cost**: The dollar amount mentioned (Float).

### Example Input
"Look, it was a mess. John Doe reported it on 2023-10-12. The server room flooded. We are looking at a High severity issue here. Total damages are around $1500.50. I hope this helps."

### Example Correct Output
```json
{
  "Name": "John Doe",
  "Date": "2023-10-12",
  "Severity Level": "High",
  "Cost": 1500.50
}
```

## Constraints
- **ONLY JSON**: The output must be strictly a single, valid JSON object. No pre-amble, no post-amble, no markdown code blocks (unless the prompt forces the model to include them and the parser is robust, but the evaluator expects raw JSON).
- **No Cheating**: Your prompt should be general enough to work across all 50-100 test cases provided in `input.txt`.

## Scoring (0 to 100)
- **+1 point** for every correct final answer (Exact match of JSON values against the ground truth).
- **-0.5 points** for formatting failures (If the output is not a valid JSON object or contains any conversational filler).

## Strategy Insights
Evolutionary optimization is particularly effective here because it can discover non-obvious "hacks" that influence the model's generation, such as:
- Using specific negative constraints (e.g., "NEVER START WITH 'HERE IS'").
- Appending structural hints (e.g., ending the prompt with `\n\n{`).
- Using ALL-CAPS commands or specific delimiter patterns.
