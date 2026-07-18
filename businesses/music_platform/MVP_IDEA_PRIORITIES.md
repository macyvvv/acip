# Music Platform MVP Idea Priorities (Without Success-Rate Scoring)

## Decision

- Put "success-rate scoring" on hold for now.
- Prioritize features that work with small samples and still create immediate value.

## Phase 1 (0-30 days)

1. Core event flow
- Create event
- Join event
- Add song
- Claim part

2. Missing-part board
- Show which songs are blocked by missing required parts
- Let organizers filter by instrument and urgency

3. Organizer templates
- Ready-to-use templates for:
  - Recruiting post
  - Event rules
  - Day-of guidance

## Phase 2 (31-60 days)

1. Auto matching (rule based)
- When a required part is missing, notify users who:
  - marked the instrument in profile
  - are active in nearby areas
  - opted in for invitations

2. Rehearsal prep pack
- Per-song page with:
  - reference links
  - arrangement notes
  - role notes
  - checklist

3. Day-of run sheet
- Timeline style board for:
  - set order
  - setup and teardown windows
  - contact notes

## Phase 3 (61-90 days)

1. Community continuity
- Save event archive:
  - setlist
  - photos/notes
  - next-song candidates

2. Lightweight pro plan
- Paid organizer features:
  - advanced templates
  - bulk notifications
  - exportable run sheets

## Metrics That Work With Small Samples

1. Time to first fill
- Median time from event publish to first required-part claim.

2. Preparation completion rate
- Percentage of songs with rehearsal prep pack fully filled.

3. Organizer workload proxy
- Number of manual reminder messages per event.

4. Retention proxy
- Percentage of users who join another event within 30 days.

## Why This Order

- Immediate utility for organizers and participants
- Low dependency on large historical data
- Clear monetization path without ad-first strategy

## Additional Business Idea: Studio Suggest Engine

- Add a feature to suggest studio candidates based on event size and location.
- Inputs:
  - expected attendee scale (participant count and band composition)
  - preferred area or nearest station
  - time window and budget range
  - required equipment (drums, keyboard, amp type, etc.)
- Outputs:
  - ranked studio shortlist
  - estimated total cost and per-person split
  - travel convenience score (distance and transfer count)
  - booking friction score (availability, response speed, cancellation policy)

### Why It Is Strong As A Business Idea

- Solves a high-frequency organizer pain point that exists before every event.
- Works even with small internal samples by combining static studio data and user preferences.
- Can open affiliate or lead-generation revenue with studio partners.

### MVP Scope For This Feature

1. Manual+rule-based recommendation first
- Build a curated studio dataset for top target areas.
- Match by hard filters first (capacity, location, required equipment), then rank by convenience and price.

2. Organizer feedback loop
- Collect post-event rating on recommendation relevance.
- Use ratings to tune weights without requiring a large dataset.

3. Monetization test
- Free: basic top-3 recommendations
- Pro: expanded shortlist, price comparison, and booking checklist export

## Additional Business Idea: Auto Setlist Optimizer

- Add a feature that automatically builds a setlist from established songs and assigned performers.
- Goal: minimize total transition time while keeping performer load and audience flow reasonable.

### Is This Computation Feasible?

- Yes. This is feasible and practical.
- The core problem is scheduling and combinatorial optimization, not pure prediction.
- A good approach is:
  - estimate transition costs between songs
  - run an optimizer to choose the song order with minimum weighted cost under constraints

### Where Random Forest Fits

- Random Forest is useful for predicting transition time (for example, drum kit change probability and expected minutes).
- Random Forest is not the best tool to generate the final order directly.
- Recommended architecture:
  - Model A (prediction): Random Forest estimates transition cost by instrument-change pattern, venue type, and setup notes.
  - Model B (optimization): constraint solver (or heuristic search) outputs the best sequence.

### Example Cost Design

- vocal change only: low cost (for example 1 minute)
- guitar and bass swap: medium cost
- drum reconfiguration: high cost (for example up to 10 minutes)
- optional penalties:
  - same singer appears too many consecutive songs
  - long idle gaps for specific players
  - genre or tempo monotony for audience experience

### MVP Scope For This Feature

1. Rule-based cost matrix first
- Start with manual instrument-level transition costs.
- Generate order with greedy + local swap improvement.

2. Organizer controls
- Let organizers lock opening/closing songs and no-move songs.
- Provide priority mode toggle (minimum setup time vs balanced performer rotation).

3. Learning loop
- Record actual transition durations on event day.
- Train/update Random Forest periodically to replace manual estimates.
