# PV Structure Intelligence Framework Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first working version of the shared framework assets, the Clenergy-facing `WaterBase Mount` materials, and a usable `Product Mode` demo scaffold.

**Architecture:** Phase 1 creates a shared content and logic foundation first, then layers the Clenergy-specific presentation on top, and finally exposes the core logic through a lightweight static demo. The repository stays simple: Markdown and spreadsheet-style source assets for knowledge, plus plain HTML/CSS/JS/JSON for the demo so the work remains portable and easy to present.

**Tech Stack:** Markdown, CSV, JSON, HTML, CSS, vanilla JavaScript, Pandoc, Git

---

## File Structure

### Shared framework assets

- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/README.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Framework_Philosophy.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Scenario_Logic_Table.csv`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Multi_Region_Standards_Matrix.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Risk_Taxonomy_Library.md`

### Evidence layer

- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/README.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/Case_Map_Nanchang_Water_Plant.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/Case_Map_Xiamen_Water_Plant.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/Retrospective_Framework_Upgrade.md`

### Clenergy-facing assets

- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/README.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/WaterBase_Mount_Deck_Source.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/Customer_Facing_Solution_Brief.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/Presentation_Talk_Track.md`

### CATL-facing placeholder

- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/03_View_Technical_Review/README.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/03_View_Technical_Review/Overseas_Framework_Skeleton.md`

### Demo

- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/README.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/index.html`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/styles.css`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/app.js`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/data/product_mode_rules.json`

### Existing files to reference

- Reference: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/docs/superpowers/specs/2026-04-03-waterbase-mount-design.md`

---

### Task 1: Create the framework directory tree and root readmes

**Files:**
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/README.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/03_View_Technical_Review/`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/`
- Test: repository tree via `find`

- [ ] **Step 1: Create the directories**

Run:

```bash
mkdir -p \
  '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core' \
  '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode' \
  '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/03_View_Technical_Review' \
  '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library' \
  '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/data'
```

- [ ] **Step 2: Create the root README**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/README.md` with:

```md
# PV Structure Intelligence Framework

This folder contains the shared knowledge assets, company-specific presentation views, supporting evidence, and interactive demo files for the interview project.

## Structure

- `01_Methodology_Core`: shared logic tables, standards mapping, and risk taxonomy
- `02_View_Product_Mode`: Clenergy-facing WaterBase Mount materials
- `03_View_Technical_Review`: CATL-facing overseas technical review materials
- `04_Evidence_Case_Library`: case mapping and retrospective proof
- `05_Interactive_Demo`: lightweight browser demo

## Phase 1 scope

Phase 1 focuses on the shared framework, the Clenergy presentation layer, one evidence sample, and the Product Mode demo.
```

- [ ] **Step 3: Verify the folder tree**

Run:

```bash
find '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework' -maxdepth 2 | sort
```

Expected: the five subfolders plus the root `README.md` appear.

- [ ] **Step 4: Commit**

```bash
git add '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/README.md'
git add '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework'
git commit -m "chore: scaffold pv structure intelligence framework"
```

### Task 2: Build the methodology core assets

**Files:**
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Framework_Philosophy.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Scenario_Logic_Table.csv`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Multi_Region_Standards_Matrix.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Risk_Taxonomy_Library.md`
- Test: CSV header and markdown headings

- [ ] **Step 1: Write the framework philosophy**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Framework_Philosophy.md` with:

```md
# Framework Philosophy

## Purpose

This framework turns project-based structural experience into repeatable decision logic for PV mounting scenarios.

## Decision loop

1. Define the scenario
2. Identify structural and operational constraints
3. Select a candidate path
4. Classify the standardization boundary
5. Surface the main risks
6. Adapt for target market standards

## Core variables

- Structure type
- Span and height level
- Wind level
- Corrosion level
- Equipment and pipeline interference
- O&M access requirement
- Support placement condition
- Target market

## Output types

- Recommended solution path
- Standard / parameterized / non-standard classification
- Main risks
- Region adaptation notes
- Customer-facing summary
```

- [ ] **Step 2: Write the scenario logic table**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Scenario_Logic_Table.csv` with:

```csv
scenario_id,structure_type,span_level,wind_level,corrosion_level,interference_level,om_requirement,support_condition,target_market,recommended_path,standardization_level,material_direction,foundation_note,primary_risk
WB-001,clear_water_tank,high,high,high,high,high,outer_support_only,CN,flexible,non_standard,high_corrosion_grade,check_outer_foundation_and_pipe_conflict,wind_and_operation_conflict
WB-002,clear_water_tank,medium,medium,high,medium,high,outer_support_only,EU,flexible,parameterized,high_corrosion_grade,review_foundation_and_access_path,corrosion_and_access
WB-003,sedimentation_tank,medium,medium,medium,high,high,limited_pool_wall_support,CN,compare_both,non_standard,mixed_strategy,check_equipment_interference,equipment_clearance
WB-004,roof_auxiliary_structure,low,medium,medium,low,medium,roof_support_allowed,AU,rigid,standard,lightweight_corrosion_grade,check_roof_interface,wind_adaptation
WB-005,water_plant_roof,low,low,medium,low,medium,roof_support_allowed,JP,rigid,parameterized,lightweight_corrosion_grade,check_local_detail_requirements,detail_and_seismic_check
```

- [ ] **Step 3: Write the multi-region standards matrix**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Multi_Region_Standards_Matrix.md` with:

```md
# Multi-Region Standards Matrix

| Region | Standards context | Focus items | Product or review impact |
| --- | --- | --- | --- |
| China | GB | load, structural detailing, local delivery docs | baseline domestic package |
| Europe | Eurocode / CE / TÜV | wind, certification, installation efficiency | region adaptation and technical file output |
| United States | ASCE / IBC / UL | compliance boundary, load path, documentation | stricter review gate and deliverable definition |
| Australia | AS/NZS | high wind, roof interface | wind-heavy adaptation logic |
| Japan | JIS | local detail, seismic wording, conservative review | detail-level adaptation and localized notes |
```

- [ ] **Step 4: Write the risk taxonomy library**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Risk_Taxonomy_Library.md` with:

```md
# Risk Taxonomy Library

## Structural risks

- Overstressed support system
- Foundation instability
- Excessive deformation under service load

## Operational risks

- Blocked maintenance path
- Equipment movement conflict
- Long-term plant operation disturbance

## Construction risks

- Existing pipeline clash
- Restricted work zone
- High retrofit disturbance

## Compliance risks

- Target market standard mismatch
- Missing certification or technical files
- Incomplete review basis
```

- [ ] **Step 5: Verify the core assets**

Run:

```bash
head -n 3 '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Scenario_Logic_Table.csv'
python3 -c "import csv; list(csv.DictReader(open('/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core/Scenario_Logic_Table.csv', newline='')))"
```

Expected:
- the CSV header prints correctly
- the second command exits successfully without a CSV parsing error

- [ ] **Step 6: Commit**

```bash
git add '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/01_Methodology_Core'
git commit -m "docs: add methodology core assets"
```

### Task 3: Build the evidence case library and retrospective proof

**Files:**
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/README.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/Case_Map_Nanchang_Water_Plant.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/Case_Map_Xiamen_Water_Plant.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/Retrospective_Framework_Upgrade.md`
- Test: headings and line count

- [ ] **Step 1: Create the evidence library index**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/README.md` with:

```md
# Evidence Case Library

This folder maps real project experience into the framework logic.

## Included cases

- Nanchang water plant distributed PV case
- Xiamen water plant transformation case
- Retrospective summary on how the framework upgrades earlier practice
```

- [ ] **Step 2: Map the Nanchang case**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/Case_Map_Nanchang_Water_Plant.md` with:

```md
# Case Map: Nanchang Water Plant

## Scenario

- Existing clear water tanks
- Large span and height
- Complex surrounding pipelines
- O&M continuity required

## Main conflict

Conventional rigid support placement conflicted with equipment movement and support conditions.

## Framework mapping

- Recommended path: compare rigid and flexible support
- Standardization level: non-standard
- Primary risks: wind, access, foundation disturbance
- Target value: low operational disturbance with acceptable cost

## Interview talking point

This case proves the framework is based on real structural trade-off, not abstract product language.
```

- [ ] **Step 3: Map the Xiamen case**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/Case_Map_Xiamen_Water_Plant.md` with:

```md
# Case Map: Xiamen Water Plant

## Scenario

- Water plant transformation project
- High difficulty construction constraints
- Ongoing operation and structure safety both critical

## Framework mapping

- Key constraints: construction disturbance, terrain complexity, existing operation
- Method value: early risk identification and multi-party solution balancing
- Reusable insight: difficult operating environments need a stronger review gate

## Interview talking point

This case extends the framework from support selection to broader technical control thinking.
```

- [ ] **Step 4: Write the retrospective upgrade note**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/Retrospective_Framework_Upgrade.md` with:

```md
# Retrospective Framework Upgrade

## Why this matters

The value of the framework is not only that it organizes current thinking, but also that it can be used to re-read older projects.

## Example upgrade questions

- Which risks could have been identified earlier?
- Which decisions could have been parameterized instead of handled as ad hoc design?
- Which notes should have become standard customer-facing guidance?

## Interview talking point

This retrospective view shows growth from project delivery to framework-based judgment.
```

- [ ] **Step 5: Verify the evidence files**

Run:

```bash
find '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library' -type f | sort
wc -l '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library/'*.md
```

Expected: four markdown files exist and each file has non-trivial content.

- [ ] **Step 6: Commit**

```bash
git add '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/04_Evidence_Case_Library'
git commit -m "docs: add evidence case library"
```

### Task 4: Build the Clenergy-facing presentation source files

**Files:**
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/README.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/WaterBase_Mount_Deck_Source.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/Customer_Facing_Solution_Brief.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/Presentation_Talk_Track.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/03_View_Technical_Review/README.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/03_View_Technical_Review/Overseas_Framework_Skeleton.md`
- Test: markdown headings and pandoc export

- [ ] **Step 1: Write the Product Mode README**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/README.md` with:

```md
# Product Mode

This view packages the shared framework as a Clenergy-facing product and pre-sales story.

## Main assets

- Deck source
- Customer-facing one-page brief
- Talk track
```

- [ ] **Step 2: Write the WaterBase deck source**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/WaterBase_Mount_Deck_Source.md` with:

```md
# WaterBase Mount Deck Source

## Page 1

WaterBase Mount: a multi-standard-ready PV mounting solution for existing water infrastructure.

## Page 2

Why this scenario matters: self-use load, underused structure space, high complexity, high entry barrier.

## Page 3

Translate engineering pain points into product problems.

## Page 4

Product goals and design principles.

## Page 5

Product architecture: shared platform, scenario adaptation, standards adaptation, delivery support.

## Page 6

Standard / parameterized / non-standard boundary.

## Page 7

Multi-region adaptation.

## Page 8

Selection logic and comparison path.

## Page 9

Commercial and delivery value.

## Page 10

Demo introduction.
```

- [ ] **Step 3: Write the customer-facing one-page brief**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/Customer_Facing_Solution_Brief.md` with:

```md
# Customer-Facing Solution Brief

## Positioning

WaterBase Mount is a scenario-focused mounting solution for existing water plant structures.

## Core value

- Lower disturbance to ongoing operation
- Better adaptation to difficult retrofit constraints
- Faster pre-sales path with clearer technical boundaries

## Best-fit conditions

- Existing tanks or water-related structures
- Strong O&M access requirement
- Complex surrounding interference

## Main caution

High-span, high-wind, or highly restricted support conditions should enter a non-standard review gate.
```

- [ ] **Step 4: Write the talk track and CATL placeholder**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/Presentation_Talk_Track.md` with:

```md
# Presentation Talk Track

## Opening

I did not only prepare a resume and project stories. I turned my real project experience into a scenario-based product solution and a lightweight selector demo.

## Main thread

1. Why the water plant scenario matters
2. How engineering conflicts become product logic
3. How standardization boundaries are defined
4. How region adaptation is handled
5. How the demo supports pre-sales and product communication
```

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/03_View_Technical_Review/README.md` with:

```md
# Technical Review Mode

Phase 1 keeps this view as a skeleton only. It will later package the same framework for CATL-style technical review and design control interviews.
```

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/03_View_Technical_Review/Overseas_Framework_Skeleton.md` with:

```md
# Overseas PV Structural Technical Framework

## Reserved Phase 2 sections

- Early-stage technical review
- Load and foundation review logic
- Design institute audit points
- Site issue closure
- Multi-region compliance notes
```

- [ ] **Step 5: Verify markdown export**

Run:

```bash
pandoc '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/WaterBase_Mount_Deck_Source.md' -o '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/WaterBase_Mount_Deck_Source.docx'
ls -l '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode/WaterBase_Mount_Deck_Source.docx'
```

Expected: the `.docx` file is created successfully.

- [ ] **Step 6: Commit**

```bash
git add '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/02_View_Product_Mode'
git add '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/03_View_Technical_Review'
git commit -m "docs: add product mode materials"
```

### Task 5: Build the Product Mode demo scaffold

**Files:**
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/README.md`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/index.html`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/styles.css`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/app.js`
- Create: `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/data/product_mode_rules.json`
- Test: static page load and JSON parse

- [ ] **Step 1: Write the demo README**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/README.md` with:

```md
# Interactive Demo

Phase 1 builds the Product Mode demo first.

## Purpose

The demo is a decision-guidance tool, not an engineering calculation tool.

## Outputs

- recommended path
- standardization level
- main risks
- region adaptation notes
- customer-facing summary
```

- [ ] **Step 2: Create the rules JSON**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/data/product_mode_rules.json` with:

```json
[
  {
    "id": "WB-001",
    "structureType": "clear_water_tank",
    "spanLevel": "high",
    "windLevel": "high",
    "corrosionLevel": "high",
    "interferenceLevel": "high",
    "omRequirement": "high",
    "supportCondition": "outer_support_only",
    "targetMarket": "CN",
    "recommendedPath": "Flexible support first",
    "standardizationLevel": "Non-standard review",
    "primaryRisks": [
      "Wind and global stability",
      "Operation path conflict",
      "Foundation disturbance around existing pipelines"
    ],
    "regionNote": "Use domestic load and detailing baseline, then prepare local technical clarification package.",
    "summary": "This is a high-span retrofit scenario with strong operation constraints. Compare support paths carefully and move early into a technical review gate."
  },
  {
    "id": "WB-002",
    "structureType": "water_plant_roof",
    "spanLevel": "low",
    "windLevel": "medium",
    "corrosionLevel": "medium",
    "interferenceLevel": "low",
    "omRequirement": "medium",
    "supportCondition": "roof_support_allowed",
    "targetMarket": "EU",
    "recommendedPath": "Rigid support first",
    "standardizationLevel": "Parameterized",
    "primaryRisks": [
      "Corrosion and durability",
      "Roof interface detail",
      "Region adaptation for technical file output"
    ],
    "regionNote": "Review Eurocode context and customer-facing technical file expectations.",
    "summary": "This scenario is closer to a parameterized product path, but still needs region-ready detailing and corrosion control."
  }
]
```

- [ ] **Step 3: Create the HTML shell**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/index.html` with:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PV Structure Intelligence Framework</title>
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <main class="app">
      <header class="hero">
        <p class="eyebrow">PV Structure Intelligence Framework</p>
        <h1>Product Mode</h1>
        <p class="subhead">A decision-guidance selector for WaterBase Mount scenarios.</p>
      </header>
      <section class="panel-grid">
        <form class="panel form-panel" id="selector-form">
          <label>Structure Type
            <select name="structureType">
              <option value="clear_water_tank">Clear water tank</option>
              <option value="water_plant_roof">Water plant roof</option>
            </select>
          </label>
          <label>Span Level
            <select name="spanLevel">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <label>Wind Level
            <select name="windLevel">
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <label>Corrosion Level
            <select name="corrosionLevel">
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <label>Interference Level
            <select name="interferenceLevel">
              <option value="low">Low</option>
              <option value="high">High</option>
            </select>
          </label>
          <label>O&amp;M Requirement
            <select name="omRequirement">
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <label>Support Condition
            <select name="supportCondition">
              <option value="roof_support_allowed">Roof support allowed</option>
              <option value="outer_support_only">Outer support only</option>
            </select>
          </label>
          <label>Target Market
            <select name="targetMarket">
              <option value="CN">China</option>
              <option value="EU">Europe</option>
            </select>
          </label>
          <button type="submit">Generate Recommendation</button>
        </form>
        <section class="panel result-panel" id="result-panel">
          <h2>Recommendation</h2>
          <p class="placeholder">Select scenario inputs to see the recommended path.</p>
        </section>
      </section>
    </main>
    <script src="./app.js"></script>
  </body>
</html>
```

- [ ] **Step 4: Create the CSS and JS**

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/styles.css` with:

```css
:root {
  --bg: #edf3f6;
  --panel: #ffffff;
  --ink: #17313d;
  --muted: #5b717b;
  --accent: #0d6e8a;
  --border: #d6e1e7;
}

* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Helvetica Neue", Arial, sans-serif;
  background: linear-gradient(180deg, #f4f8fa 0%, #e7eef2 100%);
  color: var(--ink);
}
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px;
}
.hero {
  margin-bottom: 24px;
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--accent);
  font-size: 12px;
}
.subhead {
  color: var(--muted);
}
.panel-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 8px 30px rgba(16, 48, 61, 0.06);
}
label {
  display: block;
  margin-bottom: 14px;
  font-size: 14px;
}
select, button {
  width: 100%;
  margin-top: 6px;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  font-size: 14px;
}
button {
  background: var(--accent);
  color: #fff;
  border: none;
  cursor: pointer;
}
.result-panel ul {
  padding-left: 20px;
}
.placeholder {
  color: var(--muted);
}
@media (max-width: 900px) {
  .panel-grid { grid-template-columns: 1fr; }
}
```

Write `/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/app.js` with:

```js
async function loadRules() {
  const response = await fetch("./data/product_mode_rules.json");
  return response.json();
}

function findBestMatch(rules, formData) {
  return rules.find((rule) =>
    Object.entries(formData).every(([key, value]) => rule[key] === value)
  );
}

function renderResult(resultPanel, rule) {
  if (!rule) {
    resultPanel.innerHTML = `
      <h2>Recommendation</h2>
      <p>No exact rule matched. This should enter a non-standard review gate.</p>
    `;
    return;
  }

  resultPanel.innerHTML = `
    <h2>Recommendation</h2>
    <p><strong>Path:</strong> ${rule.recommendedPath}</p>
    <p><strong>Level:</strong> ${rule.standardizationLevel}</p>
    <p><strong>Region note:</strong> ${rule.regionNote}</p>
    <h3>Main risks</h3>
    <ul>${rule.primaryRisks.map((risk) => `<li>${risk}</li>`).join("")}</ul>
    <h3>Summary</h3>
    <p>${rule.summary}</p>
  `;
}

async function init() {
  const rules = await loadRules();
  const form = document.getElementById("selector-form");
  const resultPanel = document.getElementById("result-panel");

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = Object.fromEntries(new FormData(form).entries());
    const rule = findBestMatch(rules, formData);
    renderResult(resultPanel, rule);
  });
}

init();
```

- [ ] **Step 5: Verify the demo**

Run:

```bash
python3 -m json.tool '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo/data/product_mode_rules.json' >/dev/null
python3 -m http.server 8000 --directory '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo'
```

Expected:
- the JSON validation command exits with code 0
- the static server starts, and `http://localhost:8000` loads the page

- [ ] **Step 6: Commit**

```bash
git add '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework/05_Interactive_Demo'
git commit -m "feat: add product mode demo scaffold"
```

### Task 6: Final verification and packaging check

**Files:**
- Modify: none
- Test: repository status, plan coverage, and export artifacts

- [ ] **Step 1: Verify the planned files exist**

Run:

```bash
find '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework' -maxdepth 3 -type f | sort
```

Expected: the framework root, core docs, evidence docs, Product Mode docs, CATL skeleton, and demo files all appear.

- [ ] **Step 2: Verify git status**

Run:

```bash
git status --short
```

Expected: only the intended framework files and any docx export created in Task 4 appear as new tracked files.

- [ ] **Step 3: Confirm spec coverage**

Manual check:

- Product architecture page source exists
- Standardization boundary source exists
- Multi-region adaptation source exists
- Commercial value source exists
- Demo first version exists
- Scenario logic table exists
- One real case mapping exists

Expected: all seven immediate-next-step items from the spec are covered.

- [ ] **Step 4: Commit**

```bash
git add '/Users/xiachen/Documents/Interview for PV Mounting System Product Manager/PV_Structure_Intelligence_Framework'
git commit -m "chore: complete phase 1 framework assets"
```
