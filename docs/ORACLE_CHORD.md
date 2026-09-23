# The Oracle Chord — Semantics

When multiple LLMs probe the same lore, the chord carries the load.

## Per-worker scores

Each worker returns:
- `composite` (0-1): mean of three voices
- `doctrine_anchor` (0-1): alignment with 5 bedrock doctrines
- `canon_worthy` (0-1): canon-worthy form
- `distinct_voice` (0-1): voice distinctiveness
- `doctrines_hit`: list of doctrines the lore anchors to
- `reasoning`: worker's explanation

## Chord aggregation

```
chord_composite = mean(worker.composite for worker in workers)
chord_doctrine_anchor = mean(worker.doctrine_anchor)
chord_canon_worthy = mean(worker.canon_worthy)
chord_distinct_voice = mean(worker.distinct_voice)

consensus_promoted = ALL(worker.composite >= 0.7 for worker in workers)
majority_promoted = SUM(worker.composite >= 0.7) > len(workers) / 2
variance = VAR(worker.composite for worker in workers)
```

## What "consensus" means

A canon cell is **canonical-consensus** when ALL workers in the chord
agree on promotion (composite >= 0.7). This is the strongest form of
canon: every voice in the chord says "this is canon."

## What "majority" means

A canon cell is **majority-promoted** when the majority of workers
promote it. This is a weaker form: most voices say "this is canon," but
not all. Useful for borderline cases where some workers are more
restrictive than others.

## What variance means

`variance` measures disagreement. High variance = workers have very
different opinions. Low variance = workers agree.

A canon cell with composite 0.85 but variance 0.04 is more reliable than
one with composite 0.85 but variance 0.10. The chord is more trustworthy
when workers agree.

## License

MIT — Casey / SuperInstance, Sept 23, 2026
