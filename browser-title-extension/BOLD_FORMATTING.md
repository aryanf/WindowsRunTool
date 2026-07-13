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
- The tab navigator searches for the **longest matching pattern** in each tab title
- When a pattern is found, only that substring is rendered bold in the navigator list
- Everything else (prefixes, suffixes, service tags) stays non-bold
- **Browser tab titles remain clean** — no markers or formatting in the actual title bar

### Architecture
- `content.js` sets clean tab titles without any formatting markers
- `tab-navigator.js` loads `bold-patterns.json` and applies bold formatting only in the navigator UI
- Bold patterns are cached after first load for performance

## Examples

**SQS Queue:**
- Tab title: `[SQS] Prod-ME-InA-Event-Operation-Queue.fifo`
- Pattern: `InA-Event-Operation` (from config)
- Navigator display: [SQS] Prod-ME-**InA-Event-Operation**-Queue.fifo

**Lambda Function:**
- Tab title: `[Lambda] Dev-ME-Estimation-WorkerLambda`
- Pattern: `Estimation-Worker` (from config)
- Navigator display: [Lambda] Dev-ME-**Estimation-Worker**Lambda

**Complex Name:**
- Tab title: `[SQS] Prod-ME-Service-InA-Event-InaEventOperationsConsum-58YrwwE7kXII`
- Pattern: `InA-Event-InaEventOperationsConsum` (from config)
- Navigator display: [SQS] Prod-ME-Service-**InA-Event-InaEventOperationsConsum**-58YrwwE7kXII

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
