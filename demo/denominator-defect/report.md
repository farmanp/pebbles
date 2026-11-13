# Pebbles investigation

Evidence discrepancies require investigation

Findings concern supplied records and declared rules. They do not establish production completeness, treatment rendering, causal validity, significance, or a shipping decision.

Run: `04372015-59e3-497a-a23f-2bbb961592de` · execution: **Completed**

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

**Verified · supplied evidence only**

Computed v1 over the valid subset of supplied records using the declared assignment, identity and time rules. Zero denominators are undefined.

```json
{
  "control": {
    "assigned": 4,
    "distinct_exposed": 3,
    "exposure_rows": 3,
    "numerator": 1,
    "denominator": 3,
    "rate": "1/3",
    "rate_percent": 33.333
  },
  "treatment": {
    "assigned": 4,
    "distinct_exposed": 3,
    "exposure_rows": 4,
    "numerator": 2,
    "denominator": 3,
    "rate": "2/3",
    "rate_percent": 66.667
  }
}
```

Sources: `configuration.json` (/; SHA-256 `465e98c2ba53f73f8a9c0cb3fcc94449674005fe13d7edfb9b306c37098a44b5`), `metric.json` (/; SHA-256 `120e51d60c4c77413d81dcf4087601dd5052d831169003e8e9ebf2745d4c4181`), `assignments.jsonl` (all records; SHA-256 `57ad938acfa6bedcb3c6c8fa6faaedf6cf19c4ae985bc2ffaf080dfd623d9f92`), `exposures.jsonl` (all records; SHA-256 `fd7bfae7b324833d5b488610160c736d7b6898ea8ab49ccdc6b5e00d43928c90`), `outcomes.jsonl` (all records; SHA-256 `5391039c97729fbf33f18426704deba8f540cf99600061318dca4e2cb44e8b9c`)

## C03 — Does the supplied SQL use the intended denominator?

**Failed · supplied evidence only**

The denominator expression counts exposure rows for treatment; the supplied definition requires distinct users. This is expression inspection only; the rest of the SQL and general query equivalence are not verified.

```json
{
  "expression": "CASE WHEN variant_id='treatment' THEN COUNT(*) ELSE COUNT(DISTINCT user_id) END"
}
```

Sources: `metric.json` (/; SHA-256 `120e51d60c4c77413d81dcf4087601dd5052d831169003e8e9ebf2745d4c4181`), `metric.sql` (/; SHA-256 `ae90d6bf47ae0d0878a52fe35100ff05ce60afb6b3a28064bc341366e67996dd`)

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
    "denominator": 4,
    "distinct_exposed": 3,
    "numerator": 2,
    "rate_percent": 50.0
  }
}
```

Sources: `scorecard.json` (/; SHA-256 `c87eb839c619c2d11a1942f3855a847dadfb9577e19ad6d8231ccddba95feaf6`)

## C05 — Does the scorecard match the declared calculation?

**Failed · supplied evidence only**

treatment: reported 2/4; supported calculation 2/3 (66.667%). Reconcile the scorecard before relying on this measurement.

```json
{
  "computed": {
    "control": {
      "assigned": 4,
      "distinct_exposed": 3,
      "exposure_rows": 3,
      "numerator": 1,
      "denominator": 3,
      "rate": "1/3",
      "rate_percent": 33.333
    },
    "treatment": {
      "assigned": 4,
      "distinct_exposed": 3,
      "exposure_rows": 4,
      "numerator": 2,
      "denominator": 3,
      "rate": "2/3",
      "rate_percent": 66.667
    }
  },
  "reported": {
    "control": {
      "denominator": 3,
      "distinct_exposed": 3,
      "numerator": 1,
      "rate_percent": 33.333
    },
    "treatment": {
      "denominator": 4,
      "distinct_exposed": 3,
      "numerator": 2,
      "rate_percent": 50.0
    }
  }
}
```

Next evidence: Ask the metric owner to correct and regenerate the scorecard using the versioned denominator rule.

Sources: `configuration.json` (/; SHA-256 `465e98c2ba53f73f8a9c0cb3fcc94449674005fe13d7edfb9b306c37098a44b5`), `metric.json` (/; SHA-256 `120e51d60c4c77413d81dcf4087601dd5052d831169003e8e9ebf2745d4c4181`), `assignments.jsonl` (all records; SHA-256 `57ad938acfa6bedcb3c6c8fa6faaedf6cf19c4ae985bc2ffaf080dfd623d9f92`), `exposures.jsonl` (all records; SHA-256 `fd7bfae7b324833d5b488610160c736d7b6898ea8ab49ccdc6b5e00d43928c90`), `outcomes.jsonl` (all records; SHA-256 `5391039c97729fbf33f18426704deba8f540cf99600061318dca4e2cb44e8b9c`), `scorecard.json` (/; SHA-256 `c87eb839c619c2d11a1942f3855a847dadfb9577e19ad6d8231ccddba95feaf6`), `inventory.json` (/; SHA-256 `addbbc2eff555e58652fbfb3a08649dcc227e1517269c39f0cda75919ce6a64f`)

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

Sources: `scorecard.json` (/; SHA-256 `c87eb839c619c2d11a1942f3855a847dadfb9577e19ad6d8231ccddba95feaf6`), `exposures.jsonl` (all records; SHA-256 `fd7bfae7b324833d5b488610160c736d7b6898ea8ab49ccdc6b5e00d43928c90`)

## C07 — Do the sources declare a shared analytical scope?

**Verified · supplied evidence only**

Inventory declares matching population, filters, window, snapshot and experiment revision. This is declared alignment, not independently proven upstream lineage.

Sources: `inventory.json` (/; SHA-256 `addbbc2eff555e58652fbfb3a08649dcc227e1517269c39f0cda75919ce6a64f`), `configuration.json` (/; SHA-256 `465e98c2ba53f73f8a9c0cb3fcc94449674005fe13d7edfb9b306c37098a44b5`), `metric.json` (/; SHA-256 `120e51d60c4c77413d81dcf4087601dd5052d831169003e8e9ebf2745d4c4181`)

## C08 — Which supplied records qualify or conflict?

**Verified · supplied evidence only**

Identified 0 excluded records, 0 identity conflicts, 0 identical replays and 1 repeat encounters. A repeat encounter is not itself a defect; an orphan in these files does not prove a production tracking failure.

```json
{
  "excluded": [],
  "conflicts": [],
  "identical_replays": 0,
  "repeat_encounters": 1
}
```

Sources: `configuration.json` (/; SHA-256 `465e98c2ba53f73f8a9c0cb3fcc94449674005fe13d7edfb9b306c37098a44b5`), `metric.json` (/; SHA-256 `120e51d60c4c77413d81dcf4087601dd5052d831169003e8e9ebf2745d4c4181`), `assignments.jsonl` (all records; SHA-256 `57ad938acfa6bedcb3c6c8fa6faaedf6cf19c4ae985bc2ffaf080dfd623d9f92`), `exposures.jsonl` (all records; SHA-256 `fd7bfae7b324833d5b488610160c736d7b6898ea8ab49ccdc6b5e00d43928c90`), `outcomes.jsonl` (all records; SHA-256 `5391039c97729fbf33f18426704deba8f540cf99600061318dca4e2cb44e8b9c`)

## C09 — Was treatment actually rendered correctly?

**Insufficient evidence · supplied evidence only**

Analytical files do not establish that treatment was actually rendered correctly. This prototype does not validate application or SDK behavior.

Next evidence: Ask the implementation owner for relevant render/instrumentation evidence if delivery is decision-critical.

Sources: `inventory.json` (/; SHA-256 `addbbc2eff555e58652fbfb3a08649dcc227e1517269c39f0cda75919ce6a64f`)

## C10 — Do these exports establish production completeness?

**Insufficient evidence · supplied evidence only**

Export counts and completeness declarations do not independently establish capture of all production activity.

Next evidence: Ask the data owner for independent capture reconciliation and source lineage if completeness is decision-critical.

Sources: `inventory.json` (/; SHA-256 `addbbc2eff555e58652fbfb3a08649dcc227e1517269c39f0cda75919ce6a64f`)

## Not evaluated

- Statistical significance and causal validity
- Production treatment delivery
- Production capture completeness
- Human shipping judgment
- Independent report-quality scoring (C11)
- Cross-run replay validation (C13; demonstrated separately in tests)
