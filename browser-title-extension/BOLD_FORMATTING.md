# Bold Title Formatting - Pattern-Based Configuration

## Overview
The extension uses a configurable list of patterns to determine what parts of tab titles should be bold. Everything is non-bold by default except for substrings that match patterns in the configuration file.

## How It Works

### Configuration File: `bold-patterns.json`
Edit this file to add or remove patterns that should be bold:

```json
{
  "boldPatterns": [
    "InA-Event-Operation",
    "InA-Event-Operations",
    "InA-Event-InaEventOperationsConsum",
    "InA-Event-PutMeasurementValueProce",
    "InA-Forwarder",
    "Estimation-Worker"
  ]
}
```

### Pattern Matching
- The code searches for the **longest matching pattern** in each resource name
- When a pattern is found, only that substring is wrapped with `**bold markers**`
- Everything else (prefixes, suffixes, service tags) stays non-bold

### Title Rendering (tab-navigator.js)
The tab navigator parses `**markers**` and renders them as bold HTML with `font-weight: 700`

## Examples

**SQS Queue:**
- Input: `Prod-ME-InA-Event-Operation-Queue.fifo`
- Pattern: `InA-Event-Operation` (from config)
- Output: `[SQS] Prod-ME-**InA-Event-Operation**-Queue.fifo`
- Visual: [SQS] Prod-ME-**InA-Event-Operation**-Queue.fifo

**Lambda Function:**
- Input: `Dev-ME-Estimation-WorkerLambda`
- Pattern: `Estimation-Worker` (from config)
- Output: `[Lambda] Dev-ME-**Estimation-Worker**Lambda`
- Visual: [Lambda] Dev-ME-**Estimation-Worker**Lambda

**Complex Name:**
- Input: `Prod-ME-Service-InA-Event-InaEventOperationsConsum-58YrwwE7kXII`
- Pattern: `InA-Event-InaEventOperationsConsum` (from config)
- Output: `[SQS] Prod-ME-Service-**InA-Event-InaEventOperationsConsum**-58YrwwE7kXII`
- Visual: [SQS] Prod-ME-Service-**InA-Event-InaEventOperationsConsum**-58YrwwE7kXII

## How to Add New Patterns

1. Open `bold-patterns.json`
2. Add your pattern to the `boldPatterns` array
3. Reload the extension or refresh the tab

**Tips:**
- Use the exact substring you want to be bold
- Longer patterns take precedence over shorter ones
- Patterns are case-sensitive
- You can include hyphens, underscores, and other characters

## Benefits

1. **Simple & Maintainable**: Just edit a JSON file, no code changes needed
2. **Precise Control**: You decide exactly what's bold
3. **No False Positives**: Only patterns you specify are bolded
4. **Easy to Update**: Add patterns as you encounter new resource names
5. **Consistent**: Same pattern always produces same result

## JIRA/Confluence

JIRA and Confluence titles currently use full title bolding:
- `[JIRA] **Issue Title**`
- `[Confluence] **Page Title**`

You can add specific JIRA patterns to the config if you want selective bolding.

## Testing
The file `test-bold.html` can be updated to test your patterns locally.
