#!/usr/bin/env python3
"""Build the GSS aggregated CSV the ``gss`` dataset adapter expects.

Downloads a single-year General Social Survey STATA release from NORC
(public domain, https://gss.norc.org), aggregates a curated set of core
attitude items into per-option counts, and writes the CSV consumed by
``synthbench.datasets.gss.GSSDataset``:

    <data-dir>/raw/gss_aggregated.csv    (question_id, question_text,
                                          year, option, count)

Design decisions (reviewable here rather than buried in a notebook):

* **Source**: the official NORC single-year release zip. The 2024 file is
  ~5 MB and contains ``GSS2024.dta`` plus the release codebook.
* **Weights**: counts are the sum of the NORC-recommended post-stratified
  nonresponse-adjusted person weight (``wtssnrps``, falling back to
  ``wtssps``) so the published ``human_distribution`` estimates the US
  adult population rather than the raw respondent pool. Pass
  ``--unweighted`` for raw respondent counts (matches the codebook's
  unweighted frequency tables exactly).
* **Options**: NORC's own value labels, verbatim (including volunteered
  categories like ``"(vol.)"`` labels), plus the explicit nonresponse
  categories ``"don't know"`` and ``"refused"`` where respondents actually
  gave them. Shipping DK/refused as first-class options mirrors the
  OpinionsQA / GlobalOpinionQA convention, gives models the same "out"
  humans had, and feeds ``extract_human_refusal_rate`` real refusal mass.
  Purely administrative codes (iap = not asked on this ballot, "skipped on
  web", "no answer", "not imputable", ...) are dropped.
* **Discriminative-power screen**: items whose ground-truth distribution
  is within Jensen-Shannon divergence ``0.03`` of the uniform distribution
  are excluded. A uniform-random null agent already reproduces those items
  almost perfectly, so they carry no signal about synthetic-respondent
  quality and would inflate the benchmark's random-baseline floor (CI
  enforces random-baseline SPS < 0.80 — see
  ``docs/baseline-floors-log.md``).
* **Question text**: the exact item wording from the GSS 2024 Codebook
  (Release 3a). Items that upstream phrases as part of a battery (the
  abortion, national-spending, confidence, and free-speech series) are
  composed with their codebook stem so each prompt is a standalone
  question.

Requires: ``pip install pandas pyreadstat`` (not part of synthbench's
runtime dependencies — this is an offline ingestion tool).

Usage:
    python scripts/ingest-gss.py                     # 2024, weighted
    python scripts/ingest-gss.py --year 2022
    python scripts/ingest-gss.py --dta /path/GSS2024.dta
    python scripts/ingest-gss.py --unweighted
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

_NORC_ZIP_URL = (
    "https://gss.norc.org/content/dam/gss/get-the-data/documents/stata/{year}_stata.zip"
)

_WEIGHT_PREFERENCE = ("wtssnrps", "wtssps")

# Battery stems, from the GSS 2024 Codebook (Release 3a).
_STEM_AB = (
    "Please tell me whether or not you think it should be possible for a "
    "pregnant woman to obtain a legal abortion "
)
_STEM_NAT = (
    "We are faced with many problems in this country, none of which can be "
    "solved easily or inexpensively. Are we spending too much, too little, "
    "or about the right amount on "
)
_STEM_CON = (
    "I am going to name an institution in this country. As far as the people "
    "running this institution are concerned, would you say you have a great "
    "deal of confidence, only some confidence, or hardly any confidence at "
    "all in "
)
_STEM_ATH = "Consider somebody who is against all churches and religion. "
_STEM_SASD = (
    "Please indicate whether you strongly agree, agree, disagree, or "
    "strongly disagree with the following statement: "
)

# Curated core items: GSS mnemonic -> full standalone question wording.
# Wordings follow the GSS 2024 Codebook (Release 3a) section index; battery
# items are composed with the stems above. Options come from NORC's value
# labels at aggregation time and are validated against the data.
QUESTION_TEXTS: dict[str, str] = {
    # ── Well-being, social trust, personal situation ─────────────────
    "HAPPY": (
        "Taken all together, how would you say things are these days--would "
        "you say that you are very happy, pretty happy, or not too happy?"
    ),
    "HEALTH": (
        "Would you say your own health, in general, is excellent, good, fair, or poor?"
    ),
    "LIFE": "In general, do you find life exciting, pretty routine, or dull?",
    "TRUST": (
        "Generally speaking, would you say that most people can be trusted "
        "or that you can't be too careful in dealing with people?"
    ),
    "FAIR": (
        "Do you think most people would try to take advantage of you if "
        "they got a chance, or would they try to be fair?"
    ),
    "HELPFUL": (
        "Would you say that most of the time people try to be helpful, or "
        "that they are mostly just looking out for themselves?"
    ),
    "SATFIN": (
        "We are interested in how people are getting along financially "
        "these days. So far as you and your family are concerned, would you "
        "say that you are pretty well satisfied with your present financial "
        "situation, more or less satisfied, or not satisfied at all?"
    ),
    "FINRELA": (
        "Compared with American families in general, would you say your "
        "family income is far below average, below average, average, above "
        "average, or far above average?"
    ),
    "CLASS": (
        "If you were asked to use one of four names for your social class, "
        "which would you say you belong in: the lower class, the working "
        "class, the middle class, or the upper class?"
    ),
    "GETAHEAD": (
        "Some people say that people get ahead by their own hard work; "
        "others say that lucky breaks or help from other people are more "
        "important. Which do you think is most important?"
    ),
    # ── Crime, guns, courts, civic policy ────────────────────────────
    "GUNLAW": (
        "Would you favor or oppose a law which would require a person to "
        "obtain a police permit before he or she could buy a gun?"
    ),
    "CAPPUN": (
        "Do you favor or oppose the death penalty for persons convicted of murder?"
    ),
    "GRASS": "Do you think the use of marijuana should be made legal or not?",
    "COURTS": (
        "In general, do you think the courts in this area deal too harshly "
        "or not harshly enough with criminals?"
    ),
    "TAX": (
        "Do you consider the amount of federal income tax which you have to "
        "pay as too high, about right, or too low?"
    ),
    "OWNGUN": ("Do you happen to have in your home or garage any guns or revolvers?"),
    # ── Politics ─────────────────────────────────────────────────────
    "POLVIEWS": (
        "I'm going to show you a seven-point scale on which the political "
        "views that people might hold are arranged from extremely "
        "liberal--point 1--to extremely conservative--point 7. Where would "
        "you place yourself on this scale?"
    ),
    "PARTYID": (
        "Generally speaking, do you usually think of yourself as a "
        "Republican, Democrat, Independent, or what?"
    ),
    # ── Gender roles ─────────────────────────────────────────────────
    "FEPOL": (
        "Tell me if you agree or disagree with this statement: Most men are "
        "better suited emotionally for politics than are most women."
    ),
    "FEFAM": _STEM_SASD
    + (
        "It is much better for everyone involved if the man is the achiever "
        "outside the home and the woman takes care of the home and family."
    ),
    "FECHLD": _STEM_SASD
    + (
        "A working mother can establish just as warm and secure a "
        "relationship with her children as a mother who does not work."
    ),
    "FEPRESCH": _STEM_SASD
    + "A preschool child is likely to suffer if his or her mother works.",
    # ── Religion ─────────────────────────────────────────────────────
    "ATTEND": "How often do you attend religious services?",
    "POSTLIFE": "Do you believe there is a life after death?",
    "BIBLE": (
        "Which of these statements comes closest to describing your "
        "feelings about the Bible? The Bible is the actual word of God and "
        "is to be taken literally, word for word; the Bible is the inspired "
        "word of God but not everything in it should be taken literally, "
        "word for word; or the Bible is an ancient book of fables, legends, "
        "history, and moral precepts recorded by men."
    ),
    "GOD": (
        "Which statement comes closest to expressing what you believe about "
        "God? I don't believe in God; I don't know whether there is a God "
        "and I don't believe there is any way to find out; I don't believe "
        "in a personal God, but I do believe in a Higher Power of some "
        "kind; I find myself believing in God some of the time, but not at "
        "others; while I have doubts, I feel that I do believe in God; or I "
        "know God really exists and I have no doubts about it."
    ),
    "PRAYER": (
        "The United States Supreme Court has ruled that no state or local "
        "government may require the reading of the Lord's Prayer or Bible "
        "verses in public schools. What are your views on this--do you "
        "approve or disapprove of the court ruling?"
    ),
    # ── Family, sexuality, morality ──────────────────────────────────
    "DIVLAW": (
        "Should divorce in this country be easier or more difficult to "
        "obtain than it is now?"
    ),
    "PREMARSX": (
        "If a man and a woman have sexual relations before marriage, do you "
        "think it is always wrong, almost always wrong, wrong only "
        "sometimes, or not wrong at all?"
    ),
    "XMARSEX": (
        "What is your opinion about a married person having sexual "
        "relations with someone other than the marriage partner--is it "
        "always wrong, almost always wrong, wrong only sometimes, or not "
        "wrong at all?"
    ),
    "HOMOSEX": (
        "What about sexual relations between two adults of the same sex--do "
        "you think it is always wrong, almost always wrong, wrong only "
        "sometimes, or not wrong at all?"
    ),
    "PORNLAW": (
        "Which of these statements comes closest to your feelings about "
        "pornography laws? There should be laws against the distribution of "
        "pornography whatever the age; there should be laws against the "
        "distribution of pornography to persons under 18; or there should "
        "be no laws forbidding the distribution of pornography."
    ),
    "LETDIE1": (
        "When a person has a disease that cannot be cured, do you think "
        "doctors should be allowed by law to end the patient's life by some "
        "painless means if the patient and his family request it?"
    ),
    "SUICIDE1": (
        "Do you think a person has the right to end his or her own life if "
        "this person has an incurable disease?"
    ),
    "SPANKING": (
        "Do you strongly agree, agree, disagree, or strongly disagree that "
        "it is sometimes necessary to discipline a child with a good, hard "
        "spanking?"
    ),
    "SEXEDUC": ("Would you be for or against sex education in the public schools?"),
    # ── Race and opportunity ─────────────────────────────────────────
    "RACOPEN": (
        "Suppose there is a community-wide vote on the general housing "
        "issue. There are two possible laws to vote on: One law says that a "
        "homeowner can decide whom to sell his house to, even if he prefers "
        "not to sell to someone because of their race. The second law says "
        "that a homeowner cannot refuse to sell to someone because of their "
        "race. Which law would you vote for?"
    ),
    "AFFRMACT": (
        "Some people say that because of past discrimination, Black people "
        "should be given preference in hiring and promotion. Others say "
        "that such preference in hiring and promotion of Black people is "
        "wrong because it discriminates against other Americans. What about "
        "your opinion--are you for or against preferential hiring and "
        "promotion of Black people, and do you feel that way strongly or "
        "not strongly?"
    ),
    "WRKWAYUP": (
        "Do you agree strongly, agree somewhat, neither agree nor disagree, "
        "disagree somewhat, or disagree strongly with the following "
        "statement: Irish, Italians, Jewish and many other minorities "
        "overcame prejudice and worked their way up. Black people should do "
        "the same without special favors."
    ),
    # ── Free-speech battery ──────────────────────────────────────────
    "SPKATH": _STEM_ATH
    + (
        "If such a person wanted to make a speech in your city, town, or "
        "community against churches and religion, should he be allowed to "
        "speak, or not?"
    ),
    "COLATH": _STEM_ATH
    + ("Should such a person be allowed to teach in a college or university, or not?"),
    "LIBATH": _STEM_ATH
    + (
        "If some people in your community suggested that a book he wrote "
        "against churches and religion should be removed from your public "
        "library, would you favor removing this book, or not?"
    ),
    "SPKRAC": (
        "Consider a person who believes that Black people are genetically "
        "inferior. If such a person wanted to make a speech in your "
        "community claiming that Black people are inferior, should he be "
        "allowed to speak, or not?"
    ),
    "SPKCOM": (
        "Consider a man who admits he is a Communist. Suppose this admitted "
        "Communist wanted to make a speech in your community. Should he be "
        "allowed to speak, or not?"
    ),
    # ── Abortion battery ─────────────────────────────────────────────
    "ABANY": _STEM_AB + "if the woman wants it for any reason?",
    "ABDEFECT": _STEM_AB + "if there is a strong chance of serious defect in the baby?",
    "ABNOMORE": _STEM_AB + "if she is married and does not want any more children?",
    "ABHLTH": _STEM_AB
    + "if the woman's own health is seriously endangered by the pregnancy?",
    "ABPOOR": _STEM_AB
    + ("if the family has a very low income and cannot afford any more children?"),
    "ABRAPE": _STEM_AB + "if she became pregnant as a result of rape?",
    "ABSINGLE": _STEM_AB + "if she is not married and does not want to marry the man?",
    # ── National spending battery ────────────────────────────────────
    "NATSPAC": _STEM_NAT + "the space exploration program?",
    "NATENVIR": _STEM_NAT + "improving and protecting the environment?",
    "NATHEAL": _STEM_NAT + "improving and protecting the nation's health?",
    "NATCITY": _STEM_NAT + "solving the problems of the big cities?",
    "NATCRIME": _STEM_NAT + "halting the rising crime rate?",
    "NATDRUG": _STEM_NAT + "dealing with drug addiction?",
    "NATEDUC": _STEM_NAT + "improving the nation's education system?",
    "NATRACE": _STEM_NAT + "improving the conditions of Black people?",
    "NATARMS": _STEM_NAT + "the military, armaments, and defense?",
    "NATAID": _STEM_NAT + "foreign aid?",
    "NATFARE": _STEM_NAT + "welfare?",
    # ── Confidence-in-institutions battery ───────────────────────────
    "CONFINAN": _STEM_CON + "banks and financial institutions?",
    "CONBUS": _STEM_CON + "major companies?",
    "CONCLERG": _STEM_CON + "organized religion?",
    "CONEDUC": _STEM_CON + "education?",
    "CONFED": _STEM_CON + "the executive branch of the federal government?",
    "CONLABOR": _STEM_CON + "organized labor?",
    "CONPRESS": _STEM_CON + "the press?",
    "CONMEDIC": _STEM_CON + "medicine?",
    "CONTV": _STEM_CON + "television?",
    "CONJUDGE": _STEM_CON + "the U.S. Supreme Court?",
    "CONSCI": _STEM_CON + "the scientific community?",
    "CONLEGIS": _STEM_CON + "Congress?",
    "CONARMY": _STEM_CON + "the military?",
}

# Questions with fewer weighted respondents than this are skipped (a wave
# may not carry every item on every ballot).
_MIN_RESPONDENTS = 300

# Nonresponse value labels shipped as explicit options (see module
# docstring). Everything else that is a tagged-missing label is dropped.
_NONRESPONSE_KEEP = ("don't know", "refused")
_NONRESPONSE_DROP = (
    "iap",
    "no answer",
    "skipped on web",
    "not imputable",
    "uncodeable",
    "dk, na, iap",
    "see codebook",
    "not available in this release",
    "not available in this year",
    "I don't have a job",
)

# Discriminative-power screen: minimum Jensen-Shannon divergence (base 2)
# between the ground-truth distribution and the uniform distribution over
# the same options. Items below this are trivially matched by a uniform
# null agent and excluded (see module docstring).
_MIN_UNIFORM_JSD = 0.03


def _uniform_jsd(dist: list[float]) -> float:
    """Jensen-Shannon divergence (base 2) between *dist* and uniform."""
    import math

    n = len(dist)
    if n == 0:
        return 0.0
    u = 1.0 / n

    def _kl(p: list[float], q: list[float]) -> float:
        return sum(a * math.log2(a / b) for a, b in zip(p, q) if a > 0)

    m = [(a + u) / 2 for a in dist]
    return 0.5 * _kl(dist, m) + 0.5 * _kl([u] * n, m)


def _default_data_dir() -> Path:
    return Path.home() / ".synthbench" / "data" / "gss"


def _fetch_with_retries(url: str, attempts: int = 3, timeout: int = 120) -> bytes:
    """Fetch *url*, retrying transient failures with backoff.

    NORC's CDN intermittently times out on first contact; a bare urlopen
    with no timeout turned that into an indefinite hang or a hard failure
    for third-party replicators (issue #339 friction log). On exhaustion,
    point at the --dta manual fallback rather than a bare traceback.
    """
    import time

    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
            if attempt < attempts:
                wait = 5 * attempt
                print(f"  attempt {attempt} failed ({exc}); retrying in {wait}s ...")
                time.sleep(wait)
    raise SystemExit(
        f"Failed to download {url} after {attempts} attempts (last: {last}).\n"
        "Download the zip manually, extract the .dta file, and re-run with\n"
        "  python scripts/ingest-gss.py --dta /path/to/GSS<year>.dta"
    )


def _download_dta(year: int, dest_dir: Path) -> Path:
    """Download and extract the NORC single-year STATA release."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dta_path = dest_dir / f"GSS{year}.dta"
    if dta_path.exists():
        print(f"Using cached {dta_path}")
        return dta_path

    url = _NORC_ZIP_URL.format(year=year)
    print(f"Downloading {url} ...")
    payload = _fetch_with_retries(url)
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        member = next(
            (n for n in zf.namelist() if n.lower().endswith(f"gss{year}.dta")),
            None,
        )
        if member is None:
            raise SystemExit(
                f"No GSS{year}.dta inside {url}; archive lists: {zf.namelist()}"
            )
        with zf.open(member) as src, open(dta_path, "wb") as dst:
            dst.write(src.read())
    print(f"Extracted {dta_path} ({dta_path.stat().st_size:,} bytes)")
    return dta_path


def build_aggregated_csv(
    dta_path: Path,
    out_csv: Path,
    year: int,
    *,
    weighted: bool = True,
) -> tuple[int, int]:
    """Aggregate curated items into (question_id, year, option, count) rows.

    Returns ``(n_questions_written, n_questions_skipped)``.
    """
    import pyreadstat

    wanted = [q.lower() for q in QUESTION_TEXTS]
    # apply_value_formats=True vends NORC's value labels as strings;
    # user_missing=True keeps tagged codes (don't know / refused / iap /
    # skipped on web ...) so we can ship real nonresponse mass as options
    # instead of silently dropping it.
    df, meta = pyreadstat.read_dta(
        str(dta_path), apply_value_formats=True, user_missing=True
    )
    present = [c for c in wanted if c in df.columns]
    absent = sorted(set(wanted) - set(present))
    if absent:
        print(f"Not in this release (skipped): {', '.join(absent)}")

    weight_col = None
    if weighted:
        weight_col = next((w for w in _WEIGHT_PREFERENCE if w in df.columns), None)
        if weight_col is None:
            raise SystemExit(
                f"No known weight column found (looked for "
                f"{_WEIGHT_PREFERENCE}); re-run with --unweighted."
            )
        print(f"Weighting counts by '{weight_col}'.")
    else:
        print("Using unweighted respondent counts.")

    import pandas as pd

    rows: list[dict[str, object]] = []
    skipped = 0
    for col in present:
        qid = col.upper()
        series = df[col]
        # Drop NaN and administrative codes; keep substantive answers plus
        # the explicit "don't know" / "refused" nonresponse categories.
        mask = series.notna() & ~series.isin(_NONRESPONSE_DROP)
        n_resp = int(mask.sum())
        if n_resp < _MIN_RESPONDENTS:
            print(f"  {qid}: only {n_resp} respondents — skipped")
            skipped += 1
            continue

        values = series[mask]
        non_str = sorted({str(v) for v in values.unique() if not isinstance(v, str)})
        if non_str:
            print(f"  {qid}: unlabeled numeric codes {non_str} — skipped")
            skipped += 1
            continue

        # Preserve NORC's codebook ordering (value labels are ordered by
        # numeric code) so the adapter's first-seen option order is sane.
        # Nonresponse options go last, mirroring survey presentation.
        labels = meta.variable_value_labels.get(col, {})
        ordered = [
            v
            for k, v in sorted(
                ((k, v) for k, v in labels.items() if isinstance(k, int)),
                key=lambda kv: kv[0],
            )
        ]
        observed = set(values.unique())
        option_order = [o for o in ordered if o in observed]
        option_order += [
            o for o in _NONRESPONSE_KEEP if o in observed and o not in option_order
        ]
        unexpected = observed - set(option_order)
        if unexpected:
            print(f"  {qid}: unexpected labels {sorted(unexpected)} — skipped")
            skipped += 1
            continue

        if weight_col is not None:
            weights = pd.to_numeric(df.loc[mask, weight_col], errors="coerce")
            grouped = weights.groupby(values, observed=True).sum()
            counts = {str(k): float(v) for k, v in grouped.items()}
        else:
            counts = {str(k): float(v) for k, v in values.value_counts().items()}

        dist_options = [o for o in option_order if counts.get(o, 0.0) > 0]
        total = sum(counts[o] for o in dist_options)
        if total <= 0:
            skipped += 1
            continue
        dist = [counts[o] / total for o in dist_options]
        u_jsd = _uniform_jsd(dist)
        if u_jsd < _MIN_UNIFORM_JSD:
            print(
                f"  {qid}: ground truth within JSD {u_jsd:.4f} of uniform "
                f"(< {_MIN_UNIFORM_JSD}) — screened out as non-discriminative"
            )
            skipped += 1
            continue

        for option in dist_options:
            rows.append(
                {
                    "question_id": qid,
                    "question_text": QUESTION_TEXTS[qid],
                    "year": year,
                    "option": option,
                    "count": round(counts[option], 4),
                }
            )

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["question_id", "question_text", "year", "option", "count"],
        )
        writer.writeheader()
        writer.writerows(rows)

    n_written = len({r["question_id"] for r in rows})
    print(f"Wrote {len(rows)} rows / {n_written} questions -> {out_csv}")
    return n_written, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=_default_data_dir(),
        help="GSS adapter data dir (default: ~/.synthbench/data/gss).",
    )
    parser.add_argument(
        "--dta",
        type=Path,
        default=None,
        help="Use an existing GSS<year>.dta instead of downloading.",
    )
    parser.add_argument(
        "--unweighted",
        action="store_true",
        help="Raw respondent counts instead of wtssnrps/wtssps weighting.",
    )
    args = parser.parse_args()

    data_dir: Path = args.data_dir
    dta_path = args.dta or _download_dta(args.year, data_dir / "raw")
    out_csv = data_dir / "raw" / "gss_aggregated.csv"

    build_aggregated_csv(dta_path, out_csv, args.year, weighted=not args.unweighted)

    # Invalidate the adapter cache so the next load() rebuilds from the CSV.
    cache = data_dir / "questions.json"
    if cache.exists():
        cache.unlink()
        print(f"Removed stale cache {cache}")

    # Build (and cache) questions via the adapter to prove the round trip.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
    from synthbench.datasets.gss import GSSDataset

    questions = GSSDataset(data_dir=data_dir).load()
    print(f"Adapter loads {len(questions)} questions; cache rebuilt at {cache}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
