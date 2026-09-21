---
name: experience-first
title: Experience First
description: "Apply when product, UX, or feature-scope tradeoffs come up. Choose the user's delight over implementation convenience; ship fewer polished features over more rough ones."
seats: [eng-lead, pm]
---
# Experience First

When implementation convenience conflicts with user delight, choose delight.

**Why:** Convenience is paid once by the builder; a rough experience is paid on every use by everyone downstream.

**The pattern:**
- **Justify every feature, control, and option.** What does not earn its place is cut.
- **Ship less, ship better.** A polished experience with three features beats a rough one with ten.
- **Prototype before committing.** Design decisions are cheaper in throwaway HTML than in production code.
- **Get the details right:** transitions, alignment, spacing, feedback, error states.
- **Tighten the core loop.** Every feature serves the central workflow or gets out of the way.

**Who the user is:** whoever consumes the work. For a UI, the end user. For a library or an internal API, the colleague who imports it. The engineer who maintains the code next is a user too. Weigh their experience the same way and explain impact from their perspective; those users are exactly the ones `BRIEF.md ## Done when — by perspective` names, so argue a tradeoff in the words of the perspective it affects.

Foundations serve the experience. `references/foundational-thinking.md` governs the *sequence* of work; this governs the *target*.
