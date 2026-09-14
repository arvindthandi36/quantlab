# Information boundaries

The threat model is the application user/agent API, not a hostile owner inspecting Python
memory or reading their own imported CSV. The local backend necessarily stores the file.
A user who previously viewed the dataset cannot be made uninformed by software.

Historical storage is immutable. Only `prefix(index)` and a public state projection feed
charts, risk, causal models, Explain, what-if and Tutor. Public chart buffers retain at most
300 revealed bars; their axes are calculated from those returned values, never future extrema.
Live provenance omits complete-file hashes, future end dates and total stored row counts.
A full hash would itself violate strict future-mutation equality despite revealing no direct price.

The invariant is: given the same valid metadata, history through t and actions through t,
any valid replacement of observations after t leaves all current public state unchanged.
Dedicated tests mutate **every future OHLC value, volume and timestamp** for one and two
instruments, multiple t and different mutations. They compare whole public fingerprints,
orders/action digests, VaR/ES, regression/z-score, explanation and public Tutor questions,
and isolated current-position risk. No incomplete/failing reconciliation is repaired.

Complete journals and full-file identity metadata require an ended frame. Explicit ended
research is a separate analysis and cannot feed a previous live decision. Historical mode
has no latent value. It can explain the recorded movement and its accounting; prices alone
do not establish the real-market cause. Unavailable quotes, options and risk measures stay unavailable.

Hidden scenarios use a server-selected key and seed. Supplying a known key/seed to the hidden
browser endpoint is rejected. The public allowlist excludes actual configuration, seed,
process type, future shock schedule and hidden flow parameters. Historical and hidden contexts
are dispatched to their environment-specific Explain/Tutor builders, which receive public DTOs.
Old standalone lab endpoints are blocked while an external environment is selected, preventing
an unrelated synthetic account from masquerading as the selected market.

Public prices, displayed depth, current option quotes/IV, account fills and causal estimates
remain visible: a consequence is evidence, even if it helps a user infer a regime. The
scenario library is public; the selected entry is hidden. Some engines have few candidate
regimes, so engine capabilities can narrow guesses. This is educational information hiding,
not cryptographic concealment or a statistically blind experiment.

Reveal requires an explicit action at the ended frame. Replaying a hidden scenario starts
with hidden public frames again, despite the user now knowing more. Revealed configuration
is not a live quiz input. Tutor awards evidence only for submitted answers and rejects a
question if its public context changed. Environment interview questions currently use the
same immediate-feedback grader; this is not an examination-security system.

The environment protocol is a software boundary, not a process sandbox. Python library
callers can deliberately access private attributes. No live broker, external paid feed or
real order path is present.
