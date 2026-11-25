# Validation notes: goodman-networks-flight-policy (wave 2 paid validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w2_2026-11-25/` (arm `full`, DeepSeek V4 Flash,
temperature 0, max_steps 6), plugin head 34ed190. Line numbers are lines of `src/plugin/data/policy.txt`.

## Result

20/24 valid (83.3%). Easy 5/5, boundary_twin 6/6, distractor 2/2, hidden_clause 2/2, multi_rule 4/4, refusal 1/2,
flag 0/3. Every run stopped on `answer`; none hit max_steps.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| thistle-bay | refusal | REFUSE, PERSONAL_TRAVEL_NOT_COVERED, NONE right; clause GENERAL_PHILOSOPHY, key INTRODUCTION / POLICY_ENFORCEMENT / SCOPE / TRAVEL_AUTHORIZATIONS | **grader defect** (narrow) | The reasoning quotes line 11 ("business travel is authorized only...") and names the next heading. General Philosophy (line 19) states the same ground: travel "on company business", and "employees suffer no financial loss nor realize any financial gain from such business travel"; a family holiday billed to the company is that gain. The key already accepts four sections for the same ground; refusing the one that defines covered travel fails a correct refusal. Q2: unaffected (the always-cheapest agent books). |
| vale-crocus | flag | BOOK United business ZL7S-BNLG, INTERNATIONAL_LONG_FLIGHT, EXECUTIVE_VP; key FLAG (either Chicago offer), UNCLEAR_POLICY_TEXT | model slip | It quoted line 647's "from the point of origin to the first destination point", wrote "Hmm ... let me reconsider", then took the per-segment reading as settled ("The international flight segment (the transatlantic leg) needs to exceed 6 hours") without weighing the origin-to-first-stop reading (Austin to Chicago, 160 minutes, coach). The ambiguity is real: the phrase only bites on connections, and every offer connects. Twins birch-quarry and lark-basin passed. |
| willow-shoal | flag | BOOK American nonstop AXEW-RNP9, ALTERNATE_ROUTE_WITHIN_MARGIN; key FLAG, UNCLEAR_POLICY_TEXT | model slip | It applied the first sentence of line 707 ($45 < $100) and never read the parenthesis "(i.e., the connecting flight would have added more than a 2-hour extension of travel time each way ...)"; the connection adds only 90 minutes. The second reading never appears in the reasoning. Twins hazel-rook and iris-spindle passed. |
| yarrow-fern | flag | BOOK TS6P-N2D4 (right offer), LOWEST_FARE, NONE; key FLAG, APPROVAL_REQUIRED, VICE_PRESIDENT or DIVISION_GENERAL_MANAGER | model slip | "Approval thresholds: fare is $241, within $1-$500, Manager approval. Director signed off, so fine." Table 2 (lines 369-407) is "the hierarchy of approvals required for travel expenses" (line 369), and the record's `trip_estimate_cents` is documented as "the whole trip's estimated travel expenses ..., the amount the trip's sign-off was asked for": $751, the VP/DGM tier. The model applied the table to the airfare instead. Twin quince-ridge ($750, Director, BOOK) passed with the same request text. |

**Are the three flag failures systematic?** No common scenario cause: one reading taken as settled after seeing the
phrase (vale-crocus), the qualifying parenthesis never read (willow-shoal), the table applied to the wrong amount
(yarrow-fern). In each the text and record are coherent and the twins pass. The model books rather than holds on
flags across plugins (Thornton 0/3 and NJC 0/4 on 2026-11-24), which is a model trait, not a defect here.

## Fix (one commit)

- `thistle-bay`: `GENERAL_PHILOSOPHY` added to the personal-travel refusal clauses in `src/plugin/rules.py` and
  `verifier/rules.py` (byte-identical), `tests/build_scenarios.py` (key and design note), the regenerated
  `src/plugin/data/scenarios/thistle-bay.json`, and the README row. Id unchanged; no other scenario takes this branch.
- No accept set was widened for a slip.

Always-cheapest baseline: 6/24 (25%) before and after (the agent books, so a refusal's clause set cannot change it).
Always-flag: at most 2, unchanged.

Checks at the fix commit: `uv run pytest -q` (204 passed), `uv run ruff check .`, `uv lock --check`,
`check_shared.py`, `tools/stock_verify.py` (24 scenarios, 0 failures), stock `nanoagent plugin inspect .` (exit 0).

## Re-run

- `thistle-bay` (grader fix; the paid answer now scores valid offline, so a re-run is optional confirmation).
- The three flags need no re-run for a fix; re-run only to measure slip variance.
