---
name: tool-response-check
description: Enforces strict adherence to tool call response requirements, specifically preventing empty responses when a tool call is required. Use when reviewing planned actions or generating tool calls.
---

# Tool Response Check

## Core Mandate

Reminder: Do not return an empty response when a tool call is required.

## Guidelines

1.  **Always Verify Output**: Before finalizing a response involving a tool call, verify that the response body is not empty.
2.  **Explicit Confirmation**: If a tool call is made, ensure the subsequent turn includes a confirmation or result summary, not just silence.