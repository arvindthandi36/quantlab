# Phase 1 review for Arvind

Status: retained for repetition. Arvind approved progression to Phase 2 without
claiming independent mastery of these questions. Explain your reasoning; uncertainty is useful evidence.
Start from first principles. These questions progress from mechanics to model
criticism; there is no score based on reading time or generated code.

1. **Limit versus execution price.** An ask offers 4 units at £100.02. You submit
   a buy limit for 3 units at £100.05. What trades and what remains? Why isn't
   £100.05 necessarily the execution price?
2. **Price before time.** A submits 3 sell units at £100.03. Later B submits 2
   sell units at £100.02. A market buyer requests 4 units. List the fills in order
   and calculate the volume-weighted average price.
3. **Quantity accounting.** An empty book receives a sell limit for 7 units and
   then a buy market order for 10. What happens to each quantity? Verify
   accepted order-units = twice traded volume + resting + cancelled.
4. **Data structures.** Two orders share a price. The older one partially fills.
   Why should its remainder keep its place, and how do our data structures support
   that while still letting us cancel the second order directly?
5. **Model criticism.** All matching tests pass and the book has a positive spread.
   Why does neither fact establish that a market-making strategy will be profitable?
   Name two missing mechanisms we will need to model.

Review procedure: identify which part of an answer is sound; if needed, give a
focused hint and allow another attempt before explaining the full result. Record
evidence in `LEARNING_LOG.md`. Do not infer mastery from the guided prediction
already answered. Phase 2 requires Arvind's review and agreement to proceed.
