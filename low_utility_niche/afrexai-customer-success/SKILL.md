---
name: Customer Success Engine
description: Complete customer success, retention, and expansion revenue system. Use for churn prevention, health scoring, onboarding optimization, QBR preparation, expansion playbooks, win-back campaigns, and CS team operations.
metadata:
  category: business
  skills: ["customer-success", "retention", "churn", "expansion", "onboarding", "health-score", "nrr"]
---

# Customer Success Engine

Complete system for preventing churn, driving expansion, and turning customers into advocates. Covers the full lifecycle from onboarding through renewal and growth.

---

## Phase 1: Customer Health Scoring

### Health Score Model (0-100)

Build a composite score from leading indicators. Weight by your business model.

**Score Components:**

| Dimension | Weight | Signals | Scoring |
|-----------|--------|---------|---------|
| Product Usage | 30% | DAU/MAU ratio, feature breadth, core action frequency | <20% DAU/MAU = 0-3, 20-40% = 4-6, >40% = 7-10 |
| Engagement | 20% | Login trend (up/flat/down), support tickets, community activity | Declining = 0-3, Flat = 4-6, Growing = 7-10 |
| Relationship | 15% | Champion identified, exec sponsor, multi-threaded | No champion = 0-3, Champion only = 4-6, Multi-thread = 7-10 |
| Outcomes | 20% | Stated goals tracked, ROI documented, success milestones hit | 0 goals met = 0-3, Some = 4-6, All = 7-10 |
| Financial | 15% | Payment history, contract value trend, expansion signals | Late payments = 0-3, On-time = 4-6, Expanding = 7-10 |

**Health Tiers:**

| Score | Tier | Color | Action |
|-------|------|-------|--------|
| 80-100 | Thriving | 🟢 Green | Expansion plays, advocacy asks |
| 60-79 | Healthy | 🟡 Yellow | Monitor, nurture, prepare upsell |
| 40-59 | At-Risk | 🟠 Orange | Intervention plan within 48 hours |
| 0-39 | Critical | 🔴 Red | Executive escalation, save plan within 24 hours |

### Health Score YAML Template

```yaml
customer_health:
  account: "[Company Name]"
  arr: 0
  tier: "enterprise|mid-market|smb"
  csm: "[CSM Name]"
  renewal_date: "YYYY-MM-DD"
  scores:
    product_usage:
      score: 0  # 0-10
      dau_mau_ratio: 0.0
      core_actions_weekly: 0
      features_adopted: 0  # out of total available
      trend: "up|flat|down"
    engagement:
      score: 0
      login_trend: "up|flat|down"
      support_tickets_30d: 0
      last_proactive_contact: "YYYY-MM-DD"
      community_active: false
    relationship:
      score: 0
      champion: "[Name, Title]"
      exec_sponsor: "[Name, Title]"
      contacts_count: 0
      last_exec_touch: "YYYY-MM-DD"
    outcomes:
      score: 0
      goals_defined: 0
      goals_achieved: 0
      roi_documented: false
      last_success_milestone: ""
    financial:
      score: 0
      payment_status: "current|late|delinquent"
      expansion_signals: []
      contraction_risk: false
  composite_score: 0  # Weighted calculation
  tier: "thriving|healthy|at-risk|critical"
  last_updated: "YYYY-MM-DD"
```

---

## Phase 2: Onboarding (First 90 Days)

The first 90 days determine whether a customer stays for years or churns at renewal.

### Time-to-First-Value (TTFV) Framework

**Goal:** Get every customer to their "aha moment" as fast as possible.

**Step 1 — Define the Aha Moment by Segment:**

| Segment | Aha Moment | Target TTFV |
|---------|-----------|-------------|
| Enterprise | First workflow automated + team adopted | 30 days |
| Mid-Market | Core use case live + 3 users active | 14 days |
| SMB | First value-generating action completed | 24 hours |
| Self-serve | Core action completed | 10 minutes |

**Step 2 — Onboarding Milestones:**

```
Week 1: Technical Setup
  □ Account provisioned and configured
  □ Integration(s) connected
  □ Admin trained on core settings
  □ Success plan created (goals, timeline, stakeholders)
  □ Kickoff call completed — attendees: champion + exec sponsor

Week 2-3: Core Adoption
  □ Primary use case configured
  □ First 5 users activated
  □ Core workflow running
  □ Quick win documented and shared with sponsor

Week 4-6: Expansion Adoption
  □ Second use case identified and configured
  □ 80% of licensed users active
  □ Self-service resources shared (docs, videos, community)
  □ 30-day check-in: review progress vs success plan

Week 7-12: Optimization
  □ Advanced features introduced
  □ Workflow optimization session
  □ ROI calculation (first draft)
  □ 90-day review: success plan scorecard, next quarter goals
```

### Onboarding Risk Signals

Flag immediately if any of these appear during onboarding:

| Signal | Severity | Response |
|--------|----------|----------|
| Champion leaves company | 🔴 Critical | Find new champion within 48h, re-establish exec relationship |
| No login after Day 3 | 🟠 High | Personal outreach (call, not email) |
| Integration fails | 🟠 High | Escalate to engineering, provide workaround |
| Kickoff delayed >1 week | 🟡 Medium | Escalate internally, offer flexible scheduling |
| <50% user activation by Day 30 | 🟡 Medium | User adoption campaign (training, incentives) |
| No exec sponsor identified | 🟡 Medium | Ask champion to intro their manager |

### Success Plan Template

```yaml
success_plan:
  account: "[Company Name]"
  created: "YYYY-MM-DD"
  owner: "[CSM Name]"
  stakeholders:
    champion: { name: "", title: "", email: "" }
    exec_sponsor: { name: "", title: "", email: "" }
    technical_lead: { name: "", title: "", email: "" }
  business_objectives:
    - objective: "[What they want to achieve]"
      metric: "[How we'll measure it]"
      baseline: "[Current state]"
      target: "[Goal state]"
      timeline: "[By when]"
  use_cases:
    - name: "[Use case]"
      status: "not-started|in-progress|live|optimizing"
      go_live_date: "YYYY-MM-DD"
  milestones:
    - name: "Technical Setup Complete"
      target_date: "YYYY-MM-DD"
      status: "pending|complete|at-risk"
    - name: "First Value Delivered"
      target_date: ""
      status: ""
    - name: "Full Adoption"
      target_date: ""
      status: ""
  risks:
    - risk: ""
      mitigation: ""
      owner: ""
  next_review: "YYYY-MM-DD"
```

---

## Phase 3: Ongoing Engagement & Lifecycle

### Touch Cadence by Tier

| Tier | Sync Meetings | Async Check-ins | QBRs | Executive Touch |
|------|--------------|-----------------|------|-----------------|
| Enterprise ($100K+) | Bi-weekly | Weekly | Quarterly | Quarterly |
| Mid-Market ($25-100K) | Monthly | Bi-weekly | Semi-annual | Semi-annual |
| SMB ($5-25K) | Quarterly | Monthly | Annual | None |
| Self-Serve (<$5K) | None (reactive) | Automated | None | None |

### Engagement Playbook by Health Tier

**🟢 Thriving (80-100):**
- Share product roadmap previews (make them feel insider)
- Ask for case study / testimonial / reference
- Introduce expansion opportunities
- Invite to beta programs and advisory board
- Request G2/Capterra review

**🟡 Healthy (60-79):**
- Proactive best-practice sharing
- Feature adoption campaign for unused capabilities
- Schedule optimization workshop
- Update and review success plan goals
- Strengthen multi-threading (meet more stakeholders)

**🟠 At-Risk (40-59):**
- 48-hour intervention plan required
- Root cause analysis: is it product, people, or process?
- Executive-to-executive outreach
- Offer dedicated support window or on-site visit
- Create 30-day recovery plan with weekly checkpoints

**🔴 Critical (0-39):**
- Same-day executive escalation
- Save call within 24 hours (CSM + manager + exec)
- Offer: dedicated implementation resource, contract restructure, product concessions
- Document blockers and get engineering commitment on fixes
- Daily check-in until health improves to Orange

### Lifecycle Email Sequences

**Adoption Nudge Sequence (triggered when feature adoption < 50%):**

```
Day 0: "You're missing out on [Feature] — here's what teams like yours do with it"
Day 3: "[Customer Name] saved 10 hours/week using [Feature] — quick setup guide"
Day 7: "Want a 15-min walkthrough of [Feature]? Here's my calendar link"
Day 14: [If no action] Flag for CSM personal outreach
```

**Renewal Prep Sequence (starts 90 days before renewal):**

```
Day -90: Internal — CSM reviews health score, usage data, open issues
Day -75: Success recap email — "Here's what you've achieved this year"
Day -60: ROI presentation — document value delivered
Day -45: Renewal discussion — terms, expansion, multi-year options
Day -30: Contract sent — if not signed, escalate
Day -14: Final follow-up — executive involvement if needed
Day -7: If unsigned — red alert, daily follow-up
```

---

## Phase 4: Churn Prevention

### Early Warning System

**Leading Indicators (detect 60-90 days before churn):**

| Indicator | Detection Method | Lead Time |
|-----------|-----------------|-----------|
| Usage decline >30% MoM | Automated monitoring | 90 days |
| Champion job change | LinkedIn monitoring, email bounce | 60-90 days |
| Support ticket spike then silence | Ticket trend analysis | 60 days |
| Billing page visits (no upgrade) | Product analytics | 45 days |
| Competitor evaluation | Web traffic, sales intel | 30-60 days |
| Data export requests | Product analytics | 30 days |
| Contract non-renewal signals | Procurement delays, legal questions | 30-45 days |
| Team member removals | License/seat changes | 30 days |

### Churn Reason Taxonomy

Classify every churn for pattern analysis:

| Category | Sub-Reasons | Preventable? |
|----------|-------------|-------------|
| Product | Missing feature, poor UX, bugs, performance | ✅ Partially |
| Value | ROI not realized, wrong use case, over-sold | ✅ Yes |
| Relationship | Champion left, poor CS experience, trust broken | ✅ Yes |
| Financial | Budget cuts, M&A, bankruptcy, price too high | ⚠️ Sometimes |
| Competition | Switched to competitor, built in-house | ✅ Partially |
| Strategic | Business pivot, division shut down, deprioritized | ❌ Rarely |

### Save Plays by Churn Reason

**Product gap:**
- Escalate to product team with revenue impact ($ARR at risk)
- Offer workaround or professional services to bridge gap
- Share roadmap with delivery commitment and timeline
- If feature is coming in <90 days, offer bridge discount

**Value not realized:**
- Re-onboard: new success plan, new goals, fresh training
- Assign senior CS resource or solutions architect
- Offer "value sprint" — 30-day intensive to prove ROI
- Document quick wins weekly and share with exec sponsor

**Champion left:**
- Within 48 hours: identify new primary contact
- Offer "new stakeholder onboarding" session
- Re-establish exec-to-exec relationship
- Provide business case document new champion can use internally

**Price objection:**
- Never discount without getting something back (multi-year, case study, referral)
- Restructure: remove unused features/seats, right-size the contract
- Offer payment terms (quarterly → annual = discount)
- Show ROI math: "You're paying $X, generating $Y in value"

**Competitor threat:**
- Competitive battlecard deployment
- Offer feature matching roadmap commitment
- Executive relationship leverage
- Switch cost analysis (show total cost of switching)

---

## Phase 5: Expansion Revenue

### Net Revenue Retention (NRR) Framework

**Target NRR by segment:**

| Segment | Good | Great | World-Class |
|---------|------|-------|-------------|
| Enterprise SaaS | 110% | 120% | 130%+ |
| Mid-Market SaaS | 105% | 110% | 120%+ |
| SMB SaaS | 95% | 100% | 110%+ |

**NRR Formula:** (Start MRR + Expansion - Contraction - Churn) / Start MRR × 100

### Expansion Signals

Watch for these buying signals:

| Signal | Strength | Play |
|--------|----------|------|
| Hitting usage limits | 🔥 Hot | Proactive upgrade conversation |
| New team/department asking about product | 🔥 Hot | Land-and-expand intro meeting |
| Requesting features on higher tier | 🔥 Hot | Demo premium tier capabilities |
| Company funding round or growth announcement | 🟡 Warm | Congratulate + "as you scale, here's how we help" |
| Champion promoted | 🟡 Warm | Congratulate + "bring product to your new scope" |
| High health score + approaching renewal | 🟡 Warm | Multi-year + expansion bundle |
| Requesting API access or integrations | 🟡 Warm | Platform/enterprise tier positioning |

### Expansion Playbooks

**Seat Expansion:**
1. Monitor seat utilization monthly
2. When >80% seats used: "You're almost at capacity — here's a volume tier that saves $X per seat"
3. Offer: bulk discount for 2x seats, annual commitment for better rate
4. Share adoption success: "Your team's usage is in the top 10% of our customers"

**Tier Upgrade:**
1. Identify which premium features align with their goals
2. Run a "premium preview" — trial of advanced features for 14 days
3. Calculate ROI of upgrade: "Feature X will save your team Y hours/month"
4. Offer: upgrade at renewal for price lock, or mid-cycle upgrade with pro-rata

**Cross-Sell (New Product):**
1. Map customer's tech stack and identify gaps you fill
2. Warm intro: share relevant case study from similar company
3. Offer pilot: "30-day proof of concept, no commitment"
4. Bundle pricing: "Add Product B for 20% less than standalone"

**Land-and-Expand (New Department):**
1. Ask champion: "Which other teams face similar challenges?"
2. Offer: free workshop for new department
3. Provide champion with internal pitch deck
4. New department = new success plan, new champion, separate health tracking

---

## Phase 6: Quarterly Business Reviews (QBRs)

### QBR Structure (60 Minutes)

```
1. Business Context (10 min)
   - Customer shares business updates, priorities, challenges
   - CS listens — do NOT present slides first

2. Value Delivered (15 min)
   - Usage dashboard: adoption, engagement, trends
   - ROI recap: goals set → outcomes achieved → dollar impact
   - Success stories: specific wins this quarter
   - Comparison: "Here's how you compare to peers in your industry"

3. Roadmap & Innovation (10 min)
   - Product roadmap aligned to THEIR priorities
   - Early access / beta opportunities
   - Industry trends and best practices

4. Success Plan Review (15 min)
   - Score previous quarter's goals
   - Set next quarter's objectives
   - Identify blockers and resource needs
   - Assign owners and timelines

5. Strategic Discussion (10 min)
   - "What keeps you up at night?"
   - "Where is the business heading in the next 12 months?"
   - Expansion opportunities (based on their strategy)
   - Introduce new stakeholders if relationship gaps exist
```

### QBR Prep Checklist

```
□ Pull 90-day usage data and create dashboard
□ Calculate ROI / value delivered (specific numbers)
□ Review health score trend (improving? declining?)
□ Check open support tickets — resolve before QBR
□ Review success plan — score each goal
□ Draft next quarter objectives (aligned to their business)
□ Prepare 1-2 expansion recommendations with ROI projections
□ Identify who should attend (their side + yours)
□ Send pre-read agenda 5 days before
□ Prepare competitive intel (in case competitors come up)
```

### Post-QBR Follow-Up Template

```
Subject: [Company] + [Your Company] — Q[X] Review Recap & Next Steps

Hi [Name],

Thank you for a productive review today. Here's a summary:

**What We Achieved in Q[X]:**
- [Goal 1]: [Result + metric]
- [Goal 2]: [Result + metric]
- [Goal 3]: [Result + metric]

**Q[X+1] Objectives:**
1. [Objective] — Owner: [Name], Target: [Date]
2. [Objective] — Owner: [Name], Target: [Date]
3. [Objective] — Owner: [Name], Target: [Date]

**Action Items:**
- [ ] [Action] — [Owner] by [Date]
- [ ] [Action] — [Owner] by [Date]

**Next QBR:** [Date]

Looking forward to another strong quarter together.

[Name]
```

---

## Phase 7: Win-Back Campaigns

### Win-Back Timing

| Time Since Churn | Approach | Success Rate |
|-----------------|----------|-------------|
| 0-30 days | "We miss you" + address churn reason | 15-25% |
| 30-90 days | Product update + improvement proof | 10-15% |
| 90-180 days | Major release + special offer | 5-10% |
| 180-365 days | Annual check-in + case study | 2-5% |
| >365 days | Remove from active campaigns | <2% |

### Win-Back Email Sequence

**Email 1 (Day 7 post-churn):**
```
Subject: We fixed [their specific issue]

Hi [Name],

I know [specific churn reason] was frustrating. I wanted you to know we've [specific improvement].

[If product: "Here's what changed: [feature/fix description]"]
[If value: "We've redesigned onboarding to get to value in [X days]"]
[If price: "We have new plans that might work better for your budget"]

No pressure — but if you'd like to take another look, I'm here.

[Name]
```

**Email 2 (Day 30):**
```
Subject: [Their industry] companies are seeing [specific result]

Hi [Name],

Since we last spoke, [similar company] achieved [specific metric] using [product].

We've shipped [X] improvements in the past month, including:
- [Improvement 1]
- [Improvement 2]

Would a quick catch-up be useful? Happy to show what's new.

[Name]
```

**Email 3 (Day 90 — major release only):**
```
Subject: [Product] [Version] — built with your feedback

Hi [Name],

We just launched [major feature/version] and your feedback directly influenced it.

[1-2 sentence description of what's new and why it matters to them]

I'd love to give you a private preview. Want to jump on a 15-minute call this week?

[Name]
```

---

## Phase 8: CS Metrics Dashboard

### Weekly CS Metrics

```yaml
cs_dashboard:
  week: "YYYY-WXX"
  portfolio:
    total_accounts: 0
    total_arr: 0
    health_distribution:
      green: { count: 0, arr: 0 }
      yellow: { count: 0, arr: 0 }
      orange: { count: 0, arr: 0 }
      red: { count: 0, arr: 0 }
  retention:
    gross_retention_rate: 0.0  # Target: >90%
    net_retention_rate: 0.0    # Target: >110%
    logo_retention_rate: 0.0   # Target: >85%
    arr_churned_mtd: 0
    arr_contracted_mtd: 0
  expansion:
    arr_expanded_mtd: 0
    expansion_pipeline: 0
    upsell_conversations: 0
    expansion_rate: 0.0  # Target: >15% annually
  engagement:
    avg_health_score: 0      # Target: >70
    health_score_trend: "up|flat|down"
    qbrs_completed: 0
    nps_score: 0             # Target: >50
    csat_score: 0.0          # Target: >4.5/5
  onboarding:
    active_onboardings: 0
    avg_ttfv_days: 0         # Target: <14 for MM, <30 for Ent
    onboarding_completion_rate: 0.0  # Target: >90%
  renewals:
    upcoming_30d: { count: 0, arr: 0 }
    upcoming_60d: { count: 0, arr: 0 }
    upcoming_90d: { count: 0, arr: 0 }
    on_track: 0
    at_risk: 0
```

### Monthly Review Questions

1. Which accounts moved from Green → Yellow or worse? Why?
2. Which accounts moved UP in health? What worked?
3. What's the #1 churn reason this month? Is it trending?
4. Are we multi-threaded in our top 10 accounts?
5. What expansion pipeline exists for next quarter?
6. Which CSMs are carrying at-risk concentration?
7. Are QBRs driving measurable behavior change?
8. What product feedback should we escalate to product team?

---

## Phase 9: Cohort Analysis & Retention Metrics

### Building a Retention Cohort Table

Track by signup month (or contract start). Measure at regular intervals.

**Example SaaS Retention Cohort:**

```
              Month 0  Month 1  Month 2  Month 3  Month 6  Month 12
Jan cohort    100%     92%      87%      84%      78%      68%
Feb cohort    100%     94%      90%      88%      82%      —
Mar cohort    100%     91%      85%      —        —        —
```

**What to look for:**
- **Vertical improvement:** Are newer cohorts retaining better? (product/onboarding improving)
- **Drop-off cliff:** Where's the steepest decline? (Month 1-2 = onboarding problem, Month 6-12 = value/renewal problem)
- **Cohort outliers:** Which cohort retained best? What was different? (marketing channel, sales rep, onboarding changes)
- **Revenue retention vs logo retention:** Are you keeping ARR even if losing logos? (expansion offsetting churn)

### Engagement-to-Retention Mapping

| Engagement Level | Behavior | Retention Prediction | Action |
|-----------------|----------|---------------------|--------|
| Power User | Daily, multi-feature, creates content | 95%+ renewal | Advocate program, expansion |
| Regular | 3-4x/week, core features | 85-95% | Feature adoption, optimization |
| Casual | 1-2x/week, limited features | 60-80% | Re-engagement campaign |
| Dormant | <1x/week or inactive | 20-40% | Urgent intervention |
| Ghost | No activity 30+ days | <20% | Win-back or churn prep |

---

## Phase 10: Advanced Patterns

### Segmented Retention Strategies

**By Company Size:**
- Enterprise: relationship-driven, executive alignment, dedicated CSM, custom integrations
- Mid-Market: process-driven, scalable touch model, pooled CS with named CSM
- SMB: product-driven, self-service resources, automated engagement, 1:many CS

**By Customer Maturity:**
- Year 1: Onboarding focus, TTFV, quick wins, habit formation
- Year 2: Optimization, expansion, deeper integration, advocacy
- Year 3+: Strategic partnership, executive alignment, platform consolidation, co-innovation

### Customer Advisory Board (CAB)

**Structure:**
- 8-12 customers, mix of segments and industries
- Quarterly virtual meetings (90 min) + annual in-person
- Topics: product roadmap input, market trends, peer networking
- Incentive: early access to features, direct access to product leadership, recognition

**Selection criteria:**
- Health score >70
- Active for >6 months
- Willing to provide candid feedback
- Represents a strategic segment or use case

### Voice of Customer (VoC) Program

**Collection Points:**
1. NPS survey: quarterly (relationship) + post-interaction (transactional)
2. CSAT: after support tickets, after onboarding, after QBR
3. In-app feedback: feature requests, bug reports, satisfaction micro-surveys
4. Win/loss interviews: 30-min call within 2 weeks of decision
5. Churn interviews: exit survey + optional call
6. Advisory board: structured feedback sessions

**Action Framework:**
- Score 0-6 (Detractor): Personal outreach within 24h, root cause, recovery plan
- Score 7-8 (Passive): Follow up with improvement survey, feature education
- Score 9-10 (Promoter): Thank you, ask for review/referral/case study

### Multi-Product Customer Success

When a customer uses multiple products:
- Unified health score (weighted by product ARR contribution)
- Single CSM as primary, product specialists as needed
- Cross-product adoption: "Since you use Product A for X, Product B handles Y"
- Bundled QBRs: one strategic review covering all products
- Cross-product churn risk: losing one product increases risk for others

---

## Edge Cases

### Mergers & Acquisitions
- Customer acquires company: opportunity to expand (new users/departments)
- Customer gets acquired: risk — new leadership may consolidate vendors. Get ahead: meet new stakeholders, re-prove value, prepare competitive defense
- You get acquired: proactive communication, continuity assurance, retention incentives

### Seasonal Businesses
- Adjust health scoring for expected usage dips (don't flag summer slowdown as churn risk)
- Front-load engagement before peak season
- QBRs timed to pre-season planning

### Champion Burnout
- If your champion is carrying the product internally with no support, help them: provide internal presentation decks, ROI docs, and executive summaries they can share
- Reduce their burden: offer admin training for their team, self-service resources
- Celebrate their wins publicly (with permission) to increase their internal visibility

### Economic Downturn
- Proactive outreach: "We know budgets are tight — let's review your ROI together"
- Offer: right-size contracts, payment flexibility, ROI workshops
- Position as cost-saving: "Here's what you'd spend replacing us with manual work"
- Lock in multi-year at current rate before price increases

### High-Touch to Low-Touch Transition
- When downgrading a customer's CS tier (e.g., after contraction):
- Communicate clearly: "Here's what changes and what stays the same"
- Provide self-service toolkit to replace CSM meetings
- Set up automated health monitoring with escalation triggers
- Transition call: introduce new support model, share resources

---

## Natural Language Commands

Use these to interact with the system:

1. **"Score [account]"** — Run health score calculation
2. **"Onboarding plan for [account]"** — Generate 90-day onboarding plan
3. **"QBR prep for [account]"** — Generate QBR agenda, data summary, and recommendations
4. **"Churn risk for [account]"** — Analyze leading indicators and generate risk assessment
5. **"Expansion opportunities for [account]"** — Identify and score expansion plays
6. **"Win-back plan for [account]"** — Generate win-back sequence based on churn reason
7. **"Renewal prep for [account]"** — Generate renewal timeline, risk assessment, and talk track
8. **"Portfolio review"** — Generate weekly CS dashboard from all tracked accounts
9. **"Cohort analysis"** — Build retention cohort table from customer data
10. **"Success plan for [account]"** — Generate or update success plan with goals and milestones
11. **"Save play for [account]"** — Generate intervention plan for at-risk customer
12. **"NRR report"** — Calculate net revenue retention with expansion/contraction breakdown
