# Forge Deployment Examples

Curated deployment scenarios for Forge V3.2–V4 across different sizes and domains.

---

## 1. Solo Developer & One-Person Business

### 1.1 Personal AI Lab

**Size:** 1 Person  
**Goal:** Private AI lab for code review, research notes, and experiment tracking.

- **Infrastructure:** Local OpenClaw + Docker, PostgreSQL on laptop.
- **Tiers:** Only Tier 1 (10 REP) used; Tier 2/3 reserved for future collaborators.
- **Agents:** CodeReviewer, ResearchSummarizer, NoteIndexer.
- **Economy:** No external M2M; internal "compute credits" for tracking usage.
- **Why Forge:** Same architecture as bigger orgs, but fully local and private.

### 1.2 Solopreneur with 4 Core Agents [web:301][web:304][web:307][web:310]

**Size:** 1 Person (founder/freelancer/creator)  
**Goal:** Scale like a 5-person team without hiring anyone.

- **Infra:** Cloud (Vercel/Netlify + Optimism testnet), lightweight K8s or Docker.
- **The 4 Agent Stack:**
  1. **Marketing Agent:** Content creation, SEO optimization, social scheduling [web:296][web:300]
     - Tools: LLM for drafts, SocialSchedulerAgent, SEO-Agent
     - M2M: Pays ImageGenerator for visuals, BuyerAgent for stock photos
  2. **Sales Agent:** Lead qualification, email sequences, demo booking [web:306]
     - Tools: CRM integration, EmailAgent, CalendarAgent
     - M2M: Pays LeadEnrichmentAgent for prospect data
  3. **Operations Agent:** Invoice generation, data sync, task tracking [web:301]
     - Tools: Airtable/Notion sync, InvoiceBot, ReportAgent
     - M2M: Pays AccountingAgent for bookkeeping
  4. **Support Agent:** 24/7 chatbot, ticket triage, FAQ answers [web:301]
     - Tools: Chatbot on website, TicketAgent, KnowledgeBaseAgent
     - M2M: Pays AnalyticsAgent for satisfaction reports

- **Tiers:**  
  - Tier 0: Public (read-only access to blog/docs)
  - Tier 1: Solo founder (full control)
  - Tier 2/3: Reserved for future contractors or partners

- **M2M Economy:**  
  - Founder allocates monthly "compute budget" to each agent.
  - Agents trade services (e.g., Marketing pays Sales for qualified leads).
  - Dashboard shows ROI per agent → adjust budgets monthly.

- **Real Results:** [web:301]
  - 60% less time on content creation
  - 24/7 support with zero staff
  - 10x content output vs. manual work

---

### 1.3 Department-Level Deployment: Marketing Team [web:296][web:298][web:300][web:303][web:309]

**Size:** 5–15 people (CMO + content, demand gen, ops)  
**Goal:** Automate repetitive marketing workflows, prove ROI, scale without headcount.

#### Specialized Marketing Agents

1. **Content Creation Agent:** [web:300][web:309]
   - Research trending topics via APIs
   - Generate SEO-optimized blog drafts (brand voice preserved)
   - Produce social variants for each platform
   - M2M: Pays DesignAgent for graphics, SEO-Agent for keyword research

2. **ABM (Account-Based Marketing) Agent:** [web:298][web:300]
   - Build ICP (Ideal Customer Profile) from CRM + intent data
   - Create personalized email sequences per account
   - Track engagement and hand off hot leads to Sales
   - M2M: Buys enrichment data from DataProviderAgent

3. **Distribution & Scheduling Agent:** [web:300][web:309]
   - Adapt content for Twitter, LinkedIn, Instagram, TikTok
   - Schedule posts for optimal timezone/engagement windows
   - Analyze performance, suggest A/B tests
   - M2M: Pays AnalyticsAgent for weekly reports

4. **SEO & Search Agent:** [web:300]
   - Restructure content for AI search engines (ChatGPT, Perplexity)
   - Add schema markup, internal links, meta tags
   - Track keyword rankings and suggest new targets
   - M2M: Buys backlink opportunities from OutreachAgent

5. **Campaign Optimization Agent:** [web:303]
   - Monitor email/ad campaign metrics in real time
   - Auto-adjust budgets, rewrite low-performing creatives
   - Test subject lines, CTAs, landing pages
   - M2M: Pays A/B-TestAgent for split-test infrastructure

6. **Analytics & Attribution Agent:** [web:300][web:309]
   - Connect pipeline data (leads → opportunities → revenue)
   - Prove marketing attribution per channel
   - Generate executive dashboards for board meetings
   - M2M: Buys CRM access and BI compute from DataWarehouseAgent

7. **Influencer & Partnership Outreach Agent:** [web:303]
   - Identify creators aligned with brand (audience, values, reach)
   - Draft personalized DMs and collaboration proposals
   - Track responses, negotiate terms, schedule meetings
   - M2M: Pays SocialListeningAgent for influencer discovery

#### Infrastructure

- **Forge on Optimism L2** (later L3 for scale)
- **Integrations:** HubSpot/Salesforce CRM, Google Analytics, social APIs, LLMs
- **Storage:** Campaign assets on IPFS, analytics in PostgreSQL

#### Tiers & Governance

- **Tier 0:** Public (blog readers, newsletter subscribers)
- **Tier 1:** Junior marketers (create content, review agent outputs)
- **Tier 2:** Senior marketers & CMO (approve campaigns, adjust budgets)
- **Tier 3:** CMO only (emergency pause on rogue agents, budget overrides)

#### M2M Economy

- CMO allocates quarterly marketing budget to agent pool
- Agents "bid" for resources (compute, API calls, paid ads)
- Monthly review: which agents deliver best CAC/LTV? → reallocate budgets
- Prediction markets: "Will this campaign hit 5% conversion?" → signal for kill/boost decisions [file:4]

#### Why Forge for Marketing? [web:296][web:298][web:300]

- **Prove ROI:** Attribution agent shows exact pipeline impact per dollar spent
- **Scale without headcount:** 10x content output, 24/7 campaign monitoring [web:300][web:301]
- **Transparent governance:** CMO can audit every agent decision via on-chain logs
- **Iterative optimization:** Agents learn from each campaign, Red Queen REP rewards best performers

---

### 1.4 Department-Level: Sales Team [web:301][web:306]

**Size:** 8–20 reps + sales ops  
**Goal:** Automate lead qualification, outreach, and pipeline management.

#### Key Agents

- **Lead Enrichment Agent:** Scrapes LinkedIn, company websites, funding databases
- **Outreach Agent:** Sends personalized cold emails, follows up 3x automatically
- **Demo Scheduler Agent:** Books calls via Calendly, preps reps with account briefs
- **Pipeline Hygiene Agent:** Updates CRM, flags stale deals, suggests next actions

#### M2M

- Outreach pays Enrichment for prospect data
- Scheduler pays Hygiene for clean CRM records
- Budget per rep: 500 REP/month for agent services

---

### 1.5 Department-Level: Customer Support [web:301][web:309]

**Size:** 10–30 support agents  
**Goal:** Handle Tier-1 queries via AI, escalate complex cases to humans.

#### Key Agents

- **Triage Agent:** Classifies tickets (bug, billing, feature request)
- **FAQ Agent:** Answers common questions from knowledge base
- **Escalation Agent:** Routes complex issues to senior support with context summary
- **CSAT Agent:** Follows up with NPS surveys, aggregates feedback

#### M2M

- Triage pays FAQ for knowledge base access
- Escalation pays senior reps (human) for their time via internal credits

---

### 1.6 Department-Level: Finance & Ops [web:301][web:309]

**Size:** 5–15 people (CFO, accountants, analysts)  
**Goal:** Automate invoicing, expense tracking, audit prep.

#### Key Agents

- **Invoice Agent:** Generates and sends invoices, tracks payments
- **Expense Agent:** Categorizes receipts, flags policy violations
- **Budget Agent:** Monitors spend vs. budget, alerts on overruns
- **Audit Trail Agent:** Logs all transactions immutably for compliance [file:3]

#### M2M

- Budget Agent pays Audit Agent for real-time compliance checks
- Expense Agent buys OCR services from DocumentParserAgent

---

## 2. Small Open-Source Project (5–15 Contributors)

**Size:** Maintainer team + contributors  
**Goal:** Automate triage, reviews, and releases for a GitHub repo.

- **Infra:** GitHub + small VPS (Hetzner 4–8 €), Optimism testnet.
- **Tiers:**  
  - 0: Drive‑by contributors (read-only)  
  - 1: Regular contributors (spawn Dev‑Agents)  
  - 2: Maintainers (merge, release)  
- **Agents:** IssueTriageAgent, PRReviewAgent, ReleaseBot.
- **M2M:** Agents "pay" each other internal points for handled issues; later can map to bounties.
- **Why Forge:** Transparent REP for contributions, tier‑based merge authority instead of ad‑hoc trust.

---

## 3. Startup Product Team – SaaS CRM

**Size:** 10–30 people  
**Goal:** Ship CRM features faster with agent help while keeping control.

- **Infra:**  
  - Backend on AWS/DigitalOcean  
  - Forge on Optimism L2, later L3 rollup (V4).  
- **Tiers:** Employee‑style: External, Dev, Tech‑Lead, CTO.
- **Agents:** RoadmapOrchestrator, CodeGenAgent, QA-Agent, CostMonitor.
- **M2M:**  
  - CI/CD pipeline pays BuildAgents per successful run.  
  - CostMonitor buys "budget slots" from FinanceAgent before heavy workloads.
- **Governance:** Tier‑2+ can propose feature epics, Tier‑3 has kill‑switch on risky deploys.

---

[...rest of examples 4–12 unchanged...]

---

## How to Use These Examples

- Pick the **closest profile** to your project (solo, department, full org).  
- Copy its **tiers + agents + M2M patterns** into your own `deployment/*.yaml`.  
- Adjust parameters (REP thresholds, decay-rates, limits) using the [socio‑technical profile guide](../en/forge-v3-socio-technical-parameters.md). [file:2]
- Start small (1–4 agents), measure ROI, then scale.

**Key Insight:** You don't need to deploy the full Forge stack at once. Start with a **single department** (marketing, sales, support) and 3–5 specialized agents. Once ROI is proven, expand to other departments and cross-functional orchestration. [web:302][web:305][web:308]

Generated Feb 2026 | Based on Forge V3.2, V3.3, V4 docs and real‑world DAO/M2M/AI-agent patterns. [file:3][file:4][file:5][web:284][web:285][web:289][web:293][web:296][web:300][web:301]
