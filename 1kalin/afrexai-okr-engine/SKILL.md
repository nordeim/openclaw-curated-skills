# OKR & Goal Alignment Engine

> A complete Objectives and Key Results system — from company vision to individual weekly tasks. No scripts, no dependencies. Pure methodology.

## When to Use This Skill

- Quarterly planning / OKR setting
- Cascading company goals to teams and individuals
- Mid-quarter check-ins and scoring
- Annual strategic planning
- Aligning cross-functional teams
- Evaluating goal quality before committing

---

## Phase 1: Strategic Foundation

Before writing OKRs, establish the strategic context.

### Company Context Brief

```yaml
company_context:
  mission: "[Why you exist — one sentence]"
  vision_3yr: "[Where you'll be in 3 years]"
  current_stage: "[Pre-revenue | Early | Growth | Scale | Mature]"
  annual_theme: "[One phrase that captures this year's focus]"
  revenue_target: "$[X] by [date]"
  headcount: [N]
  
  strategic_pillars:  # Max 3-4. Everything ladders to these.
    - name: "[Pillar 1]"
      why: "[Why this matters now]"
    - name: "[Pillar 2]"
      why: "[Why this matters now]"
    - name: "[Pillar 3]"
      why: "[Why this matters now]"

  constraints:  # Be honest about these
    - "[Budget constraint]"
    - "[Hiring constraint]"
    - "[Technical constraint]"
    - "[Market constraint]"
```

### Annual → Quarterly Breakdown

| Timeframe | Purpose | # Objectives | Review Cadence |
|-----------|---------|-------------|----------------|
| Annual | Direction setting, North Stars | 3-5 | Quarterly |
| Quarterly | Execution focus, measurable outcomes | 3-5 per team | Weekly |
| Monthly | Sprint-level milestones | N/A (use KR progress) | Weekly |
| Weekly | Individual commitments | 3-5 priorities | Daily |

**Rule: Quarterly OKRs are the primary unit.** Annual OKRs provide direction. Weekly priorities provide execution.

---

## Phase 2: Writing Objectives

### The Objective Formula

```
[Action verb] + [what you're changing] + [qualitative aspiration]
```

**Quality Test (all must pass):**

| Test | Question | ❌ Fail Example | ✅ Pass Example |
|------|----------|----------------|-----------------|
| Inspiring | Would someone get excited reading this? | "Improve database performance" | "Make our app feel instant for every user" |
| Directional | Does it point clearly without prescribing HOW? | "Migrate to AWS Lambda" | "Build infrastructure that scales effortlessly" |
| Time-bounded | Is the quarter enough time, but not too much? | "Eventually become profitable" | "Prove our unit economics work" |
| Memorable | Can you say it from memory in a meeting? | "Optimize cross-functional alignment of go-to-market activities" | "Win in enterprise sales" |
| Ambitious | Is there a 30-50% chance of NOT hitting it? | "Maintain current growth rate" | "Double our growth rate" |

### Objective Types by Strategic Intent

| Intent | Objective Pattern | When to Use |
|--------|------------------|-------------|
| **Build** | "Launch [X] that [outcome]" | New products, features, markets |
| **Grow** | "Accelerate [metric] by [doing X]" | Scaling what works |
| **Fix** | "Eliminate [problem] for [who]" | Fixing broken things |
| **Explore** | "Validate whether [hypothesis]" | Testing new ideas |
| **Defend** | "Protect [asset] from [threat]" | Retention, security, compliance |
| **Transform** | "Shift from [old] to [new]" | Major strategic pivots |

### Common Objective Mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| Too vague | "Improve customer experience" | "Make onboarding so smooth customers reach value in < 1 day" |
| Actually a KR | "Increase NPS to 50" | "Become the product customers can't stop recommending" |
| Business as usual | "Continue serving customers well" | Don't OKR it — that's a health metric |
| Too many | 7+ objectives | Cut to 3-5. If everything's a priority, nothing is |
| No stretch | 100% certain to achieve | Add the "and then what?" — push further |

---

## Phase 3: Writing Key Results

### The Key Result Formula

```
[Verb] [metric] from [baseline] to [target] by [date]
```

**Every KR must have:**
1. **A number** — if you can't measure it, it's not a KR
2. **A baseline** — where you are today
3. **A target** — where you want to be
4. **A date** — by when (usually end of quarter)

### KR Quality Scoring (0-10)

| Dimension | 0-3 (Weak) | 4-6 (OK) | 7-10 (Strong) |
|-----------|-----------|----------|---------------|
| Measurable | Subjective ("improve quality") | Proxy metric available | Exact metric with dashboard |
| Baseline known | "We don't track this yet" | Rough estimate available | Precise current number |
| Ambitious | Already on track to hit | Requires some new effort | Requires focused execution |
| Outcome-based | Measures activity | Measures output | Measures business impact |
| Within control | Depends on external factors | Partially controllable | Team has 80%+ influence |

**Minimum score: 6/10 per dimension before committing.**

### KR Types (use a mix)

| Type | What It Measures | Example | When to Use |
|------|-----------------|---------|-------------|
| **Metric KR** | Quantitative change | "Increase WAU from 10K to 25K" | When you have data |
| **Milestone KR** | Binary completion of outcome | "Launch v2.0 with 5 enterprise customers live" | For new initiatives |
| **Threshold KR** | Maintain a standard | "Keep uptime above 99.95%" | For defend objectives |
| **Learning KR** | Validated understanding | "Interview 30 enterprise buyers and identify top 3 objections" | For explore objectives |

### KR Scoring Method

| Score | Meaning | Action |
|-------|---------|--------|
| 0.0 | No progress | Root cause analysis required |
| 0.1-0.3 | Significant miss | Needs retro — was it the right goal? |
| 0.4-0.6 | Partial | Healthy if ambitious. Learn and adjust |
| 0.7 | Target | Sweet spot for stretch goals |
| 0.8-0.9 | Strong delivery | Were we ambitious enough? |
| 1.0 | Full achievement | Goal may have been too easy |

**Healthy team average: 0.6-0.7.** If averaging 0.9+, you're sandbagging.

---

## Phase 4: Cascading OKRs

### The Cascade Architecture

```
Company OKR (CEO/Leadership)
  ├── Department OKR (VP/Director) — contributes to company KR
  │     ├── Team OKR (Manager) — contributes to department KR
  │     │     ├── Individual Priorities (IC) — contributes to team KR
  │     │     └── Individual Priorities (IC)
  │     └── Team OKR (Manager)
  └── Department OKR (VP/Director)
```

### Cascade Template

```yaml
company_okr:
  objective: "[Company-level objective]"
  key_results:
    - kr: "Increase ARR from $2M to $5M"
      id: "C-KR1"
      owner: "CRO"
      
department_okrs:
  - department: "Sales"
    objective: "Build a repeatable enterprise sales motion"
    contributes_to: "C-KR1"  # Link to company KR
    key_results:
      - kr: "Close 15 new enterprise deals (>$50K ACV)"
        id: "S-KR1"
        owner: "VP Sales"
      - kr: "Reduce sales cycle from 90 to 60 days"
        id: "S-KR2"
        owner: "VP Sales"

  - department: "Product"
    objective: "Make the product enterprise-ready"
    contributes_to: "C-KR1"  # Same company KR, different angle
    key_results:
      - kr: "Ship SSO, audit logs, and role-based access"
        id: "P-KR1"
        owner: "VP Product"
      - kr: "Achieve SOC 2 Type II certification"
        id: "P-KR2"
        owner: "VP Engineering"

team_okrs:
  - team: "Enterprise Sales Team"
    department: "Sales"
    objective: "Win marquee logos that open market categories"
    contributes_to: "S-KR1"
    key_results:
      - kr: "Close 3 Fortune 500 accounts"
        id: "ES-KR1"
        owner: "Enterprise AE Lead"
      - kr: "Build 40 qualified enterprise opportunities"
        id: "ES-KR2"
        owner: "Enterprise SDR Lead"
```

### Cascade Rules

1. **Each level adds specificity, not just smaller numbers** — don't just split "100 customers" into "25 per team"
2. **Not every company KR needs every department** — only cascade where there's genuine contribution
3. **Cross-functional KRs need one owner** — shared ownership = no ownership
4. **Max depth: 3 levels** — Company → Department → Team. Individuals use weekly priorities, not OKRs
5. **Alignment ≠ cascading** — Teams can have 1-2 OKRs that don't cascade (team health, innovation)

### Cross-Functional Alignment Matrix

For KRs that require multiple teams:

```yaml
cross_functional_kr:
  kr: "Reduce time-to-value from 14 days to 3 days"
  primary_owner: "VP Product"
  
  contributions:
    - team: "Product"
      commitment: "Ship guided onboarding wizard"
      deadline: "Week 6"
      
    - team: "Engineering"
      commitment: "Build self-serve provisioning API"
      deadline: "Week 4"
      
    - team: "Customer Success"
      commitment: "Create 5 onboarding playbooks by segment"
      deadline: "Week 3"
      
    - team: "Sales"
      commitment: "Set realistic TTV expectations in deal cycle"
      deadline: "Ongoing"

  sync_cadence: "Weekly cross-functional standup, Tuesdays 10am"
  escalation: "[Primary owner] resolves conflicts within 48h"
```

---

## Phase 5: Weekly Execution System

### From KRs to Weekly Priorities

```yaml
weekly_plan:
  week: "W3 of Q1 2026"
  team: "[Team Name]"
  
  kr_progress:
    - kr_id: "T-KR1"
      target: 100
      current: 35
      on_track: true
      confidence: "🟢 High"
      
    - kr_id: "T-KR2"
      target: 50
      current: 8
      on_track: false
      confidence: "🔴 At Risk"
      blocker: "Waiting on API access from partner"
      
  priorities_this_week:  # Max 3-5 per person
    - who: "Alice"
      priorities:
        - "Complete partner API integration [T-KR2]"
        - "Review 3 enterprise pilot proposals [T-KR1]"
        - "Prepare board deck section on pipeline"
        
    - who: "Bob"
      priorities:
        - "Ship onboarding email sequence [T-KR3]"
        - "Run 5 customer discovery calls [T-KR1]"
```

### Weekly Check-in Template (15 min max)

```
1. CONFIDENCE SCORES (2 min)
   - Each KR: 🟢 On Track | 🟡 Needs Attention | 🔴 At Risk
   
2. AT-RISK DEEP DIVE (5 min)
   - What's blocking? When will it unblock?
   - Do we need to adjust the KR or the approach?
   
3. PRIORITIES THIS WEEK (5 min)
   - Each person: top 3 commitments linked to KRs
   
4. HELP NEEDED (3 min)
   - Cross-team dependencies, escalations, decisions
```

### Confidence Assessment Guide

| Signal | 🟢 On Track | 🟡 Needs Attention | 🔴 At Risk |
|--------|------------|--------------------|-----------| 
| Progress vs. linear | ≥80% of expected | 50-80% of expected | <50% of expected |
| Blockers | None | Identified, plan exists | Unresolved, no clear path |
| Dependencies | Met or on track | Delayed but recoverable | Delayed, threatens KR |
| Team capacity | Sufficient | Tight but manageable | Insufficient |
| External factors | Favorable | Neutral | Unfavorable |

---

## Phase 6: Mid-Quarter Review (Week 6)

### Review Agenda (60 min)

```
1. SCORE ALL KRs (15 min)
   - Current score (0.0-1.0) per KR
   - Projected end-of-quarter score
   
2. DIAGNOSE (20 min)
   - Why are at-risk KRs behind?
   - Root cause: wrong target? wrong approach? wrong resourcing?
   
3. DECIDE (15 min)
   For each at-risk KR, choose one:
   □ RECOMMIT — same target, change approach
   □ ADJUST — lower target with documented reasoning
   □ ABANDON — kill the KR (redirect resources)
   □ ESCALATE — needs leadership decision or cross-team help
   
4. RESOURCE REBALANCE (10 min)
   - Can we move people/effort from green KRs to red ones?
   - Any new information that changes priorities?
```

### Mid-Quarter Health Score

| Dimension | Weight | Score (1-10) |
|-----------|--------|-------------|
| KR progress vs. linear | 25% | |
| Team confidence average | 20% | |
| Blocker resolution speed | 15% | |
| Cross-team alignment | 15% | |
| Leading indicators trending right | 15% | |
| Team energy/morale | 10% | |
| **Weighted Total** | **100%** | **/10** |

**Interpretation:**
- 8-10: Strong quarter. Maintain cadence.
- 6-7: Normal. Address specific gaps.
- 4-5: Concerning. Major course correction needed.
- 1-3: Quarter is failing. Emergency replanning session.

---

## Phase 7: End-of-Quarter Scoring & Retrospective

### Final Scoring

```yaml
quarter_results:
  quarter: "Q1 2026"
  team: "[Team Name]"
  
  objectives:
    - objective: "[Objective text]"
      score: 0.7  # Average of KR scores
      key_results:
        - kr: "[KR text]"
          target: 100
          actual: 72
          score: 0.72
          learning: "Conversion rate assumption was wrong — need better qualification"
          
        - kr: "[KR text]"  
          target: 50
          actual: 50
          score: 1.0
          learning: "Target was too conservative — should have been 75"

  overall_score: 0.65
  narrative: "[2-3 sentences: What did we achieve? What did we learn? What changes for next quarter?]"
```

### Retrospective Questions

**What worked:**
1. Which KRs exceeded expectations? Why?
2. What processes or habits drove success?
3. What should we keep doing?

**What didn't work:**
1. Which KRs missed significantly? Root cause?
2. Were any objectives wrong to pursue in hindsight?
3. What did we learn about our capabilities?

**Next quarter inputs:**
1. What unfinished work carries over?
2. What new information changes our strategy?
3. What do we stop doing?

### Score Calibration Across Teams

To prevent sandbagging and ensure fairness:

| Pattern | Diagnosis | Fix |
|---------|-----------|-----|
| Team averages 0.9+ every quarter | Goals too easy | Require 2x stretch on next cycle |
| Team averages 0.3 every quarter | Goals unrealistic OR execution problem | Review goal-setting process AND team capacity |
| Wide variance (some 1.0, some 0.1) | Poor prioritization | Focus on fewer, more impactful OKRs |
| All teams score similarly | Possible social norming | Introduce peer calibration |

---

## Phase 8: OKR Anti-Patterns & Fixes

### The 12 Most Common OKR Failures

| # | Anti-Pattern | Symptom | Fix |
|---|-------------|---------|-----|
| 1 | **Too many OKRs** | Team can't remember them | Max 3 objectives, 3-4 KRs each |
| 2 | **Output not outcome** | KRs track tasks ("Ship feature X") | Ask "So what?" — what changes after shipping? |
| 3 | **No baseline** | "Improve NPS" (from what?) | Measure baseline BEFORE setting target |
| 4 | **Set and forget** | Written in week 1, reviewed in week 12 | Weekly check-ins mandatory |
| 5 | **Tied to compensation** | Sandbagging, gaming, risk aversion | Separate OKRs from performance reviews |
| 6 | **Top-down only** | No team buy-in | 40% top-down, 60% bottom-up |
| 7 | **KRs are tasks** | "Complete migration" | Task ≠ KR. What outcome does migration drive? |
| 8 | **Binary KRs** | "Launch product" (done or not) | Add quality/quantity dimension: "Launch with 100 beta users and 4.5★ rating" |
| 9 | **Vanity metrics** | "Reach 1M page views" | Use metrics that correlate with business value |
| 10 | **No owner** | "The team owns it" | One person accountable per KR |
| 11 | **Quarterly waterfall** | Treat OKRs as fixed project plans | OKRs are outcomes — approach can change mid-quarter |
| 12 | **Perfecting the process** | Endless debates about OKR formatting | Good enough OKRs executed > perfect OKRs debated |

---

## Phase 9: OKR Templates by Company Stage

### Startup (Pre-PMF, <20 people)

```yaml
# Keep it SIMPLE. 1-2 company OKRs. No cascading.
company_okrs:
  - objective: "Prove customers will pay for our solution"
    key_results:
      - "Sign 10 paying customers (not free trials)"
      - "Achieve 40%+ 'very disappointed' on Sean Ellis test"
      - "Reach $15K MRR with zero paid acquisition"
    
  - objective: "Build a product people use daily"
    key_results:
      - "Reach 60% DAU/MAU ratio"
      - "Reduce time-to-value from 7 days to same-day"
      - "Get 5 customers who proactively refer others"
```

### Growth Stage (PMF proven, 20-200 people)

```yaml
# 3-4 company OKRs. Cascade to departments.
company_okrs:
  - objective: "Scale revenue predictably"
    key_results:
      - "Grow ARR from $2M to $5M"
      - "Achieve 120%+ net revenue retention"
      - "Reduce CAC payback from 18 to 12 months"
      
  - objective: "Build the team that builds the company"
    key_results:
      - "Hire 15 A-players (>4.0 scorecard average)"
      - "Achieve 90%+ new hire retention at 6 months"
      - "Every manager completes leadership training"
      
  - objective: "Expand into enterprise segment"
    key_results:
      - "Close 5 enterprise deals (>$100K ACV)"
      - "Ship SOC 2 + SSO + audit logs"
      - "Build 3 enterprise case studies"
```

### Enterprise / Scale (200+ people)

```yaml
# Max 5 company OKRs. Cascade to departments + teams.
# Include 1 "innovation" objective to prevent bureaucratic drift.
company_okrs:
  - objective: "Dominate our core market"
    key_results:
      - "Reach #1 market share in [segment]"
      - "Achieve $50M ARR"
      - "Win 3 competitive displacements from [incumbent]"
      
  - objective: "Build our next growth engine"
    key_results:
      - "Launch v1 of [new product] with 50 beta customers"
      - "Validate $10M+ TAM with 20 customer interviews"
      - "Hire founding team lead for new business unit"
```

---

## Phase 10: OKRs for Special Contexts

### Engineering Team OKRs

| Don't | Do |
|-------|-----|
| "Complete 100% of sprint tickets" | "Reduce P1 incidents from 8/month to 2/month" |
| "Improve code quality" | "Reduce escaped defects from 15% to 5% of releases" |
| "Modernize architecture" | "Reduce deploy time from 2 hours to 15 minutes" |
| "Pay down tech debt" | "Reduce mean time to onboard new engineer from 3 weeks to 1 week" |

### Sales Team OKRs

| Don't | Do |
|-------|-----|
| "Make 200 cold calls per week" | "Generate 40 SQLs from outbound" |
| "Increase pipeline" | "Build $2M qualified pipeline with >30% close rate" |
| "Close more deals" | "Increase average deal size from $25K to $40K ACV" |

### Marketing Team OKRs

| Don't | Do |
|-------|-----|
| "Post 3x per week on social" | "Generate 500 MQLs from content marketing" |
| "Redesign the website" | "Increase website-to-trial conversion from 2% to 5%" |
| "Increase brand awareness" | "Achieve 30% unaided brand recall in target segment" |

### Customer Success Team OKRs

| Don't | Do |
|-------|-----|
| "Conduct 100 QBRs" | "Achieve 95%+ gross retention rate" |
| "Respond to tickets faster" | "Reduce time-to-resolution from 48h to 12h" |
| "Upsell more" | "Grow expansion revenue from 15% to 25% of total" |

---

## Phase 11: 100-Point OKR Quality Rubric

Score your OKRs before committing:

| Dimension | Weight | Criteria | Score |
|-----------|--------|----------|-------|
| **Strategic Alignment** | 15 | Every objective ladders to company strategy | /15 |
| **Ambition Level** | 15 | 30-50% chance of missing (stretch but not fantasy) | /15 |
| **Measurability** | 15 | Every KR has a number, baseline, and target | /15 |
| **Outcome Focus** | 15 | KRs measure results, not activities | /15 |
| **Scope** | 10 | 3-5 objectives, 2-4 KRs each (no bloat) | /10 |
| **Ownership** | 10 | Every KR has exactly one owner | /10 |
| **Cascade Clarity** | 10 | Clear links between levels, no orphans | /10 |
| **Executability** | 10 | Team knows what to do Monday morning | /10 |
| **Total** | **100** | | **/100** |

**Grading:**
- 90-100: Ship it. Start executing.
- 75-89: Good. Minor refinements then go.
- 60-74: Needs work. Revisit weak dimensions.
- Below 60: Rewrite. Fundamental issues.

---

## Natural Language Commands

| Command | What It Does |
|---------|-------------|
| "Set company OKRs for Q[N]" | Guide through strategic foundation → objective → KR writing |
| "Cascade [objective] to [team]" | Generate department/team OKRs aligned to company OKR |
| "Score our OKRs" | Run 100-point quality rubric on current OKRs |
| "Weekly check-in for [team]" | Generate weekly progress template with confidence scores |
| "Mid-quarter review" | Run mid-quarter health assessment |
| "Score Q[N] results" | Guide through end-of-quarter scoring |
| "Help me write a KR for [goal]" | Coach through the KR formula with quality checks |
| "Are these OKRs or tasks?" | Evaluate whether items are true OKRs or disguised task lists |
| "OKR retro for Q[N]" | Run full retrospective with next-quarter inputs |
| "Compare [team A] vs [team B] OKRs" | Check for alignment, gaps, and conflicts |
| "What's wrong with this OKR?" | Diagnose anti-patterns and suggest fixes |
| "Generate weekly priorities from OKRs" | Break KRs into this week's actionable priorities |

---

## Edge Cases

### First Time Doing OKRs
- Start with company-level only. No cascading.
- Run a "practice quarter" — score but don't tie to anything.
- Common mistake: making them too easy to "prove OKRs work." Resist.

### Remote/Distributed Teams
- Async weekly updates (written, not meetings)
- Over-document confidence reasoning
- Use shared dashboards, not verbal updates

### OKRs During Uncertainty (Pivoting, Market Shifts)
- Shorten cycle to 6-week OKRs
- Use more "learning KRs" and fewer "metric KRs"
- Build in explicit review points with pivot criteria

### Integrating OKRs with Agile/Scrum
- OKRs = quarterly outcomes
- Sprints = 2-week execution chunks toward KRs
- Sprint goals should map to KRs
- Don't create separate sprint OKRs — that's overhead, not alignment

### OKRs for Solo Founders
- Max 2 objectives per quarter
- 2-3 KRs each
- Weekly self-review (5 min) — be honest about confidence
- Share with an accountability partner or advisor

---

*Built by AfrexAI — the AI workforce company. Free skills that actually work.*
