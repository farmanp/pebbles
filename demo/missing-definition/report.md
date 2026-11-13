# Pebbles investigation

Supported checks completed; important evidence limits remain

Findings concern supplied records and declared rules. They do not establish production completeness, treatment rendering, causal validity, significance, or a shipping decision.

Run: `e98d6916-379b-4e76-ac8b-8004e74e5e38` · execution: **Completed**

[Open HTML report](report.html) · [Machine-readable report](report.json)

## C01 — What records are present?

**Verified · supplied evidence only**

These are literal counts in the supplied files; they do not establish metric eligibility or production coverage.

```json
{
  "assignments.jsonl": {
    "rows": 8,
    "distinct_users": 8
  },
  "exposures.jsonl": {
    "rows": 7,
    "distinct_users": 6
  },
  "outcomes.jsonl": {
    "rows": 3,
    "distinct_users": 3
  }
}
```

Sources: `assignments.jsonl` (all records; SHA-256 `57ad938acfa6bedcb3c6c8fa6faaedf6cf19c4ae985bc2ffaf080dfd623d9f92`), `exposures.jsonl` (all records; SHA-256 `fd7bfae7b324833d5b488610160c736d7b6898ea8ab49ccdc6b5e00d43928c90`), `outcomes.jsonl` (all records; SHA-256 `5391039c97729fbf33f18426704deba8f540cf99600061318dca4e2cb44e8b9c`)

## C02 — What does the declared metric calculate?

**Insufficient evidence · supplied evidence only**

Required evidence is missing: metric.json

Next evidence: Ask the analyst or metric owner for metric.json to assess this check.

Sources: `configuration.json` (/; SHA-256 `109e433e38ec86260ac920490627e6ca6e845872b1f8c694cde901eb846d79f4`), `assignments.jsonl` (all records; SHA-256 `57ad938acfa6bedcb3c6c8fa6faaedf6cf19c4ae985bc2ffaf080dfd623d9f92`), `exposures.jsonl` (all records; SHA-256 `fd7bfae7b324833d5b488610160c736d7b6898ea8ab49ccdc6b5e00d43928c90`), `outcomes.jsonl` (all records; SHA-256 `5391039c97729fbf33f18426704deba8f540cf99600061318dca4e2cb44e8b9c`)

## C03 — Does the supplied SQL use the intended denominator?

**Insufficient evidence · supplied evidence only**

Required evidence is missing: metric.json, metric.sql

Next evidence: Ask the analyst or metric owner for metric.json, metric.sql to assess this check.

Sources:

## C04 — Do the scorecard fields agree arithmetically?

**Verified · supplied evidence only**

Reported percentages match the scorecard’s own numerator and denominator fields within three-decimal percentage rounding. This does not validate the intended denominator.

```json
{
  "control": {
    "denominator": 3,
    "distinct_exposed": 3,
    "numerator": 1,
    "rate_percent": 33.333
  },
  "treatment": {
    "denominator": 3,
    "distinct_exposed": 3,
    "numerator": 2,
    "rate_percent": 66.667
  }
}
```

Sources: `scorecard.json` (/; SHA-256 `dded54fa494e6ff49f11146de38a8ef135bf7afb259e26933a116633e1d033fa`)

## C05 — Does the scorecard match the declared calculation?

**Insufficient evidence · supplied evidence only**

Required evidence is missing: metric.json

Next evidence: Ask the analyst or metric owner for metric.json to assess this check.

Sources: `configuration.json` (/; SHA-256 `109e433e38ec86260ac920490627e6ca6e845872b1f8c694cde901eb846d79f4`), `assignments.jsonl` (all records; SHA-256 `57ad938acfa6bedcb3c6c8fa6faaedf6cf19c4ae985bc2ffaf080dfd623d9f92`), `exposures.jsonl` (all records; SHA-256 `fd7bfae7b324833d5b488610160c736d7b6898ea8ab49ccdc6b5e00d43928c90`), `outcomes.jsonl` (all records; SHA-256 `5391039c97729fbf33f18426704deba8f540cf99600061318dca4e2cb44e8b9c`), `scorecard.json` (/; SHA-256 `dded54fa494e6ff49f11146de38a8ef135bf7afb259e26933a116633e1d033fa`), `inventory.json` (/; SHA-256 `4e0d9ec19975cf90ed683431e389954942c6549766a189e1204f3b550f1c9e20`)

## C06 — Do the reported and exported exposure counts agree?

**Verified · supplied evidence only**

The displayed distinct-exposure counts equal the distinct users by arm in the exposure file.

```json
{
  "control": {
    "reported_distinct_exposed": 3,
    "export_distinct_users": 3
  },
  "treatment": {
    "reported_distinct_exposed": 3,
    "export_distinct_users": 3
  }
}
```

Sources: `scorecard.json` (/; SHA-256 `dded54fa494e6ff49f11146de38a8ef135bf7afb259e26933a116633e1d033fa`), `exposures.jsonl` (all records; SHA-256 `fd7bfae7b324833d5b488610160c736d7b6898ea8ab49ccdc6b5e00d43928c90`)

## C07 — Do the sources declare a shared analytical scope?

**Insufficient evidence · supplied evidence only**

Cannot establish shared analytical scope without metric.json

Next evidence: Provide the missing definitions/exports and aligned population, filters, window and snapshot metadata.

Sources: `inventory.json` (/; SHA-256 `4e0d9ec19975cf90ed683431e389954942c6549766a189e1204f3b550f1c9e20`)

## C08 — Which supplied records qualify or conflict?

**Verified · supplied evidence only**

Counted repeated IDs, repeat encounters and users absent from the supplied assignments. These are record facts only; metric eligibility and production root causes remain unresolved.

```json
{
  "conflicts": [],
  "identical_replays": 0,
  "orphan_record_ids": [],
  "repeat_encounters": 1
}
```

Sources: `assignments.jsonl` (all records; SHA-256 `57ad938acfa6bedcb3c6c8fa6faaedf6cf19c4ae985bc2ffaf080dfd623d9f92`), `exposures.jsonl` (all records; SHA-256 `fd7bfae7b324833d5b488610160c736d7b6898ea8ab49ccdc6b5e00d43928c90`)

## C09 — Was treatment actually rendered correctly?

**Insufficient evidence · supplied evidence only**

Analytical files do not establish that treatment was actually rendered correctly. This prototype does not validate application or SDK behavior.

Next evidence: Ask the implementation owner for relevant render/instrumentation evidence if delivery is decision-critical.

Sources: `inventory.json` (/; SHA-256 `4e0d9ec19975cf90ed683431e389954942c6549766a189e1204f3b550f1c9e20`)

## C10 — Do these exports establish production completeness?

**Insufficient evidence · supplied evidence only**

Export counts and completeness declarations do not independently establish capture of all production activity.

Next evidence: Ask the data owner for independent capture reconciliation and source lineage if completeness is decision-critical.

Sources: `inventory.json` (/; SHA-256 `4e0d9ec19975cf90ed683431e389954942c6549766a189e1204f3b550f1c9e20`)

## Not evaluated

- Statistical significance and causal validity
- Production treatment delivery
- Production capture completeness
- Human shipping judgment
- Independent report-quality scoring (C11)
- Cross-run replay validation (C13; demonstrated separately in tests)
