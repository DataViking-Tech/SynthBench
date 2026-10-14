# Ensembles

An ensemble averages its members' per-question answer distributions with equal
weights and is scored like any other system (`synthbench ensemble`). Each
member set has its own slug (`--name`) and leaderboard row.

## How the complementary blends were chosen

Picking the highest-scoring models and checking the blend on the same
questions overstates the gain. The `complementary-*` blends were chosen this
way instead (`scripts/search-ensembles.py`, run 2026-10-14):

1. Candidates: the 30 current default systems on all four core datasets
   (newest scoring; no template, temperature or persona-pack variants; no
   claude-code harness).
2. Every 2-, 3- and 4-model blend (about 64,000) was scored on the **public**
   questions only.
3. Blends were picked from that public ranking and from how differently their
   members err. Every number below is on the **private holdout** questions,
   which played no part in choosing.

Two things predict whether a blend beats its best member:

- **Error direction.** Blends gain when members err in opposite directions
  (one over-picks an option another under-picks). Holding member quality
  fixed, each 0.1 drop in the mean correlation of members' signed errors
  adds about 3 Index points over the best member. The size of errors (JSD per
  question) is a weaker signal, because it mostly tracks questions that are
  hard for every model.
- **Balanced members.** One strong model with two weak ones does poorly; the
  spread of member quality is the strongest predictor of the gain.

The Althing persona makes models err alike: signed errors correlate at 0.63
between Althing systems and 0.49 between raw ones. A blend of three Althing
systems (`flash3-althing`, minted earlier) beat its best member by only 3
points on the private questions and was dropped.

## Held-out results

| Blend | Members | Private-question Index | Best member, private |
|---|---|---|---|
| `complementary-mid` | Haiku 5.5 (Althing), Llama 3.3 70B, Gemini 2.5 Flash-Lite | 40 | 17 |
| `complementary-top` | Haiku 5.5 (Althing), DeepSeek V4.1 Flash, Gemini 2.5 Flash-Lite | 43 | 31 |
| `complementary-4` | Qwen 3.8 Flash (Althing), Sonnet 4 (Althing), DeepSeek V4.1 Flash, Gemini 2.5 Flash-Lite | 46 | 32 |
| `flash3-raw` (top three raw models by score) | Qwen 3.8 Flash, DeepSeek V4.1 Flash, Gemini 3.5 Flash-Lite | 42 | 31 |
| Best single system | Qwen 3.8 Flash (Althing) | 32 | |

`complementary-mid` is three mid-table models that each score 12 to 17 on
their own. Gemini 2.5 Flash-Lite (raw) appears in most strong blends: its
errors are the least like the other systems', so it adds the most to a blend
despite a middling score of its own.

The leaderboard scores ensembles on all questions, public and private, like
every other row, so their published Index differs slightly from the private
numbers above.
