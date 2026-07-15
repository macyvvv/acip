# CHAT_LOG_CAPTURE_RESEARCH

## Conclusion
The most robust method for ACIP is to treat the official ChatGPT data export as the canonical source for chat logs, then import the exported archive into `platform/inbox/chat_logs/` through a repository-native importer.

This is the safest option because it is officially supported, durable across UI changes, and avoids scraping or policy-sensitive automation.

## Why manual copy-paste is rejected
- It is error-prone and non-deterministic.
- It loses structure, metadata, and provenance.
- It scales poorly as conversation volume grows.
- It forces Human to act as a transport layer, which conflicts with ACIP goals.

## Compared methods

| Method | Automation | Maintainability | Reliability | Security / Privacy Risk | Cost |
|---|---:|---:|---:|---:|---:|
| ChatGPT data export | Medium | High | High | Low | Low |
| Browser automation | High | Medium | Medium | Medium | Medium |
| Browser extension | High | Low | Medium | Medium-High | Medium |
| Shared-link scraping | Medium | Low | Low | High | Medium |
| Official API | Low / unavailable for ChatGPT web history export | High if available | N/A | Low | Low |

## Method notes

### ChatGPT data export
Official OpenAI help documents describe exporting ChatGPT history and data from settings, including shared link data in exports. This is the strongest source of truth for repository ingestion.

Pros:
- official and supportable
- preserves history in a structured archive
- lowest long-term maintenance burden

Cons:
- export initiation is not fully hands-free
- not a live stream

### Browser automation
Can automate the export click path and download handling.

Pros:
- reduces Human interaction
- can be integrated into a repeatable flow

Cons:
- brittle to UI changes
- may require explicit approvals or auth handling
- more maintenance than export-based ingestion alone

### Browser extension
Can capture conversations or export individual threads.

Pros:
- user-friendly
- can be convenient for ad hoc capture

Cons:
- third-party trust surface
- more fragile than official export
- harder to standardize across environments

### Shared-link scraping
Uses public or shared conversation links as input.

Pros:
- can capture a specific conversation quickly

Cons:
- privacy and policy risk
- incomplete history
- not a good repository-wide capture mechanism

### Official API
No official ChatGPT web-history API is exposed as a canonical export pathway in the public help materials reviewed for this research.

## Recommendation for ACIP
Use **official ChatGPT data export as the canonical capture method**.

Operationally, ACIP should:
1. request or trigger the export,
2. unpack the export locally,
3. normalize the conversations into `platform/inbox/chat_logs/`,
4. run `python platform/scripts/extract_knowledge.py`.

If later automation is needed, add browser automation only as a thin trigger around the official export flow, not as the SSOT.

## Next implementation EP
Create a **Chat Log Importer EP** that:
- reads ChatGPT export archives,
- extracts conversation text deterministically,
- writes normalized logs to `platform/inbox/chat_logs/`,
- preserves provenance metadata,
- deduplicates imports by conversation ID and export timestamp.

## Proposed input format
- ZIP export from ChatGPT settings
- optional folder containing `conversations.json` and related export files

## Expected output
- `platform/inbox/chat_logs/*.md`
- `platform/inbox/chat_logs/*.txt`
- knowledge extraction summary from `python platform/scripts/extract_knowledge.py`
