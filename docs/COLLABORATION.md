# How we build Tasteprint together

Confirmed by the user on 2026-09-30. Applies to product, UI, data, ML, and project setup work. This is the project's collaboration standard, not a globally installed skill.

## 1. Explain completed work

After an implementation milestone, give a moderately detailed, plain-language handoff in the conversation. The user should understand what changed without reading the code or opening a document.

Cover:

- What was implemented, using Tasteprint's vocabulary: Discover, food choices, Your Tasteprint, personalized recommendations, MealMerge.
- What a person can now do and what happens to their choices or data. Describe the behavior, not just a list of files or libraries.
- What is still sample content, a simple rule, a proposal, or unimplemented. Especially distinguish a descriptive profile from a trained model.
- What was verified, any limitations, and how the user can try or judge the result.

Lead with the outcome. Explain necessary technical terms once in ordinary language. Include file links as supporting detail, not as a substitute for the explanation.

## 2. Discuss the next change

Present the next bounded milestone as a proposal. Explain what it would add to Tasteprint, why it is useful now, and what it leaves out. Give a recommendation with reasons and alternatives when they materially change the experience, effort, or deadline risk.

Ask focused questions and allow back-and-forth about what the user understands, agrees with, or wants changed. Reuse settled decisions rather than restarting the design interview. User disagreement is a reason to examine the trade-off together, not silently replace their choice or accept it without explaining relevant evidence.

Read-only inspection or research may inform the discussion. Clearly distinguish findings from implementation. A roadmap's sequence or a prior general request to build does not approve every subsequent milestone.

## 3. Establish the agreed scope

Before implementation, summarize the concrete outcome, included changes, important exclusions, and meaningful choices. Record approved scope in the relevant project document; leave unresolved options marked as proposals.

Proceed when the user clearly approves that scope or directly requests the specific change. An explicit request already authorizes its stated scope; avoid a redundant confirmation. When a proposal remains unresolved, end the turn with the decision needed and wait for the user's reply. Silence, a suggested option, or a deadline is not agreement.

Normal coding details and verification steps within the agreed scope can be handled independently. If implementation requires a material change to product behavior, data/model approach, dependencies with significant trade-offs, external access, or deadline scope, return to discussion before expanding the work.

## 4. Implement, verify, and hand back

Implement the agreed changes and give concise progress updates that connect the work to the agreed outcome. Verify in proportion to the change. Then return to step 1: explain the result and discuss—not automatically implement—the next milestone.

## ML conversations

Before an ML milestone, explain:

- The Tasteprint problem it solves: starting recommendations for a new person, learning from ratings, or finding a group compromise.
- What data goes in and what the user sees come out, using a concrete dish example where helpful.
- What we will train ourselves versus reuse, and what is just a hand-authored rule or baseline.
- How we will judge whether it works; explain metrics before presenting numbers.
- What decisions or actions the user needs to take, and what can stay a technical implementation detail.

Afterward report what was actually learned or measured and what remains uncertain. Keep preference, ranking score, and dietary safety distinct. Do not present planned experiments as completed results.

## Deadline-aware decisions

Use the deadline recorded in `PROJECT_BRIEF.md` to explain scope trade-offs. Treat cuts, priority changes, and optional experiments as decisions to agree on together. A tight deadline does not bypass this collaboration process.
