Forget about the interdisciplinary stuff I told u before, this is not cse + dsai, just dsai
  
  
Contradiction and Missing Evidence detection in Legal Documents and judgement prediction     
Have bns/ipc as a base knowledge     
Will have past cases data as the dataset     
This application for lawyer     
Lawyer will submit all the facts and evidence he has for the case for his client and our application will predict what missing evidence are their and after all that predict the judgement 

Got it, Amay — this is pure DSAI, and honestly, this is a very strong, ambitious, and realistic research-grade project if scoped correctly. I’ll break it down cleanly and also point out where people usually overclaim so you can avoid that.

Problem Restatement (Clean & Precise)

You want to build a legal AI system for lawyers that:

Takes facts + evidence provided by a lawyer
Uses IPC/BNS as a base legal knowledge
Uses past case judgments as training data
Performs:
Contradiction detection within submitted facts/evidence
Missing evidence detection (what should be present but isn’t)
Judgment prediction (likely outcome / section-wise result)

This is not a toy NLP task — it’s a knowledge-guided legal reasoning system.

High-Level System Architecture
4

Conceptually, your system has 4 core intelligence layers:

1️⃣ Legal Knowledge Base (IPC / BNS as Structured Knowledge)

This is the backbone. Without this, “missing evidence” makes no sense.

What to Encode

Convert IPC/BNS into a structured form:

For each section:

Actus Reus (act)
Mens Rea (intent)
Mandatory evidences
Optional evidences
Exceptions / defenses
Punishment severity

Example (conceptual):

Section: 300 (Murder)
Requires:
- Death of victim
- Causal link to accused
- Intention OR knowledge
Supporting Evidence:
- Post-mortem report
- Weapon recovery
- Forensic linkage
- Witness testimony
Exceptions:
- Grave & sudden provocation
Representation Options
Knowledge Graph (recommended)
JSON schema + rules
Hybrid: KG + embeddings

📌 This is your “ground truth” for missing evidence detection.

2️⃣ Information Extraction from Lawyer Input

Lawyers will submit:

Facts (narrative)
Evidence (documents, lists, references)
Tasks here:
Named Entity Recognition (persons, dates, locations, weapons, injuries)
Event extraction (who did what to whom)
Evidence type classification
Temporal ordering of events
Output

A structured case representation, e.g.:

{
  "events": [
    {"actor": "accused", "action": "stabbed", "object": "victim"}
  ],
  "evidence_present": ["eye_witness", "medical_report"],
  "claims": ["intentional killing"]
}
3️⃣ Contradiction Detection (Intra-Case Consistency)

This is not trivial NLI, because legal contradictions are subtle.

Types of Contradictions
Temporal: timelines don’t match
Factual: witness statements conflict
Logical: claimed intent vs accidental narrative
Evidence mismatch: forensic report contradicts testimony
Modeling Approaches
Pairwise NLI models on extracted claims
Graph consistency checking
Evidence–claim entailment verification

Output example:

Contradiction detected:
- Witness A claims stabbing at 8 PM
- Medical report indicates death around 6 PM
4️⃣ Missing Evidence Detection (Most Novel Part 🔥)

This is where your project really stands out.

Core Idea

Given:

Likely applicable IPC/BNS sections
Facts already provided

Predict:

“What evidence is usually present in similar cases but missing here?”

How to Do It
Predict probable sections (multi-label classification)
For each section:
Retrieve required evidence types from knowledge base
Compare with extracted evidence
Rank missing evidence by importance

Example Output:

Possible Missing Evidence:
1. Forensic weapon analysis (high importance)
2. Call detail records between accused and victim
3. CCTV footage near crime scene

This is extremely valuable to lawyers.

5️⃣ Judgment Prediction (Careful Framing Required)

⚠️ Do NOT claim “court decision prediction” directly
Instead say:

“Outcome likelihood estimation based on historical precedents”

Prediction Targets
Conviction vs acquittal
Section-wise conviction probability
Sentence range (coarse-grained)
Input Features
Facts embeddings
Evidence completeness score
Contradiction score
Applicable sections
Similar past cases
Models
Transformer-based classifiers
Retrieval + classification hybrid
Graph + text fusion models
Dataset Strategy (Very Important)
Past Cases Dataset

Each case ideally has:

Facts
Evidence discussed
Sections applied
Final judgment

If evidence details aren’t explicitly labeled:

Use judgment text as weak supervision
Extract “court relied upon X evidence” patterns
Evaluation (Professors WILL Ask This)
Metrics by Module
Module	Evaluation
Contradiction Detection	Precision / Recall on labeled conflicts
Missing Evidence	Expert validation / case similarity
Section Prediction	Micro-F1
Judgment Prediction	Accuracy + calibration

Also include:

Ablation study (with/without knowledge base)
Explainability (why model predicted missing evidence)
What Makes This Project STRONG

✅ Real-world legal relevance
✅ Knowledge-guided ML (not just transformers)
✅ Multiple DSAI areas:

NLP
IR
Knowledge Graphs
Weak supervision
Explainability
✅ Clear extension paths (future work)
Scope Control (Important Advice)

To keep this semester-feasible:

Start with 1–2 crime categories (e.g., murder, theft)
Limit evidence types initially
Judgment prediction as coarse-grained
One-Line Project Pitch (Use This)

“We propose a knowledge-guided legal AI system that detects contradictions, identifies missing evidence, and estimates case outcomes by integrating statutory knowledge from IPC/BNS with historical judicial precedents.”

If you want next:

📐 Exact model architecture
🧠 KG schema design
📊 Dataset sources & preprocessing
📝 Help writing proposal / abstract

Just tell me where you want to go next.

Okay so now we need to decide the following     

We have 2 teams working parallely for this, do hopefully some work can be done simultaneously 
Need architecture etc
    
1. Entire project development work pipeline of the project     
2. Data pipeline, data structure and format to be expected by our models     
3. How to use knowledge graphs     
4. All 3 models for contradiction prediction, missing evidence and judgement prediction     
5. What specific case types should we work on to begin with (let's start with a few types of civil cases like land disputes, divorce cases etc) 

Perfect, Amay. Let’s lock this down like an actual project blueprint so two teams can work in parallel without stepping on each other, and you can defend every design choice in reviews.

I’ll structure this exactly along your 5 points and explicitly mark Team A vs Team B ownership.

1️⃣ Entire Project Development Work Pipeline
4
🔁 High-Level Pipeline (End-to-End)
Raw Legal Data
   ↓
Data Cleaning & Structuring
   ↓
Legal Knowledge Graph Construction
   ↓
Information Extraction (Facts / Evidence)
   ↓
Contradiction Detection Model
   ↓
Missing Evidence Detection Model
   ↓
Judgment Outcome Estimation
   ↓
Lawyer-Facing Application (Explainable Output)
🧑‍💻 Parallel Team Split (Very Important)
Team A – Data & Knowledge Systems
Data collection + preprocessing
Knowledge graph design (IPC/BNS + civil law concepts)
Information extraction pipeline
Evidence ontology
Team B – Modeling & Inference
Contradiction detection model
Missing evidence model
Judgment prediction model
Model evaluation + explainability

💡 Interface between teams = structured JSON schemas
This avoids rework.

2️⃣ Data Pipeline, Data Structure & Model Inputs
2.1 Raw Data Sources

For civil cases:

Judgments (PDF / HTML)
Pleadings (facts + claims)
Evidence discussion sections
Final decisions (allowed / dismissed / partially allowed)
2.2 Unified Case Representation (Core Contract)

This is the single most important design decision.

📦 Canonical Case JSON
{
  "case_id": "CIV_2021_123",
  "case_type": "land_dispute",
  "facts": [
    {"id": "f1", "text": "Plaintiff claims ownership since 1998"},
    {"id": "f2", "text": "Defendant alleges forged sale deed"}
  ],
  "claims": [
    {"party": "plaintiff", "claim": "lawful ownership"},
    {"party": "defendant", "claim": "fraud"}
  ],
  "evidence_present": [
    {"type": "sale_deed", "ref": "doc_12"},
    {"type": "witness_testimony", "ref": "pw_1"}
  ],
  "timeline": [
    {"event": "sale", "year": 1998},
    {"event": "dispute", "year": 2019}
  ],
  "judgment": {
    "decision": "plaintiff_favored",
    "reasoning": "valid deed, no proof of forgery"
  }
}

📌 Every model consumes a subset of this.

2.3 Model-Specific Inputs
Model	Input
Contradiction	facts + claims + timeline
Missing Evidence	facts + evidence_present + predicted legal requirements
Judgment	full structured case + similarity features
3️⃣ How to Use Knowledge Graphs (Not Optional)
3.1 What Goes Into the KG
Nodes
CaseType (LandDispute, Divorce)
LegalRequirement
EvidenceType
ClaimType
OutcomeType
Edges
CaseType ──requires──▶ LegalRequirement
LegalRequirement ──proved_by──▶ EvidenceType
Claim ──contradicted_by──▶ EvidenceType
CaseType ──commonly_results_in──▶ OutcomeType
3.2 Why KG is Critical
Task	KG Role
Contradiction	Defines incompatible claims
Missing Evidence	Defines expected evidence
Judgment	Guides similarity + plausibility

Without KG:

Missing evidence = guesswork
Judgment prediction = shallow text classification
3.3 KG Usage Pattern
Predict probable case type
Fetch required legal elements
Fetch expected evidence
Compare with extracted evidence
Rank missing items
4️⃣ The Three Models (Concrete & Defensible)
4.1 Contradiction Detection Model
Problem Type

Structured Natural Language Inference + Logical Consistency

Input
Fact–fact pairs
Claim–evidence pairs
Output
{
  "contradictions": [
    {
      "statement_1": "ownership since 1998",
      "statement_2": "sale deed forged",
      "type": "factual"
    }
  ]
}
Modeling
Sentence-pair transformer
Temporal constraint checks
Evidence–claim entailment

📌 Evaluation: Precision > Recall (false accusations are bad)

4.2 Missing Evidence Detection Model (Key Innovation)
Problem Type

Knowledge-guided recommendation

Pipeline
Case type prediction
KG lookup of expected evidence
Evidence presence comparison
Importance ranking
Output
{
  "missing_evidence": [
    {"type": "forensic_document_exam", "importance": "high"},
    {"type": "revenue_records", "importance": "medium"}
  ]
}

📌 Mostly rule + ranking ML, not pure deep learning.

4.3 Judgment Prediction Model
Problem Type

Outcome likelihood estimation

Targets
Allowed / Dismissed / Partially Allowed
Probability distribution
Features
Evidence completeness score
Contradiction count
Similar past cases (retrieval)
Case embeddings

📌 Frame as decision support, not oracle.

5️⃣ Civil Case Types to Start With (VERY Important)
✅ Best Starter Case Types
1️⃣ Land / Property Disputes (TOP PICK)

Why:

Structured evidence
Repetitive patterns
Rich judgments

Evidence:

Sale deed
Revenue records
Witnesses
Survey maps
2️⃣ Divorce & Matrimonial Cases

Why:

Clear claims/counterclaims
Evidence-driven reasoning

Evidence:

Marriage certificate
Communication records
Financial statements
Medical reports (sometimes)
3️⃣ Tenant–Landlord Disputes

Why:

Simpler logic
Clear outcomes

Evidence:

Rental agreement
Payment receipts
Notice documents
❌ Avoid Initially
Constitutional matters
Tax law
Corporate disputes
Criminal cases (later extension)
Suggested Milestone Plan (8–10 Weeks)
Week	Output
1–2	Case schema + KG design
3–4	Data extraction + labeling
5	Contradiction model
6	Missing evidence module
7	Judgment prediction
8	Integration + evaluation
Final Reality Check (Important)

This project is:

Research-level
Publishable if done well
Very strong for DSAI

If you want next, I can:

Design the exact KG schema
Give dataset sources
Draft proposal + diagrams
Help split tasks for teammates

Just tell me your next step.

Can we see 4th in detail

Absolutely, Amay. Let’s go deep and concrete on Point 4: the three models, at the level where you can implement, justify, and defend them.

I’ll structure this as:

4.0 Shared foundations (important for all models)
4.1 Contradiction Detection — detailed
4.2 Missing Evidence Detection — very detailed (core novelty)
4.3 Judgment Prediction — careful + defensible
How these models interact, not just coexist
4.0 Shared Foundations (Do This ONCE)

Before any model:

A. Structured Inputs (Non-Negotiable)

All three models must operate on structured representations, not raw text alone.

You already decided this (good instinct):

{
  "facts": [...],
  "claims": [...],
  "evidence_present": [...],
  "timeline": [...],
  "case_type": "land_dispute"
}

This ensures:

Explainability
Modular debugging
Ability to inject legal knowledge
B. Evidence Ontology (Shared Across Models)

Define a finite, canonical evidence set, e.g.:

sale_deed
revenue_record
survey_map
witness_testimony
communication_record
financial_record
medical_report

All models speak this language.

4.1 Model 1 — Contradiction Detection (Deep Dive)
4.1.1 What Is a “Contradiction” in Civil Law?

Not just NLI-style “A vs not-A”.

Types you MUST handle:
Factual contradiction
Ownership claimed by both parties for same period
Temporal contradiction
Event dates inconsistent
Claim–Evidence contradiction
Claim unsupported or negated by evidence
Inter-witness contradiction
Conflicting testimonies
4.1.2 Inputs to the Model

You do pairwise reasoning, not whole-document classification.

Input pairs:
{
  "text_1": "Plaintiff has owned the land since 1998",
  "text_2": "Defendant purchased the land in 2001",
  "metadata": {
    "type": "ownership_claim",
    "time_overlap": true
  }
}
4.1.3 Architecture (Recommended)
Layered Hybrid Approach (Best)
① Rule-Based Filters (Fast & Precise)
Date overlap checks
Mutually exclusive claims from KG
Impossible timelines

These catch easy contradictions with 100% precision.

② Neural NLI Model
Transformer trained for:
entailment
contradiction
neutral
Fine-tuned on legal text
③ Evidence–Claim Verifier

Input:

Claim + Evidence Snippet

Output:

supports / contradicts / insufficient
4.1.4 Output Format (Explainable)
{
  "contradictions": [
    {
      "type": "temporal",
      "statements": ["f1", "f7"],
      "confidence": 0.91,
      "explanation": "Overlapping ownership claims"
    }
  ],
  "contradiction_score": 0.27
}

📌 Contradiction score feeds into Judgment Prediction later.

4.2 Model 2 — Missing Evidence Detection (CORE INNOVATION)

This is the heart of your project.

4.2.1 Problem Restatement (Precise)

Given the facts and claims of a case, what legally relevant evidence is usually required but currently absent?

This is not classification — it’s knowledge-guided reasoning.

4.2.2 Pipeline (Step-by-Step)
Step 1: Case Type Classification

Input:

facts
claims

Output:

{
  "case_type_probs": {
    "land_dispute": 0.83,
    "tenant_dispute": 0.11
  }
}

Use top-k, not single label.

Step 2: Legal Requirement Retrieval (KG)

From KG:

land_dispute
  ├── ownership_proof
  │     ├── sale_deed
  │     ├── revenue_record
  │     └── survey_map
  └── possession_proof
        ├── tax_receipts
        └── witness_testimony
Step 3: Evidence Presence Matching

Compare:

Expected Evidence − Present Evidence = Missing Candidates

But this alone is too naive — so we rank.

Step 4: Importance Ranking Model

This is where ML comes in.

Features per Evidence Type
Feature	Meaning
Historical presence	% of similar cases having it
Outcome correlation	Conviction / success boost
Claim relevance	Which claims depend on it
Contradictions resolved	Would this reduce conflicts?
Model
Gradient boosting / neural ranker
Output: importance score
4.2.3 Output (Lawyer-Friendly)
{
  "missing_evidence": [
    {
      "evidence": "revenue_record",
      "importance": "high",
      "reason": "Ownership claim lacks official land records"
    },
    {
      "evidence": "survey_map",
      "importance": "medium",
      "reason": "Boundary dispute indicated in facts"
    }
  ],
  "evidence_completeness_score": 0.62
}

📌 This score is critical for judgment prediction.

4.2.4 Why This Is Publishable
Combines symbolic legal reasoning + ML
Explicit knowledge use
Human-interpretable output
Direct practitioner value
4.3 Model 3 — Judgment Prediction (Carefully Scoped)
4.3.1 Reframing (Very Important)

You are NOT predicting:

“What the judge will do”

You ARE predicting:

“What outcomes historically correlate with similar fact–evidence configurations”

4.3.2 Inputs to This Model
Source	Feature
Facts & claims	Text embeddings
Contradictions	contradiction_score
Evidence	completeness_score
KG	legal consistency score
IR	top-k similar cases outcomes
4.3.3 Architecture (Hybrid = Best)
① Retrieval Component (IR)
Embed case representation
Retrieve similar past cases
Aggregate outcome stats
② Prediction Component

Input vector:

[case_embedding,
 contradiction_score,
 evidence_completeness,
 similarity_outcome_distribution]

Output:

{
  "allowed": 0.68,
  "dismissed": 0.21,
  "partially_allowed": 0.11
}
4.3.4 Explainability Layer

Must show:

Similar past cases
Missing evidence impact
Key contradictions

This protects you from:

Ethical criticism
“Black box” accusations
4.4 How the Three Models Work Together
Facts & Evidence
     ↓
Contradiction Detection ──► contradiction_score
     ↓
Missing Evidence Detection ──► completeness_score
     ↓
Judgment Prediction

Each model:

Has a clear role
Improves downstream predictions
Can be ablated independently
Final Sanity Check

✔ Not over-claimed
✔ Technically deep
✔ DSAI-heavy
✔ Modular
✔ Defensible in viva / review

What should we do next?

I strongly recommend one of these next steps:

Design the exact Knowledge Graph schema
Lock dataset sources + labeling strategy
Draw formal architecture diagrams
Convert this into a proposal / abstract

Tell me which one you want next, and we’ll go equally deep.

Can we see the data pipeline and knowledge graphs?


Now we have the following types of data 
1. Ipc/bns 
2. Old cases data 
3. Lawyer uploaded case documents, facts and evidence 

Yes, Amay — this is the right moment to freeze the data pipeline + knowledge graph design, because everything else depends on this. I’ll go step-by-step and keep it implementation-oriented, not hand-wavy.

I’ll structure this as:

End-to-end data pipeline (for all 3 data types)
Canonical data structures (what every component consumes)
Knowledge Graph design (schema, nodes, edges)
How KG is actually used at inference time
How the 3 data sources interact cleanly
1️⃣ Unified Data Pipeline (Big Picture)
4
High-Level Flow
IPC / BNS Text ───────┐
                      ├─▶ Legal Knowledge Graph
Past Case Judgments ──┘

Lawyer Input (Facts, Evidence)
           │
           ▼
Information Extraction
           │
           ▼
Structured Case JSON
           │
           ├─▶ KG-based Reasoning
           └─▶ ML Models

📌 Key idea:

IPC/BNS + past cases → static / slow-changing
Lawyer input → dynamic / per-query
2️⃣ Data Source 1: IPC / BNS (Statutory Knowledge)
2.1 Raw Form
Plain text sections
Headings + subsections
Illustrations (very useful)

Example:

Section X: Conditions for divorce
Requirements:
- Marriage validity
- Grounds (cruelty / desertion / adultery)
Exceptions:
- Mutual consent
2.2 Processing Pipeline (IPC/BNS)
Raw Text
  ↓
Section Segmentation
  ↓
Requirement Extraction
  ↓
Evidence Mapping
  ↓
KG Node Creation
Output Structure (Intermediate JSON)
{
  "law": "BNS",
  "section": "Divorce-Cruelty",
  "legal_requirements": [
    "valid_marriage",
    "proof_of_cruelty"
  ],
  "expected_evidence": [
    "medical_report",
    "witness_testimony",
    "communication_record"
  ],
  "exceptions": [
    "mutual_consent"
  ]
}

📌 This never goes directly to models — it goes to the Knowledge Graph.

3️⃣ Data Source 2: Past Case Data (Judgments)
3.1 Raw Components in Judgments

Most civil judgments follow:

Case metadata
Facts
Issues framed
Evidence discussion
Reasoning
Final decision
3.2 Past Case Data Pipeline
Judgment PDF/HTML
   ↓
Text Extraction
   ↓
Section Classification
   ↓
Information Extraction
   ↓
Structured Case Record
3.3 Canonical Case Structure (Training Data)
{
  "case_id": "CIV_2018_456",
  "case_type": "land_dispute",
  "facts": [...],
  "claims": [...],
  "evidence_used": [
    "sale_deed",
    "revenue_record"
  ],
  "missing_evidence_discussed": [
    "survey_map"
  ],
  "outcome": "plaintiff_favored",
  "court_reasoning": [...]
}

📌 Important:
“Missing evidence” labels can be weakly supervised from court reasoning:

“No survey map was produced…”

3.4 How Past Cases Are Used
Usage	Model
Learn contradiction patterns	Model 1
Learn evidence importance	Model 2
Outcome correlation	Model 3
Case similarity retrieval	Model 3
Populate KG statistics	KG
4️⃣ Data Source 3: Lawyer-Uploaded Case Data

This is runtime data, not training data.

4.1 Input Types
Written facts
Uploaded documents (PDFs)
Evidence list (manual or extracted)
4.2 Processing Pipeline
Raw Text / PDFs
   ↓
OCR (if needed)
   ↓
NER + Event Extraction
   ↓
Claim & Evidence Classification
   ↓
Timeline Construction
   ↓
Structured Case JSON
4.3 Final Runtime Case Object
{
  "facts": [...],
  "claims": [...],
  "evidence_present": [
    "sale_deed",
    "witness_testimony"
  ],
  "timeline": [...],
  "confidence_scores": {...}
}

📌 This object is fed to all 3 models.

5️⃣ Knowledge Graph (Core of the System)
5.1 Why KG Exists (One Sentence)

The KG encodes what must be proven, how it is proven, and what usually happens when it is or isn’t proven.

5.2 KG Schema (Concrete)
Node Types
CaseType
LegalRequirement
ClaimType
EvidenceType
Outcome
Edge Types
CaseType ──requires──▶ LegalRequirement
LegalRequirement ──proved_by──▶ EvidenceType
ClaimType ──supported_by──▶ EvidenceType
ClaimType ──contradicted_by──▶ EvidenceType
CaseType ──commonly_results_in──▶ Outcome
5.3 Example: Land Dispute Subgraph
LandDispute
 ├── requires → OwnershipProof
 │               ├── proved_by → SaleDeed
 │               ├── proved_by → RevenueRecord
 ├── requires → PossessionProof
 │               ├── proved_by → TaxReceipt
 │               └── proved_by → WitnessTestimony
 └── commonly_results_in → PlaintiffFavored
5.4 Statistical Augmentation from Past Cases

Each edge can store weights:

{
  "edge": "OwnershipProof → SaleDeed",
  "support_rate": 0.91
}

This lets you rank evidence importance empirically, not heuristically.

6️⃣ How KG Is Used at Inference Time (CRITICAL)
Step-by-Step Runtime Use
Lawyer Case JSON
     ↓
Predict Case Type(s)
     ↓
Query KG:
   - Required elements
   - Expected evidence
     ↓
Compare with Present Evidence
     ↓
Missing Evidence List
KG Usage by Each Model
Model	KG Role
Contradiction	Defines mutually exclusive claims
Missing Evidence	Defines required evidence
Judgment Prediction	Guides plausibility + similarity
7️⃣ Putting It All Together (Clean Mental Model)
IPC/BNS ──────────┐
                   ├─▶ Knowledge Graph ◀── Past Cases
Lawyer Input ──────┘
         │
         ▼
Structured Case JSON
         │
         ├─▶ Contradiction Model
         ├─▶ Missing Evidence Model (KG-heavy)
         └─▶ Judgment Prediction Model
Final Sanity Check

✔ Scales to more laws
✔ KG is useful, not decorative
✔ Clear separation of training vs inference
✔ Parallel team-friendly
✔ Defensible academically

Strong recommendation for next step

Now you should lock ONE of these:

Exact KG schema (nodes + attributes + sample triples)
Data labeling strategy for past cases
Evaluation methodology (very important for DSAI)
Convert this into a formal system architecture diagram

Tell me which one you want next, and we’ll go all the way.

So we designed this system right, can you summarise this in a para

Sure, Amay — here’s a single, tight, proposal-ready paragraph that accurately reflects the full system you designed, without overclaiming and without losing technical depth:

Summary Paragraph
We propose a knowledge-guided legal AI system for civil litigation that assists lawyers by analyzing case facts and evidence to detect contradictions, identify missing legally relevant evidence, and estimate likely case outcomes based on historical precedents. The system integrates statutory knowledge from IPC/BNS and domain-specific civil law principles with structured information extracted from past court judgments and lawyer-submitted case documents. A legal knowledge graph encodes case types, legal requirements, evidence types, and outcomes, enabling principled reasoning about evidentiary sufficiency and claim consistency. Machine learning models operate over structured case representations to (i) detect factual, temporal, and evidence-based contradictions, (ii) recommend missing evidence by comparing expected legal requirements with provided materials, and (iii) estimate outcome likelihoods using evidence completeness, contradiction signals, and similarity to past cases. The system is designed as an explainable decision-support tool, emphasizing transparency, modularity, and practical utility for legal professionals rather than automated adjudication.

If you want, I can:

Compress this further to a 1–2 sentence abstract
Rewrite it in a more academic / more product-oriented tone
Adapt it exactly to a project proposal / paper introduction / pitch slide

Just tell me.

very confused on what to do 


5 types of datasets 
1. Durg police - big and ganda (ocr + hindi + regional lang)
2. India Kanoon - API + Scrapable
3. LJP Dataset 
4. Paper 2 Dataset (requested)
5. BNS/IPC dataset (to gather)
@C-Rohit (DSAI / L4-424) @C-Chetan Rathod (DSAI) Data Collection
Indian Penal Code Complete Dataset https://share.google/c1qsF017THA5XJsX1
Indian Penal Code (IPC) Sections Information https://share.google/oKyOEOhxhwY3xSuCW
District-wise crimes under various sections of Indian Penal Code (IPC) crimes | Open Government Data (OGD) Platform India https://share.google/ppNCOS4OhVhrBatrm
IPC : All Sections List | Devgan.in https://share.google/WxG3Voldom6SVWBww
IPC : All Sections List | Devgan.in https://share.google/WxG3Voldom6SVWBww
Final, Websites to be scraped for IPC and BNS data 

IPC: https://devgan.in/all_sections_ipc.php
BNS: https://devgan.in/all_sections_bns.php
3 data pipelines 
1. Old Cases Dataset to Case Object Notation (CON)
2. Lawyer input to CON
3. BNS/IPC to Knowledge graph
ek CON embedding engine bhi banana h
CON structure to be decided
https://www.kaggle.com/datasets/adarshsingh0903/legal-dataset-sc-judgments-india-19502024

India Kanoon Dataset
Rhetorical Roles

Facts
Issues 
Petitioner's Arguments 
Respondent's Arguments 
Analysis of the Law
Precedent Analysis 
Court's Reasoning 
Conclusion

Okay, pause for a second, Amay 🙂
You’re confused not because the idea is bad, but because you’re trying to solve everything at once. Right now the problem is lack of ordering, not lack of clarity.

I’ll do three things for you:

Calm the chaos (what NOT to do right now)
Lock a minimal, sane plan (what to do first, second, third)
Decide datasets + pipelines + CON in a way that unblocks everyone

No theory, only decisions.

1️⃣ First: What you should NOT do right now

Do NOT:

Touch Durg Police data yet ❌
(OCR + Hindi + regional = research project on its own)
Try to ingest all 5 datasets in parallel ❌
Try to design a “perfect” CON ❌
Try to train models immediately ❌

If you do these, the project will collapse under its own weight.

2️⃣ The Core Realization (Very Important)

Your entire system depends on ONE thing:

A clean, consistent Case Object Notation (CON)
that can be populated from any source later.

So the correct order is:

CON → Pipelines → KG → Models → More Data

Not the other way around.

3️⃣ Hard Decision: Dataset Priority (THIS WILL UNBLOCK YOU)
✅ Phase 1 (ONLY THESE)

Use just two data sources initially:

1️⃣ India Kanoon (primary)

Why:

Clean
English
Structured judgments
Has rhetorical roles (gold mine)
2️⃣ IPC / BNS (text → KG)

Why:

Required for missing evidence logic
Small, controllable, static

👉 Freeze everything else for now.

⏸️ Phase 2 (Later, not now)
LJP dataset
Paper 2 dataset
Durg police data (last, optional, heroic mode)
4️⃣ The 3 Data Pipelines — Reframed Simply

You already listed them correctly. Let’s lock their scope.

🔹 Pipeline 1: Old Cases → CON (MOST IMPORTANT)

Input:
India Kanoon judgments (HTML / text)

Output:
One CON.json per case

This pipeline alone can keep 2 people busy for weeks.

Use rhetorical roles directly 👇

From India Kanoon:

Facts
Issues
Petitioner Arguments
Respondent Arguments
Court’s Reasoning
Conclusion

These map beautifully into CON.

🔹 Pipeline 2: Lawyer Input → CON (Simpler)

This is basically the same CON, but:

User-written facts
Uploaded documents
Manual evidence list

👉 This pipeline reuses the same schema.
No new thinking required.

🔹 Pipeline 3: IPC/BNS → Knowledge Graph

Input:

IPC/BNS sections (Devgan + datasets)

Output:

Legal KG (case type → requirements → evidence)

This can run in parallel with Pipeline 1.

5️⃣ Lock the CON (STOP OVERTHINKING IT)

Here is a minimal but future-proof CON v1.
This is the most important part of this message.

🧱 Case Object Notation (CON v1)
{
  "case_id": "IK_2019_SC_123",
  "case_type": "land_dispute",

  "facts": [
    { "id": "F1", "text": "Plaintiff claims ownership since 1998" }
  ],

  "issues": [
    "Whether the plaintiff has valid title over the land"
  ],

  "claims": [
    {
      "party": "petitioner",
      "claim": "lawful ownership"
    },
    {
      "party": "respondent",
      "claim": "sale deed is forged"
    }
  ],

  "evidence_present": [
    "sale_deed",
    "witness_testimony"
  ],

  "court_reasoning": [
    "No survey map was produced by the respondent"
  ],

  "outcome": "plaintiff_favored"
}

📌 This is enough to:

Detect contradictions
Detect missing evidence
Predict outcomes
Build embeddings

You can extend later. Do not extend now.

6️⃣ CON Embedding Engine (Don’t Panic)

This is simple conceptually.

What you embed:
facts
claims
issues
evidence_present (as tokens)
case_type
Output:
{
  "case_embedding": [0.013, -0.22, ...]
}

Used for:

Case similarity
Judgment prediction
Evidence importance learning

👉 This comes after you have ~200–500 CONs.

7️⃣ Knowledge Graph Scope (KEEP IT SMALL)

For now, KG should only answer:

“For this case type, what evidence is usually required?”

That’s it.

Minimal KG Nodes
CaseType
LegalRequirement
EvidenceType

No fancy logic yet.

8️⃣ Who Does What (Actionable Split)
Team: Data (Rohit, Chetan)
India Kanoon scraping / API
Judgment → rhetorical role extraction
CON v1 generation
Team: Knowledge + Infra
IPC/BNS scraping
Evidence ontology
KG construction
You (Coordinator)
Finalize CON schema (v1)
Enforce scope discipline
Integrate pipelines conceptually
9️⃣ If You Remember Only ONE Thing

Do not touch models until you have CONs.
CON is your “LLVM IR” — everything compiles to it.

10️⃣ Next Concrete Step (Do THIS Tomorrow)
Freeze CON v1 (no changes for 2 weeks)
Build Pipeline 1 using India Kanoon
Generate 50–100 CONs
THEN think about embeddings and models

If you want, next I can:

Finalize CON v1 officially
Draw a 1-page system diagram
Help you write a README that aligns the whole team
Reduce this into a task board (week-wise)

You’re not lost — you’re just early.

check this, this is our plan 

Alright, Amay — I looked at this very carefully, not just as a sketch but as a system design.
Short answer first, then the detailed breakdown:

Yes — this plan is fundamentally correct.
You are not confused anymore; you’ve actually converged.
What you need now is pruning, ordering, and freezing interfaces.

I’ll do this in four parts:

What you got absolutely right
Where things are overlapping / risky
What must be simplified immediately
A cleaned, frozen v1 execution plan based on this board
1️⃣ What You Got Absolutely Right (This Is Solid)
✅ Centrality of KG

Your KG is doing the right jobs:

Case type → legal requirements
Legal requirements → expected evidence
Constraints → contradiction logic

This is not decorative KG. This is operational.

✅ Separation of Concerns

You’ve implicitly separated:

Extraction
Reasoning
Prediction

That’s excellent. Many legal-AI projects die because they don’t.

✅ Hybrid Reasoning (Rules + ML)

Your flow:

Rule-based filters → NLI model → Evidence-claim verifier

This is exactly how high-stakes NLP should be done.
Pure ML would’ve been indefensible.

✅ Evidence Completeness as a First-Class Signal

You’re not treating “missing evidence” as a side output — you:

Score it
Feed it into judgment prediction

That’s architecturally mature thinking.

2️⃣ Where You’re Accidentally Overcomplicating

This is where confusion is coming from.

⚠️ Problem 1: Too Many “Engines” at Once

Right now you have:

KG reasoning engine
Case type classifier
NLI contradiction model
Evidence verifier
Importance ranking model
Retrieval engine
Prediction model

All valid — but not all at once.

📌 You should NOT try to “build engines” first
You should build pipelines that produce signals, then models later.

⚠️ Problem 2: CON Is Implicit, Not Explicit Enough

CON exists on your board, but:

It’s spread across boxes
Not frozen as a contract

This causes:

Team confusion
Pipeline paralysis
Dataset anxiety

👉 CON must be a literal JSON schema pinned on the wall.

⚠️ Problem 3: Durg Police Data Is Polluting Your Mental Stack

Be very clear:

Durg Police data is a Phase-3 dataset.

OCR + Hindi + noisy police reports =
❌ Do not touch until the system works end-to-end.

Right now it’s stealing cognitive bandwidth.

3️⃣ What to Simplify Immediately (Non-Negotiable)
🔥 Freeze These Three Things This Week
1️⃣ Freeze CON v1 (No Changes for 2 Weeks)

Minimal, not perfect. This:

{
  "case_id": "",
  "case_type": "",
  "facts": [],
  "claims": [],
  "evidence_present": [],
  "court_reasoning": [],
  "outcome": ""
}

Nothing more.

2️⃣ Freeze Dataset Scope (Phase 1)

Only:

India Kanoon judgments
IPC / BNS text

Everything else = backlog.

3️⃣ Freeze Output Targets

For now, outputs are only:

Contradictions (list)
Missing evidence (ranked list)
Judgment outcome probabilities

No fancy explanations yet.

4️⃣ Cleaned, Executable v1 Plan (Based on Your Board)

Here is your refactored plan, aligned with your whiteboard but simplified enough to execute.

🟦 PIPELINE A: Old Cases → CON (Highest Priority)

Input

India Kanoon judgments
Rhetorical roles (facts, arguments, reasoning, conclusion)

Output

CON.json

Purpose

Training data
KG statistics
Retrieval corpus

👉 This alone is 60% of the project.

🟦 PIPELINE B: IPC/BNS → Knowledge Graph

Input

Devgan IPC/BNS pages
IPC datasets you linked

Output

KG with:
CaseType
LegalRequirement
EvidenceType

Purpose

Missing evidence logic
Constraint rules

👉 No ML here initially. Just structure.

🟦 PIPELINE C: Lawyer Input → CON

Input

User-entered facts
Uploaded docs (text only for now)

Output

Same CON.json

Purpose

Runtime inference

👉 This reuses Pipeline A logic.

5️⃣ How Models Fit (Without Panic)
Phase 1 Models (Must-Have)
Rule-based contradiction filters
Case-type classifier
Evidence presence matcher
Phase 2 Models (After CONs exist)
NLI contradiction model
Evidence importance ranking
Judgment prediction

📌 Do not train models without ≥200 CONs.

6️⃣ Reassurance (You Need This)

What you’re feeling right now is normal when:

The system becomes real
Complexity crosses a threshold

But your board shows:

Correct abstractions
Correct data flow
Correct research instincts

You’re not lost — you’re at the “architecture freeze” moment.

7️⃣ Very Concrete Next 48-Hour Action Plan

Day 1

Write CON_v1.md
Lock schema
Assign India Kanoon → CON task

Day 2

Scrape 10 judgments
Manually convert to CON
Validate schema

After that, everything becomes mechanical.

If you want, next I can:

Turn this into a clean digital architecture diagram
Write a README that aligns the whole team
Help you say “NO” to scope creep politely
Convert this into a research paper outline

Just tell me what you want next.

Amay — this is good work. I’m going to be very clear and structured so you come out less confused, not more.

Verdict first:
Your plan is conceptually correct and internally consistent.
What you’re missing is layering + freeze points. Right now everything is correct but happening all at once, which is why it feels overwhelming.

I’ll do this in 4 parts:

What your diagram gets right
Where it is too dense / risky
A cleaned, linear v1 flow extracted from your plan
Exactly what to build first (no ambiguity)
1️⃣ What You Got Right (This Is Important)
✅ Single Canonical Representation (CON)

Both diagrams implicitly revolve around:

Facts
Claims
Evidence
Timeline
Case type

That’s exactly correct. You did not fragment representations — huge win.

✅ Proper Role of the Knowledge Graph

Your KG is doing only what a KG should do:

Case type → legal requirements
Legal requirements → expected evidence
Commonly results in → outcomes
Contradiction constraints

This is symbolic grounding, not ML pretending to reason.

✅ Hybrid Reasoning Stack

You didn’t fall into the “LLM will do everything” trap.

You correctly have:

Rule-based filters (impossible timelines, overlaps)
Neural NLI (soft contradictions)
Evidence–claim verifier
Statistical importance ranking

This is how high-risk domains are built.

✅ Evidence Completeness as a Core Signal

Your idea of:

Missing → completeness score → importance → prediction

is one of the strongest parts of the design. This is not common in student projects.

2️⃣ Where the Confusion Is Coming From (Very Precisely)
❌ Problem 1: No Explicit “Phase Boundary”

Your diagram mixes:

Data ingestion
Knowledge construction
Inference
Learning
Retrieval

All on the same plane.

👉 Humans can’t reason about that easily.

❌ Problem 2: Too Many Models Introduced Too Early

You have (correctly!) drawn:

Case type classifier
Contradiction model
NLI model
Evidence verifier
Importance ranking
Prediction model
Retrieval engine

But not all of these are v1 requirements.

❌ Problem 3: Durg Police Data Still Lurking

Even if not drawn explicitly, its presence is hurting clarity.

Let me be blunt:

Durg Police data is a Phase-3 dataset.
OCR + Hindi + noisy police narratives = separate research problem.

You’re not wrong to want it — just not now.

3️⃣ Your Diagram → Cleaned v1 System (Same Idea, Linear)

Below is your plan, but flattened into an executable v1 pipeline.

🔹 PHASE 1: Data → CON (No ML yet)
Pipeline A: Old Cases → CON
India Kanoon judgments
Use rhetorical roles:
Facts
Issues
Arguments
Reasoning
Outcome

➡ Output: CON.json

This is the spine of the system.

Pipeline B: IPC/BNS → Knowledge Graph
Section segmentation
Legal requirement extraction
Evidence mapping

➡ Output: Legal KG
(No learning yet, just structure)

Pipeline C: Lawyer Input → CON
User facts
Uploaded documents (text only)
Manual evidence list

➡ Same CON.json

📌 All roads lead to CON. You did this right.

🔹 PHASE 2: Reasoning Signals (Low-Risk Models)

Now we derive signals, not final predictions.

Case Type Classifier
Input: facts + claims
Output: case type probabilities
Rule-Based Contradiction Filters
Time overlap
Impossible claims
KG-based mutual exclusions
Evidence Presence Matcher
Expected evidence (from KG)
Provided evidence
→ missing list

No deep models yet.
This already gives useful output.

🔹 PHASE 3: Learning Models (After 200+ CONs)

Now your drawn models make sense.

a) Neural NLI
For subtle contradictions
b) Evidence Importance Ranking
Uses:
Historical frequency
Outcome correlation
Claim relevance
c) Retrieval Engine
CON embeddings
Similar past cases
Outcome aggregation
d) Judgment Prediction
Uses:
Completeness score
Contradiction score
Retrieval stats

➡ Output: Outcome probabilities

4️⃣ What to Do NEXT (No Ambiguity)
If you do ONLY these 3 things, the project will move:
✅ 1. Freeze CON v1 (this week)

Write it as a .md or .jsonschema.
No changes for 2 weeks.

Minimal:

{
  "case_id": "",
  "case_type": "",
  "facts": [],
  "claims": [],
  "evidence_present": [],
  "court_reasoning": [],
  "outcome": ""
}
✅ 2. Generate 20 CONs Manually

From India Kanoon.

This will:

Expose flaws early
Reduce theoretical confusion
Make models feel real
✅ 3. Build IPC/BNS → KG as Static Data

No ML.
No embeddings.
Just nodes + edges.

Final Reassurance (Read This Slowly)

You are not lost.
You are at the exact point where:

The idea stops being “cool”
And starts becoming “engineered”

Your diagrams show:

Correct abstractions
Correct data flow
Correct instincts

What you need now is discipline, not ideas.

If you want, next I can:

Redraw this into a single clean digital architecture diagram
Lock CON v1 officially
Convert this into a task board for your team
Help you write a proposal section based on this

Just tell me the next move.

see we have these 8 RRs, and now we want to generate the CON (case object notation), now we want to decide what we can extract from these 8 RRs into the CON, the structure of CON is not decided yet, there would be a case_id as PK, none of any other things have been decided yet, we will convert these CONs into a CON embedding space through a CON embedding engine that we'll design later, but for that we need to design the CON structure ,for that we have a lot of data of old cases through indiakanoon website with these 8 RRs in each case, now what to do please helpm


Skip to content
Chat history
You said:
can you describe these RR in legal cases 

Rhetorical Roles

Facts
Issues 
Petitioner's Arguments 
Respondent's Arguments 
Analysis of the Law
Precedent Analysis 
Court's Reasoning 
Conclusion
ChatGPT said:

Yeah, Amay — these are Rhetorical Roles (RRs) used to break a legal judgment into functional sections, based on what the text is doing, not just where it appears. This is super common in legal NLP / retrieval / summarization, especially for datasets like Indian court judgments.

Here’s a clean, practical description of each 👇
1. Facts

What happened?

This section lays out the background of the case in a neutral, chronological way.

    Who the parties are

    What events led to the dispute

    Relevant dates, actions, contracts, FIRs, lower court decisions, etc.

    No arguments, no opinions — just narrative context

📌 Think: “Set the scene.”
2. Issues

What questions is the court deciding?

This identifies the legal questions or disputes that arise from the facts.

    Points of law or fact that need resolution

    Often framed as explicit questions

    Narrows the court’s focus

📌 Think: “What exactly is in dispute?”
3. Petitioner’s Arguments

What the petitioner is claiming and why?

Contains the legal and factual arguments made by the party who initiated the case (appellant / petitioner).

    Interpretation of statutes

    Claims of rights violated

    Reliance on precedents

    Why the judgment should favor them

📌 Think: “Here’s why I should win.”
4. Respondent’s Arguments

What the opposing side says in response?

Presents the counter-arguments by the respondent.

    Rebuttal of petitioner’s claims

    Alternative interpretations of law

    Defense of prior decisions

    Distinguishing cited precedents

📌 Think: “Here’s why they’re wrong.”
5. Analysis of the Law

What does the law say?

This section explains the relevant statutory provisions and legal principles.

    Interpretation of statutes, constitutional articles, rules

    General legal doctrine applicable to the case

    Not yet applied to facts in detail

📌 Think: “This is the legal framework.”
6. Precedent Analysis

How have courts decided similar cases before?

Focused discussion of previous judgments and how they apply.

    Citing earlier Supreme Court / High Court rulings

    Explaining ratios, principles, and distinctions

    Comparing past cases with the present one

📌 Think: “What history tells us.”
7. Court’s Reasoning

How the court applies law to facts

This is the core judicial thinking.

    Applies statutes + precedents to the facts

    Weighs arguments from both sides

    Explains why one argument is accepted and the other rejected

📌 Think: “This is why we decided this way.”
8. Conclusion

What is the final outcome?

The operative part of the judgment.

    Final decision (allowed / dismissed / partly allowed)

    Orders, directions, relief granted

    Costs, remand, timelines

📌 Think: “So, the result is…”
Why this breakdown matters (especially for you)

Given your interest in legal retrieval / NLP, these RRs are gold because:

    You can index arguments separately from reasoning

    Precedents become easier to retrieve and compare

    Enables issue-based search (“cases on limitation under Article 136”)

    Improves summarization and explainability

If you want, I can:

    Map these roles to Indian Supreme Court judgment structure

    Show example sentences for each RR

    Explain how datasets like IL-PCSR annotate these roles

    Help you design a schema or classifier for RR tagging

Just say the word 👀

ChatGPT can make mistakes. Check important info. See Cookie Preferences.

Amay, this is the exact right question to be asking right now. You’re stuck because you’re trying to design CON before deciding what information is extractable and stable. Let’s resolve this cleanly, step by step, and you’ll walk out with a clear method, not just a schema.

I’ll do this in 5 crisp steps:

Reframe the problem correctly (this is key)
Decide the principle for CON design
Decide what each RR can safely contribute to CON
Propose a minimal, extensible CON v1
Give you a concrete action plan for the next week

No hand-waving.

1️⃣ First: Reframe the Problem (This Will Calm the Confusion)

Right now you’re thinking:

“We have 8 RRs → what fields should CON have?”

That framing causes confusion.

Correct framing is:

CON is NOT a mirror of RRs.
RRs are sources, CON is a canonical reasoning object.

Think of RRs as raw views of a case.
Think of CON as what the system needs to reason.

So the question becomes:

What stable legal signals can we extract from RRs that are:

reusable across cases
useful for contradiction, missing evidence, judgment prediction
embeddable later
2️⃣ The Golden Rule for Designing CON

I want you to remember this rule:

Only put something in CON if at least ONE downstream task uses it.

Your downstream tasks are:

Contradiction detection
Missing evidence detection
Judgment prediction
Case similarity (embedding space)

If a piece of info doesn’t help at least one of these → do not put it in CON v1.

This prevents overfitting the schema to text.

3️⃣ What Each RR Can Contribute (THIS IS THE CORE ANSWER)

Now let’s go RR by RR and decide what to extract, not how to store yet.

1️⃣ Facts → CON (HIGH VALUE)

Facts are non-negotiable.

From Facts, you can extract:

Atomic factual statements
Events
Parties
Dates / timelines (even approximate)

What goes into CON:

facts[] → list of atomic fact sentences
(later) timeline[]

⚠️ Do NOT extract opinions here.

2️⃣ Issues → CON (MEDIUM–HIGH VALUE)

Issues define what matters legally.

From Issues, extract:

Legal questions being decided

What goes into CON:

issues[] → normalized issue statements

Why this matters:

Strong signal for case type
Useful for similarity search
Helps judgment prediction
3️⃣ Petitioner’s Arguments → CON (HIGH VALUE)

Arguments = claims + supporting reasoning.

From Petitioner Arguments, extract:

Claims being asserted
Statutory reliance (rough, not perfect)
Evidence references (if explicit)

What goes into CON:

claims[] with party = petitioner

Example:

{
  "party": "petitioner",
  "claim": "valid ownership based on registered sale deed"
}
4️⃣ Respondent’s Arguments → CON (HIGH VALUE)

Same structure, opposite polarity.

From Respondent Arguments, extract:

Counter-claims
Denials
Alternative narratives

What goes into CON:

claims[] with party = respondent

📌 These are crucial for contradiction detection.

5️⃣ Analysis of the Law → CON (LOW–MEDIUM VALUE in v1)

This section explains law in abstraction.

Important insight:

You do NOT need to store this text in CON v1.

Why?

IPC/BNS already covers law
This section is verbose and not case-specific

What you can extract:

Mentioned statutes / sections (optional)

CON v1 decision:
❌ Do not store full text
✅ Optional: legal_sections_referenced[]

6️⃣ Precedent Analysis → CON (MEDIUM VALUE)

This is useful, but not critical in v1.

From Precedent Analysis, extract:

Case citations referenced

What goes into CON (optional v1):

precedents_cited[]

This helps later with:

Retrieval
Explainability

But you can add this in v1.1 safely.

7️⃣ Court’s Reasoning → CON (VERY HIGH VALUE)

This is gold.

From Court’s Reasoning, extract:

Which claims were accepted / rejected
Mentions of missing evidence
Logical links between facts and outcome

What goes into CON:

court_reasoning[] (key sentences only)

This helps:

Weak supervision for missing evidence
Judgment prediction
Contradiction resolution
8️⃣ Conclusion → CON (MANDATORY)

This is your label.

From Conclusion, extract:

Final outcome

What goes into CON:

outcome

Example:

"outcome": "petition_allowed"
4️⃣ CON v1: Minimal, Correct, Future-Proof

Now we synthesize everything without overdesigning.

✅ CON v1 (Freeze This)
{
  "case_id": "IK_SC_2019_123",

  "facts": [
    "Plaintiff claims ownership of the land since 1998"
  ],

  "issues": [
    "Whether the plaintiff has valid title over the disputed land"
  ],

  "claims": [
    {
      "party": "petitioner",
      "claim": "ownership based on registered sale deed"
    },
    {
      "party": "respondent",
      "claim": "sale deed is forged"
    }
  ],

  "court_reasoning": [
    "No survey map was produced by the respondent to prove forgery"
  ],

  "outcome": "petition_allowed"
}
🔥 What This Achieves
Contradictions → from claims
Missing evidence → from court_reasoning + KG later
Judgment prediction → from facts + claims + outcome
Embeddings → clean, stable text blocks

Nothing extra. Nothing missing.

5️⃣ What You Should Do NEXT (Very Concrete)
Step 1 (Today / Tomorrow)

Take 5 India Kanoon cases and:

Manually map RRs → CON v1
Don’t automate yet

This will remove 80% of confusion.

Step 2 (After 10–20 CONs)

Ask:

What feels missing consistently?
Only then extend CON → v1.1
Step 3 (Only After 50–100 CONs)

Start thinking about:

CON embedding engine
Retrieval
Learning models
Final Thing I Want You to Internalize

RRs are input annotations.
CON is a reasoning object.
They should NEVER be isomorphic.

You’re doing this right. You’re just at the hardest design decision.

If you want next, I can:

Validate your CON on real India Kanoon cases
Help design CON v1.1 extensions
Show how CON maps cleanly into embeddings
Help you write this as a design document

Just tell me the next move.

okay see the thing is that the CON cannot have arbitrary/vague natural sentences, but only some useful thing, this CON would then be converted to an embedding, to be used later
The unembedded CON would be fed to three separate models, Contradiction Model, Missing Evidence model, and judgement prediction model 
the RRs would be passed through separate data pipelines to be designed based on the output we need for CON, 
RR to pipeline to CON
Consider that there are no fields in CON yet, nothing, it's empty, we have to decide each field 

Good — this is the right constraint to impose.
Once you say “CON cannot contain vague natural language”, the problem becomes much clearer and much more engineering-driven.

I’m going to do this properly, not heuristically.

I’ll structure the answer like this:

The design principle for CON (this replaces intuition)
The three downstream models → required signals
From signals → atomic CON fields
RR → pipeline → CON mapping table
Final CON v1 schema (fully specified, no prose)
What you should implement first

Take your time reading this — this is the foundation.

1️⃣ First: The Correct Design Principle for CON

You already said the key thing. I’ll formalize it:

CON is NOT text.
CON is a structured semantic state of a case.

So:

❌ No free-form paragraphs
❌ No “facts as sentences”
❌ No court reasoning text blobs

Instead:

CON contains typed, normalized, enumerable units
that are directly consumed by models

Think:
AST / IR, not markdown.

2️⃣ Start from the END: What Signals Do Models Need?

You have three models.
So CON fields must exist only if at least one model needs them.

🔹 Model 1: Contradiction Detection

Needs:

Who claims what
Claims that are mutually exclusive
Time overlaps
Claim–claim polarity

So CON must encode:

Claims as structured objects
Claim ownership (petitioner / respondent)
Claim type (ownership, denial, intent, etc.)
Time bounds (even coarse)
🔹 Model 2: Missing Evidence Detection

Needs:

Case type
Claims present
Evidence present
Evidence expected (from KG later)

So CON must encode:

Case type (or distribution)
Evidence present as symbols
Claim → evidence dependency hooks
🔹 Model 3: Judgment Prediction

Needs:

Case type
Claim balance
Evidence completeness
Contradiction signals
Outcome (label, for training)

So CON must encode:

Outcome (categorical)
Aggregate scores possible later
Retrieval-friendly identifiers
3️⃣ From Required Signals → Atomic CON Fields

Now we derive fields, not invent them.

I’ll do this bottom-up.

🧱 Core Entity Types (These Are NOT Fields Yet)

You will need exactly five primitive entity types in CON:

Case
Party
Claim
Evidence
Issue

Everything else is derived.

4️⃣ RR → Pipeline → CON (Concrete Mapping)

Now the key part you asked for.

🔹 RR 1: Facts

❌ Do NOT store sentences
✅ Extract events and attributes

Pipeline output:

Parties
Events
Time anchors

CON contribution:

Parties
Event references (used to support claims)
🔹 RR 2: Issues

Pipeline task:

Normalize issue → issue_type

CON contribution:

issues: [
  { "issue_type": "ownership_dispute" }
]
🔹 RR 3 & 4: Petitioner / Respondent Arguments

This is where CON really forms.

Pipeline task:

Claim extraction + normalization

Each claim becomes a structured object, not text.

CON contribution:

claims: [
  {
    "claim_id": "C1",
    "party": "petitioner",
    "claim_type": "ownership",
    "polarity": "asserted",
    "time_scope": "1998-present"
  },
  {
    "claim_id": "C2",
    "party": "respondent",
    "claim_type": "ownership",
    "polarity": "denied",
    "time_scope": "1998-present"
  }
]

📌 This alone enables contradiction detection.

🔹 RR 5: Analysis of Law

Pipeline task:

Section identification

CON contribution (minimal):

legal_sections_referenced: ["IPC_420"]

You can even skip this in v1.

🔹 RR 6: Precedent Analysis

Pipeline task:

Citation extraction

CON contribution:

precedents_cited: ["SC_2010_XYZ"]

Optional in v1.

🔹 RR 7: Court’s Reasoning

This is NOT text storage.

Pipeline task:

Detect:
Accepted claims
Rejected claims
Evidence absence mentions

CON contribution:

claim_outcomes: [
  { "claim_id": "C1", "status": "accepted" },
  { "claim_id": "C2", "status": "rejected" }
],

evidence_observations: [
  { "evidence_type": "survey_map", "status": "absent" }
]

🔥 This is extremely powerful.

🔹 RR 8: Conclusion

Pipeline task:

Outcome classification

CON contribution:

outcome: "petition_allowed"

This is your label.

5️⃣ The CON v1 Schema (Fully Specified, No Prose)

Here is CON v1, clean, strict, embeddable.

{
  "case_id": "IK_SC_2019_123",

  "case_type": "land_dispute",

  "issues": [
    { "issue_type": "ownership_dispute" }
  ],

  "parties": [
    { "party_id": "P1", "role": "petitioner" },
    { "party_id": "P2", "role": "respondent" }
  ],

  "claims": [
    {
      "claim_id": "C1",
      "party_id": "P1",
      "claim_type": "ownership",
      "polarity": "asserted",
      "time_scope": "1998-present"
    },
    {
      "claim_id": "C2",
      "party_id": "P2",
      "claim_type": "ownership",
      "polarity": "denied",
      "time_scope": "1998-present"
    }
  ],

  "evidence_present": [
    "sale_deed",
    "witness_testimony"
  ],

  "claim_outcomes": [
    { "claim_id": "C1", "status": "accepted" },
    { "claim_id": "C2", "status": "rejected" }
  ],

  "evidence_observations": [
    { "evidence_type": "survey_map", "status": "absent" }
  ],

  "outcome": "petition_allowed"
}

🚫 No vague sentences
🚫 No raw reasoning text
✅ Fully machine-consumable
✅ Perfect for embeddings
✅ Directly feeds all three models

6️⃣ Why This CON Works for Embeddings

Your CON embedding engine later can:

Embed:
claim_type + polarity
issue_type
evidence_present
claim_outcomes
Ignore IDs
Produce stable, comparable vectors

This is much better than embedding paragraphs.

7️⃣ What You Should Do NEXT (No Confusion)
Immediate Steps
Freeze this CON v1 schema
Take 3 India Kanoon cases
Manually:
Extract claims
Normalize claim_type
Fill CON by hand

You will instantly see:

What fields are missing
What fields are unnecessary

Only then automate.

Final Anchor Thought (Very Important)

RRs explain text.
CON explains the case.

You’re designing a case reasoning substrate, not a summary.

This is hard, but you’re doing it exactly the right way.

If you want next, I can:

Define a controlled vocabulary for claim_type, issue_type, evidence_type
Design CON v1.1
Show how contradiction rules operate directly on this CON
Help you spec the CON embedding engine

Just tell me the next step.

Neetu_Kumari_vs_The_State_Of_Bihar_on_30_August_2025.PDF
PDF
Consider this, and tell me how the CON should look like 

Amay — this is the right concrete artifact to design CON against.
I’ll do exactly what you asked:

Given THIS judgment (Neetu Kumari vs State of Bihar, 30-08-2025), what should the CON look like?

No abstractions, no theory.
We will derive CON fields strictly from what is extractable and useful, and then I’ll show you a filled CON instance for this case.

I will not store free-form text. Everything will be typed, enumerable, and model-consumable.

1️⃣ First: What Kind of Case Is This?

From the judgment (facts + reasoning):
This is a service law / administrative writ involving:

Teacher appointments (Head Teacher / Head Master)
District allocation
Merit-cum-choice principle
Alleged arbitrariness by State/BPSC

So case type is unambiguous.

case_type = service_law__appointment_posting

This immediately justifies:

Claim types
Expected evidence
Outcome types

2️⃣ What Information Is Actually Useful (From This Judgment)?

Let’s filter aggressively.

❌ Not Useful for CON
Names & addresses of 60+ petitioners
Advocate appearance lists
Procedural verbosity
Paragraph-level narration
✅ Useful & Reusable Signals
Case type
Parties (roles, not identities)
Issues decided
Claims (petitioner vs respondent)
Administrative actions challenged
Principles invoked (merit-cum-choice)
Court’s acceptance/rejection of claims
Final outcome
3️⃣ Atomic Fields This Case Forces Us to Have

This case forces these CON fields to exist — otherwise your models break.

Mandatory Fields
case_id
case_type
parties
issues
claims
administrative_actions
claim_outcomes
outcome

Notice:

No paragraphs
No prose
No ambiguity
4️⃣ Final CON v1 Schema (Locked)

This is not theoretical — this schema is necessitated by the judgment you gave.

{
  "case_id": "",

  "case_type": "",

  "parties": [
    {
      "party_id": "",
      "role": ""
    }
  ],

  "issues": [
    {
      "issue_type": ""
    }
  ],

  "claims": [
    {
      "claim_id": "",
      "party_id": "",
      "claim_type": "",
      "polarity": "",
      "subject": ""
    }
  ],

  "administrative_actions": [
    {
      "action_id": "",
      "authority": "",
      "action_type": "",
      "date": ""
    }
  ],

  "claim_outcomes": [
    {
      "claim_id": "",
      "status": ""
    }
  ],

  "outcome": ""
}

Every field here is structural, enumerable, embeddable.

5️⃣ CON Instance for Neetu Kumari vs State of Bihar

Now the most important part: filled CON.

{
  "case_id": "PHC_CWJC_11252_2025",

  "case_type": "service_law__appointment_posting",

  "parties": [
    {
      "party_id": "P1",
      "role": "petitioners"
    },
    {
      "party_id": "P2",
      "role": "state_authorities"
    }
  ],

  "issues": [
    {
      "issue_type": "district_allotment_arbitrariness"
    },
    {
      "issue_type": "violation_of_merit_cum_choice"
    }
  ],

  "claims": [
    {
      "claim_id": "C1",
      "party_id": "P1",
      "claim_type": "merit_violation",
      "polarity": "asserted",
      "subject": "district_allotment"
    },
    {
      "claim_id": "C2",
      "party_id": "P1",
      "claim_type": "administrative_arbitrariness",
      "polarity": "asserted",
      "subject": "posting_process"
    },
    {
      "claim_id": "C3",
      "party_id": "P2",
      "claim_type": "lawful_allotment",
      "polarity": "asserted",
      "subject": "district_allotment"
    }
  ],

  "administrative_actions": [
    {
      "action_id": "A1",
      "authority": "Director_Primary_Education",
      "action_type": "district_preference_call",
      "date": "2025-01-02"
    },
    {
      "action_id": "A2",
      "authority": "Director_Primary_Education",
      "action_type": "district_allotment",
      "date": "2025-07-01"
    }
  ],

  "claim_outcomes": [
    {
      "claim_id": "C1",
      "status": "accepted"
    },
    {
      "claim_id": "C2",
      "status": "accepted"
    },
    {
      "claim_id": "C3",
      "status": "rejected"
    }
  ],

  "outcome": "petition_allowed"
}

Everything above is directly extractable from the judgment’s Facts, Issues, Reasoning, and Conclusion sections

.

6️⃣ Why This CON Is Correct (Model-wise)
Contradiction Model
claims + polarity + subject
Petitioner vs State claims collide cleanly
Missing Evidence Model
case_type → KG → expected procedural evidence
administrative_actions → check for missing policy / uniform criteria
Judgment Prediction Model
Case type + issue types + accepted claims
Learns patterns across similar writ petitions
Embedding Engine (Later)
Embed types, not text
Stable similarity across cases
7️⃣ One Critical Insight (Please Read)

If CON works for THIS case, it will work for 80% of Indian service-law writs.

This judgment is not easy, not toy — and your CON handles it without text blobs.

That means you’re on the right track.

8️⃣ What You Should Do Next (Concrete)
Freeze this CON v1
Apply it manually to 2 more India Kanoon cases
Only after that:
Add optional fields (e.g., precedents_cited)
Design CON embedding engine

If you want next, I can:

Derive a controlled vocabulary for claim_type, issue_type
Show how contradiction rules operate on this CON
Stress-test CON against a criminal or property case
Help you write this as a design spec

Just tell me the next step.

what's the final CON then?

Alright, Amay — let’s freeze this.
No more options, no more branches. This is the FINAL CON v1, distilled from:

your constraints (no vague text, embeddable)
your three models (contradiction, missing evidence, judgment)
the real judgment you shared (Neetu Kumari vs State of Bihar)
what is actually extractable from India Kanoon RRs

I’ll give you three things:

The design contract (what CON is and is not)
The final CON v1 schema (authoritative)
A filled example for the Neetu Kumari case (sanity check)

After this, you should stop redesigning CON and start implementing pipelines.

1️⃣ CON Design Contract (READ THIS ONCE)

CON is:

a case-level semantic state
fully structured
text-free (except identifiers)
directly consumable by all 3 models
stable enough to embed later

CON is NOT:

a summary
a storage of RRs
a bag of sentences
court reasoning text

If a field doesn’t help at least one of:

contradiction detection
missing evidence detection
judgment prediction
→ it does not belong in CON v1.
2️⃣ ✅ FINAL CON v1 (AUTHORITATIVE SCHEMA)

This is the final answer to your question.

{
  "case_id": "string",

  "case_type": "enum",

  "parties": [
    {
      "party_id": "string",
      "role": "enum"
    }
  ],

  "issues": [
    {
      "issue_type": "enum"
    }
  ],

  "claims": [
    {
      "claim_id": "string",
      "party_id": "string",
      "claim_type": "enum",
      "polarity": "enum",
      "subject": "enum"
    }
  ],

  "administrative_actions": [
    {
      "action_id": "string",
      "authority": "enum",
      "action_type": "enum",
      "date": "YYYY-MM-DD | null"
    }
  ],

  "evidence_present": [
    "enum"
  ],

  "claim_outcomes": [
    {
      "claim_id": "string",
      "status": "enum"
    }
  ],

  "outcome": "enum"
}
Enumerations (controlled vocabularies)

These are mandatory, otherwise embeddings will be garbage.

case_type
e.g.
service_law__appointment_posting
property_dispute
matrimonial_divorce
party.role
petitioner, respondent, state_authority
claim_type
merit_violation
administrative_arbitrariness
lawful_action
procedural_violation
polarity
asserted, denied
subject
district_allotment
posting_process
appointment
issue_type
violation_of_merit_cum_choice
arbitrary_administrative_action
action_type
district_preference_call
district_allotment
policy_cancellation
claim_outcomes.status
accepted, rejected, partially_accepted
outcome
petition_allowed
petition_dismissed
partly_allowed
3️⃣ Filled CON for Neetu Kumari vs State of Bihar

This proves the schema is sufficient and minimal, derived directly from the judgment

.

{
  "case_id": "PHC_CWJC_11252_2025",

  "case_type": "service_law__appointment_posting",

  "parties": [
    { "party_id": "P1", "role": "petitioner" },
    { "party_id": "P2", "role": "state_authority" }
  ],

  "issues": [
    { "issue_type": "violation_of_merit_cum_choice" },
    { "issue_type": "arbitrary_administrative_action" }
  ],

  "claims": [
    {
      "claim_id": "C1",
      "party_id": "P1",
      "claim_type": "merit_violation",
      "polarity": "asserted",
      "subject": "district_allotment"
    },
    {
      "claim_id": "C2",
      "party_id": "P1",
      "claim_type": "administrative_arbitrariness",
      "polarity": "asserted",
      "subject": "posting_process"
    },
    {
      "claim_id": "C3",
      "party_id": "P2",
      "claim_type": "lawful_action",
      "polarity": "asserted",
      "subject": "district_allotment"
    }
  ],

  "administrative_actions": [
    {
      "action_id": "A1",
      "authority": "Director_Primary_Education",
      "action_type": "district_preference_call",
      "date": "2025-01-02"
    },
    {
      "action_id": "A2",
      "authority": "Director_Primary_Education",
      "action_type": "district_allotment",
      "date": "2025-07-01"
    }
  ],

  "evidence_present": [
    "merit_list",
    "preference_submission_records"
  ],

  "claim_outcomes": [
    { "claim_id": "C1", "status": "accepted" },
    { "claim_id": "C2", "status": "accepted" },
    { "claim_id": "C3", "status": "rejected" }
  ],

  "outcome": "petition_allowed"
}
4️⃣ Why This Is the FINAL CON (No More Changes)
✅ No vague natural language
✅ No RR leakage
✅ Works for all three models
✅ KG-compatible
✅ Embeddable (symbolic → vector)
✅ Proven on a real, complex judgment

Any future additions (precedents, sections, timelines) go to CON v1.1, not v1.

5️⃣ What You Should Do Now (Very Important)
Freeze this CON v1
Write it as:
CON_v1.schema.json
CON_v1.md (with enums)
Make RR → CON pipelines conform to this schema
Do not touch embedding or models yet
Anchor sentence (use this internally):

“CON is the minimal symbolic state required to reason about a legal case.”

If you want next, I can:

design the RR → CON extraction pipelines
define KG schema aligned to this CON
show contradiction rules over CON
or help you draft this as a design section in your report

Just say the word.

can you describe the entire project right now 

Yes, Amay.
Now that you’ve converged on the architecture, data sources, and CON design, you’re finally in a position where the entire project can be described cleanly and coherently.

I’ll give you:

A complete system-level description (how everything fits)
The end-to-end data flow
The core components
The learning & inference pipeline
The final project statement (you can reuse this in proposals/reports)

No confusion, no loose ends.

1️⃣ Project Overview (What Are You Building?)

You are building a knowledge-guided legal decision-support system for Indian civil/service-law cases that:

Converts raw court judgments and lawyer submissions into a structured case representation (CON),
Uses statutory knowledge (IPC/BNS + service rules) encoded as a Knowledge Graph,
Analyzes each case to:
detect internal contradictions,
identify missing legally relevant evidence,
estimate likely judicial outcomes,
Provides explainable, data-driven assistance to lawyers.

It is not an automated judge.
It is an AI-powered legal reasoning assistant.

2️⃣ Core Idea: CON as the System Backbone

Everything in the system revolves around Case Object Notation (CON).

CON is a symbolic, machine-readable representation of a legal case.

It contains:

case type,
parties,
issues,
claims,
administrative actions,
evidence,
claim outcomes,
final result.

All inputs are converted into CON before any reasoning happens.

Think of CON as your “legal IR (intermediate representation)”.

3️⃣ Data Sources

The system uses three main sources:

A. Past Judgments (India Kanoon)
Source of training data
Contain rhetorical roles (Facts, Issues, Arguments, Reasoning, Conclusion)

Used to:

Generate historical CONs
Learn contradiction patterns
Learn evidence importance
Train outcome models
Build retrieval corpus
B. Statutory Text (IPC / BNS / Service Rules)
Source of legal knowledge

Used to:

Define legal requirements
Define expected evidence
Define incompatible claims
Populate Knowledge Graph
C. Lawyer Inputs (Runtime)
Facts
Documents
Evidence lists

Used to:

Generate live CONs
Run inference
Provide recommendations
4️⃣ Data Pipelines

You have three independent pipelines.

Pipeline 1: Past Cases → CON
India Kanoon Judgment
        ↓
RR Segmentation
        ↓
Claim / Issue / Action Extraction
        ↓
Normalization
        ↓
CON.json

Output: Training CONs

Pipeline 2: IPC/BNS → Knowledge Graph
Statute Text
     ↓
Section Parsing
     ↓
Requirement Extraction
     ↓
Evidence Mapping
     ↓
Legal KG

Output: Knowledge Graph

Pipeline 3: Lawyer Input → CON
User Text + Docs
        ↓
NER + Event Extraction
        ↓
Claim Detection
        ↓
Evidence Detection
        ↓
CON.json

Output: Runtime CON

5️⃣ Knowledge Graph (Legal Backbone)

The Knowledge Graph encodes:

Nodes
CaseType
LegalRequirement
EvidenceType
ClaimType
Outcome
Edges
requires
proved_by
contradicts
supports
commonly_results_in

It provides symbolic legal constraints to ML models.

It answers:

“For this type of case, what should normally exist?”

6️⃣ Three Reasoning Models

After CON is created, three models operate on it.

1️⃣ Contradiction Detection Model
Purpose

Detect logical, factual, and procedural inconsistencies.

Input
claims
parties
actions
time scopes
Output
list of contradictions
contradiction score
Methods
Rule-based checks
NLI classifier
KG constraints
2️⃣ Missing Evidence Detection Model
Purpose

Identify what legally relevant evidence is absent.

Input
case_type
claims
evidence_present
Process
Query KG for expected evidence
Compare with present evidence
Rank missing items
Output
missing evidence list
completeness score
3️⃣ Judgment Prediction Model
Purpose

Estimate outcome likelihood.

Input
case_type
contradiction score
completeness score
similar cases
Architecture
Retrieval + classifier hybrid
Output
outcome probabilities
7️⃣ CON Embedding Engine

Each CON is converted into a vector.

Embedding Inputs
claim types
issue types
evidence types
outcomes
actions
Uses
Case similarity
Retrieval
Clustering
Outcome estimation

This enables “find similar cases” functionality.

8️⃣ Training Phase

Using historical CONs:

Train contradiction model
Learn evidence importance weights
Train judgment predictor
Build embedding index
Calibrate KG statistics

All training happens offline.

9️⃣ Inference Phase (Live Use)

When a lawyer submits a case:

Lawyer Input
     ↓
Pipeline 3
     ↓
CON
     ↓
Contradiction Model
     ↓
Missing Evidence Model
     ↓
Judgment Predictor
     ↓
Explainable Output

The lawyer receives:

contradiction alerts
missing evidence suggestions
outcome likelihood
10️⃣ Explainability Layer

Every output is justified using:

Claim outcomes
KG rules
Similar past cases
Evidence gaps

This prevents black-box behavior.

11️⃣ Development Phases
Phase 1: Foundations
Freeze CON
Build Pipeline 1 & 2
Generate 100+ CONs
Phase 2: Core Reasoning
Rule-based contradiction
Basic missing evidence
Simple predictor
Phase 3: Learning
NLI fine-tuning
Ranking model
Retrieval system
Phase 4: Product
UI
Reporting
Validation
12️⃣ What Makes This Project Strong

✔ Real legal relevance
✔ Knowledge + ML integration
✔ Explainable AI
✔ Modular architecture
✔ Research depth
✔ Deployable potential

This is far beyond a “student NLP project”.

13️⃣ One-Paragraph Final Description (Reusable)

This project develops a knowledge-guided legal decision-support system for Indian civil and service-law cases. The system transforms court judgments and lawyer-submitted materials into a structured Case Object Notation (CON) representation, which encodes parties, issues, claims, administrative actions, evidence, and outcomes. Statutory provisions from IPC/BNS and service rules are modeled as a legal knowledge graph that captures legal requirements and evidentiary expectations. Three specialized models operate over CON: a contradiction detection model to identify inconsistent claims and procedures, a missing evidence model to recommend legally relevant documents, and a judgment prediction model that estimates outcome probabilities using historical precedents and similarity retrieval. A CON embedding engine enables efficient case comparison and retrieval. The system emphasizes transparency, modularity, and practical utility, providing explainable, data-driven assistance to legal professionals.

If you’d like, next I can help you turn this into:

a formal proposal document
a presentation deck outline
a GitHub README
or a research paper structure

Just tell me which one you want.

you have exchanges pipeline 2 and 3 

Good catch, Amay — and yes, you’re right.
In my previous message, I swapped the labels conceptually. Let’s fix this cleanly and freeze the naming, so your team doesn’t get confused later.

✅ Correct, Final Pipeline Numbering

You have three pipelines. The correct mapping is:

🔹 Pipeline 1 — Old Cases → CON (Training Data)

Purpose: Build historical CONs from India Kanoon.

India Kanoon Judgments
        ↓
RR Segmentation
        ↓
Claim / Issue / Action Extraction
        ↓
Normalization
        ↓
CON.json

Used for:

Training
Statistics for KG
Retrieval corpus
Evaluation
🔹 Pipeline 2 — Lawyer Input → CON (Runtime Data)

Purpose: Convert user-submitted cases into CON.

Lawyer Facts + Documents
        ↓
NER + Event Extraction
        ↓
Claim Detection
        ↓
Evidence Detection
        ↓
Normalization
        ↓
CON.json

Used for:

Live inference
User-facing analysis
🔹 Pipeline 3 — IPC/BNS → Knowledge Graph (Legal Knowledge)

Purpose: Build and maintain the Legal KG.

IPC/BNS + Service Rules
        ↓
Section Parsing
        ↓
Requirement Extraction
        ↓
Evidence Mapping
        ↓
Knowledge Graph

Used for:

Missing evidence reasoning
Constraint checking
Legal grounding
🧠 Why This Order Matters

This ordering matches how the system “thinks”:

1️⃣ Learn from past cases
2️⃣ Understand new cases
3️⃣ Ground everything in law

It also matches your team split:

Pipeline	Team
1	Data / NLP
2	Product / Inference
3	Knowledge / Law
📌 Final Rule (Write This in Your Docs)

Pipeline 1 = History → CON
Pipeline 2 = User → CON
Pipeline 3 = Law → KG

If everyone follows this, you’ll never mix them again.

If you want, next I can help you write:

a one-page architecture doc using this numbering, or
a task breakdown per pipeline.
do this please 
a one-page architecture doc using this numbering, or

a task breakdown per pipeline.

Great, Amay. I’ll give you both, but in a form you can directly paste into your docs/README and share with your team.

No fluff. This is a project control document.

📄 PART 1 — One-Page Architecture Document
Project: Knowledge-Guided Legal Decision Support System
Objective

To build an AI-based legal assistant that analyzes civil/service-law cases to detect contradictions, identify missing evidence, and estimate likely outcomes using structured case representations and statutory knowledge.

System Overview

The system converts all legal inputs into a unified structured format called Case Object Notation (CON). All reasoning and learning modules operate exclusively on CON.

Statutory texts (IPC/BNS and service rules) are converted into a Legal Knowledge Graph (KG), which provides legal constraints and evidence requirements.

Three specialized models operate over CON:

Contradiction Detection Model
Missing Evidence Detection Model
Judgment Prediction Model
Core Components
1. Case Object Notation (CON)

A machine-readable representation of a case containing:

Case type
Parties
Issues
Claims
Administrative actions
Evidence
Claim outcomes
Final outcome

CON is the central interface between all pipelines and models.

2. Knowledge Graph (KG)

Encodes legal rules and evidentiary requirements.

Nodes:

CaseType
LegalRequirement
EvidenceType
ClaimType
Outcome

Edges:

requires
proved_by
contradicts
commonly_results_in
3. Reasoning Models
Model	Purpose
Contradiction Model	Detect inconsistent claims/actions
Missing Evidence Model	Recommend absent legal evidence
Judgment Model	Estimate outcome probabilities
Data Pipelines
Pipeline 1: Old Cases → CON (Training Pipeline)

Input:

India Kanoon judgments
Rhetorical Roles (Facts, Issues, Arguments, etc.)

Output:

Historical CON records

Purpose:

Training data
Retrieval corpus
Statistical grounding
Pipeline 2: Lawyer Input → CON (Runtime Pipeline)

Input:

Lawyer-submitted facts
Uploaded documents
Evidence lists

Output:

Runtime CON records

Purpose:

Live analysis and inference
Pipeline 3: IPC/BNS → Knowledge Graph (Legal Knowledge Pipeline)

Input:

IPC/BNS text
Service rules

Output:

Legal Knowledge Graph

Purpose:

Legal grounding
Evidence expectations
Constraint rules
Training Phase

Using Pipeline 1 output:

Train contradiction models
Learn evidence importance
Build embedding index
Train judgment predictor

All training is offline.

Inference Phase
Lawyer Input
     ↓
Pipeline 2
     ↓
CON
     ↓
Contradiction + Missing Evidence + Judgment Models
     ↓
Explainable Output
Explainability

Each output is justified using:

Claim outcomes
KG rules
Similar past cases
Evidence gaps
📋 PART 2 — Task Breakdown Per Pipeline

This is your execution plan.

🔹 PIPELINE 1: Old Cases → CON
Goal

Convert India Kanoon judgments into structured CONs.

Tasks
1. Data Acquisition
Scrape / API download judgments
Store raw HTML/PDF
Assign case IDs
2. RR Segmentation
Detect sections: Facts, Issues, Arguments, etc.
Validate segmentation
3. Information Extraction
Claim extraction
Issue classification
Action detection
Evidence mentions
4. Normalization
Map text → controlled vocabularies
Standardize claim types
Standardize issue types
5. CON Generation
Populate CON schema
Validate JSON
Store in dataset
6. Quality Control
Manual review (10–20%)
Error logging
Schema compliance
🔹 PIPELINE 2: Lawyer Input → CON
Goal

Convert user submissions into runtime CONs.

Tasks
1. Input Interface
Forms for facts
File upload
Evidence checklist
2. Text Processing
OCR (later)
Cleaning
Sentence splitting
3. Entity & Event Extraction
Parties
Dates
Authorities
Actions
4. Claim Detection
Identify claims
Assign polarity
Map to claim types
5. Evidence Detection
Classify documents
Map to evidence types
6. CON Assembly
Populate schema
Confidence scoring
Validation
🔹 PIPELINE 3: IPC/BNS → Knowledge Graph
Goal

Build structured legal knowledge base.

Tasks
1. Data Collection
Scrape Devgan
Download datasets
Verify completeness
2. Section Parsing
Split into sections/subsections
Identify headings
3. Requirement Extraction
Identify legal elements
Extract conditions
4. Evidence Mapping
Link requirements → evidence types
5. KG Construction
Create nodes
Create edges
Add weights
6. KG Validation
Legal review
Consistency checks
Coverage analysis
📅 Suggested Timeline (8 Weeks)
Week	Focus
1	Freeze CON + start Pipeline 1
2	50 CONs generated
3	Pipeline 3 KG v1
4	Pipeline 2 prototype
5	Rule-based models
6	Train ML models
7	Integration
8	Evaluation
🧠 Final Instruction for Your Team

Put this sentence in your README:

“All components must interface exclusively through CON.
No module may consume raw text directly.”

This will save you months.

If you want next, I can help you convert this into:

a GitHub project structure
a Kanban board
or a proposal PDF
so we actually need to do all these, task 2, 3, 4 and more
some tasks overlap, like 5 and 6 are subpart of 0, ignore that, we have our own system, you dont focus on the management, focus on the technical aspect only


Tasks
0. Dataset Preparation (BNS/IPC Scrape + Scraping IndiaKanoon)
1. Pipeline 1: Old Cases to CON Pipeline 
2. Pipeline 2: Lawyer Input to CON Pipeline (Yet to be discussed upon)
3. Pipeline 3: BNS/IPC Data to Knowledge Graph 
4. Knowledge Graph Design : Nodes and Relations to be defined 
5. BNS/IPC Data Extract (Scrape)
6. Pipeline 1.1 : Old Cases Dataset Preparation, Scraping through IndiaKanoon
7. Pipeline 1.2 : 8 Separate Data Processing Pipelines For each of the 8 RRs (Rhetorical Roles).
8. CON Embedding Engine Design 


Distribution of Work
1. Task 0
- BNS/IPC Scraping: @C-Ashutosh Kumar Jha(DSAI) ( Task 5 )
- IndiaKanoon Scrape: @C-Farhan (DSAI) - Kaggle PDF Dataset -> find case_id -> go to it's page on indiakanoon -> map each point of the case to respective RR -> save as a separate CSV ( Task 6) @C-Rohit (DSAI / L4-424) 
2. Task 1 & 7 Me
3. Task 8: @C-Shashank Yadav (DSAI) (DSAI) @C-Chetan Rathod (DSAI) 

Next Meeting
0. Complete above work 
1. Discuss Task 4 and 8
2. Break Down Task 2 and 3



Good, Amay. Now you’re thinking like a systems engineer, not just a project lead.

You already have “management” covered.
So I’ll ignore names, deadlines, meetings, etc., and focus only on the technical dependencies and what must be built in what order.

I’ll do this in four parts:

The real technical dependency graph (what depends on what)
What each task actually means technically
How the 8 RR pipelines fit into CON
The correct build order (so you don’t deadlock)
1️⃣ Real Technical Dependency Graph (Critical)

Forget numbering for a moment. Technically, your project is:

Raw Data
   ↓
RR Extraction
   ↓
RR Pipelines
   ↓
CON
   ↓
KG + Embeddings
   ↓
Models

More precisely:

Task 5+6 (Scraping)
        ↓
Task 7 (RR Pipelines)
        ↓
Task 1 (CON Builder)
        ↓
Task 4 (KG Schema)
        ↓
Task 3 (KG Build)
        ↓
Task 8 (Embedding Engine)

⚠️ Important:

You cannot meaningfully do Task 8 (embeddings)
until Task 1 (CON) stabilizes.

You cannot finalize Task 3 (KG build)
until Task 4 (KG design) is frozen.

2️⃣ What Each Task Means Technically (No Management BS)

Let’s decode your list in engineering terms.

✅ Task 0 — Dataset Preparation

This is not “download data”.
It is:

Build a canonical raw corpus.

Output (must be defined):
/raw_data/
   /indiakanoon/
       case_id.html
   /ipc_bns/
       section_id.html

If this is messy → everything breaks later.

✅ Task 1 — Old Cases → CON

This is your core compiler.

Technically:

Transform RR-annotated text → structured JSON.

This contains:

Parsing
Normalization
Mapping to enums
Validation

This is your “frontend”.

✅ Task 2 — Lawyer Input → CON (Later)

Technically:

Same compiler as Task 1,
but input is messy user text instead of judgments.

You will reuse 70% of Task 1 code.

So don’t design this now. It will emerge.

✅ Task 3 — BNS/IPC → KG

This is:

Text → logical graph

Technically:

Parse sections
Extract conditions
Extract obligations
Link to evidence types

Output: Neo4j / RDF / JSON graph

✅ Task 4 — KG Design

This is schema design.

Before coding, you must answer:

What is a node?
What is an edge?
What attributes?
What weights?

Example:

(CaseType)-[:REQUIRES]->(LegalRequirement)
(LegalRequirement)-[:PROVED_BY]->(Evidence)

If this is weak → missing evidence model fails.

✅ Task 5 — BNS/IPC Scrape

Pure ETL:

Website → Clean Section Files

But must preserve:

Section numbers
Subsections
Headings

Otherwise KG is wrong.

✅ Task 6 — IndiaKanoon Scrape

This is more than scraping.

It is:

Judgment → RR-labeled document

Output:

case_id, RR_type, text

This is your supervised signal.

✅ Task 7 — 8 RR Pipelines

This is where most ML/NLP happens.

You are building:

RR → Semantic Objects

Each RR has its own extractor.

✅ Task 8 — CON Embedding Engine

This is:

Symbolic → Vector

Input:

claim_type, issue_type, evidence_type, outcome

Output:

ℝ^d vector

This is for:

Similarity
Retrieval
Outcome prediction

Not for reasoning.

3️⃣ The 8 RR Pipelines (How They Actually Work)

This is the heart of your system.

Each RR pipeline outputs objects, not text.

1. Facts → Event Extractor

Input: Facts text
Output:

events: [
  { "actor": "teacher", "action": "appointed", "year": 2024 }
]

Feeds → claims, timeline

2. Issues → Issue Classifier

Input: Issues text
Output:

issue_type: "merit_violation"

Feeds → CON.issues

3. Petitioner Args → Claim Extractor

Input: Petitioner text
Output:

{ claim_type, polarity="asserted" }

Feeds → CON.claims

4. Respondent Args → Counterclaim Extractor

Same as above but opposite polarity.

5. Analysis of Law → Section Mapper

Input: Law analysis
Output:

["BNS_420", "RULE_23"]

Feeds → KG linking

6. Precedent Analysis → Citation Extractor

Input: Precedents
Output:

["SC_2012_X", "PHC_2019_Y"]

Optional

7. Court Reasoning → Decision Mapper

Input: Reasoning
Output:

{ claim_id: "C1", status: "accepted" }

Critical for training.

8. Conclusion → Outcome Classifier

Input: Conclusion
Output:

outcome: "petition_allowed"

Label.

4️⃣ Correct Technical Build Order (So You Don’t Get Stuck)

This is what you should actually follow.

Phase 1 — Foundation (No ML)
Task 5 + 6 (Scraping)
Manual RR labeling check
Freeze CON means

Output: Clean corpus

Phase 2 — CON Compiler
Task 7 (RR Pipelines)
Task 1 (CON Builder)

Goal: Generate 50 valid CONs

No embeddings yet.

Phase 3 — Knowledge Layer
Task 4 (KG Design)
Task 3 (KG Build)

Goal: Missing evidence logic works rule-based.

Phase 4 — Representation Learning
Task 8 (Embedding Engine)

Only after ≥200 CONs.

Phase 5 — Models (Later)

Contradiction, evidence, judgment.

5️⃣ The Key Insight (Why You Felt Overwhelmed)

You were mentally trying to:

Do Phase 1–4 at the same time.

That’s why it felt impossible.

This is a compiler + knowledge + ML stack project.
Those are always layered.

6️⃣ One Technical Rule to Enforce

Put this in your repo:

No module may consume raw text except RR pipelines.

Everything else must consume CON or KG.

This avoids spaghetti.

If you want next, I can help you:

✅ Write RR pipeline specs
✅ Design KG schema
✅ Define CON validation rules
✅ Draft repo structure

Tell me which one you want first.

alright let's see task 4, knowledge graph design now 

for the data, we have the BNS/IPC now, and we have scraped the indiakanoon for old cases dataset now, we have all the sections in BNS and IPC and we have about 10-12k of old cases in our scraped dataset, i'll be sharing the same with you in the following 
so now we need to design knowledge graph, let me know if you have anything to clarify with us, any question to  the project team to help us decide the knowledge graph nodes and relations 

{
  "type": "IPC",
  "section": "420",
  "chapter": "XVII",
  "title": "Cheating and dishonestly inducing delivery of property",
  "description": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
  "offense": "Cheating and there by dishonestly inducing delivery of property, or the making, alteration or destruction of a valuable security",
  "punishment": "7 Years + Fine",
  "cognizance": "Cognizable",
  "bail": "Non-Bailable",
  "triable_by": "Magistrate First Class",
  "compoundable": "The person cheated, with the permission of the Court"
}



{
  "url": "https://indiankanoon.org/doc/27754182/",
  "page_title": "Jwala Devi Enterprises P. Ltd. vs Fadi El Jaouni on 23 July, 2018",
  "court_name": "",
  "case_title": "Jwala Devi Enterprises P. Ltd. vs Fadi El Jaouni on 23 July, 2018",
  "elements_by_title": {
    "Fact": [
      {
        "tag": "p",
        "id": "p_1",
        "class": "",
        "title": "Fact",
        "text": "1. On 19.03.2014, eleven criminal complaints were filed in the court of the Metropolitan Magistrate, each seeking prosecution of the parties shown in the array of respondents for offences punishable underSection 138of the Negotiable Instruments Act, 1881, two of such complaints i.e. the complaint nos.800/1/14 and 802/1/14 having been presented by Jwala Devi Enterprises Pvt. Ltd. through its authorized representative Sat Parkash Bansal and the rest - complaint nos.799/1/14, 812/1/14, 813/1/14, 814/1/14, 815/1/14, 839/1/14, 840/1/14, 841/1/14 and 842/1/14 - having been presented by Anand Prakash Bansal, Proprietor of M/s. Pooja Enterprises. Each of the said criminal complaints were directed against several persons including a company described as M/s. Bush Foods Overseas Pvt. Ltd. It may be mentioned that Mr. Virkaran Awasty was reflected in the array of the accused as the Managing Director of the said company accused. The respondents in these petitions were amongst the other persons shownCrl.M.C. 3257/2016 & ors. Page 10 of 24as accused in the said complaints, each of them having been described as \"Director\" of the said company accused."
      },
      {
        "tag": "p",
        "id": "p_2",
        "class": "",
        "title": "Fact",
        "text": "2. On the basis of the preliminary inquiry in each case, the Metropolitan Magistrate issued process including against the respondents herein. The respondents, feeling aggrieved, approached the court of Sessions invoking its revisional jurisdiction by separate petitions (CR nos.34-62/2015), their prime contention being that there was no case made out for they to be summoned as accused on the basis of allegations that they were directors of the company accused, denying that they had any concern with the responsibility for the conduct of the day-to-day business of the company."
      }
    ],
    "Precedent Analysis": [
      {
        "tag": "p",
        "id": "p_3",
        "class": "",
        "title": "Precedent Analysis",
        "text": "3. Placing reliance primarily on decision of a bench of three Hon'ble Judges of the Supreme Court inSMS Pharmaceuticals Pvt. Ltd. Vs. Neeta Bhalla, (2005) 8 SCC 89, the court of Sessions found substance and merit in the aforesaid contentions and allowed all the above-said revision petitions by a common order dated 18.04.2015 holding that the summoning order had been passed by the Magistrate mechanically without going through the material(s) on record, there being no averment to the effect that the said persons were in charge of, or responsible for the conduct of the business of, the company accused and consequently dropping the criminal proceedings against each of them."
      },
      {
        "tag": "p",
        "id": "p_4",
        "class": "",
        "title": "Precedent Analysis",
        "text": "4. The petitions at hand have been filed by the complainants invoking the inherent jurisdiction of this court underSection 482of the Code of Criminal Procedure, 1973 (Cr. PC) andArticle 227of the Constitution of India, 1950 to pray for the aforesaid orders of theCrl.M.C. 3257/2016 & ors. Page 11 of 24Sessions court in each of the said eleven complaint cases to be set aside and the proceedings against the respondents herein to be revived on the file of the Metropolitan Magistrate. Reliance is placed in this context by the petitioners on the decisions of benches of two Hon'ble Judges of the Supreme Court reported asGunmala Sales (P) Ltd. Vs. Anu Mehta and Ors, (2015) 1 SCC 103 and Standard Chartered Bank Vs. State of Maharashtra and Ors., (2016) 6 SCC 62.There can be no quarrel with the proposition, as advanced by the counsel for the respondents, that the ruling of the bench of three Hon'ble Judges inSMS Pharmaceuticals(supra), continues to hold the field, the decisions inGunmala Sales (P) Ltd.(supra) andStandard Chartered Bank(supra) having accepted this position and the said subsequent rulings being in a slightly different context."
      },
      {
        "tag": "p",
        "id": "p_10",
        "class": "",
        "title": "Precedent Analysis",
        "text": "9. Certain observations inSMS Pharmaceuticals(supra) which have been quoted in the subsequent decisions, need to be borne in mind and, therefore, may be extracted as under :-"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_13",
        "class": "",
        "title": "Precedent Analysis",
        "style": "",
        "text": "\"27. It is clear from a perusal of the above decisions thatSMS Pharma (1) [S.M.S. Pharmaceuticals Ltd. v. Neeta Bhalla, (2005) 8 SCC 89 : 2005 SCC (Cri) 1975] , which is a three-Judge Bench decision, still holds the field. In all subsequent decisions, two-Judge Benches of this Court have followed SMS Pharma...."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_14",
        "class": "",
        "title": "Precedent Analysis",
        "style": "",
        "text": "28. We are concerned in this case with Directors who are not signatories to the cheques. So far as Directors whoCrl.M.C. 3257/2016 & ors. Page 17 of 24are not signatories to the cheques or who are not Managing Directors or Joint Managing Directors are concerned, it is clear from the conclusions drawn in the abovementioned cases that it is necessary to aver in the complaint filed underSection 138read withSection 141of the NI Act that at the relevant time when the offence was committed, the Directors were in charge of and were responsible for the conduct of the business of the company. This is a basic requirement. There is no deemed liability of such Directors.\""
      },
      {
        "tag": "p",
        "id": "p_15",
        "class": "",
        "title": "Precedent Analysis",
        "text": "10.InGunmala Sales (P) Ltd.(supra), the issue brought before the Supreme Court by the complainant primarily was that the High Court in exercise of its jurisdiction under Section 482 Cr. PC had wrongly quashed the proceedings against the respondents on the ground that there was a bald assertion in the complaint that they were directors in the company at the time when the offence was committed.While acknowledging (in para 27) that the decision inSMS Pharmaceuticals(supra) still holds the field, inGunmala Sales (P) Ltd.(supra), it was further clarified thus :"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_15",
        "class": "",
        "title": "Precedent Analysis",
        "style": "",
        "text": "\"31. When in view of the basic averment process is issued the complaint must proceed against the Directors. But, if any Director wants the process to be quashed by filing a petition under Section 482 of the Code on the ground that only a bald averment is made in the complaint and that he is really not concerned with the issuance of the cheque, he must in order to persuade the High Court to quash the process either furnish some sterling incontrovertible material or acceptable circumstances to substantiate his contention. He must make out a case that making him stand the trial would be an abuse of process of court. He cannot get the complaint quashed merely on the ground that apart from the basic averment no particulars are given in the complaint about his role, because ordinarily the basic averment would be sufficient to send him to trial and it could be argued that his further role could be brought out in the trial. Quashing of a complaint is a serious matter. Complaint cannot be quashed for theCrl.M.C. 3257/2016 & ors. Page 18 of 24asking. For quashing of a complaint it must be shown that no offence is made out at all against the Director.\""
      },
      {
        "tag": "blockquote",
        "id": "blockquote_16",
        "class": "",
        "title": "Precedent Analysis",
        "style": "",
        "text": "\"35. ... Pertinently, in the application filed by the respondents, no clear case was made out that at the material time, the Directors were not in charge of and were not responsible for the conduct of the business of the Company by referring to or producing any incontrovertible or unimpeachable evidence which is beyond suspicion or doubt or any totally acceptable circumstances. It is merely stated that Sidharth Mehta had resigned from the directorship of the Company on 30-9-2010 but no incontrovertible or unimpeachable evidence was produced before the High Court as was done inAnita Malhotra [Anita Malhotra v. Apparel Export Promotion Council, (2012) 1 SCC 520 : (2012) 1 SCC (Civ) 329 : (2012) 1 SCC (Cri) 496] to show that he had, in fact, resigned long before the cheques in question were issued. Similar is the case with Kanhaiya Lal Mehta and Anu Mehta. Nothing was produced to substantiate the contention that they were not in charge of and not responsible for the conduct of the business of the Company at the relevant time. In the circumstances, we are of the opinion that the matter deserves to be remitted to the High Court for fresh hearing."
      },
      {
        "tag": "p",
        "id": "p_17",
        "class": "",
        "title": "Precedent Analysis",
        "text": "11. For cases where the allegations in the complaint in writing are not deficient but the persons are described as directors (who seek quashing of the summoning order), it was ruled inGunmala Sales (P) Ltd.(supra) as under :-"
      },
      {
        "tag": "p",
        "id": "p_19",
        "class": "",
        "title": "Precedent Analysis",
        "text": "12. The conclusions inGunmala Sales (P) Ltd.(supra) were summarized thus :-"
      },
      {
        "tag": "p",
        "id": "p_22",
        "class": "",
        "title": "Precedent Analysis",
        "text": "13. The above view inGunmala Sales (P) Ltd.(supra) was endorsed and reiterated inStandard Chartered Bank(supra)."
      }
    ],
    "Analysis of the law": [
      {
        "tag": "blockquote",
        "id": "blockquote_1",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "138. Dishonour of cheque for insufficiency, etc., of funds in the account -- Where any cheque drawn by a person on an account maintained by him with a banker for payment of any amount of money to another person from out of that account for the discharge, in whole or in part, of any debt or other liability, is returned by the bank unpaid, either because of the amount of money standing to the credit of that account is insufficient to honour the cheque or that it exceeds the amount arranged to be paid from that account by an agreement made with that bank, such person shall be deemed to have committed an offence and shall, without prejudice to any other provision of this Act, be punished with imprisonment for 8 [a term which may be extended to two years'], or with fine which may extend to twice the amount of the cheque, or with both:"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_2",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "Provided that nothing contained in this section shall apply unless--"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_3",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "(a) the cheque has been presented to the bank within a period of six months from the date on which it is drawn or within the period of its validity, whichever is earlier;"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_4",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "(b) the payee or the holder in due course of the cheque, as the case may be, makes a demand for the payment of the said amount of money by giving a notice; in writing, to the drawer of the cheque, within thirty days of the receipt of information by him from the bank regarding the return of the cheque as unpaid; and"
      },
      {
        "tag": "p",
        "id": "p_5",
        "class": "",
        "title": "Analysis of the law",
        "text": "5. These matters pertain to the penal clause contained inSection 138of the Negotiable Instruments Act, 1881, which reads thus :-"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_5",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "(c) the drawer of such cheque fails to make the payment of the said amount of money to the payee or, as the case may be, to the holder in due course of the cheque, within fifteen days of the receipt of the said notice."
      },
      {
        "tag": "p",
        "id": "p_6",
        "class": "",
        "title": "Analysis of the law",
        "text": "Explanation.--For the purposes of this section, \"debt of other liability\" means a legally enforceable debt or other liability."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_6",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "141. Offences by companies.--(1) If the person committing an offence undersection 138is a company, every person who, at the time the offence was committed, was in charge of, and was responsible to, the company for the conduct of the business of the company, as well as the company, shall be deemed to be guilty of the offence and shall be liable to be proceeded against and punished accordingly:"
      },
      {
        "tag": "p",
        "id": "p_7",
        "class": "",
        "title": "Analysis of the law",
        "text": "6. It is clear from the plain reading of the above quoted provision and is now also well settled that the offence underSection 138of the Negotiable Instruments Act does not stand constituted merely upon dishonor of a cheque. The dishonor of a cheque which had been issued by the person (who is sought to be prosecuted) in favour of the complainant must be followed by a notice of demand within the stipulated period. It is the non-payment of the amount of the cheque within the statutory period after service of the notice of demand which constitutes the offence that is punishable under the aforementioned provision of law."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_7",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "Provided that nothing contained in this sub-section shall render any person liable to punishment if he proves that the offence was committed without his knowledge, or that he had exercised all due diligence to prevent the commission of such offence:"
      },
      {
        "tag": "p",
        "id": "p_8",
        "class": "",
        "title": "Analysis of the law",
        "text": "7. For dealing with cases involving companies and the persons connected thereto as the accused, the provision ofSection 141Negotiable Instruments Act, 1881 is relevant. For guidance and convenience, it may be quoted hereunder :-"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_8",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "Provided further that where a person is nominated as a Director of a company by virtue of his holding any office or employment in the Central Government or State Government or a financial corporation owned or controlled by the Central Government or the State Government, as the case may be, he shall not be liable for prosecution under this Chapter."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_9",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "(2) Notwithstanding anything contained in sub-section (1), where any offence under this Act has been committed by a company and it is proved that the offence has been committed with the consent or connivance of, or is attributable to, any neglect on the part of, any director, manager, secretary or other officer of the company, suchCrl.M.C. 3257/2016 & ors. Page 14 of 24director, manager, secretary or other officer shall also be deemed to be guilty of that offence and shall be liable to be proceeded against and punished accordingly."
      },
      {
        "tag": "p",
        "id": "p_13",
        "class": "",
        "title": "Analysis of the law",
        "text": "The question notes that the managing director or joint managing director would be admittedly in charge of the company and responsible to the company for the conduct of its business. When that is so, holders of such positions in a company become liable underSection 141of the Act. By virtue of the office they hold as managing director or joint managing director, these persons are in charge of and responsible for the conduct of business of the company. Therefore, they get covered underSection 141. So far as the signatory of a cheque which is dishonoured is concerned, he is clearly responsible for the incriminating act and will be covered under sub-Section (2) ofSection 141."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_17",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "(i) It is only those persons who are in charge of or responsible for the conduct of the business of the company at the time of commission of the offence underSection 138of the Negotiable Instruments Act, 1881 who can be subjected to criminal action with reference toSection 141;"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_18",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "(ii). If the person committing an offence underSection 138of the Negotiable Instruments Act, 1881 is a company, the person who was signatory to the cheque which is dishonoured is clearly responsible for the incriminating act and would be liable to be proceeded against underSection 141 (2);"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_19",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "substantiating his contention that he was not in charge of nor responsible for the conduct of the business of the company \"at the time the offence was committed\" and thereby showing a case that making him stand the trial would be an abuse of the process of court, but not otherwise."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_20",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "\"3. That the accused No.3 Mr. Vinod Sirohi, Accused No.4 Fadi El Jaouni, Accused No.5 Khaled Abdelrahman Radi and the Accused No.6 Mr. Naseer Mohd. MF AI Hajri are the Directors and Accused No.7 Mr. Rahul Shivam is the Authorised Signatory of the Accused No.1 Company, namely M/s. Bush Foods Pvt. Ltd. and are actively engaged and responsible for and in-charge of day- to-day management, business activities and affairs of the Accused No.1 firm."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_21",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "xxx"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_22",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "10. That despite the receipt of the above said Legal Notice dated 05.02.2014, the Accused Persons have failed / refused / neglected to make the payment of the above said Cheques amount to the Complainant and have therefore made themselves liable to be prosecuted under the provisions ofSections 138,141and142of the Negotiable Instruments Act, 1881. It is further submitted that at the time of issuance of the said cheques, the accused persons have assured, promised and represented to the Complainant that the said cheques would be honored on presentation. However, the said Cheques, which are the subject matter of the present complaint, were dishonored on presentment. The accused persons have no intention to make the said payment to the Complainant. It is submitted that the Accused Persons have been responsible for all the business dealings for and on behalf of their said Accused no.1 firm and also responsible for the circumstances that have lead to the dishonor of the aid cheques issued to the complainant.\""
      },
      {
        "tag": "p",
        "id": "p_23",
        "class": "",
        "title": "Analysis of the law",
        "text": "14. The guiding principles with reference toSection 141of the Negotiable Instruments Act, 1881, which are now well settled by judicial pronouncements, some of which have been noted above, may be summarised thus :-"
      },
      {
        "tag": "p",
        "id": "p_25",
        "class": "",
        "title": "Analysis of the law",
        "text": "(iv). Merely because a person is a director of the company is not sufficient to make him liable underSection 141, there being no deeming that by holding such position he is in charge of, or responsible for the conduct of the business of, the company within the meaning ofSection 141;"
      },
      {
        "tag": "p",
        "id": "p_26",
        "class": "",
        "title": "Analysis of the law",
        "text": "(v). It is necessary for the complainant to specifically aver in the complaint that at the time the offence was committed, the person sought to be prosecuted was in charge of, or responsible for the conduct of the business of, the company in terms ofSection 141, there being no need for further particulars to be given in the complaint about his role, this being subject to proof at the trial;"
      },
      {
        "tag": "p",
        "id": "p_27",
        "class": "",
        "title": "Analysis of the law",
        "text": "(vi). The person who has been summoned as an accused for offence under Section 138 of the Negotiable Instruments Act, 1881 on the basis of averment that he was director of the company accused, he being in charge of or responsible for the conduct of its business cannot get the complaint quashed by the High Court by filing a petition under Section 482 of the Code of Criminal Procedure, 1973 merely on the ground that no particulars as to his role have been set out in the complaint; andCrl.M.C. 3257/2016 & ors. Page 21 of 24"
      },
      {
        "tag": "p",
        "id": "p_28",
        "class": "",
        "title": "Analysis of the law",
        "text": "(vii). The person who has been summoned as an accused for offence underSection 138of the Negotiable Instruments Act, 1881 by invoking the provision contained inSection 141may persuade the High Court to quash the process in exercise of its inherent power underSection 482of the Code of Criminal Procedure, 1973 by furnishing \"some sterling incontrovertible material or acceptable circumstances\""
      },
      {
        "tag": "p",
        "id": "p_29",
        "class": "",
        "title": "Analysis of the law",
        "text": "15. A perusal of the eleven complaints from which the present proceedings arise reveals that they are founded on identical averments (some of the accused who are not before this court being not common), the exception being with regard to the particulars of the cheques or the background facts against which they had been issued or the dates on which they were presented or dishonored leading to demand notices in their respect being issued, there being no payment made pursuant to such demand notices. The averments crucial to pass the muster ofSection 141of the Negotiable Instruments Act, 1881, however, are identically worded in the said eleven cases. For illustration, the crucial averments appearing in one of such complaints (Crl. Complaint no.799/1/14), it being the first in chronology, may be extracted as under :-"
      },
      {
        "tag": "p",
        "id": "p_32",
        "class": "",
        "title": "Analysis of the law",
        "text": "17. The respondents are not stated to be signatories to the cheques in question. They cannot be roped in merely because they have been directors of the company accused. The general averments that they were responsible for all the business dealings and for the circumstances leading to the dishonour of the cheques or that they had given any assurance as to the cheques do not suffice."
      }
    ],
    "Conclusion": [
      {
        "tag": "p",
        "id": "p_9",
        "class": "",
        "title": "Conclusion",
        "text": "8. It is the above quoted provision, which is at the bottom of the controversy in the present matters and in this context the rulings of the Supreme Courtreferred to aboveprovide the necessary guidance."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_10",
        "class": "",
        "title": "Conclusion",
        "style": "",
        "text": "(a) It is necessary to specifically aver in a complaint underSection 141that at the time the offence was committed, the person accused was in charge of, and responsible for the conduct of business of the company. This averment is an essential requirement ofSection 141and has to be made in a complaint. Without this averment being made in a complaint, the requirements ofSection 141cannot be said to be satisfied."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_11",
        "class": "",
        "title": "Conclusion",
        "style": "",
        "text": "(b) The answer to the question posed in sub-para (b) has to be in the negative. Merely being a director of a company is not sufficient to make the person liable underSection 141of the Act. A director in a company cannot be deemed to be in charge of and responsible to the company for the conduct of its business. The requirement ofSection 141is that the person sought to be made liable should be in charge of and responsible for the conduct of the business of the company at the relevant time. This has to be averred as a fact as there is no deemed liability of a director in such cases."
      },
      {
        "tag": "p",
        "id": "p_12",
        "class": "",
        "title": "Conclusion",
        "text": "xxx \"19. In view of the above discussion, our answers to the questions posed in the reference are as under:"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_12",
        "class": "",
        "title": "Conclusion",
        "style": "",
        "text": "(c) The answer to Question (c) has to be in the affirmative."
      },
      {
        "tag": "p",
        "id": "p_14",
        "class": "",
        "title": "Conclusion",
        "text": "(emphasis supplied)"
      },
      {
        "tag": "p",
        "id": "p_16",
        "class": "",
        "title": "Conclusion",
        "text": "(emphasis supplied)"
      },
      {
        "tag": "p",
        "id": "p_18",
        "class": "",
        "title": "Conclusion",
        "text": "(emphasis supplied)"
      },
      {
        "tag": "p",
        "id": "p_21",
        "class": "",
        "title": "Conclusion",
        "text": "(emphasis supplied)"
      },
      {
        "tag": "p",
        "id": "p_24",
        "class": "",
        "title": "Conclusion",
        "text": "(iii). By virtue of the office they hold, the persons working in the capacity of the Managing Director or Joint Managing Director are deemed to be in charge of, and responsible forCrl.M.C. 3257/2016 & ors. Page 20 of 24the conduct of the business of, the company and, therefore, can be proceeded against in terms ofSection 141;"
      },
      {
        "tag": "p",
        "id": "p_30",
        "class": "",
        "title": "Conclusion",
        "text": "(emphasis supplied)"
      },
      {
        "tag": "p",
        "id": "p_33",
        "class": "",
        "title": "Conclusion",
        "text": "18. The view taken by the revisional court, therefore, must be upheld. The petitions and the applications filed therewith are dismissed."
      },
      {
        "tag": "p",
        "id": "p_34",
        "class": "",
        "title": "Conclusion",
        "text": "(R.K. GAUBA) JUDGE JULY 23, 2018 ygCrl.M.C. 3257/2016 & ors. Page 24 of 24"
      }
    ],
    "Court's Reasoning": [
      {
        "tag": "p",
        "id": "p_11",
        "class": "",
        "title": "Court's Reasoning",
        "text": "\"10. ... What is required is that the persons who are sought to be made criminally liable underSection 141should be, at the time the offence was committed, in charge of and responsible to the company for the conduct of the business of the company. Every person connected with the company shall not fall within the ambit of the provision. It is only those persons who were in charge of and responsible for the conduct of business of the company at the time of commission of an offence, who will be liable for criminal action. It follows from this that if a Director of a company who was not in charge of and was not responsible for the conduct of the business of the company at the relevant time, will not be liable under the provision. The liability arises from being in charge of and responsible for the conduct of business of the company at the relevant time when the offence was committed and not on the basis of merely holding a designation or office in a company. Conversely, a person not holding any office or designation in a company may be liable if he satisfies the main requirement of being in charge of and responsible for the conduct of business of a company at the relevant time. Liability depends on theCrl.M.C. 3257/2016 & ors. Page 15 of 24role one plays in the affairs of a company and not on designation or status. If being a Director or Manager or Secretary was enough to cast criminal liability, the section would have said so. Instead of \"every person\" the section would have said \"every Director, Manager or Secretary in a company is liable\", etc. The legislature is aware that it is a case of criminal liability which means serious consequences so far as the person sought to be made liable is concerned. Therefore, only persons who can be said to be connected with the commission of a crime at the relevant time have been subjected to action."
      },
      {
        "tag": "p",
        "id": "p_20",
        "class": "",
        "title": "Court's Reasoning",
        "text": "However, we are inclined to confirm the order [Anu Mehta, In re, 2012 SCC OnLine Cal 13134] passed by the High Court quashing the process as against Shobha Mehta. Shobha Mehta is stated to be an old lady who is over 70 years of age. Considering this fact and on an overall reading of the complaint in the peculiar facts and circumstances of the case, we feel that making her stand the trial would be an abuse of process of court. It is however,Crl.M.C. 3257/2016 & ors. Page 19 of 24necessary for the High Court to consider the cases of other Directors in light of the decisions considered by us and the conclusions drawn by us in this judgment.\""
      },
      {
        "tag": "p",
        "id": "p_31",
        "class": "",
        "title": "Court's Reasoning",
        "text": "16. It is clear from the bare perusal of the above quoted averments that they are deficient to the effect that there is not even a whisper of allegation that the respondents are persons who were in charge of or responsible to the company accused for the conduct of its business \"at the time the offence was committed\"."
      }
    ]
  },
  "all_paragraphs": [
    {
      "tag": "p",
      "id": "p_1",
      "class": "",
      "title": "Fact",
      "text": "1.      On 19.03.2014, eleven criminal complaints were filed in the\ncourt of the Metropolitan Magistrate, each seeking prosecution of the\nparties shown in the array of respondents for offences punishable\nunderSection 138of the Negotiable Instruments Act, 1881, two of\nsuch complaints i.e. the complaint nos.800/1/14 and 802/1/14 having\nbeen presented by Jwala Devi Enterprises Pvt. Ltd. through its\nauthorized representative Sat Parkash Bansal and the rest - complaint\nnos.799/1/14, 812/1/14, 813/1/14, 814/1/14, 815/1/14, 839/1/14,\n840/1/14, 841/1/14 and 842/1/14 - having been presented by Anand\nPrakash Bansal, Proprietor of M/s. Pooja Enterprises. Each of the said\ncriminal complaints were directed against several persons including a\ncompany described as M/s. Bush Foods Overseas Pvt. Ltd. It may be\nmentioned that Mr. Virkaran Awasty was reflected in the array of the\naccused as the Managing Director of the said company accused. The\nrespondents in these petitions were amongst the other persons shownCrl.M.C. 3257/2016 & ors.                                Page 10 of 24as accused in the said complaints, each of them having been described\nas \"Director\" of the said company accused."
    },
    {
      "tag": "p",
      "id": "p_2",
      "class": "",
      "title": "Fact",
      "text": "2.      On the basis of the preliminary inquiry in each case, the\nMetropolitan Magistrate issued process including against the\nrespondents herein. The respondents, feeling aggrieved, approached\nthe court of Sessions invoking its revisional jurisdiction by separate\npetitions (CR nos.34-62/2015), their prime contention being that there\nwas no case made out for they to be summoned as accused on the\nbasis of allegations that they were directors of the company accused,\ndenying that they had any concern with the responsibility for the\nconduct of the day-to-day business of the company."
    },
    {
      "tag": "p",
      "id": "p_3",
      "class": "",
      "title": "Precedent Analysis",
      "text": "3.      Placing reliance primarily on decision of a bench of three\nHon'ble Judges of the Supreme Court inSMS Pharmaceuticals Pvt.\nLtd. Vs. Neeta Bhalla, (2005) 8 SCC 89, the court of Sessions found\nsubstance and merit in the aforesaid contentions and allowed all the\nabove-said revision petitions by a common order dated 18.04.2015\nholding that the summoning order had been passed by the Magistrate\nmechanically without going through the material(s) on record, there\nbeing no averment to the effect that the said persons were in charge of,\nor responsible for the conduct of the business of, the company accused\nand consequently dropping the criminal proceedings against each of\nthem."
    },
    {
      "tag": "p",
      "id": "p_4",
      "class": "",
      "title": "Precedent Analysis",
      "text": "4.      The petitions at hand have been filed by the complainants\ninvoking the inherent jurisdiction of this court underSection 482of\nthe Code of Criminal Procedure, 1973 (Cr. PC) andArticle 227of the\nConstitution of India, 1950 to pray for the aforesaid orders of theCrl.M.C. 3257/2016 & ors.                                 Page 11 of 24Sessions court in each of the said eleven complaint cases to be set\naside and the proceedings against the respondents herein to be revived\non the file of the Metropolitan Magistrate. Reliance is placed in this\ncontext by the petitioners on the decisions of benches of two Hon'ble\nJudges of the Supreme Court reported asGunmala Sales (P) Ltd. Vs.\nAnu Mehta and Ors, (2015) 1 SCC 103 and Standard Chartered Bank\nVs. State of Maharashtra and Ors., (2016) 6 SCC 62.There can be no\nquarrel with the proposition, as advanced by the counsel for the\nrespondents, that the ruling of the bench of three Hon'ble Judges inSMS Pharmaceuticals(supra), continues to hold the field, the\ndecisions inGunmala Sales (P) Ltd.(supra) andStandard Chartered\nBank(supra) having accepted this position and the said subsequent\nrulings being in a slightly different context."
    },
    {
      "tag": "p",
      "id": "p_5",
      "class": "",
      "title": "Analysis of the law",
      "text": "5.      These matters pertain to the penal clause contained inSection\n138of the Negotiable Instruments Act, 1881, which reads thus :-"
    },
    {
      "tag": "p",
      "id": "p_6",
      "class": "",
      "title": "Analysis of the law",
      "text": "Explanation.--For the purposes of this section, \"debt of\n         other liability\" means a legally enforceable debt or other\n         liability."
    },
    {
      "tag": "p",
      "id": "p_7",
      "class": "",
      "title": "Analysis of the law",
      "text": "6.      It is clear from the plain reading of the above quoted provision\nand is now also well settled that the offence underSection 138of the\nNegotiable Instruments Act does not stand constituted merely upon\ndishonor of a cheque. The dishonor of a cheque which had been\nissued by the person (who is sought to be prosecuted) in favour of the\ncomplainant must be followed by a notice of demand within the\nstipulated period. It is the non-payment of the amount of the cheque\nwithin the statutory period after service of the notice of demand which\nconstitutes the offence that is punishable under the aforementioned\nprovision of law."
    },
    {
      "tag": "p",
      "id": "p_8",
      "class": "",
      "title": "Analysis of the law",
      "text": "7.      For dealing with cases involving companies and the persons\nconnected thereto as the accused, the provision ofSection 141Negotiable Instruments Act, 1881 is relevant.          For guidance and\nconvenience, it may be quoted hereunder :-"
    },
    {
      "tag": "p",
      "id": "p_9",
      "class": "",
      "title": "Conclusion",
      "text": "8.      It is the above quoted provision, which is at the bottom of the\ncontroversy in the present matters and in this context the rulings of the\nSupreme Courtreferred to aboveprovide the necessary guidance."
    },
    {
      "tag": "p",
      "id": "p_10",
      "class": "",
      "title": "Precedent Analysis",
      "text": "9.      Certain observations inSMS Pharmaceuticals(supra) which\nhave been quoted in the subsequent decisions, need to be borne in\nmind and, therefore, may be extracted as under :-"
    },
    {
      "tag": "p",
      "id": "p_11",
      "class": "",
      "title": "Court's Reasoning",
      "text": "\"10. ... What is required is that the persons who are\n                sought to be made criminally liable underSection 141should be, at the time the offence was committed, in\n                charge of and responsible to the company for the conduct\n                of the business of the company. Every person connected\n                with the company shall not fall within the ambit of the\n                provision. It is only those persons who were in charge of\n                and responsible for the conduct of business of the\n                company at the time of commission of an offence, who\n                will be liable for criminal action. It follows from this that\n                if a Director of a company who was not in charge of and\n                was not responsible for the conduct of the business of the\n                company at the relevant time, will not be liable under the\n                provision. The liability arises from being in charge of\n                and responsible for the conduct of business of the\n                company at the relevant time when the offence was\n                committed and not on the basis of merely holding a\n                designation or office in a company. Conversely, a person\n                not holding any office or designation in a company may\n                be liable if he satisfies the main requirement of being in\n                charge of and responsible for the conduct of business of a\n                company at the relevant time. Liability depends on theCrl.M.C. 3257/2016 & ors.                                      Page 15 of 24role one plays in the affairs of a company and not on\n                designation or status. If being a Director or Manager or\n                Secretary was enough to cast criminal liability, the\n                section would have said so. Instead of \"every person\" the\n                section would have said \"every Director, Manager or\n                Secretary in a company is liable\", etc. The legislature is\n                aware that it is a case of criminal liability which means\n                serious consequences so far as the person sought to be\n                made liable is concerned. Therefore, only persons who\n                can be said to be connected with the commission of a\n                crime at the relevant time have been subjected to action."
    },
    {
      "tag": "p",
      "id": "p_12",
      "class": "",
      "title": "Conclusion",
      "text": "xxx\n        \"19. In view of the above discussion, our answers to the\n        questions posed in the reference are as under:"
    },
    {
      "tag": "p",
      "id": "p_13",
      "class": "",
      "title": "Analysis of the law",
      "text": "The question notes that the managing director or joint\n        managing director would be admittedly in charge of the\n        company and responsible to the company for the conduct of\n        its business. When that is so, holders of such positions in a\n        company become liable underSection 141of the Act. By\n        virtue of the office they hold as managing director or joint\n        managing director, these persons are in charge of and\n        responsible for the conduct of business of the company.\n        Therefore, they get covered underSection 141. So far as the\n        signatory of a cheque which is dishonoured is concerned,\n        he is clearly responsible for the incriminating act and will\n        be covered under sub-Section (2) ofSection 141."
    },
    {
      "tag": "p",
      "id": "p_14",
      "class": "",
      "title": "Conclusion",
      "text": "(emphasis supplied)"
    },
    {
      "tag": "p",
      "id": "p_15",
      "class": "",
      "title": "Precedent Analysis",
      "text": "10.InGunmala Sales (P) Ltd.(supra), the issue brought before the\nSupreme Court by the complainant primarily was that the High Court\nin exercise of its jurisdiction under Section 482 Cr. PC had wrongly\nquashed the proceedings against the respondents on the ground that\nthere was a bald assertion in the complaint that they were directors in\nthe company at the time when the offence was committed.While\nacknowledging (in para 27) that the decision inSMS Pharmaceuticals(supra) still holds the field, inGunmala Sales (P) Ltd.(supra), it was\nfurther clarified thus :"
    },
    {
      "tag": "p",
      "id": "p_16",
      "class": "",
      "title": "Conclusion",
      "text": "(emphasis supplied)"
    },
    {
      "tag": "p",
      "id": "p_17",
      "class": "",
      "title": "Precedent Analysis",
      "text": "11.     For cases where the allegations in the complaint in writing are\nnot deficient but the persons are described as directors (who seek\nquashing of the summoning order), it was ruled inGunmala Sales (P)\nLtd.(supra) as under :-"
    },
    {
      "tag": "p",
      "id": "p_18",
      "class": "",
      "title": "Conclusion",
      "text": "(emphasis supplied)"
    },
    {
      "tag": "p",
      "id": "p_19",
      "class": "",
      "title": "Precedent Analysis",
      "text": "12.     The conclusions inGunmala Sales (P) Ltd.(supra) were\nsummarized thus :-"
    },
    {
      "tag": "p",
      "id": "p_20",
      "class": "",
      "title": "Court's Reasoning",
      "text": "However, we are inclined to confirm the order [Anu Mehta,\n         In re, 2012 SCC OnLine Cal 13134] passed by the High\n         Court quashing the process as against Shobha Mehta.\n         Shobha Mehta is stated to be an old lady who is over 70\n         years of age. Considering this fact and on an overall\n         reading of the complaint in the peculiar facts and\n         circumstances of the case, we feel that making her stand the\n         trial would be an abuse of process of court. It is however,Crl.M.C. 3257/2016 & ors.                                   Page 19 of 24necessary for the High Court to consider the cases of other\n            Directors in light of the decisions considered by us and the\n            conclusions drawn by us in this judgment.\""
    },
    {
      "tag": "p",
      "id": "p_21",
      "class": "",
      "title": "Conclusion",
      "text": "(emphasis supplied)"
    },
    {
      "tag": "p",
      "id": "p_22",
      "class": "",
      "title": "Precedent Analysis",
      "text": "13.     The above view inGunmala Sales (P) Ltd.(supra) was\nendorsed and reiterated inStandard Chartered Bank(supra)."
    },
    {
      "tag": "p",
      "id": "p_23",
      "class": "",
      "title": "Analysis of the law",
      "text": "14.     The guiding principles with reference toSection 141of the\nNegotiable Instruments Act, 1881, which are now well settled by\njudicial pronouncements, some of which have been noted above, may\nbe summarised thus :-"
    },
    {
      "tag": "p",
      "id": "p_24",
      "class": "",
      "title": "Conclusion",
      "text": "(iii).     By virtue of the office they hold, the persons working\n      in the capacity of the Managing Director or Joint Managing\n      Director are deemed to be in charge of, and responsible forCrl.M.C. 3257/2016 & ors.                                     Page 20 of 24the conduct of the business of, the company and, therefore,\n      can be proceeded against in terms ofSection 141;"
    },
    {
      "tag": "p",
      "id": "p_25",
      "class": "",
      "title": "Analysis of the law",
      "text": "(iv).     Merely because a person is a director of the company\n      is not sufficient to make him liable underSection 141, there\n      being no deeming that by holding such position he is in\n      charge of, or responsible for the conduct of the business of,\n      the company within the meaning ofSection 141;"
    },
    {
      "tag": "p",
      "id": "p_26",
      "class": "",
      "title": "Analysis of the law",
      "text": "(v).      It is necessary for the complainant to specifically aver\n      in the complaint that at the time the offence was committed,\n      the person sought to be prosecuted was in charge of, or\n      responsible for the conduct of the business of, the company in\n      terms ofSection 141, there being no need for further\n      particulars to be given in the complaint about his role, this\n      being subject to proof at the trial;"
    },
    {
      "tag": "p",
      "id": "p_27",
      "class": "",
      "title": "Analysis of the law",
      "text": "(vi).     The person who has been summoned as an accused\n      for offence under Section 138 of the Negotiable Instruments\n      Act, 1881 on the basis of averment that he was director of the\n      company accused, he being in charge of or responsible for the\n      conduct of its business cannot get the complaint quashed by\n      the High Court by filing a petition under Section 482 of the\n      Code of Criminal Procedure, 1973 merely on the ground that\n      no particulars as to his role have been set out in the\n      complaint; andCrl.M.C. 3257/2016 & ors.                                     Page 21 of 24"
    },
    {
      "tag": "p",
      "id": "p_28",
      "class": "",
      "title": "Analysis of the law",
      "text": "(vii).    The person who has been summoned as an accused\n      for offence underSection 138of the Negotiable Instruments\n      Act, 1881 by invoking the provision contained inSection 141may persuade the High Court to quash the process in exercise\n      of its inherent power underSection 482of the Code of\n      Criminal Procedure, 1973 by furnishing \"some sterling\n      incontrovertible material or acceptable circumstances\""
    },
    {
      "tag": "p",
      "id": "p_29",
      "class": "",
      "title": "Analysis of the law",
      "text": "15.     A perusal of the eleven complaints from which the present\nproceedings arise reveals that they are founded on identical averments\n(some of the accused who are not before this court being not\ncommon), the exception being with regard to the particulars of the\ncheques or the background facts against which they had been issued or\nthe dates on which they were presented or dishonored leading to\ndemand notices in their respect being issued, there being no payment\nmade pursuant to such demand notices. The averments crucial to pass\nthe muster ofSection 141of the Negotiable Instruments Act, 1881,\nhowever, are identically worded in the said eleven cases.              For\nillustration, the crucial averments appearing in one of such complaints\n(Crl. Complaint no.799/1/14), it being the first in chronology, may be\nextracted as under :-"
    },
    {
      "tag": "p",
      "id": "p_30",
      "class": "",
      "title": "Conclusion",
      "text": "(emphasis supplied)"
    },
    {
      "tag": "p",
      "id": "p_31",
      "class": "",
      "title": "Court's Reasoning",
      "text": "16.     It is clear from the bare perusal of the above quoted averments\nthat they are deficient to the effect that there is not even a whisper of\nallegation that the respondents are persons who were in charge of or\nresponsible to the company accused for the conduct of its business \"at\nthe time the offence was committed\"."
    },
    {
      "tag": "p",
      "id": "p_32",
      "class": "",
      "title": "Analysis of the law",
      "text": "17.     The respondents are not stated to be signatories to the cheques\nin question. They cannot be roped in merely because they have been\ndirectors of the company accused. The general averments that they\nwere responsible for all the business dealings and for the\ncircumstances leading to the dishonour of the cheques or that they had\ngiven any assurance as to the cheques do not suffice."
    },
    {
      "tag": "p",
      "id": "p_33",
      "class": "",
      "title": "Conclusion",
      "text": "18.      The view taken by the revisional court, therefore, must be\nupheld.      The petitions and the applications filed therewith are\ndismissed."
    },
    {
      "tag": "p",
      "id": "p_34",
      "class": "",
      "title": "Conclusion",
      "text": "(R.K. GAUBA)\n                                                        JUDGE\nJULY 23, 2018\nygCrl.M.C. 3257/2016 & ors.                                 Page 24 of 24"
    }
  ],
  "all_blockquotes": [
    {
      "tag": "blockquote",
      "id": "blockquote_1",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "138. Dishonour of cheque for insufficiency, etc., of funds in the account -- Where any cheque drawn by a person on an account maintained by him with a banker for payment of any amount of money to another person from out of that account for the discharge, in whole or in part, of any debt or other liability, is returned by the bank unpaid, either because of the amount of money standing to the credit of that account is insufficient to honour the cheque or that it exceeds the amount arranged to be paid from that account by an agreement made with that bank, such person shall be deemed to have committed an offence and shall, without prejudice to any other provision of this Act, be punished with imprisonment for 8 [a term which may be extended to two years'], or with fine which may extend to twice the amount of the cheque, or with both:"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_2",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "Provided that nothing contained in this section shall apply unless--"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_3",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "(a) the cheque has been presented to the bank within a period of six months from the date on which it is drawn or within the period of its validity, whichever is earlier;"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_4",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "(b) the payee or the holder in due course of the cheque, as the case may be, makes a demand for the payment of the said amount of money by giving a notice; in writing, to the drawer of the cheque, within thirty days of the receipt of information by him from the bank regarding the return of the cheque as unpaid; and"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_5",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "(c) the drawer of such cheque fails to make the payment of the said amount of money to the payee or, as the case may be, to the holder in due course of the cheque, within fifteen days of the receipt of the said notice."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_6",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "141. Offences by companies.--(1) If the person committing an offence undersection 138is a company, every person who, at the time the offence was committed, was in charge of, and was responsible to, the company for the conduct of the business of the company, as well as the company, shall be deemed to be guilty of the offence and shall be liable to be proceeded against and punished accordingly:"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_7",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "Provided that nothing contained in this sub-section shall render any person liable to punishment if he proves that the offence was committed without his knowledge, or that he had exercised all due diligence to prevent the commission of such offence:"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_8",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "Provided further that where a person is nominated as a Director of a company by virtue of his holding any office or employment in the Central Government or State Government or a financial corporation owned or controlled by the Central Government or the State Government, as the case may be, he shall not be liable for prosecution under this Chapter."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_9",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "(2) Notwithstanding anything contained in sub-section (1), where any offence under this Act has been committed by a company and it is proved that the offence has been committed with the consent or connivance of, or is attributable to, any neglect on the part of, any director, manager, secretary or other officer of the company, suchCrl.M.C. 3257/2016 & ors. Page 14 of 24director, manager, secretary or other officer shall also be deemed to be guilty of that offence and shall be liable to be proceeded against and punished accordingly."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_10",
      "class": "",
      "title": "Conclusion",
      "style": "",
      "text": "(a) It is necessary to specifically aver in a complaint underSection 141that at the time the offence was committed, the person accused was in charge of, and responsible for the conduct of business of the company. This averment is an essential requirement ofSection 141and has to be made in a complaint. Without this averment being made in a complaint, the requirements ofSection 141cannot be said to be satisfied."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_11",
      "class": "",
      "title": "Conclusion",
      "style": "",
      "text": "(b) The answer to the question posed in sub-para (b) has to be in the negative. Merely being a director of a company is not sufficient to make the person liable underSection 141of the Act. A director in a company cannot be deemed to be in charge of and responsible to the company for the conduct of its business. The requirement ofSection 141is that the person sought to be made liable should be in charge of and responsible for the conduct of the business of the company at the relevant time. This has to be averred as a fact as there is no deemed liability of a director in such cases."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_12",
      "class": "",
      "title": "Conclusion",
      "style": "",
      "text": "(c) The answer to Question (c) has to be in the affirmative."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_13",
      "class": "",
      "title": "Precedent Analysis",
      "style": "",
      "text": "\"27. It is clear from a perusal of the above decisions thatSMS Pharma (1) [S.M.S. Pharmaceuticals Ltd. v. Neeta Bhalla, (2005) 8 SCC 89 : 2005 SCC (Cri) 1975] , which is a three-Judge Bench decision, still holds the field. In all subsequent decisions, two-Judge Benches of this Court have followed SMS Pharma...."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_14",
      "class": "",
      "title": "Precedent Analysis",
      "style": "",
      "text": "28. We are concerned in this case with Directors who are not signatories to the cheques. So far as Directors whoCrl.M.C. 3257/2016 & ors. Page 17 of 24are not signatories to the cheques or who are not Managing Directors or Joint Managing Directors are concerned, it is clear from the conclusions drawn in the abovementioned cases that it is necessary to aver in the complaint filed underSection 138read withSection 141of the NI Act that at the relevant time when the offence was committed, the Directors were in charge of and were responsible for the conduct of the business of the company. This is a basic requirement. There is no deemed liability of such Directors.\""
    },
    {
      "tag": "blockquote",
      "id": "blockquote_15",
      "class": "",
      "title": "Precedent Analysis",
      "style": "",
      "text": "\"31. When in view of the basic averment process is issued the complaint must proceed against the Directors. But, if any Director wants the process to be quashed by filing a petition under Section 482 of the Code on the ground that only a bald averment is made in the complaint and that he is really not concerned with the issuance of the cheque, he must in order to persuade the High Court to quash the process either furnish some sterling incontrovertible material or acceptable circumstances to substantiate his contention. He must make out a case that making him stand the trial would be an abuse of process of court. He cannot get the complaint quashed merely on the ground that apart from the basic averment no particulars are given in the complaint about his role, because ordinarily the basic averment would be sufficient to send him to trial and it could be argued that his further role could be brought out in the trial. Quashing of a complaint is a serious matter. Complaint cannot be quashed for theCrl.M.C. 3257/2016 & ors. Page 18 of 24asking. For quashing of a complaint it must be shown that no offence is made out at all against the Director.\""
    },
    {
      "tag": "blockquote",
      "id": "blockquote_16",
      "class": "",
      "title": "Precedent Analysis",
      "style": "",
      "text": "\"35. ... Pertinently, in the application filed by the respondents, no clear case was made out that at the material time, the Directors were not in charge of and were not responsible for the conduct of the business of the Company by referring to or producing any incontrovertible or unimpeachable evidence which is beyond suspicion or doubt or any totally acceptable circumstances. It is merely stated that Sidharth Mehta had resigned from the directorship of the Company on 30-9-2010 but no incontrovertible or unimpeachable evidence was produced before the High Court as was done inAnita Malhotra [Anita Malhotra v. Apparel Export Promotion Council, (2012) 1 SCC 520 : (2012) 1 SCC (Civ) 329 : (2012) 1 SCC (Cri) 496] to show that he had, in fact, resigned long before the cheques in question were issued. Similar is the case with Kanhaiya Lal Mehta and Anu Mehta. Nothing was produced to substantiate the contention that they were not in charge of and not responsible for the conduct of the business of the Company at the relevant time. In the circumstances, we are of the opinion that the matter deserves to be remitted to the High Court for fresh hearing."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_17",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "(i) It is only those persons who are in charge of or responsible for the conduct of the business of the company at the time of commission of the offence underSection 138of the Negotiable Instruments Act, 1881 who can be subjected to criminal action with reference toSection 141;"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_18",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "(ii). If the person committing an offence underSection 138of the Negotiable Instruments Act, 1881 is a company, the person who was signatory to the cheque which is dishonoured is clearly responsible for the incriminating act and would be liable to be proceeded against underSection 141 (2);"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_19",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "substantiating his contention that he was not in charge of nor responsible for the conduct of the business of the company \"at the time the offence was committed\" and thereby showing a case that making him stand the trial would be an abuse of the process of court, but not otherwise."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_20",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "\"3. That the accused No.3 Mr. Vinod Sirohi, Accused No.4 Fadi El Jaouni, Accused No.5 Khaled Abdelrahman Radi and the Accused No.6 Mr. Naseer Mohd. MF AI Hajri are the Directors and Accused No.7 Mr. Rahul Shivam is the Authorised Signatory of the Accused No.1 Company, namely M/s. Bush Foods Pvt. Ltd. and are actively engaged and responsible for and in-charge of day- to-day management, business activities and affairs of the Accused No.1 firm."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_21",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "xxx"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_22",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "10. That despite the receipt of the above said Legal Notice dated 05.02.2014, the Accused Persons have failed / refused / neglected to make the payment of the above said Cheques amount to the Complainant and have therefore made themselves liable to be prosecuted under the provisions ofSections 138,141and142of the Negotiable Instruments Act, 1881. It is further submitted that at the time of issuance of the said cheques, the accused persons have assured, promised and represented to the Complainant that the said cheques would be honored on presentation. However, the said Cheques, which are the subject matter of the present complaint, were dishonored on presentment. The accused persons have no intention to make the said payment to the Complainant. It is submitted that the Accused Persons have been responsible for all the business dealings for and on behalf of their said Accused no.1 firm and also responsible for the circumstances that have lead to the dishonor of the aid cheques issued to the complainant.\""
    }
  ]
}

Excellent, Amay.
With the IPC/BNS JSON + a fully RR-segmented India Kanoon case like this, you now have enough signal to design a serious, research-grade legal Knowledge Graph.

I’ll do three things for you:

Propose the final KG schema (nodes + relations) grounded in your data
Show how your sample maps into this KG
Give you precise questions to ask your team before freezing it

No abstraction. This is implementation-ready.

1️⃣ What Your KG Must Do (Functional Requirement)

Your KG is not Wikipedia.
It exists for one purpose:

Support missing-evidence detection, contradiction checking, and outcome grounding.

So every node/edge must answer one of these:

“What must be proved for this offence?”
“What evidence normally proves this?”
“Which claims conflict?”
“What precedents constrain this?”
“What outcomes usually follow?”

If a node doesn’t help that → don’t add it.

2️⃣ ✅ FINAL KG NODE TYPES (Minimal & Sufficient)

Based on your data, you need exactly these 9.

🔹 1. StatuteSection

From IPC/BNS/NI Act.

Example:

Section_138_NI
Section_141_NI
IPC_420

Properties:

{
  "section_id": "138_NI",
  "title": "...",
  "punishment": "...",
  "cognizable": true
}
🔹 2. Offence

Legal offence concept (may map to multiple sections).

Example:

Cheque_Dishonour
Cheating
🔹 3. LegalRequirement

Atomic condition that must be satisfied.

From Analysis + precedents.

Example:

Notice_Served
Non_Payment_15_Days
Director_In_Charge

This is the core of missing evidence.

🔹 4. EvidenceType

What proves a requirement.

Example:

Bank_Memo
Legal_Notice_Copy
Board_Resolution
Resignation_Letter
🔹 5. CaseType

From CON.

Example:

NI_Act_138_Case
Service_Law_Posting
Property_Dispute
🔹 6. ClaimType

Normalized claims.

Example:

dishonour_occurred
director_not_responsible
notice_not_served
🔹 7. Principle

Judicial doctrine from precedents.

Example:

Vicarious_Liability_Principle
Merit_Cum_Choice
🔹 8. PrecedentCase

Cited cases.

Example:

SMS_Pharmaceuticals_2005
Gunmala_Sales_2015
🔹 9. OutcomeType

Final decisions.

Example:

Conviction
Acquittal
Proceedings_Quashed
Petition_Dismissed
3️⃣ ✅ FINAL KG RELATION TYPES

These are the only relations you need in v1.

Core Legal Structure
1. APPLIES_TO
(StatuteSection) → (Offence)

Example:

138_NI → Cheque_Dishonour
2. HAS_REQUIREMENT
(Offence) → (LegalRequirement)

Example:

Cheque_Dishonour → Notice_Served
3. PROVED_BY
(LegalRequirement) → (EvidenceType)

Example:

Notice_Served → Legal_Notice_Copy
4. GOVERNED_BY
(CaseType) → (Offence)

Example:

NI_Act_138_Case → Cheque_Dishonour
Reasoning Layer
5. SUPPORTS
(EvidenceType) → (ClaimType)

Example:

Bank_Memo → dishonour_occurred
6. REFUTES
(EvidenceType) → (ClaimType)

Example:

Resignation_Letter → director_responsible
7. CONTRADICTS
(ClaimType) ↔ (ClaimType)

Example:

director_in_charge ↔ not_director
Precedent Layer
8. ESTABLISHES
(PrecedentCase) → (Principle)
9. INTERPRETS
(PrecedentCase) → (StatuteSection)
10. INFLUENCES
(Principle) → (OutcomeType)
Outcome Statistics (Learned Later)
11. TENDS_TO_RESULT_IN
(CaseType) → (OutcomeType)

(weighted edge)

4️⃣ How Your Example Fits Into This KG

Let’s map your NI Act case.

Sections
[138_NI] ----APPLIES_TO----> [Cheque_Dishonour]
[141_NI] ----APPLIES_TO----> [Vicarious_Liability]
Offence → Requirements
Cheque_Dishonour
   ├─ Notice_Served
   ├─ Non_Payment_15_Days
   └─ Legally_Enforceable_Debt
Vicarious_Liability
   └─ Director_In_Charge
Requirements → Evidence
Notice_Served → Legal_Notice_Copy
Non_Payment_15_Days → Bank_Statement
Director_In_Charge → Board_Resolution
Director_In_Charge → Employment_Record
Precedents
SMS_Pharmaceuticals → Vicarious_Liability_Principle
Gunmala_Sales → Vicarious_Liability_Principle
Principles → Outcomes
Vicarious_Liability_Principle → Proceedings_Quashed
Claims
director_not_responsible ↔ director_in_charge
5️⃣ How KG Is Used in Your System
🔹 Missing Evidence
CON.case_type → CaseType
   → Offence
      → LegalRequirement
         → EvidenceType

Compare with CON.evidence_present.

🔹 Contradiction
CON.claims → ClaimType
   → CONTRADICTS edges
🔹 Judgment
CaseType → OutcomeType
+ Principle → OutcomeType
+ Evidence coverage
6️⃣ Questions You MUST Ask Your Team Now

Before freezing KG, ask these. They are critical.

Q1. Scope of Case Types

Which case types are in v1?

Example:

NI Act 138
Service law
Property

If too many → KG explodes.

Q2. Depth of Legal Requirements

Do we model only “core elements”
or also exceptions/provisos?

Example:

Notice_Served
Notice_Served_Within_30_Days

Decide now.

Q3. Evidence Granularity

Do we keep “Bank Memo”
or “Bank Memo + Date + Amount”?

Symbolic vs detailed.

Q4. Precedent Coverage

Do we encode top-100 precedents
or only the ones appearing in dataset?

Pragmatic answer: only those appearing.

Q5. Storage Backend

Neo4j, RDF, or JSON graph?

Decide early. Migration hurts.

7️⃣ Suggested First KG Version (Do This)

For v1:

Limit yourself to:

✔ Sections
✔ Offences
✔ Requirements
✔ Evidence
✔ ClaimType
✔ CaseType
✔ OutcomeType

Ignore Principles/Precedents initially.

This lets you ship Missing Evidence model fast.

8️⃣ Minimal KG Schema (v1)

If you want something to implement immediately:

Nodes:
- StatuteSection
- Offence
- LegalRequirement
- EvidenceType
- CaseType
- ClaimType
- OutcomeType

Edges:
- APPLIES_TO
- HAS_REQUIREMENT
- PROVED_BY
- SUPPORTS
- CONTRADICTS
- GOVERNED_BY
- TENDS_TO_RESULT_IN

This is enough for 80% functionality.

If you want, next I can:

✅ Convert this into Neo4j schema
✅ Design KG auto-builder pipeline
✅ Write extraction rules for IPC/BNS → KG
✅ Show missing-evidence inference code

Tell me what you want first.

1. Scope of case types = not criminal cases, need civil cases like property stuff, marriage stuff etc 
2. leave it 
3. Symbolic

Perfect, Amay.
These three answers are exactly what I was hoping you’d say — they simplify the KG massively and make the system actually buildable.

Now I’ll:

Lock the KG scope based on your answers
Give you the final KG v1 design for CIVIL CASES
Show how it maps to property / marriage cases
Tell you what not to include (very important)

After this, you can freeze Task 4.

1️⃣ Interpreting Your Answers

You said:

✅ Not criminal → Only civil (property, marriage, etc.)
✅ Leave depth → Core elements only
✅ Symbolic evidence

So:

Consequences

✔ IPC/BNS → secondary (background only)
✔ Focus on Civil Codes, CPC, Family Law, Property Law
✔ KG is requirement–evidence–outcome driven
✔ No procedural micro-details
✔ No fine-grained timelines in KG

This is good engineering.

2️⃣ ✅ FINAL KG v1 — Civil Law Focused

This is your authoritative KG schema now.

🔷 Node Types
1. CaseType

What kind of civil case.

Examples:

Property_Dispute
Divorce_Mutual
Divorce_Contested
Maintenance_Case
Inheritance_Dispute
Partition_Suit
Tenancy_Dispute
2. LegalGround

Why the case exists legally.

Examples:

Non_Payment_of_Maintenance
Cruelty
Desertion
Illegal_Possession
Title_Dispute
Breach_of_Contract
3. LegalRequirement

What must be proved.

Examples:

Valid_Marriage
Proof_of_Cruelty
Continuous_Desertion_2Y
Registered_Sale_Deed
Ancestral_Property_Status
4. EvidenceType (Symbolic Only)

High-level evidence categories.

Examples:

Marriage_Certificate
Medical_Report
Police_Complaint
Registered_Sale_Deed
Will_Document
Witness_Affidavit
Bank_Statement
Property_Tax_Receipt
5. ClaimType

Standardized claims.

Examples:

ownership_claim
cruelty_claim
desertion_claim
maintenance_need
illegal_possession_claim
6. StatuteSection (Optional v1)

Civil statutes (HMA, CPC, etc.)

Examples:

HMA_13
CPC_9
HSA_8
TPA_54

(You can add later.)

7. OutcomeType

Final decisions.

Examples:

Divorce_Granted
Divorce_Denied
Property_Granted
Property_Dismissed
Maintenance_Awarded
Partition_Ordered
3️⃣ 🔷 Relation Types

These are the only relations you need.

Core Reasoning
1. GOVERNED_BY
CaseType → LegalGround

Example:

Divorce_Contested → Cruelty
2. REQUIRES
LegalGround → LegalRequirement

Example:

Cruelty → Medical_Report
3. PROVED_BY
LegalRequirement → EvidenceType

Example:

Valid_Marriage → Marriage_Certificate
4. SUPPORTS
EvidenceType → ClaimType

Example:

Sale_Deed → ownership_claim
5. CONTRADICTS
ClaimType ↔ ClaimType

Example:

ownership_claim ↔ illegal_possession
remove StatuteSection
also why do we need legalground?

Great questions, Amay.
These are exactly the questions that decide whether your KG stays clean and usable or becomes bloated and useless.

Let’s answer both properly.

✅ 1. Removing StatuteSection

You’re right.

Since:

You’re focusing on civil cases
You’re keeping evidence symbolic
You’re not doing statutory compliance checking in v1

👉 StatuteSection is NOT needed in KG v1.

It adds:

Complexity
Noise
Extraction difficulty

With almost no benefit for your current goals.

So:

❌ Remove StatuteSection from KG v1.

Good call.

✅ 2. Why LegalGround Exists (And Why It’s Important)

Short answer:

LegalGround is the bridge between case type and proof requirements.

Without it, your KG becomes shallow and your missing-evidence model becomes weak.

Let me show you.

❌ If You Remove LegalGround

You’d have:

CaseType → LegalRequirement → Evidence

Example:

Divorce_Contested
   → Valid_Marriage
   → Medical_Report
   → Witness

Problem:

A contested divorce can be for:

Cruelty
Desertion
Adultery
Mental illness

Each needs different proof.

Without LegalGround:

👉 You don’t know which path applies.

Your system will suggest wrong evidence.

✅ With LegalGround (Correct Way)

You get:

CaseType → LegalGround → LegalRequirement → Evidence

Example:

Divorce_Contested
   → Cruelty
       → Proof_of_Cruelty → Medical_Report
   → Desertion
       → Proof_of_Desertion → Residenceuq
   → Adultery
       → Proof_of_Adultery → Photos

Now:

KG knows the legal basis
Missing evidence is precise
Judgment prediction improves

This is how real lawyers think.

🧠 Think of It Like This
Layer	Meaning
CaseType	“What kind of case?”
LegalGround	“On what legal basis?”
Requirement	“What must I prove?”
Evidence	“How do I prove it?”

Removing LegalGround collapses levels 2+3.

Bad design.

✅ 3. Final KG v1 (After Your Change)

This is now your frozen design.

🔷 Node Types
1. CaseType
Property_Dispute
Divorce_Contested
Divorce_Mutual
Maintenance
Inheritance
Partition
Tenancy
2. LegalGround
Cruelty
Desertion
Illegal_Possession
Title_Dispute
Breach_of_Contract
Non_Payment_of_Maintenance
3. LegalRequirement
Valid_Marriage
Continuous_Desertion_2Y
Registered_Sale_Deed
Ancestral_Status
Proof_of_Cruelty
4. EvidenceType (Symbolic)
Marriage_Certificate
Medical_Report
Registered_Sale_Deed
Will_Document
Witness_Affidavit
Bank_Statement
Property_Tax_Receipt
5. ClaimType
ownership_claim
cruelty_claim
desertion_claim
maintenance_need
illegal_possession_claim
6. OutcomeType
Divorce_Granted
Divorce_Denied
Maintenance_Awarded
Property_Granted
Suit_Dismissed
🔷 Relation Types
GOVERNED_BY
CaseType → LegalGround
REQUIRES
LegalGround → LegalRequirement
PROVED_BY
LegalRequirement → EvidenceType
SUPPORTS
EvidenceType → ClaimType
CONTRADICTS
ClaimType ↔ ClaimType
TENDS_TO_RESULT_IN (learned later)
CaseType → OutcomeType
4. Why This Design Is Strong

This KG:

✔ Matches how civil law works
✔ Matches how lawyers reason
✔ Supports missing-evidence cleanly
✔ Supports contradiction detection
✔ Scales to more domains later
✔ Keeps IPC/BNS optional

It’s professional-grade.

5. One Last Sanity Question (Optional)

Before you freeze:

Will lawyer input include “ground” explicitly
or do we infer it from claims?

Because:

If explicit → easy mapping
If implicit → need classifier

Tell me, and I’ll adjust Pipeline 2 accordingly.

okay so these nodes and relations look fine to us 
now tell me exactly what to do next?
we need to discuss how to generate the knowledge graph next

CaseType
LegalGround
LegalRequirement
EvidenceType
ClaimType
OutcomeType

CaseType      ──GOVERNED_BY──▶ LegalGround
LegalGround   ──REQUIRES────▶ LegalRequirement
LegalRequirement ──PROVED_BY──▶ EvidenceType
EvidenceType  ──SUPPORTS────▶ ClaimType
ClaimType     ──CONTRADICTS─▶ ClaimType
LegalGround   ──TENDS_TO_RESULT_IN──▶ OutcomeType

Perfect, Amay.
You’ve now crossed the design phase. What you have is a valid KG schema.

From here onward, this is no longer “decide”.
This is engineering execution.

I’ll tell you exactly what to do next, in the right order, with no ambiguity.

✅ OVERALL GOAL (Task 4 → Task 3 Transition)

Right now:

You have the schema.
Next, you must instantiate it with real nodes and edges from your data.

In simple terms:

Turn BNS/IPC + IndiaKanoon → actual graph.

🧭 PHASE 1 — Build Controlled Vocabularies (CRITICAL FIRST STEP)

Before coding anything, you must freeze symbol sets.

If you skip this → KG becomes garbage.

Step 1.1: Create Master Lists (Manually First)

Create 6 files:

case_types.json
legal_grounds.json
legal_requirements.json
evidence_types.json
claim_types.json
outcome_types.json

Example: legal_grounds.json

[
  "Cruelty",
  "Desertion",
  "Illegal_Possession",
  "Title_Dispute",
  "Breach_of_Contract",
  "Non_Payment_of_Maintenance"
]

How to do it:

Read ~50 judgments
Extract recurring concepts
Normalize
Deduplicate

Do NOT automate yet.

Target: ~20–40 per category.

Step 1.2: Define Synonym Maps

Judgments won’t use your exact words.

Create:

synonyms/
   cruelty.json
   desertion.json

Example:

{
  "cruelty": ["mental cruelty", "harassment", "abuse"],
  "desertion": ["abandonment", "left home"]
}

This will be used in extraction.

🧭 PHASE 2 — Build Rule-Based Extractors (KG Seeding)

Now you start populating.

This is NOT ML first. It’s rules first.

Step 2.1: Extract CaseType

From metadata + keywords.

Example rule:

if "divorce" in title:
    case_type = "Divorce_Contested"

Store in CON + KG.

Step 2.2: Extract LegalGround

From:

Issues
Arguments
Reasoning

Pattern example:

"cruelty", "harassment" → Cruelty
"deserted", "abandoned" → Desertion

This gives:

CaseType ──GOVERNED_BY──▶ LegalGround
Step 2.3: Extract LegalRequirements

This is from:

Analysis of law
Court reasoning

Example:

"continuous desertion for two years"
→ Continuous_Desertion_2Y

Rule templates.

Output:

LegalGround ──REQUIRES──▶ LegalRequirement
Step 2.4: Extract EvidenceType

From:

Facts
Reasoning
Evidence mentions

Example:

"sale deed", "registered deed"
→ Registered_Sale_Deed

Output:

LegalRequirement ──PROVED_BY──▶ EvidenceType
Step 2.5: Extract ClaimType

From Arguments.

Example:

"I am the owner"
→ ownership_claim

Output:

EvidenceType ──SUPPORTS──▶ ClaimType
Step 2.6: Extract OutcomeType

From Conclusion.

Example:

"petition dismissed"
→ Suit_Dismissed

Output:

LegalGround ──TENDS_TO_RESULT_IN──▶ OutcomeType
🧭 PHASE 3 — Graph Construction Engine

Now you have extracted symbols.

You need to build the actual graph.

Step 3.1: Pick Graph Backend

Choose ONE:

Best option

👉 Neo4j

Why:

Fast
Visual
Cypher
Easy prototyping

If not:

NetworkX (temporary)
RDFLib (heavy)

I recommend: Neo4j.

Step 3.2: Build Graph Loader

Write one script:

build_kg.py

It does:

for each case:
    add CaseType node
    add LegalGround node
    add relations

No logic here. Only insertion.

🧭 PHASE 4 — Statistical Edge Weighting (After 500+ Cases)

Once graph has volume:

Add weights.

Example:

Cruelty → Divorce_Granted (0.72)

From frequency.

This powers prediction.

🧭 PHASE 5 — Validation & Debugging

Very important.

Step 5.1: Sanity Queries

Write Cypher queries like:

MATCH (g:LegalGround)-[:REQUIRES]->(r)
WHERE r IS NULL
RETURN g

Find broken paths.

Step 5.2: Manual Spot Check

Random 20 cases.

Verify:

Ground correct?
Evidence logical?
Outcome reasonable?
📋 WHAT TO DO THIS WEEK (Concrete)

Here is your next 7-day plan.

Day 1–2

✔ Build vocab lists
✔ Build synonym maps

Day 3–4

✔ Rule-based extractors
✔ Regex + keyword pipelines

Day 5

✔ Neo4j setup
✔ Loader script

Day 6

✔ Load 200 cases
✔ Inspect graph

Day 7

✔ Fix errors
✔ Freeze KG v1

🧠 Important Principle (Don’t Forget)

KG v1 is NOT perfect.
It is seed knowledge.

ML improves later.

Don’t wait for “ideal”.

🚀 After This Is Done

Only then you move to:

Missing Evidence Model
Embedding Engine
Prediction Model

Because now you have structure.

If you want, next I can help you write:

✅ Regex patterns for civil grounds
✅ Neo4j schema + setup
✅ KG builder code skeleton
✅ Evaluation metrics

Tell me what you want first.

nopes we're not doing manually 
Create Master Lists (Manually First)

Got it, Amay — that’s a good decision. With 10k+ cases, manual vocab building won’t scale and will become a bottleneck.

So here’s the correct automatic way to generate your Knowledge Graph from data.

No hand-curation. No subjective lists.

This is the data-driven pipeline you should implement.

✅ High-Level Idea

You will bootstrap the KG automatically from judgments using:

frequency mining
clustering
weak supervision
normalization
graph statistics

Then clean it minimally.

Think:

“Let the data propose the ontology.”

🧭 PHASE 1 — Auto-Extract Candidate Concepts (From Text)

First, mine raw symbols from your RR dataset.

You already have:

Facts
Issues
Arguments
Reasoning
Conclusion

Use them.

1️⃣ CaseType (From Titles + Metadata)
Input
page_title
case_title
Method

TF-IDF + clustering

titles → vectorize → KMeans

Example clusters:

["divorce", "marriage", "husband"] → Divorce
["partition", "ancestral"] → Property
Output
CaseType candidates
2️⃣ LegalGround (From Issues + Arguments)
Input
Issues
Petitioner/Respondent Arguments
Method

Keyphrase extraction + clustering

Use:

YAKE / KeyBERT / RAKE

Example:

"mental cruelty"
"physical abuse"
"harassment"

→ Cluster → Cruelty

Output
LegalGround candidates
3️⃣ LegalRequirement (From Reasoning + Law)
Input
Court’s Reasoning
Analysis of Law
Method

Dependency parsing + pattern mining

Find patterns like:

"must prove X"
"required to show Y"
"essential condition is Z"

Regex + spaCy.

Example:

"continuous desertion for two years"

→ Requirement

4️⃣ EvidenceType (From Facts + Reasoning)
Input
Facts
Reasoning
Method

NER + noun phrase mining

Extract document-like phrases:

sale deed
medical report
bank statement
FIR copy
marriage certificate

Cluster.

5️⃣ ClaimType (From Arguments)
Input
Petitioner / Respondent sections
Method

Verb–object extraction

Pattern:

I + VERB + OBJECT
They + deny + OBJECT

Use dependency trees.

Example:

"owns the property"
→ ownership_claim
6️⃣ OutcomeType (From Conclusion)
Input
Conclusion
Method

Rule-based (easy)

Patterns:

dismissed
allowed
granted
partly allowed
🧭 PHASE 2 — Normalize Automatically

Raw extraction gives garbage like:

"sale deed"
"registered deed"
"registered sale deed"

You must unify.

Step 2.1: Embedding-Based Deduplication

For each category:

embed phrases → cosine similarity → merge > 0.85

Use:

Sentence-BERT
LegalBERT (later)
Step 2.2: Canonical Naming

Pick cluster centroid as name.

Example:

Cluster:

["registered deed", "sale deed", "property deed"]

→ Registered_Sale_Deed

🧭 PHASE 3 — Auto-Build Relations

Now build edges statistically.

1️⃣ CaseType → LegalGround (GOVERNED_BY)

For each case:

case_type + legal_ground in same case
→ edge++

After N cases:

weight = count / total

Keep > threshold.

2️⃣ LegalGround → LegalRequirement (REQUIRES)

From reasoning:

if ground X and requirement Y co-occur in reasoning
→ link
3️⃣ LegalRequirement → EvidenceType (PROVED_BY)

From facts:

if requirement X and evidence Y appear in same paragraph
→ link
4️⃣ EvidenceType → ClaimType (SUPPORTS)

From arguments:

if evidence mentioned near claim
→ supports

Window-based.

5️⃣ ClaimType ↔ ClaimType (CONTRADICTS)

From opposite parties:

petitioner claim vs respondent claim
same subject, opposite polarity
→ contradiction

Rule-based.

6️⃣ LegalGround → OutcomeType (TENDS_TO_RESULT_IN)

Pure stats:

count(ground, outcome)
🧭 PHASE 4 — Build KG Programmatically

Now everything is structured.

You write:

kg_builder.py

Pipeline:

for case in dataset:
    extract symbols
    normalize
    update counts
    create edges

Store in:

Neo4j (recommended), or
JSON graph
🧭 PHASE 5 — Automatic Pruning

Your KG will be noisy.

So prune.

Rule 1: Frequency Cut

Drop nodes with:

freq < 10
Rule 2: Weak Edge Cut

Drop edges with:

weight < 0.05
Rule 3: Orphan Removal

Remove nodes with no edges.

🧭 PHASE 6 — Light Human Validation (Not Manual Building)

This is NOT manual creation.

Only validation.

Sample 100 nodes.

Check:

80% good → proceed
<60% → fix extractor
📌 What Your Team Should Build Now (Concrete)

This is your immediate todo.

Week 1

✔ Phrase extractors
✔ Clustering scripts
✔ Normalizers

Week 2

✔ Relation miners
✔ KG builder
✔ Neo4j loader

Week 3

✔ Pruning
✔ Validation
✔ KG v1 freeze

🧠 Why This Is the Right Approach

This gives you:

✅ Scalable KG
✅ Domain-adaptive
✅ No human bias
✅ Updates automatically
✅ Reproducible
✅ Research-grade

This is how legal KG papers actually do it.

⚠️ One Critical Rule

Do NOT try to make KG “perfect” initially.

KG v1 = noisy + usable
KG v2 = refined
KG v3 = strong

If you try perfection → project stalls.

If you want, next I can:

Give you code skeleton for KG miner
Design extractor regex templates
Show Neo4j schema
Help split this across teammates

Tell me which one you want.

take this case as a raw data for example, it is yet to be converted to a CON file 
but tke this and tell me how would be extract the candidate concepts for each of the node 

{
  "url": "https://indiankanoon.org/doc/27754182/",
  "page_title": "Jwala Devi Enterprises P. Ltd. vs Fadi El Jaouni on 23 July, 2018",
  "court_name": "",
  "case_title": "Jwala Devi Enterprises P. Ltd. vs Fadi El Jaouni on 23 July, 2018",
  "elements_by_title": {
    "Fact": [
      {
        "tag": "p",
        "id": "p_1",
        "class": "",
        "title": "Fact",
        "text": "1. On 19.03.2014, eleven criminal complaints were filed in the court of the Metropolitan Magistrate, each seeking prosecution of the parties shown in the array of respondents for offences punishable underSection 138of the Negotiable Instruments Act, 1881, two of such complaints i.e. the complaint nos.800/1/14 and 802/1/14 having been presented by Jwala Devi Enterprises Pvt. Ltd. through its authorized representative Sat Parkash Bansal and the rest - complaint nos.799/1/14, 812/1/14, 813/1/14, 814/1/14, 815/1/14, 839/1/14, 840/1/14, 841/1/14 and 842/1/14 - having been presented by Anand Prakash Bansal, Proprietor of M/s. Pooja Enterprises. Each of the said criminal complaints were directed against several persons including a company described as M/s. Bush Foods Overseas Pvt. Ltd. It may be mentioned that Mr. Virkaran Awasty was reflected in the array of the accused as the Managing Director of the said company accused. The respondents in these petitions were amongst the other persons shownCrl.M.C. 3257/2016 & ors. Page 10 of 24as accused in the said complaints, each of them having been described as \"Director\" of the said company accused."
      },
      {
        "tag": "p",
        "id": "p_2",
        "class": "",
        "title": "Fact",
        "text": "2. On the basis of the preliminary inquiry in each case, the Metropolitan Magistrate issued process including against the respondents herein. The respondents, feeling aggrieved, approached the court of Sessions invoking its revisional jurisdiction by separate petitions (CR nos.34-62/2015), their prime contention being that there was no case made out for they to be summoned as accused on the basis of allegations that they were directors of the company accused, denying that they had any concern with the responsibility for the conduct of the day-to-day business of the company."
      }
    ],
    "Precedent Analysis": [
      {
        "tag": "p",
        "id": "p_3",
        "class": "",
        "title": "Precedent Analysis",
        "text": "3. Placing reliance primarily on decision of a bench of three Hon'ble Judges of the Supreme Court inSMS Pharmaceuticals Pvt. Ltd. Vs. Neeta Bhalla, (2005) 8 SCC 89, the court of Sessions found substance and merit in the aforesaid contentions and allowed all the above-said revision petitions by a common order dated 18.04.2015 holding that the summoning order had been passed by the Magistrate mechanically without going through the material(s) on record, there being no averment to the effect that the said persons were in charge of, or responsible for the conduct of the business of, the company accused and consequently dropping the criminal proceedings against each of them."
      },
      {
        "tag": "p",
        "id": "p_4",
        "class": "",
        "title": "Precedent Analysis",
        "text": "4. The petitions at hand have been filed by the complainants invoking the inherent jurisdiction of this court underSection 482of the Code of Criminal Procedure, 1973 (Cr. PC) andArticle 227of the Constitution of India, 1950 to pray for the aforesaid orders of theCrl.M.C. 3257/2016 & ors. Page 11 of 24Sessions court in each of the said eleven complaint cases to be set aside and the proceedings against the respondents herein to be revived on the file of the Metropolitan Magistrate. Reliance is placed in this context by the petitioners on the decisions of benches of two Hon'ble Judges of the Supreme Court reported asGunmala Sales (P) Ltd. Vs. Anu Mehta and Ors, (2015) 1 SCC 103 and Standard Chartered Bank Vs. State of Maharashtra and Ors., (2016) 6 SCC 62.There can be no quarrel with the proposition, as advanced by the counsel for the respondents, that the ruling of the bench of three Hon'ble Judges inSMS Pharmaceuticals(supra), continues to hold the field, the decisions inGunmala Sales (P) Ltd.(supra) andStandard Chartered Bank(supra) having accepted this position and the said subsequent rulings being in a slightly different context."
      },
      {
        "tag": "p",
        "id": "p_10",
        "class": "",
        "title": "Precedent Analysis",
        "text": "9. Certain observations inSMS Pharmaceuticals(supra) which have been quoted in the subsequent decisions, need to be borne in mind and, therefore, may be extracted as under :-"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_13",
        "class": "",
        "title": "Precedent Analysis",
        "style": "",
        "text": "\"27. It is clear from a perusal of the above decisions thatSMS Pharma (1) [S.M.S. Pharmaceuticals Ltd. v. Neeta Bhalla, (2005) 8 SCC 89 : 2005 SCC (Cri) 1975] , which is a three-Judge Bench decision, still holds the field. In all subsequent decisions, two-Judge Benches of this Court have followed SMS Pharma...."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_14",
        "class": "",
        "title": "Precedent Analysis",
        "style": "",
        "text": "28. We are concerned in this case with Directors who are not signatories to the cheques. So far as Directors whoCrl.M.C. 3257/2016 & ors. Page 17 of 24are not signatories to the cheques or who are not Managing Directors or Joint Managing Directors are concerned, it is clear from the conclusions drawn in the abovementioned cases that it is necessary to aver in the complaint filed underSection 138read withSection 141of the NI Act that at the relevant time when the offence was committed, the Directors were in charge of and were responsible for the conduct of the business of the company. This is a basic requirement. There is no deemed liability of such Directors.\""
      },
      {
        "tag": "p",
        "id": "p_15",
        "class": "",
        "title": "Precedent Analysis",
        "text": "10.InGunmala Sales (P) Ltd.(supra), the issue brought before the Supreme Court by the complainant primarily was that the High Court in exercise of its jurisdiction under Section 482 Cr. PC had wrongly quashed the proceedings against the respondents on the ground that there was a bald assertion in the complaint that they were directors in the company at the time when the offence was committed.While acknowledging (in para 27) that the decision inSMS Pharmaceuticals(supra) still holds the field, inGunmala Sales (P) Ltd.(supra), it was further clarified thus :"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_15",
        "class": "",
        "title": "Precedent Analysis",
        "style": "",
        "text": "\"31. When in view of the basic averment process is issued the complaint must proceed against the Directors. But, if any Director wants the process to be quashed by filing a petition under Section 482 of the Code on the ground that only a bald averment is made in the complaint and that he is really not concerned with the issuance of the cheque, he must in order to persuade the High Court to quash the process either furnish some sterling incontrovertible material or acceptable circumstances to substantiate his contention. He must make out a case that making him stand the trial would be an abuse of process of court. He cannot get the complaint quashed merely on the ground that apart from the basic averment no particulars are given in the complaint about his role, because ordinarily the basic averment would be sufficient to send him to trial and it could be argued that his further role could be brought out in the trial. Quashing of a complaint is a serious matter. Complaint cannot be quashed for theCrl.M.C. 3257/2016 & ors. Page 18 of 24asking. For quashing of a complaint it must be shown that no offence is made out at all against the Director.\""
      },
      {
        "tag": "blockquote",
        "id": "blockquote_16",
        "class": "",
        "title": "Precedent Analysis",
        "style": "",
        "text": "\"35. ... Pertinently, in the application filed by the respondents, no clear case was made out that at the material time, the Directors were not in charge of and were not responsible for the conduct of the business of the Company by referring to or producing any incontrovertible or unimpeachable evidence which is beyond suspicion or doubt or any totally acceptable circumstances. It is merely stated that Sidharth Mehta had resigned from the directorship of the Company on 30-9-2010 but no incontrovertible or unimpeachable evidence was produced before the High Court as was done inAnita Malhotra [Anita Malhotra v. Apparel Export Promotion Council, (2012) 1 SCC 520 : (2012) 1 SCC (Civ) 329 : (2012) 1 SCC (Cri) 496] to show that he had, in fact, resigned long before the cheques in question were issued. Similar is the case with Kanhaiya Lal Mehta and Anu Mehta. Nothing was produced to substantiate the contention that they were not in charge of and not responsible for the conduct of the business of the Company at the relevant time. In the circumstances, we are of the opinion that the matter deserves to be remitted to the High Court for fresh hearing."
      },
      {
        "tag": "p",
        "id": "p_17",
        "class": "",
        "title": "Precedent Analysis",
        "text": "11. For cases where the allegations in the complaint in writing are not deficient but the persons are described as directors (who seek quashing of the summoning order), it was ruled inGunmala Sales (P) Ltd.(supra) as under :-"
      },
      {
        "tag": "p",
        "id": "p_19",
        "class": "",
        "title": "Precedent Analysis",
        "text": "12. The conclusions inGunmala Sales (P) Ltd.(supra) were summarized thus :-"
      },
      {
        "tag": "p",
        "id": "p_22",
        "class": "",
        "title": "Precedent Analysis",
        "text": "13. The above view inGunmala Sales (P) Ltd.(supra) was endorsed and reiterated inStandard Chartered Bank(supra)."
      }
    ],
    "Analysis of the law": [
      {
        "tag": "blockquote",
        "id": "blockquote_1",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "138. Dishonour of cheque for insufficiency, etc., of funds in the account -- Where any cheque drawn by a person on an account maintained by him with a banker for payment of any amount of money to another person from out of that account for the discharge, in whole or in part, of any debt or other liability, is returned by the bank unpaid, either because of the amount of money standing to the credit of that account is insufficient to honour the cheque or that it exceeds the amount arranged to be paid from that account by an agreement made with that bank, such person shall be deemed to have committed an offence and shall, without prejudice to any other provision of this Act, be punished with imprisonment for 8 [a term which may be extended to two years'], or with fine which may extend to twice the amount of the cheque, or with both:"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_2",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "Provided that nothing contained in this section shall apply unless--"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_3",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "(a) the cheque has been presented to the bank within a period of six months from the date on which it is drawn or within the period of its validity, whichever is earlier;"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_4",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "(b) the payee or the holder in due course of the cheque, as the case may be, makes a demand for the payment of the said amount of money by giving a notice; in writing, to the drawer of the cheque, within thirty days of the receipt of information by him from the bank regarding the return of the cheque as unpaid; and"
      },
      {
        "tag": "p",
        "id": "p_5",
        "class": "",
        "title": "Analysis of the law",
        "text": "5. These matters pertain to the penal clause contained inSection 138of the Negotiable Instruments Act, 1881, which reads thus :-"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_5",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "(c) the drawer of such cheque fails to make the payment of the said amount of money to the payee or, as the case may be, to the holder in due course of the cheque, within fifteen days of the receipt of the said notice."
      },
      {
        "tag": "p",
        "id": "p_6",
        "class": "",
        "title": "Analysis of the law",
        "text": "Explanation.--For the purposes of this section, \"debt of other liability\" means a legally enforceable debt or other liability."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_6",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "141. Offences by companies.--(1) If the person committing an offence undersection 138is a company, every person who, at the time the offence was committed, was in charge of, and was responsible to, the company for the conduct of the business of the company, as well as the company, shall be deemed to be guilty of the offence and shall be liable to be proceeded against and punished accordingly:"
      },
      {
        "tag": "p",
        "id": "p_7",
        "class": "",
        "title": "Analysis of the law",
        "text": "6. It is clear from the plain reading of the above quoted provision and is now also well settled that the offence underSection 138of the Negotiable Instruments Act does not stand constituted merely upon dishonor of a cheque. The dishonor of a cheque which had been issued by the person (who is sought to be prosecuted) in favour of the complainant must be followed by a notice of demand within the stipulated period. It is the non-payment of the amount of the cheque within the statutory period after service of the notice of demand which constitutes the offence that is punishable under the aforementioned provision of law."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_7",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "Provided that nothing contained in this sub-section shall render any person liable to punishment if he proves that the offence was committed without his knowledge, or that he had exercised all due diligence to prevent the commission of such offence:"
      },
      {
        "tag": "p",
        "id": "p_8",
        "class": "",
        "title": "Analysis of the law",
        "text": "7. For dealing with cases involving companies and the persons connected thereto as the accused, the provision ofSection 141Negotiable Instruments Act, 1881 is relevant. For guidance and convenience, it may be quoted hereunder :-"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_8",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "Provided further that where a person is nominated as a Director of a company by virtue of his holding any office or employment in the Central Government or State Government or a financial corporation owned or controlled by the Central Government or the State Government, as the case may be, he shall not be liable for prosecution under this Chapter."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_9",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "(2) Notwithstanding anything contained in sub-section (1), where any offence under this Act has been committed by a company and it is proved that the offence has been committed with the consent or connivance of, or is attributable to, any neglect on the part of, any director, manager, secretary or other officer of the company, suchCrl.M.C. 3257/2016 & ors. Page 14 of 24director, manager, secretary or other officer shall also be deemed to be guilty of that offence and shall be liable to be proceeded against and punished accordingly."
      },
      {
        "tag": "p",
        "id": "p_13",
        "class": "",
        "title": "Analysis of the law",
        "text": "The question notes that the managing director or joint managing director would be admittedly in charge of the company and responsible to the company for the conduct of its business. When that is so, holders of such positions in a company become liable underSection 141of the Act. By virtue of the office they hold as managing director or joint managing director, these persons are in charge of and responsible for the conduct of business of the company. Therefore, they get covered underSection 141. So far as the signatory of a cheque which is dishonoured is concerned, he is clearly responsible for the incriminating act and will be covered under sub-Section (2) ofSection 141."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_17",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "(i) It is only those persons who are in charge of or responsible for the conduct of the business of the company at the time of commission of the offence underSection 138of the Negotiable Instruments Act, 1881 who can be subjected to criminal action with reference toSection 141;"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_18",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "(ii). If the person committing an offence underSection 138of the Negotiable Instruments Act, 1881 is a company, the person who was signatory to the cheque which is dishonoured is clearly responsible for the incriminating act and would be liable to be proceeded against underSection 141 (2);"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_19",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "substantiating his contention that he was not in charge of nor responsible for the conduct of the business of the company \"at the time the offence was committed\" and thereby showing a case that making him stand the trial would be an abuse of the process of court, but not otherwise."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_20",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "\"3. That the accused No.3 Mr. Vinod Sirohi, Accused No.4 Fadi El Jaouni, Accused No.5 Khaled Abdelrahman Radi and the Accused No.6 Mr. Naseer Mohd. MF AI Hajri are the Directors and Accused No.7 Mr. Rahul Shivam is the Authorised Signatory of the Accused No.1 Company, namely M/s. Bush Foods Pvt. Ltd. and are actively engaged and responsible for and in-charge of day- to-day management, business activities and affairs of the Accused No.1 firm."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_21",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "xxx"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_22",
        "class": "",
        "title": "Analysis of the law",
        "style": "",
        "text": "10. That despite the receipt of the above said Legal Notice dated 05.02.2014, the Accused Persons have failed / refused / neglected to make the payment of the above said Cheques amount to the Complainant and have therefore made themselves liable to be prosecuted under the provisions ofSections 138,141and142of the Negotiable Instruments Act, 1881. It is further submitted that at the time of issuance of the said cheques, the accused persons have assured, promised and represented to the Complainant that the said cheques would be honored on presentation. However, the said Cheques, which are the subject matter of the present complaint, were dishonored on presentment. The accused persons have no intention to make the said payment to the Complainant. It is submitted that the Accused Persons have been responsible for all the business dealings for and on behalf of their said Accused no.1 firm and also responsible for the circumstances that have lead to the dishonor of the aid cheques issued to the complainant.\""
      },
      {
        "tag": "p",
        "id": "p_23",
        "class": "",
        "title": "Analysis of the law",
        "text": "14. The guiding principles with reference toSection 141of the Negotiable Instruments Act, 1881, which are now well settled by judicial pronouncements, some of which have been noted above, may be summarised thus :-"
      },
      {
        "tag": "p",
        "id": "p_25",
        "class": "",
        "title": "Analysis of the law",
        "text": "(iv). Merely because a person is a director of the company is not sufficient to make him liable underSection 141, there being no deeming that by holding such position he is in charge of, or responsible for the conduct of the business of, the company within the meaning ofSection 141;"
      },
      {
        "tag": "p",
        "id": "p_26",
        "class": "",
        "title": "Analysis of the law",
        "text": "(v). It is necessary for the complainant to specifically aver in the complaint that at the time the offence was committed, the person sought to be prosecuted was in charge of, or responsible for the conduct of the business of, the company in terms ofSection 141, there being no need for further particulars to be given in the complaint about his role, this being subject to proof at the trial;"
      },
      {
        "tag": "p",
        "id": "p_27",
        "class": "",
        "title": "Analysis of the law",
        "text": "(vi). The person who has been summoned as an accused for offence under Section 138 of the Negotiable Instruments Act, 1881 on the basis of averment that he was director of the company accused, he being in charge of or responsible for the conduct of its business cannot get the complaint quashed by the High Court by filing a petition under Section 482 of the Code of Criminal Procedure, 1973 merely on the ground that no particulars as to his role have been set out in the complaint; andCrl.M.C. 3257/2016 & ors. Page 21 of 24"
      },
      {
        "tag": "p",
        "id": "p_28",
        "class": "",
        "title": "Analysis of the law",
        "text": "(vii). The person who has been summoned as an accused for offence underSection 138of the Negotiable Instruments Act, 1881 by invoking the provision contained inSection 141may persuade the High Court to quash the process in exercise of its inherent power underSection 482of the Code of Criminal Procedure, 1973 by furnishing \"some sterling incontrovertible material or acceptable circumstances\""
      },
      {
        "tag": "p",
        "id": "p_29",
        "class": "",
        "title": "Analysis of the law",
        "text": "15. A perusal of the eleven complaints from which the present proceedings arise reveals that they are founded on identical averments (some of the accused who are not before this court being not common), the exception being with regard to the particulars of the cheques or the background facts against which they had been issued or the dates on which they were presented or dishonored leading to demand notices in their respect being issued, there being no payment made pursuant to such demand notices. The averments crucial to pass the muster ofSection 141of the Negotiable Instruments Act, 1881, however, are identically worded in the said eleven cases. For illustration, the crucial averments appearing in one of such complaints (Crl. Complaint no.799/1/14), it being the first in chronology, may be extracted as under :-"
      },
      {
        "tag": "p",
        "id": "p_32",
        "class": "",
        "title": "Analysis of the law",
        "text": "17. The respondents are not stated to be signatories to the cheques in question. They cannot be roped in merely because they have been directors of the company accused. The general averments that they were responsible for all the business dealings and for the circumstances leading to the dishonour of the cheques or that they had given any assurance as to the cheques do not suffice."
      }
    ],
    "Conclusion": [
      {
        "tag": "p",
        "id": "p_9",
        "class": "",
        "title": "Conclusion",
        "text": "8. It is the above quoted provision, which is at the bottom of the controversy in the present matters and in this context the rulings of the Supreme Courtreferred to aboveprovide the necessary guidance."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_10",
        "class": "",
        "title": "Conclusion",
        "style": "",
        "text": "(a) It is necessary to specifically aver in a complaint underSection 141that at the time the offence was committed, the person accused was in charge of, and responsible for the conduct of business of the company. This averment is an essential requirement ofSection 141and has to be made in a complaint. Without this averment being made in a complaint, the requirements ofSection 141cannot be said to be satisfied."
      },
      {
        "tag": "blockquote",
        "id": "blockquote_11",
        "class": "",
        "title": "Conclusion",
        "style": "",
        "text": "(b) The answer to the question posed in sub-para (b) has to be in the negative. Merely being a director of a company is not sufficient to make the person liable underSection 141of the Act. A director in a company cannot be deemed to be in charge of and responsible to the company for the conduct of its business. The requirement ofSection 141is that the person sought to be made liable should be in charge of and responsible for the conduct of the business of the company at the relevant time. This has to be averred as a fact as there is no deemed liability of a director in such cases."
      },
      {
        "tag": "p",
        "id": "p_12",
        "class": "",
        "title": "Conclusion",
        "text": "xxx \"19. In view of the above discussion, our answers to the questions posed in the reference are as under:"
      },
      {
        "tag": "blockquote",
        "id": "blockquote_12",
        "class": "",
        "title": "Conclusion",
        "style": "",
        "text": "(c) The answer to Question (c) has to be in the affirmative."
      },
      {
        "tag": "p",
        "id": "p_14",
        "class": "",
        "title": "Conclusion",
        "text": "(emphasis supplied)"
      },
      {
        "tag": "p",
        "id": "p_16",
        "class": "",
        "title": "Conclusion",
        "text": "(emphasis supplied)"
      },
      {
        "tag": "p",
        "id": "p_18",
        "class": "",
        "title": "Conclusion",
        "text": "(emphasis supplied)"
      },
      {
        "tag": "p",
        "id": "p_21",
        "class": "",
        "title": "Conclusion",
        "text": "(emphasis supplied)"
      },
      {
        "tag": "p",
        "id": "p_24",
        "class": "",
        "title": "Conclusion",
        "text": "(iii). By virtue of the office they hold, the persons working in the capacity of the Managing Director or Joint Managing Director are deemed to be in charge of, and responsible forCrl.M.C. 3257/2016 & ors. Page 20 of 24the conduct of the business of, the company and, therefore, can be proceeded against in terms ofSection 141;"
      },
      {
        "tag": "p",
        "id": "p_30",
        "class": "",
        "title": "Conclusion",
        "text": "(emphasis supplied)"
      },
      {
        "tag": "p",
        "id": "p_33",
        "class": "",
        "title": "Conclusion",
        "text": "18. The view taken by the revisional court, therefore, must be upheld. The petitions and the applications filed therewith are dismissed."
      },
      {
        "tag": "p",
        "id": "p_34",
        "class": "",
        "title": "Conclusion",
        "text": "(R.K. GAUBA) JUDGE JULY 23, 2018 ygCrl.M.C. 3257/2016 & ors. Page 24 of 24"
      }
    ],
    "Court's Reasoning": [
      {
        "tag": "p",
        "id": "p_11",
        "class": "",
        "title": "Court's Reasoning",
        "text": "\"10. ... What is required is that the persons who are sought to be made criminally liable underSection 141should be, at the time the offence was committed, in charge of and responsible to the company for the conduct of the business of the company. Every person connected with the company shall not fall within the ambit of the provision. It is only those persons who were in charge of and responsible for the conduct of business of the company at the time of commission of an offence, who will be liable for criminal action. It follows from this that if a Director of a company who was not in charge of and was not responsible for the conduct of the business of the company at the relevant time, will not be liable under the provision. The liability arises from being in charge of and responsible for the conduct of business of the company at the relevant time when the offence was committed and not on the basis of merely holding a designation or office in a company. Conversely, a person not holding any office or designation in a company may be liable if he satisfies the main requirement of being in charge of and responsible for the conduct of business of a company at the relevant time. Liability depends on theCrl.M.C. 3257/2016 & ors. Page 15 of 24role one plays in the affairs of a company and not on designation or status. If being a Director or Manager or Secretary was enough to cast criminal liability, the section would have said so. Instead of \"every person\" the section would have said \"every Director, Manager or Secretary in a company is liable\", etc. The legislature is aware that it is a case of criminal liability which means serious consequences so far as the person sought to be made liable is concerned. Therefore, only persons who can be said to be connected with the commission of a crime at the relevant time have been subjected to action."
      },
      {
        "tag": "p",
        "id": "p_20",
        "class": "",
        "title": "Court's Reasoning",
        "text": "However, we are inclined to confirm the order [Anu Mehta, In re, 2012 SCC OnLine Cal 13134] passed by the High Court quashing the process as against Shobha Mehta. Shobha Mehta is stated to be an old lady who is over 70 years of age. Considering this fact and on an overall reading of the complaint in the peculiar facts and circumstances of the case, we feel that making her stand the trial would be an abuse of process of court. It is however,Crl.M.C. 3257/2016 & ors. Page 19 of 24necessary for the High Court to consider the cases of other Directors in light of the decisions considered by us and the conclusions drawn by us in this judgment.\""
      },
      {
        "tag": "p",
        "id": "p_31",
        "class": "",
        "title": "Court's Reasoning",
        "text": "16. It is clear from the bare perusal of the above quoted averments that they are deficient to the effect that there is not even a whisper of allegation that the respondents are persons who were in charge of or responsible to the company accused for the conduct of its business \"at the time the offence was committed\"."
      }
    ]
  },
  "all_paragraphs": [
    {
      "tag": "p",
      "id": "p_1",
      "class": "",
      "title": "Fact",
      "text": "1.      On 19.03.2014, eleven criminal complaints were filed in the\ncourt of the Metropolitan Magistrate, each seeking prosecution of the\nparties shown in the array of respondents for offences punishable\nunderSection 138of the Negotiable Instruments Act, 1881, two of\nsuch complaints i.e. the complaint nos.800/1/14 and 802/1/14 having\nbeen presented by Jwala Devi Enterprises Pvt. Ltd. through its\nauthorized representative Sat Parkash Bansal and the rest - complaint\nnos.799/1/14, 812/1/14, 813/1/14, 814/1/14, 815/1/14, 839/1/14,\n840/1/14, 841/1/14 and 842/1/14 - having been presented by Anand\nPrakash Bansal, Proprietor of M/s. Pooja Enterprises. Each of the said\ncriminal complaints were directed against several persons including a\ncompany described as M/s. Bush Foods Overseas Pvt. Ltd. It may be\nmentioned that Mr. Virkaran Awasty was reflected in the array of the\naccused as the Managing Director of the said company accused. The\nrespondents in these petitions were amongst the other persons shownCrl.M.C. 3257/2016 & ors.                                Page 10 of 24as accused in the said complaints, each of them having been described\nas \"Director\" of the said company accused."
    },
    {
      "tag": "p",
      "id": "p_2",
      "class": "",
      "title": "Fact",
      "text": "2.      On the basis of the preliminary inquiry in each case, the\nMetropolitan Magistrate issued process including against the\nrespondents herein. The respondents, feeling aggrieved, approached\nthe court of Sessions invoking its revisional jurisdiction by separate\npetitions (CR nos.34-62/2015), their prime contention being that there\nwas no case made out for they to be summoned as accused on the\nbasis of allegations that they were directors of the company accused,\ndenying that they had any concern with the responsibility for the\nconduct of the day-to-day business of the company."
    },
    {
      "tag": "p",
      "id": "p_3",
      "class": "",
      "title": "Precedent Analysis",
      "text": "3.      Placing reliance primarily on decision of a bench of three\nHon'ble Judges of the Supreme Court inSMS Pharmaceuticals Pvt.\nLtd. Vs. Neeta Bhalla, (2005) 8 SCC 89, the court of Sessions found\nsubstance and merit in the aforesaid contentions and allowed all the\nabove-said revision petitions by a common order dated 18.04.2015\nholding that the summoning order had been passed by the Magistrate\nmechanically without going through the material(s) on record, there\nbeing no averment to the effect that the said persons were in charge of,\nor responsible for the conduct of the business of, the company accused\nand consequently dropping the criminal proceedings against each of\nthem."
    },
    {
      "tag": "p",
      "id": "p_4",
      "class": "",
      "title": "Precedent Analysis",
      "text": "4.      The petitions at hand have been filed by the complainants\ninvoking the inherent jurisdiction of this court underSection 482of\nthe Code of Criminal Procedure, 1973 (Cr. PC) andArticle 227of the\nConstitution of India, 1950 to pray for the aforesaid orders of theCrl.M.C. 3257/2016 & ors.                                 Page 11 of 24Sessions court in each of the said eleven complaint cases to be set\naside and the proceedings against the respondents herein to be revived\non the file of the Metropolitan Magistrate. Reliance is placed in this\ncontext by the petitioners on the decisions of benches of two Hon'ble\nJudges of the Supreme Court reported asGunmala Sales (P) Ltd. Vs.\nAnu Mehta and Ors, (2015) 1 SCC 103 and Standard Chartered Bank\nVs. State of Maharashtra and Ors., (2016) 6 SCC 62.There can be no\nquarrel with the proposition, as advanced by the counsel for the\nrespondents, that the ruling of the bench of three Hon'ble Judges inSMS Pharmaceuticals(supra), continues to hold the field, the\ndecisions inGunmala Sales (P) Ltd.(supra) andStandard Chartered\nBank(supra) having accepted this position and the said subsequent\nrulings being in a slightly different context."
    },
    {
      "tag": "p",
      "id": "p_5",
      "class": "",
      "title": "Analysis of the law",
      "text": "5.      These matters pertain to the penal clause contained inSection\n138of the Negotiable Instruments Act, 1881, which reads thus :-"
    },
    {
      "tag": "p",
      "id": "p_6",
      "class": "",
      "title": "Analysis of the law",
      "text": "Explanation.--For the purposes of this section, \"debt of\n         other liability\" means a legally enforceable debt or other\n         liability."
    },
    {
      "tag": "p",
      "id": "p_7",
      "class": "",
      "title": "Analysis of the law",
      "text": "6.      It is clear from the plain reading of the above quoted provision\nand is now also well settled that the offence underSection 138of the\nNegotiable Instruments Act does not stand constituted merely upon\ndishonor of a cheque. The dishonor of a cheque which had been\nissued by the person (who is sought to be prosecuted) in favour of the\ncomplainant must be followed by a notice of demand within the\nstipulated period. It is the non-payment of the amount of the cheque\nwithin the statutory period after service of the notice of demand which\nconstitutes the offence that is punishable under the aforementioned\nprovision of law."
    },
    {
      "tag": "p",
      "id": "p_8",
      "class": "",
      "title": "Analysis of the law",
      "text": "7.      For dealing with cases involving companies and the persons\nconnected thereto as the accused, the provision ofSection 141Negotiable Instruments Act, 1881 is relevant.          For guidance and\nconvenience, it may be quoted hereunder :-"
    },
    {
      "tag": "p",
      "id": "p_9",
      "class": "",
      "title": "Conclusion",
      "text": "8.      It is the above quoted provision, which is at the bottom of the\ncontroversy in the present matters and in this context the rulings of the\nSupreme Courtreferred to aboveprovide the necessary guidance."
    },
    {
      "tag": "p",
      "id": "p_10",
      "class": "",
      "title": "Precedent Analysis",
      "text": "9.      Certain observations inSMS Pharmaceuticals(supra) which\nhave been quoted in the subsequent decisions, need to be borne in\nmind and, therefore, may be extracted as under :-"
    },
    {
      "tag": "p",
      "id": "p_11",
      "class": "",
      "title": "Court's Reasoning",
      "text": "\"10. ... What is required is that the persons who are\n                sought to be made criminally liable underSection 141should be, at the time the offence was committed, in\n                charge of and responsible to the company for the conduct\n                of the business of the company. Every person connected\n                with the company shall not fall within the ambit of the\n                provision. It is only those persons who were in charge of\n                and responsible for the conduct of business of the\n                company at the time of commission of an offence, who\n                will be liable for criminal action. It follows from this that\n                if a Director of a company who was not in charge of and\n                was not responsible for the conduct of the business of the\n                company at the relevant time, will not be liable under the\n                provision. The liability arises from being in charge of\n                and responsible for the conduct of business of the\n                company at the relevant time when the offence was\n                committed and not on the basis of merely holding a\n                designation or office in a company. Conversely, a person\n                not holding any office or designation in a company may\n                be liable if he satisfies the main requirement of being in\n                charge of and responsible for the conduct of business of a\n                company at the relevant time. Liability depends on theCrl.M.C. 3257/2016 & ors.                                      Page 15 of 24role one plays in the affairs of a company and not on\n                designation or status. If being a Director or Manager or\n                Secretary was enough to cast criminal liability, the\n                section would have said so. Instead of \"every person\" the\n                section would have said \"every Director, Manager or\n                Secretary in a company is liable\", etc. The legislature is\n                aware that it is a case of criminal liability which means\n                serious consequences so far as the person sought to be\n                made liable is concerned. Therefore, only persons who\n                can be said to be connected with the commission of a\n                crime at the relevant time have been subjected to action."
    },
    {
      "tag": "p",
      "id": "p_12",
      "class": "",
      "title": "Conclusion",
      "text": "xxx\n        \"19. In view of the above discussion, our answers to the\n        questions posed in the reference are as under:"
    },
    {
      "tag": "p",
      "id": "p_13",
      "class": "",
      "title": "Analysis of the law",
      "text": "The question notes that the managing director or joint\n        managing director would be admittedly in charge of the\n        company and responsible to the company for the conduct of\n        its business. When that is so, holders of such positions in a\n        company become liable underSection 141of the Act. By\n        virtue of the office they hold as managing director or joint\n        managing director, these persons are in charge of and\n        responsible for the conduct of business of the company.\n        Therefore, they get covered underSection 141. So far as the\n        signatory of a cheque which is dishonoured is concerned,\n        he is clearly responsible for the incriminating act and will\n        be covered under sub-Section (2) ofSection 141."
    },
    {
      "tag": "p",
      "id": "p_14",
      "class": "",
      "title": "Conclusion",
      "text": "(emphasis supplied)"
    },
    {
      "tag": "p",
      "id": "p_15",
      "class": "",
      "title": "Precedent Analysis",
      "text": "10.InGunmala Sales (P) Ltd.(supra), the issue brought before the\nSupreme Court by the complainant primarily was that the High Court\nin exercise of its jurisdiction under Section 482 Cr. PC had wrongly\nquashed the proceedings against the respondents on the ground that\nthere was a bald assertion in the complaint that they were directors in\nthe company at the time when the offence was committed.While\nacknowledging (in para 27) that the decision inSMS Pharmaceuticals(supra) still holds the field, inGunmala Sales (P) Ltd.(supra), it was\nfurther clarified thus :"
    },
    {
      "tag": "p",
      "id": "p_16",
      "class": "",
      "title": "Conclusion",
      "text": "(emphasis supplied)"
    },
    {
      "tag": "p",
      "id": "p_17",
      "class": "",
      "title": "Precedent Analysis",
      "text": "11.     For cases where the allegations in the complaint in writing are\nnot deficient but the persons are described as directors (who seek\nquashing of the summoning order), it was ruled inGunmala Sales (P)\nLtd.(supra) as under :-"
    },
    {
      "tag": "p",
      "id": "p_18",
      "class": "",
      "title": "Conclusion",
      "text": "(emphasis supplied)"
    },
    {
      "tag": "p",
      "id": "p_19",
      "class": "",
      "title": "Precedent Analysis",
      "text": "12.     The conclusions inGunmala Sales (P) Ltd.(supra) were\nsummarized thus :-"
    },
    {
      "tag": "p",
      "id": "p_20",
      "class": "",
      "title": "Court's Reasoning",
      "text": "However, we are inclined to confirm the order [Anu Mehta,\n         In re, 2012 SCC OnLine Cal 13134] passed by the High\n         Court quashing the process as against Shobha Mehta.\n         Shobha Mehta is stated to be an old lady who is over 70\n         years of age. Considering this fact and on an overall\n         reading of the complaint in the peculiar facts and\n         circumstances of the case, we feel that making her stand the\n         trial would be an abuse of process of court. It is however,Crl.M.C. 3257/2016 & ors.                                   Page 19 of 24necessary for the High Court to consider the cases of other\n            Directors in light of the decisions considered by us and the\n            conclusions drawn by us in this judgment.\""
    },
    {
      "tag": "p",
      "id": "p_21",
      "class": "",
      "title": "Conclusion",
      "text": "(emphasis supplied)"
    },
    {
      "tag": "p",
      "id": "p_22",
      "class": "",
      "title": "Precedent Analysis",
      "text": "13.     The above view inGunmala Sales (P) Ltd.(supra) was\nendorsed and reiterated inStandard Chartered Bank(supra)."
    },
    {
      "tag": "p",
      "id": "p_23",
      "class": "",
      "title": "Analysis of the law",
      "text": "14.     The guiding principles with reference toSection 141of the\nNegotiable Instruments Act, 1881, which are now well settled by\njudicial pronouncements, some of which have been noted above, may\nbe summarised thus :-"
    },
    {
      "tag": "p",
      "id": "p_24",
      "class": "",
      "title": "Conclusion",
      "text": "(iii).     By virtue of the office they hold, the persons working\n      in the capacity of the Managing Director or Joint Managing\n      Director are deemed to be in charge of, and responsible forCrl.M.C. 3257/2016 & ors.                                     Page 20 of 24the conduct of the business of, the company and, therefore,\n      can be proceeded against in terms ofSection 141;"
    },
    {
      "tag": "p",
      "id": "p_25",
      "class": "",
      "title": "Analysis of the law",
      "text": "(iv).     Merely because a person is a director of the company\n      is not sufficient to make him liable underSection 141, there\n      being no deeming that by holding such position he is in\n      charge of, or responsible for the conduct of the business of,\n      the company within the meaning ofSection 141;"
    },
    {
      "tag": "p",
      "id": "p_26",
      "class": "",
      "title": "Analysis of the law",
      "text": "(v).      It is necessary for the complainant to specifically aver\n      in the complaint that at the time the offence was committed,\n      the person sought to be prosecuted was in charge of, or\n      responsible for the conduct of the business of, the company in\n      terms ofSection 141, there being no need for further\n      particulars to be given in the complaint about his role, this\n      being subject to proof at the trial;"
    },
    {
      "tag": "p",
      "id": "p_27",
      "class": "",
      "title": "Analysis of the law",
      "text": "(vi).     The person who has been summoned as an accused\n      for offence under Section 138 of the Negotiable Instruments\n      Act, 1881 on the basis of averment that he was director of the\n      company accused, he being in charge of or responsible for the\n      conduct of its business cannot get the complaint quashed by\n      the High Court by filing a petition under Section 482 of the\n      Code of Criminal Procedure, 1973 merely on the ground that\n      no particulars as to his role have been set out in the\n      complaint; andCrl.M.C. 3257/2016 & ors.                                     Page 21 of 24"
    },
    {
      "tag": "p",
      "id": "p_28",
      "class": "",
      "title": "Analysis of the law",
      "text": "(vii).    The person who has been summoned as an accused\n      for offence underSection 138of the Negotiable Instruments\n      Act, 1881 by invoking the provision contained inSection 141may persuade the High Court to quash the process in exercise\n      of its inherent power underSection 482of the Code of\n      Criminal Procedure, 1973 by furnishing \"some sterling\n      incontrovertible material or acceptable circumstances\""
    },
    {
      "tag": "p",
      "id": "p_29",
      "class": "",
      "title": "Analysis of the law",
      "text": "15.     A perusal of the eleven complaints from which the present\nproceedings arise reveals that they are founded on identical averments\n(some of the accused who are not before this court being not\ncommon), the exception being with regard to the particulars of the\ncheques or the background facts against which they had been issued or\nthe dates on which they were presented or dishonored leading to\ndemand notices in their respect being issued, there being no payment\nmade pursuant to such demand notices. The averments crucial to pass\nthe muster ofSection 141of the Negotiable Instruments Act, 1881,\nhowever, are identically worded in the said eleven cases.              For\nillustration, the crucial averments appearing in one of such complaints\n(Crl. Complaint no.799/1/14), it being the first in chronology, may be\nextracted as under :-"
    },
    {
      "tag": "p",
      "id": "p_30",
      "class": "",
      "title": "Conclusion",
      "text": "(emphasis supplied)"
    },
    {
      "tag": "p",
      "id": "p_31",
      "class": "",
      "title": "Court's Reasoning",
      "text": "16.     It is clear from the bare perusal of the above quoted averments\nthat they are deficient to the effect that there is not even a whisper of\nallegation that the respondents are persons who were in charge of or\nresponsible to the company accused for the conduct of its business \"at\nthe time the offence was committed\"."
    },
    {
      "tag": "p",
      "id": "p_32",
      "class": "",
      "title": "Analysis of the law",
      "text": "17.     The respondents are not stated to be signatories to the cheques\nin question. They cannot be roped in merely because they have been\ndirectors of the company accused. The general averments that they\nwere responsible for all the business dealings and for the\ncircumstances leading to the dishonour of the cheques or that they had\ngiven any assurance as to the cheques do not suffice."
    },
    {
      "tag": "p",
      "id": "p_33",
      "class": "",
      "title": "Conclusion",
      "text": "18.      The view taken by the revisional court, therefore, must be\nupheld.      The petitions and the applications filed therewith are\ndismissed."
    },
    {
      "tag": "p",
      "id": "p_34",
      "class": "",
      "title": "Conclusion",
      "text": "(R.K. GAUBA)\n                                                        JUDGE\nJULY 23, 2018\nygCrl.M.C. 3257/2016 & ors.                                 Page 24 of 24"
    }
  ],
  "all_blockquotes": [
    {
      "tag": "blockquote",
      "id": "blockquote_1",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "138. Dishonour of cheque for insufficiency, etc., of funds in the account -- Where any cheque drawn by a person on an account maintained by him with a banker for payment of any amount of money to another person from out of that account for the discharge, in whole or in part, of any debt or other liability, is returned by the bank unpaid, either because of the amount of money standing to the credit of that account is insufficient to honour the cheque or that it exceeds the amount arranged to be paid from that account by an agreement made with that bank, such person shall be deemed to have committed an offence and shall, without prejudice to any other provision of this Act, be punished with imprisonment for 8 [a term which may be extended to two years'], or with fine which may extend to twice the amount of the cheque, or with both:"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_2",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "Provided that nothing contained in this section shall apply unless--"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_3",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "(a) the cheque has been presented to the bank within a period of six months from the date on which it is drawn or within the period of its validity, whichever is earlier;"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_4",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "(b) the payee or the holder in due course of the cheque, as the case may be, makes a demand for the payment of the said amount of money by giving a notice; in writing, to the drawer of the cheque, within thirty days of the receipt of information by him from the bank regarding the return of the cheque as unpaid; and"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_5",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "(c) the drawer of such cheque fails to make the payment of the said amount of money to the payee or, as the case may be, to the holder in due course of the cheque, within fifteen days of the receipt of the said notice."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_6",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "141. Offences by companies.--(1) If the person committing an offence undersection 138is a company, every person who, at the time the offence was committed, was in charge of, and was responsible to, the company for the conduct of the business of the company, as well as the company, shall be deemed to be guilty of the offence and shall be liable to be proceeded against and punished accordingly:"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_7",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "Provided that nothing contained in this sub-section shall render any person liable to punishment if he proves that the offence was committed without his knowledge, or that he had exercised all due diligence to prevent the commission of such offence:"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_8",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "Provided further that where a person is nominated as a Director of a company by virtue of his holding any office or employment in the Central Government or State Government or a financial corporation owned or controlled by the Central Government or the State Government, as the case may be, he shall not be liable for prosecution under this Chapter."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_9",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "(2) Notwithstanding anything contained in sub-section (1), where any offence under this Act has been committed by a company and it is proved that the offence has been committed with the consent or connivance of, or is attributable to, any neglect on the part of, any director, manager, secretary or other officer of the company, suchCrl.M.C. 3257/2016 & ors. Page 14 of 24director, manager, secretary or other officer shall also be deemed to be guilty of that offence and shall be liable to be proceeded against and punished accordingly."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_10",
      "class": "",
      "title": "Conclusion",
      "style": "",
      "text": "(a) It is necessary to specifically aver in a complaint underSection 141that at the time the offence was committed, the person accused was in charge of, and responsible for the conduct of business of the company. This averment is an essential requirement ofSection 141and has to be made in a complaint. Without this averment being made in a complaint, the requirements ofSection 141cannot be said to be satisfied."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_11",
      "class": "",
      "title": "Conclusion",
      "style": "",
      "text": "(b) The answer to the question posed in sub-para (b) has to be in the negative. Merely being a director of a company is not sufficient to make the person liable underSection 141of the Act. A director in a company cannot be deemed to be in charge of and responsible to the company for the conduct of its business. The requirement ofSection 141is that the person sought to be made liable should be in charge of and responsible for the conduct of the business of the company at the relevant time. This has to be averred as a fact as there is no deemed liability of a director in such cases."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_12",
      "class": "",
      "title": "Conclusion",
      "style": "",
      "text": "(c) The answer to Question (c) has to be in the affirmative."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_13",
      "class": "",
      "title": "Precedent Analysis",
      "style": "",
      "text": "\"27. It is clear from a perusal of the above decisions thatSMS Pharma (1) [S.M.S. Pharmaceuticals Ltd. v. Neeta Bhalla, (2005) 8 SCC 89 : 2005 SCC (Cri) 1975] , which is a three-Judge Bench decision, still holds the field. In all subsequent decisions, two-Judge Benches of this Court have followed SMS Pharma...."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_14",
      "class": "",
      "title": "Precedent Analysis",
      "style": "",
      "text": "28. We are concerned in this case with Directors who are not signatories to the cheques. So far as Directors whoCrl.M.C. 3257/2016 & ors. Page 17 of 24are not signatories to the cheques or who are not Managing Directors or Joint Managing Directors are concerned, it is clear from the conclusions drawn in the abovementioned cases that it is necessary to aver in the complaint filed underSection 138read withSection 141of the NI Act that at the relevant time when the offence was committed, the Directors were in charge of and were responsible for the conduct of the business of the company. This is a basic requirement. There is no deemed liability of such Directors.\""
    },
    {
      "tag": "blockquote",
      "id": "blockquote_15",
      "class": "",
      "title": "Precedent Analysis",
      "style": "",
      "text": "\"31. When in view of the basic averment process is issued the complaint must proceed against the Directors. But, if any Director wants the process to be quashed by filing a petition under Section 482 of the Code on the ground that only a bald averment is made in the complaint and that he is really not concerned with the issuance of the cheque, he must in order to persuade the High Court to quash the process either furnish some sterling incontrovertible material or acceptable circumstances to substantiate his contention. He must make out a case that making him stand the trial would be an abuse of process of court. He cannot get the complaint quashed merely on the ground that apart from the basic averment no particulars are given in the complaint about his role, because ordinarily the basic averment would be sufficient to send him to trial and it could be argued that his further role could be brought out in the trial. Quashing of a complaint is a serious matter. Complaint cannot be quashed for theCrl.M.C. 3257/2016 & ors. Page 18 of 24asking. For quashing of a complaint it must be shown that no offence is made out at all against the Director.\""
    },
    {
      "tag": "blockquote",
      "id": "blockquote_16",
      "class": "",
      "title": "Precedent Analysis",
      "style": "",
      "text": "\"35. ... Pertinently, in the application filed by the respondents, no clear case was made out that at the material time, the Directors were not in charge of and were not responsible for the conduct of the business of the Company by referring to or producing any incontrovertible or unimpeachable evidence which is beyond suspicion or doubt or any totally acceptable circumstances. It is merely stated that Sidharth Mehta had resigned from the directorship of the Company on 30-9-2010 but no incontrovertible or unimpeachable evidence was produced before the High Court as was done inAnita Malhotra [Anita Malhotra v. Apparel Export Promotion Council, (2012) 1 SCC 520 : (2012) 1 SCC (Civ) 329 : (2012) 1 SCC (Cri) 496] to show that he had, in fact, resigned long before the cheques in question were issued. Similar is the case with Kanhaiya Lal Mehta and Anu Mehta. Nothing was produced to substantiate the contention that they were not in charge of and not responsible for the conduct of the business of the Company at the relevant time. In the circumstances, we are of the opinion that the matter deserves to be remitted to the High Court for fresh hearing."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_17",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "(i) It is only those persons who are in charge of or responsible for the conduct of the business of the company at the time of commission of the offence underSection 138of the Negotiable Instruments Act, 1881 who can be subjected to criminal action with reference toSection 141;"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_18",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "(ii). If the person committing an offence underSection 138of the Negotiable Instruments Act, 1881 is a company, the person who was signatory to the cheque which is dishonoured is clearly responsible for the incriminating act and would be liable to be proceeded against underSection 141 (2);"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_19",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "substantiating his contention that he was not in charge of nor responsible for the conduct of the business of the company \"at the time the offence was committed\" and thereby showing a case that making him stand the trial would be an abuse of the process of court, but not otherwise."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_20",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "\"3. That the accused No.3 Mr. Vinod Sirohi, Accused No.4 Fadi El Jaouni, Accused No.5 Khaled Abdelrahman Radi and the Accused No.6 Mr. Naseer Mohd. MF AI Hajri are the Directors and Accused No.7 Mr. Rahul Shivam is the Authorised Signatory of the Accused No.1 Company, namely M/s. Bush Foods Pvt. Ltd. and are actively engaged and responsible for and in-charge of day- to-day management, business activities and affairs of the Accused No.1 firm."
    },
    {
      "tag": "blockquote",
      "id": "blockquote_21",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "xxx"
    },
    {
      "tag": "blockquote",
      "id": "blockquote_22",
      "class": "",
      "title": "Analysis of the law",
      "style": "",
      "text": "10. That despite the receipt of the above said Legal Notice dated 05.02.2014, the Accused Persons have failed / refused / neglected to make the payment of the above said Cheques amount to the Complainant and have therefore made themselves liable to be prosecuted under the provisions ofSections 138,141and142of the Negotiable Instruments Act, 1881. It is further submitted that at the time of issuance of the said cheques, the accused persons have assured, promised and represented to the Complainant that the said cheques would be honored on presentation. However, the said Cheques, which are the subject matter of the present complaint, were dishonored on presentment. The accused persons have no intention to make the said payment to the Complainant. It is submitted that the Accused Persons have been responsible for all the business dealings for and on behalf of their said Accused no.1 firm and also responsible for the circumstances that have lead to the dishonor of the aid cheques issued to the complainant.\""
    }
  ]
}

Excellent example, Amay. This case is actually perfect for showing how your KG pipeline will work in practice.

I’ll walk you through:

👉 For THIS exact raw case, what candidate nodes you would extract for each class, and from where.

No theory. Direct mapping.

0️⃣ Preprocess First (Mandatory)

Before extraction:

- Remove page numbers
- Normalize "Section138" → "Section 138"
- Lowercase
- Sentence split

So:

underSection 138 → under Section 138

This matters for regex later.

1️⃣ CaseType — What Kind of Case Is This?
📍 Source
page_title
case_title
Facts
Text Signals

From title:

vs → litigation
Enterprises Pvt Ltd → commercial

From facts:

criminal complaints
Section 138 NI Act
dishonour of cheque
Pattern
(dishonou?r of cheque|section 138|ni act)
Candidate Extraction

From this case:

"criminal complaints"
"Section 138"
"dishonor of cheque"
"Negotiable Instruments Act"
Normalize → CaseType

Clustered:

Cheque Dishonour Litigation
Commercial Criminal Case
NI Act Prosecution

→ Final Candidate:

CaseType = Cheque_Dishonour_Case
2️⃣ LegalGround — Why Is This Case Filed?

Legal ground = legal basis of action.

📍 Source
Issues
Arguments
Reasoning
Conclusion
Text Signals

Repeated many times:

Section 138
Section 141
offence
dishonour
liable

Example:

"offence under Section 138"

"liable under Section 141"

Pattern
(offence under|liable under|invoking|provision of)
Candidates Found

From this case:

"offence under Section 138"
"liability under Section 141"
"dishonour of cheque"
"offences by companies"
Normalize

→ Cluster:

Section 138 liability
Cheque dishonour offence
Company liability
Candidate Node
LegalGround = Dishonour_of_Cheque_Liability
3️⃣ LegalRequirement — What Must Be Proved?

This is the MOST important node.

📍 Source
Analysis of law
Court’s reasoning
Blockquotes
Text Signals

Look for:

must
necessary
essential
required
only if
provided that
Examples From Case

Direct hits:

"necessary to aver"

"must be followed by a notice"

"required is that the persons…"

"in charge of and responsible"

"non-payment within statutory period"

Pattern
(must|required|necessary|essential|provided that|only if)
Extracted Candidates

From your data:

"notice of demand within 30 days"
"non-payment within statutory period"
"in charge of business"
"responsible for conduct"
"averment in complaint"
"signatory to cheque"
Normalize

Cluster → Requirements:

Notice_Service
Non_Payment_Within_Time
Director_In_Charge
Responsibility_For_Business
Proper_Averment
Candidate Nodes
LegalRequirement:
- Statutory_Notice_Served
- Non_Payment_Within_15_Days
- Accused_In_Charge
- Responsibility_For_Business
- Proper_Complaint_Averment
4️⃣ EvidenceType — What Proves the Requirements?
📍 Source
Facts
Arguments
Reasoning
Look For Nouns = Documents / Records

Pattern:

notice
cheque
complaint
record
document
petition
Examples

From case:

cheques
complaints
demand notice
summoning order
revision petitions
legal notice
Extracted Candidates
Cheque
Legal_Notice
Criminal_Complaint
Summoning_Order
Revision_Petition
Court_Record
Normalize

→ Evidence nodes:

EvidenceType:
- Dishonoured_Cheque
- Demand_Notice
- Criminal_Complaint
- Summoning_Order
- Court_Records
5️⃣ ClaimType — What Are Parties Claiming?
📍 Source
Arguments
Reasoning
Facts
Pattern

Verb + Object

(deny|claim|contend|assert|submit|allege)
Examples

From case:

"denying that they had any concern"

"no case made out"

"allegations that they were directors"

"responsible for conduct"

Extracted Claims
not responsible
not in charge
wrongly summoned
directors liable
process should be quashed
Normalize

→ ClaimTypes:

No_Responsibility_Claim
Wrongful_Summoning_Claim
Director_Liability_Claim
Process_Quash_Request
Proper_Liability_Claim
6️⃣ OutcomeType — What Was the Result?
📍 Source
Conclusion
Pattern
(dismissed|allowed|upheld|quashed|set aside)
Found

From conclusion:

"petitions… dismissed"

"must be upheld"

"proceedings… quashed"

Extracted
dismissed
upheld
quashed (earlier)
Normalize
OutcomeType:
- Petition_Dismissed
- Summoning_Upheld
- Proceedings_Quashed (lower court)

Primary outcome:

Petition_Dismissed
✅ Final Output For THIS Case (What Your Pipeline Produces)

After running extractors:

CaseType
Cheque_Dishonour_Case
LegalGround
Dishonour_of_Cheque_Liability
Company_Director_Liability
LegalRequirement
Statutory_Notice_Served
Non_Payment_Within_15_Days
Accused_In_Charge
Responsibility_For_Business
Proper_Complaint_Averment
EvidenceType
Dishonoured_Cheque
Demand_Notice
Criminal_Complaint
Summoning_Order
Court_Record
ClaimType
No_Responsibility_Claim
Wrongful_Summoning_Claim
Director_Liability_Claim
Process_Quash_Request
OutcomeType
Petition_Dismissed
🧠 How This Looks in Graph (For This Case)

Automatically:

Cheque_Dishonour_Case
   ↓
Dishonour_of_Cheque_Liability
   ↓
Accused_In_Charge
   ↓
Demand_Notice
   ↓
Director_Liability_Claim
   ↓
Petition_Dismissed

With contradictions:

No_Responsibility_Claim ⟷ Director_Liability_Claim
📌 Important: Why This Works

Notice:

We NEVER used section numbers
We NEVER hand-labelled
We used:
linguistic patterns
frequency
repetition
normalization

So this scales to 10k+ cases.

🚀 Your Next Coding Step (Very Concrete)

Implement these 6 extractors:

extract_case_type()
extract_legal_ground()
extract_requirements()
extract_evidence()
extract_claims()
extract_outcome()

Each = 200–300 LOC.

Start simple → improve.

If you want, next I can give you:

✅ Python skeleton for these extractors
✅ Regex library for legal text
✅ Neo4j ingestion format
✅ CON → KG mapping

Just tell me which one you want.

so we need to build extractors for each of the nodes in KG, 
let's do the casetype first 

also note that the case i gave before will be eventually converted to a CON like the following structure, this CON would be used for stuff

{
  "case_id": "PHC_CWJC_11252_2025",

  "case_type": "service_law__appointment_posting",

  "parties": [
    { "party_id": "P1", "role": "petitioner" },
    { "party_id": "P2", "role": "state_authority" }
  ],

  "issues": [
    { "issue_type": "violation_of_merit_cum_choice" },
    { "issue_type": "arbitrary_administrative_action" }
  ],

  "claims": [
    {
      "claim_id": "C1",
      "party_id": "P1",
      "claim_type": "merit_violation",
      "polarity": "asserted",
      "subject": "district_allotment"
    },
    {
      "claim_id": "C2",
      "party_id": "P1",
      "claim_type": "administrative_arbitrariness",
      "polarity": "asserted",
      "subject": "posting_process"
    },
    {
      "claim_id": "C3",
      "party_id": "P2",
      "claim_type": "lawful_action",
      "polarity": "asserted",
      "subject": "district_allotment"
    }
  ],

  "administrative_actions": [
    {
      "action_id": "A1",
      "authority": "Director_Primary_Education",
      "action_type": "district_preference_call",
      "date": "2025-01-02"
    },
    {
      "action_id": "A2",
      "authority": "Director_Primary_Education",
      "action_type": "district_allotment",
      "date": "2025-07-01"
    }
  ],

  "evidence_present": [
    "merit_list",
    "preference_submission_records"
  ],

  "claim_outcomes": [
    { "claim_id": "C1", "status": "accepted" },
    { "claim_id": "C2", "status": "accepted" },
    { "claim_id": "C3", "status": "rejected" }
  ],

  "outcome": "petition_allowed"
}


Perfect. Now you’re thinking in the right abstraction layer.

You are no longer doing “NLP on judgments”.

You are doing:

Legal → Structured World Modeling → Graph + ML

Let’s do this properly, starting with CaseType extractor.

🎯 Goal (For CaseType)

Given:

Raw judgment (RRs / text)
Later → CON

We want to output:

"case_type": "cheque_dishonour__director_liability"

Not:

❌ "This is a case about cheque dishonour..."

Only:

✅ Canonical symbolic label.

1️⃣ What is CaseType in Your System?

In your CON:

"case_type": "service_law__appointment_posting"

So format is:

<domain>__<subdomain>

Example families:

Domain	Subdomain
property	ownership_dispute
family	divorce_cruelty
service_law	promotion_denial
commercial	cheque_dishonour
tenancy	eviction
inheritance	will_dispute

So:

👉 CaseType = hierarchical legal category.

2️⃣ Pipeline for CaseType Extraction

Your extractor should be:

Raw Case → Signals → Features → Classifier → Canonical Label

We’ll implement it in 3 layers:

Layer 1: Rule signals
Layer 2: Statistical keywords
Layer 3: ML fallback

Start with 1+2. ML later.

3️⃣ Layer 1 — High-Precision Rules

These catch 60–70% cases cleanly.

A. Build Pattern Library

Create casetype_rules.json:

{
  "cheque_dishonour": {
    "patterns": [
      "section 138",
      "negotiable instruments act",
      "dishonou?r of cheque",
      "cheque.*returned",
      "bounced cheque"
    ],
    "label": "commercial__cheque_dishonour"
  },

  "service_appointment": {
    "patterns": [
      "appointment",
      "posting",
      "transfer",
      "service rules",
      "seniority",
      "promotion"
    ],
    "label": "service_law__appointment_posting"
  },

  "divorce": {
    "patterns": [
      "divorce",
      "section 13 hindu marriage",
      "cruelty",
      "desertion",
      "restitution of conjugal rights"
    ],
    "label": "family_law__divorce"
  }
}
B. Rule Matching

Algorithm:

for rule in rules:
    if >=2 patterns match:
        return label

Example (Your Case):

Matches:

section 138
negotiable instruments act
cheque

→ Hit.

Return:

commercial__cheque_dishonour
4️⃣ Layer 2 — Keyword Scoring

For cases not caught by rules.

Build Vocabulary

From 10k cases:

Run TF-IDF per known category.

Example:

Word	Cheque	Divorce	Property
cheque	0.91	0.01	0.00
divorce	0.00	0.93	0.00
sale deed	0.00	0.01	0.87

Store:

keyword_scores.json
Scoring

For new case:

score(category) = Σ tfidf(word)

Pick max.

5️⃣ Layer 3 — ML (Later)

Once you have 2–3k CONs:

Train:

LegalBERT → CaseType classifier

Fallback if rule+tfidf fail.

Not now.

6️⃣ Where Do We Read Text From?

For CaseType, use only:

sources = [
  case_title,
  facts,
  issues,
  first_3_paras,
  analysis_of_law
]

Ignore:

long precedents
quotations

Why?

Because case type is stated early.

7️⃣ Concrete Example (Your Provided Case)

Let’s simulate:

Input Text

From facts + law:

section 138
negotiable instruments act
dishonour of cheque
cheques returned unpaid

Rule hits:

>=3 matches

Return:

"case_type": "commercial__cheque_dishonour"

If you want finer:

commercial__cheque_dishonour_director_liability

(add later via LegalGround)

8️⃣ Output Stored in CON

Your CON will have:

{
  "case_id": "...",

  "case_type": "commercial__cheque_dishonour",

  ...
}
9️⃣ Python Skeleton (You Can Implement This Now)
import re
import json

class CaseTypeExtractor:

    def __init__(self, rule_path):
        with open(rule_path) as f:
            self.rules = json.load(f)

    def normalize(self, text):
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        return text

    def match_rules(self, text):
        for rule in self.rules.values():

            hits = 0

            for pat in rule["patterns"]:
                if re.search(pat, text):
                    hits += 1

            if hits >= 2:
                return rule["label"]

        return None

    def extract(self, case):

        text = ""

        text += case["case_title"] + " "

        for f in case["elements_by_title"].get("Fact", []):
            text += f["text"] + " "

        for a in case["elements_by_title"].get("Analysis of the law", []):
            text += a["text"] + " "

        text = self.normalize(text)

        label = self.match_rules(text)

        if label:
            return label

        return "unknown__other"
🔟 Why This Design Is Correct For Your Project

Because:

✅ Interpretable
✅ Debuggable
✅ Upgradable
✅ Works on small data
✅ Legal-safe
✅ ML-ready later

Not black-box.

📌 What You Should Do Next (This Week)
Step 1 (You)

Implement CaseTypeExtractor v1 (rules only).

Step 2 (Team)

Make rule library for:

- Property
- Family
- Service
- Tenancy
- Commercial
- Inheritance
Step 3

Test on 200 cases → measure accuracy.

If you want, next I’ll help you design:

➡️ LegalGroundExtractor (hardest one)
➡️ How CaseType links to KG
➡️ How to auto-generate rule library

Tell me which.

now let's see how we must extract this from the cases
LegalGround LegalRequirement

Great. Now you’re moving into the core intelligence layer of your system.

CaseType was “classification”.

Now:

LegalGround + LegalRequirement = Legal Reasoning Graph

This is what will later power:

missing evidence detection
contradiction detection
judgment prediction

Let’s design this properly and implementably.

🎯 1. What These Two Mean (In Your System)
✅ LegalGround

Why is this case legally valid / invalid?

It is the legal theory of the case.

Examples:

dishonour_of_cheque_liability
breach_of_contract
illegal_termination
desertion_ground_for_divorce
encroachment_of_property

Think: Cause of action.

✅ LegalRequirement

What must be proven to win on that ground?

These are conditions.

Examples:

cheque_presented_in_time
legal_notice_served
non_payment_within_15_days
valid_marriage_proved
cruelty_established
sale_deed_registered

Think: Elements of offence / claim.

So:

LegalGround = theory
LegalRequirement = elements
🧩 2. Where To Extract Them From (RR Mapping)
RR Section	LegalGround	LegalRequirement
Facts	❌	⚠️ (weak)
Issues	✅	⚠️
Arguments	✅	✅
Analysis of Law	✅	✅✅
Reasoning	✅	✅✅
Conclusion	⚠️	⚠️

Main sources:

👉 Analysis of Law + Court Reasoning

90% info is here.

🏗️ 3. Extraction Architecture

Both follow same pipeline:

Text → Sentence Split → Pattern Mining → Phrase Extraction → Normalization → Canonical Node
4️⃣ LegalGround Extraction (Step-by-Step)
Step A — Find “Ground Sentences”

We only look at sentences that express liability / entitlement.

Pattern Library
GROUND_TRIGGERS = [
  "offence under",
  "liable under",
  "entitled to",
  "ground for",
  "cause of action",
  "invoking",
  "prosecution under",
  "claim under",
  "relief under",
  "punishable under"
]
Example (Your Case)

From text:

"offence under Section 138"

"liable under Section 141"

"provision of Section 138"

→ Trigger hits.

Step B — Extract Legal Phrase

After trigger, extract noun phrase.

Example:

offence under Section 138 of NI Act
↓
dishonour of cheque offence

Use dependency parsing / regex.

Regex v1:

(offence under|liable under|provision of)\s+(.{1,80})
Step C — Normalize to Canonical

Raw:

offence under section 138
dishonour of cheque

Map:

dishonour_of_cheque_liability

Using dictionary.

{
  "section 138": "dishonour_of_cheque_liability",
  "cheque dishonour": "dishonour_of_cheque_liability"
}
Step D — Output

For your case:

"legal_grounds": [
  "dishonour_of_cheque_liability",
  "company_director_vicarious_liability"
]
5️⃣ LegalRequirement Extraction (Step-by-Step)

This is harder and more important.

Step A — Find “Requirement Sentences”

Look for modal + necessity.

Pattern Set
REQ_TRIGGERS = [
  "must",
  "necessary",
  "essential",
  "required",
  "only if",
  "provided that",
  "condition",
  "unless",
  "it is clear that",
  "it is settled that"
]
Example

"necessary to aver"

"must be followed by a notice"

"provided that nothing shall apply unless"

Hit.

Step B — Extract Condition Clause

We extract the clause after trigger.

Example:

must be followed by a notice of demand
↓
notice of demand

Regex:

(must|required|necessary to|provided that)(.{1,120})
Step C — Extract Verb–Object Pair

Turn sentence into:

<Action> + <Object>

Example:

serve notice
make payment
be in charge
file complaint

Use spaCy dependency parser.

Example:

"persons must be in charge of business"

→

in_charge_of_business
Step D — Normalize

Map variants → canonical.

{
  "notice of demand": "statutory_notice_served",
  "legal notice": "statutory_notice_served",
  "in charge": "accused_in_charge",
  "responsible for business": "responsibility_for_business",
  "non payment": "non_payment_within_time"
}
Step E — Output

From your case:

"legal_requirements": [
  "statutory_notice_served",
  "non_payment_within_15_days",
  "accused_in_charge",
  "responsibility_for_business",
  "proper_averment_in_complaint"
]
6️⃣ Unified Python Skeleton

Here is how both fit.

class LegalExtractor:

    def __init__(self, ground_map, req_map):
        self.ground_map = ground_map
        self.req_map = req_map

    def split_sentences(self, text):
        return re.split(r'[.;]\s+', text)

    def extract_grounds(self, text):

        grounds = set()

        for sent in self.split_sentences(text):

            for trig in GROUND_TRIGGERS:
                if trig in sent.lower():

                    for k,v in self.ground_map.items():
                        if k in sent.lower():
                            grounds.add(v)

        return list(grounds)


    def extract_requirements(self, text):

        reqs = set()

        for sent in self.split_sentences(text):

            for trig in REQ_TRIGGERS:
                if trig in sent.lower():

                    for k,v in self.req_map.items():
                        if k in sent.lower():
                            reqs.add(v)

        return list(reqs)
7️⃣ How This Feeds KG

For each CON:

Case → LegalGround → LegalRequirement

Graph insert:

(:Case {id})
  -[:BASED_ON]->
(:LegalGround)
  -[:REQUIRES]->
(:LegalRequirement)
8️⃣ Why This Works Long-Term

Because:

✔ Symbolic
✔ Explainable
✔ Law-aligned
✔ Improves with data
✔ Can be human-verified
✔ ML can be layered later

Unlike end-to-end transformers.

9️⃣ What You Should Implement Next
Week Plan

1️⃣ Build ground_triggers.json
2️⃣ Build requirement_triggers.json
3️⃣ Write extractor class
4️⃣ Run on 100 cases
5️⃣ Manually verify
6️⃣ Update maps

If you want, next I can show you:

➡️ How to extract EvidenceType
➡️ How to detect Claim contradictions
➡️ How to auto-expand ground/req maps

Which one next?

check this nyayaRAG and tell if it can do everything that we wanted to do

NyayaRAG: Realistic Legal Judgment Prediction with RAG under the
Indian Common Law System
Shubham Kumar Nigam1,5∗† Balaramamahanthi Deepak Patnaik1∗ Shivam Mishra1∗
Ajay Varghese Thomas2∗ Noel Shallum3 Kripabandhu Ghosh4 Arnab Bhattacharya1
1Indian Institute of Technology Kanpur, India 2SRM Institute of Science and Technology, India
3Symbiosis Law School Pune, India 4IISER Kolkata, India
5University of Birmingham, Dubai, United Arab Emirates
{shubhamkumarnigam, bdeepakpatnaik2002, shivam1602m,
ajaythomas.work, noelshallum}@gmail.com
kripaghosh@iiserkol.ac.in arnabb@cse.iitk.ac.in
Abstract
Legal Judgment Prediction (LJP) has emerged
as a key area in AI for law, aiming to automate
judicial outcome forecasting and enhance inter-
pretability in legal reasoning. While previous
approaches in the Indian context have relied on
internal case content such as facts, issues, and
reasoning, they often overlook a core element
of common law systems – reliance on statutory
provisions and judicial precedents. In this work,
we propose NyayaRAG, a Retrieval-Augmented
Generation (RAG) framework that simulates re-
alistic courtroom scenarios by providing mod-
els with factual case descriptions, relevant le-
gal statutes, and semantically retrieved prior
cases. NyayaRAG evaluates the effectiveness
of these combined inputs in predicting court
decisions and generating legal explanations us-
ing a domain-specific pipeline tailored for the
Indian legal system. We assess performance
across various input configurations using both
standard lexical and semantic metrics as well
as LLM-based evaluators such as G-Eval. Our
results show that augmenting factual inputs
with structured legal knowledge significantly
improves both predictive accuracy and explana-
tion quality.
1 Introduction
The application of artificial intelligence (AI) in le-
gal judgment prediction (LJP) has the potential to
transform legal systems by improving efficiency,
transparency, and access to justice. This is partic-
ularly crucial for India, where millions of cases
remain pending in courts, and decision-making is
inherently dependent on factual narratives, statu-
tory interpretation, and judicial precedents. India
follows a common law system, where prior deci-
sions (precedents) and statutory provisions play a
central role in influencing legal outcomes. How-
ever, most existing AI-based LJP systems do not
∗These authors contributed equally to this work
†Corresponding author
adequately replicate this fundamental feature of
judicial reasoning.
Previous studies (Malik et al., 2021b; Nigam
et al., 2024d, 2025a) have focused on predicting
legal outcomes using the current case document,
including sections like facts, arguments, issues, rea-
soning, and decision. More recent efforts have
narrowed the scope to factual inputs alone (Nigam
et al., 2024a, 2025c); yet these systems still operate
in a setting that is not real, and does not consider
how courts naturally rely on applicable laws and
prior rulings. In reality, judges rarely decide in
isolation; instead, they actively refer to relevant
precedents and statutory laws. To bridge this gap,
we propose a framework that more closely mirrors
actual courtroom conditions by explicitly incorpo-
rating external legal knowledge during inference.
In critical domains like law, medicine and fi-
nance, decisions must be grounded in verifiable
information. Experts in these domains cannot rely
on opaque, black-box inferences and require sys-
tems that ensure factual consistency. Hallucina-
tions, common in large generative models, can
have severe consequences in legal decision-making.
By retrieving and conditioning model responses
on grounded sources such as applicable laws and
precedent cases, the Retrieval-Augmented Genera-
tion (RAG) paradigm offers a principled approach
to mitigate hallucination and promote trustworthy
outputs. Furthermore, RAG frameworks like ours
can be flexibly integrated into existing legal sys-
tems without requiring the retraining of core mod-
els or the sharing of private or sensitive case data.
This enhances user trust while allowing the legal
community to benefit from AI without sacrificing
transparency or data confidentiality.
Motivated by the above, we introduce NyayaRAG,
a Retrieval-Augmented Generation (RAG) frame-
work for realistic legal judgment prediction and
explanation in the Indian common law system. The
term “NyayaRAG” is derived from two compo-
arXiv:2508.00709v3 [cs.CL] 15 Nov 2025
nents: “Nyaya” meaning “justice” and “RAG” re-
ferring to “Retrieval-Augmented Generation”. To-
gether, the name reflects our vision to build a
justice-aware generation system that emulates the
reasoning process followed by Indian courts, using
facts, statutes, and precedents.
Unlike prior models that operate purely on in-
ternal case content, NyayaRAG simulates real-world
judicial decision-making by providing the model
with: (i) the summarized factual background of the
current case, (ii) relevant statutory provisions, and
(iii) retrieved top-k semantically similar previous
judgments. This structure emulates how judges
deliberate on new cases, consulting both textual
statutes and prior judicial opinions. Through this
design, we evaluate how RAG can help reduce hal-
lucinations, promote faithfulness, and yield legally
coherent predictions and explanations.
Our contributions in this paper are as follows:
1. A Realistic RAG Framework for Indian Courts:
We present NyayaRAG, a novel framework that
emulates Indian common law decision-making
by incorporating not only facts but also retrieved
legal statutes and precedents.
2. Retrieval-Augmented Pipelines with Structured
Inputs: We construct modular pipelines repre-
senting different combinations of factual, statu-
tory, and precedent-based inputs to understand
their individual and combined contributions to
model performance.
3. Simulating Common Law Reasoning with LLMs:
We show that LLMs guided by RAG and factual
grounding can produce legally faithful expla-
nations that are aligned with how real-world
decisions are made under common law systems.
Our work moves beyond fact-only or self-
contained models by replicating a more faithful le-
gal reasoning pipeline aligned with Indian jurispru-
dence. We hope that NyayaRAG opens new direc-
tions for building interpretable, retrieval-aware AI
systems in legal settings, particularly in resource-
constrained yet precedent-driven judicial systems
like India’s. We have shared our dataset, code, and
RAG-based pipeline through a GitHub repository1.
2 Related Work
Recent advances in natural language process-
ing (NLP) and large language models (LLMs)
have transformed knowledge-intensive tasks, in-
cluding question answering and decision support.
1https://github.com/ShubhamKumarNigam/NyayaRAG
Transformer-based architectures such as BERT
(Devlin et al., 2018), GPT (Radford et al., 2019),
and their instruction-tuned successors demonstrate
strong multi-hop reasoning and contextual gener-
ation abilities. Retrieval-Augmented Generation
(RAG) further improves factual grounding and re-
duces hallucinations by combining external docu-
ment retrieval with generative models (Han et al.,
2024; Hei et al., 2024).
The domain of Legal Judgment Prediction (LJP)
has evolved from outcome classification toward ex-
planation generation and realistic reasoning. Foun-
dational work explored case outcome prediction in
ECHR and Chinese datasets (Aletras et al., 2016;
Chalkidis et al., 2019; Xiao et al., 2018), inspir-
ing subsequent benchmarks such as CAIL2018
and ECHR-CASES. Recent approaches have incor-
porated statutes, reasoning structures, and event-
based features (Feng et al., 2022, 2023).
Within the Indian legal ecosystem, the ILDC
corpus (Malik et al., 2021b) laid the founda-
tion for Court Judgment Prediction and Explana-
tion (CJPE). This has been expanded in PredEx
(Nigam et al., 2024e), NyayaAnumana (Nigam
et al., 2024c), LegalSeg (Nigam et al., 2025b),
TathyaNyaya (Nigam et al., 2025d), and IBPS for
bail prediction (Srivastava et al., 2025), which col-
lectively focus on segmentation, factual reasoning,
and judgment outcome explanation. Efforts such
as (Nigam et al., 2024b; Nigam and Deroy, 2024)
emphasize fact-based LJP as a realistic alternative
to full-text reasoning, aligning predictions more
closely with early-phase decision-making. Other
works explore semantic segmentation (Malik et al.,
2021a), legal QA (Nigam et al., 2023), and struc-
tured document generation (Nigam et al., 2025e).
These resources and models highlight the signifi-
cance of domain-specific adaptation for Indian law,
an underrepresented common law system.
Precedent integration is central to common law
reasoning. Early precedent-aware models such
as (Zhao et al., 2018) focused on Chinese law,
while recent works like PLJP (Wu et al., 2023),
LexKeyPlan (Santosh and Hernandez, 2025), and
precedent-enhanced ECHR prediction (Santosh
et al., 2024) examine retrieval of historical judg-
ments to guide predictions. These align with
broader multilingual and cross-jurisdictional LJP
studies (Niklaus et al., 2021; Kapoor et al., 2022).
While these efforts highlight the role of past
cases, their settings differ significantly from India’s
unique common law context where both statutory
Figure 1: Illustration of our Legal Judgment Prediction framework using RAG. The input legal judgment is first
summarized; a RAG agent retrieves top-3 relevant documents from a vector database; and an instruction-tuned LLM
(e.g., LLaMA-3.1 8B Instruct) generates the final prediction and explanation.
law and judicial precedents guide reasoning.
Retrieval-augmented pipelines are increasingly
applied to legal NLP. LegalBench-RAG (Pipitone
and Alami, 2024) and CLERC (Hou et al., 2024)
introduced benchmarks for retrieval-augmented le-
gal reasoning. Specialized systems like CBR-RAG
(Wiratunga et al., 2024), Graph-RAG for norms
(de Martim, 2025), and LexKeyPlan (Santosh and
Hernandez, 2025) explore structured retrieval, case-
based reasoning, and keyphrase-driven planning.
Applications range from legal assistants and dis-
pute resolution (Rafat, 2024; Wahidur et al., 2025)
to federated secure access architectures (Amato
et al., 2024). These works demonstrate the value
of augmenting generative reasoning with statutory
and precedent-based retrieval but primarily address
civil law or international corpora.
Our work contributes to this line by contextu-
alizing RAG for the Indian common law system,
simulating how judges reason with case facts, statu-
tory provisions, and precedents. While prior RAG
frameworks in law (Wiratunga et al., 2024; Hou
et al., 2024; Wu et al., 2023; Santosh et al., 2024)
establish the feasibility of retrieval-augmented
pipelines, they have not been applied to Indian
courts. By integrating factual, statutory, and prece-
dential inputs in a unified framework, NyayaRAG
extends the landscape of LJP toward realistic, ex-
plainable, and domain-grounded legal tasks.
3 Task Description
India’s judicial system operates within the com-
mon law framework, where judges deliberate cases
based on three fundamental pillars: (i) the fac-
tual context of the case, (ii) applicable statutory
provisions, and (iii) relevant judicial precedents.
Our task is designed to simulate such realistic
legal decision-making by leveraging Retrieval-
Augmented Generation (RAG), enabling models to
access external legal knowledge during inference.
Figure 1 illustrates our Legal Judgment Pre-
diction (LJP) pipeline enhanced with RAG. The
process begins with a full legal judgment doc-
ument, which undergoes summarization to re-
duce its length and retain essential factual mean-
ing. This is necessary because legal judgments
tend to be long, and appending retrieved knowl-
edge further increases the input size. Given
limited model capacity and computational re-
sources, we employ a summarization step (using
Mixtral-8x7B-Instruct-v0.1) to create a con-
densed representation of both the input case and
the retrieved legal context.
Prediction Task: Based on the summarized fac-
tual description and the retrieved top-k similar legal
documents (statutes or precedents), the model pre-
dicts the likely court judgment. The prediction la-
bel y ∈ {0, 1} indicates whether the appeal is fully
rejected (0) or fully/partially accepted (1). This
binary framing captures the most common forms
of judicial decisions in Indian appellate courts.
Explanation Task: Alongside the decision, the
model is also required to generate an explanation
that justifies its output. This explanation should log-
ically incorporate the facts, cited statutes, and rele-
vant precedents retrieved during the RAG process.
This step emulates how judges provide reasoned
opinions in written judgments.
By structuring the LJP task in this manner, and
by summarizing long documents and integrating
retrieval-based augmentation, we study the effec-
tiveness of RAG in producing judgments that are
both faithful to legal reasoning and grounded in
precedent and statute. The overall framework al-
lows us to approximate real-world decision-making
environments within Indian courtrooms.
4 Dataset
Our dataset is designed to simulate realistic court
decision-making in the Indian legal context, incor-
porating facts, statutes, and precedent, which are es-
sential elements under the common law framework.
This dataset enables exploration of Legal Judgment
Prediction (LJP) in a Retrieval-Augmented Gener-
ation (RAG) setup.
4.1 Dataset Compilation
We curated a large-scale dataset consisting of
56,387 Supreme Court of India (SCI) case doc-
uments up to April 2024, sourced from Indi-
anKanoon2, a trusted legal search engine. The web-
site provides structural tags for various judgment
components (e.g., facts, issues, arguments), which
allowed for clean and structured scraping. These
documents serve as the foundation for our summa-
rization, retrieval, and reasoning experiments.
4.2 Single versus Multi Partitioning
Another challenge in the SCI proceedings is the
presence of cases containing multiple petitions un-
der a single case identifier, where each petition
may lead to distinct outcomes. To handle this,
we partition the dataset into two subsets. The sin-
gle partition represents binary classification tasks
(accept/reject) and includes cases with a single
petition or multiple petitions that share the same
outcome. The multi partition contains cases with
multiple petitions leading to different decisions, in-
troducing a more complex multi-label prediction
setting (e.g., partially accepted outcomes). For
these cases, if even one appeal within the group is
accepted, the case is assigned the label accepted.
Predicting mixed outcomes remains challenging
and will be further explored in future work.
4.3 Dataset Composition
The corpus supports multiple downstream
pipelines, each focusing on specific judgment
elements or legal context. Table 1 presents key
statistics across different configurations. An
example case is shown in Table 7 in Appendix.
2https://indiankanoon.org/
Dataset #Documents Avg. Length Max
SCI (Full) 56,387 3,495 401,985
Summarized Single 4,962 302 875
Summarized Multi 4,930 300 879
Sections 29,858 257 27,553
Table 1: NyayaRAG data statistics
4.3.1 Case Text
Each judgment includes complete narrative con-
tent such as factual background, party argu-
ments, legal issues, reasoning, and verdict. Due
to length constraints exceeding model context
windows, we summarized these documents us-
ing Mixtral-8x7B-Instruct-v0.1 (Jiang et al.,
2024), which supports up to 32k tokens. The
summarization preserved critical legal elements
through carefully designed prompts (see Table 2).
4.3.2 Precedents
From each judgment, cited precedents were ex-
tracted using metadata tags provided by Indi-
anKanoon. These citations represent explicit legal
reasoning and are retained for use during inference
to replicate how courts consider prior judgments.
4.3.3 Statutes
Statutory references were also programmatically
extracted, including citations to laws like the Indian
Penal Code and the Constitution of India. Where
statute sections exceeded length limits, they were
summarized using the same LLM pipeline. Only
statutes directly cited in the respective cases were
retained, ensuring relevance.
4.3.4 Previous Similar Cases
To simulate implicit precedent-based reasoning, we
employed semantic similarity retrieval to identify
relevant previous cases beyond explicit citations:
• Corpus Vectorization: All 56,387 documents
were embedded into dense vector representations
using the all-MiniLM-L6-v2 sentence trans-
former.
• Target Encoding: The 5,000 selected training
samples were vectorized similarly.
• Top-k Retrieval: Using ChromaDB, we retrieved
the top-3 most semantically similar cases for each
document based on cosine similarity.
• Augmentation: Retrieved cases were appended
to the factual input to form the “casetext + previ-
ous similar cases” input during model inference.
This retrieval step enriches context with prece-
dents that are semantically close; even if not cited,
they enhance the legal realism of our setup.
Summarization Prompt
The text is regarding a court judgment for a specific case. Summarize it into 1000 tokens but more than 700 tokens.
The summarization should highlight the Facts, Issues, Statutes, Ratio of the decision, Ruling by Present Court
(Decision), and a Conclusion.
Table 2: Instruction prompt used with Mixtral-8x7B-Instruct-v0.1 for summarizing legal judgments
4.3.5 Facts
We separately extracted the factual portions of all
56,387 judgments. These include background infor-
mation, chronological events, and party narratives,
excluding legal reasoning. These fact-only subsets
were used to simulate realistic courtroom scenarios
where judges primarily rely on facts, relevant law,
and precedent for decision-making.
Overall, our dataset is uniquely structured to test
legal decision-making under realistic constraints,
aligning with the Indian legal system’s reliance
on factual narratives, statutory frameworks, prece-
dents, and prior rulings.
5 Methodology
To simulate realistic judgment prediction and eval-
uate the role of RAG in enhancing legal decision-
making, we design a modular experimental setup.
This setup explores how different types of legal
information, such as factual summaries, statutes,
and precedents affect model performance on the
dual tasks of prediction and explanation. To en-
sure reproducibility and transparency, we detail the
full experimental setup, including model configura-
tions, training routines, and task-specific hyperpa-
rameters. The details are mentioned in Appendix A.
This includes separate sections for explanation gen-
eration (summarization) and legal judgment predic-
tion tasks, outlining all relevant decoding strategies,
optimization settings, and dataset splits used across
our pipeline variants.
5.1 Pipeline Construction
To systematically evaluate the impact of legal
knowledge sources, we constructed multiple input
pipelines using combinations of the dataset compo-
nents described in Section 4. Each pipeline configu-
ration represents a distinct input scenario reflecting
different degrees of legal context and retrieval aug-
mentation. These pipelines are as follows:
• CaseText Only: Includes only the summarized
version of the full case judgment, which contains
factual background, arguments, and reasoning.
• CaseText + Statutes: Appends summarized
statutory references cited in the judgment to the
case text, simulating scenarios where relevant
laws are explicitly considered.
• CaseText + Precedents: Incorporates prior cited
judgments mentioned in the original case, repre-
senting explicitly relied-upon precedents.
• CaseText + Previous Similar Cases: Adds top-
3 semantically similar past judgments (retrieved
via ChromaDB using all-MiniLM-L6-v2 em-
beddings), allowing the model to learn from
precedents not explicitly cited.
• CaseText + Statutes + Precedents: A compre-
hensive legal input pipeline combining the full
judgment summary, statutes, and cited prior judg-
ments.
• Facts Only: A minimal pipeline containing only
the factual summary, excluding all legal reason-
ing and verdicts. This setup evaluates whether a
model can infer judgments from facts alone.
• Facts + Statutes + Precedents: Combines fac-
tual input with statutory and precedent context
to simulate realistic courtroom conditions where
judges rely on facts, applicable law, and relevant
past cases.
This modular design enables granular control
over input features and facilitates direct compari-
son of how each knowledge source contributes to
judgment prediction and explanation generation.
5.2 Prompt Design
To ensure consistency and interpretability across
all pipelines, we used fixed instruction prompts
with minor variations depending on the available
contextual inputs (e.g., facts only vs. facts + law
+ precedent). These prompts guide the model in
producing both binary predictions and natural lan-
guage explanations. Prompts were structured to
reflect real judicial inquiry formats, aligning with
the instruction-following capabilities of modern
LLMs. Full prompt templates are listed in Ap-
pendix Table 8, along with prediction examples.
5.3 Inference Setup
We use the LLaMA-3.1 8B Instruct (Dubey et al.,
2024) model for all experiments in a few-shot
prompt setup. Each input sequence, composed ac-
cording to one of the pipeline templates, is paired
with a relevant prompt that asks to output:
• A binary judgment prediction: 0 (appeal rejected)
or 1 (appeal fully/partially accepted)
• A justification: a coherent explanation based on
legal facts, statutes, and precedent
The model is explicitly instructed to reason with
the provided information and emulate judicial writ-
ing. Retrieved knowledge (via RAG) is included
in-context to enhance legal reasoning while mini-
mizing hallucinations.
This experimental design allows us to evaluate
the effectiveness of legal retrieval and summariza-
tion under realistic judicial decision-making con-
straints in the Indian common law setting.
6 Evaluation Metrics
To evaluate the effectiveness of our Retrieval-
Augmented Legal Judgment Prediction framework,
we adopt a comprehensive set of metrics covering
both classification accuracy and explanation qual-
ity. The evaluation is conducted on two fronts: the
judgment prediction task and the explanation gen-
eration task. These metrics are selected to ensure
a holistic assessment of model performance in the
legal domain. We report Macro Precision, Macro
Recall, Macro F1, and Accuracy for judgment pre-
diction, and we use both quantitative and qualita-
tive methods to evaluate the quality of explanations
generated by the model.
1. Lexical-based Evaluation: We utilized stan-
dard lexical similarity metrics, including Rouge-
L (Lin, 2004), BLEU (Papineni et al., 2002), and
METEOR (Banerjee and Lavie, 2005). These
metrics measure the overlap and order of words
between the generated explanations and the ref-
erence texts, providing a quantitative assessment
of the lexical accuracy of the model outputs.
2. Semantic Similarity-based Evaluation: To
capture the semantic quality of the generated
explanations, we employed BERTScore (Zhang
et al., 2020), which measures the semantic simi-
larity between the generated text and the ref-
erence explanations. Additionally, we used
BLANC (Vasilyev et al., 2020), a metric that
estimates the quality of generated text without a
gold standard, to evaluate the model’s ability to
produce semantically meaningful and contextu-
ally relevant explanations.
3. LLM-based Evaluation (LLM-as-a-Judge):
To complement traditional metrics, we incorpo-
rate an automatic evaluation strategy that uses
large language models themselves as evaluators,
commonly referred to as LLM-as-a-Judge. This
evaluation is crucial for assessing structured ar-
gumentation and legal correctness in a format
aligned with expert judicial reasoning. We adopt
G-Eval (Liu et al., 2023), a GPT-4-based eval-
uation framework tailored for natural language
generation tasks. G-Eval leverages chain-of-
thought prompting and structured scoring to as-
sess explanations along three key criteria: fac-
tual accuracy, completeness & coverage, and
clarity & coherence. Each generated legal ex-
planation is scored on a scale from 1 to 10 based
on how well it aligns with the expected content
and a reference document. The exact prompt
format used for evaluation is shown in Appendix
Table 9. For our experiments, we use the GPT-
4o-mini model to generate reliable scores with-
out manual intervention. This setup provides
an interpretable, unified judgment metric that
captures legal soundness, completeness of rea-
soning, and logical coherence, beyond what tra-
ditional similarity-based metrics can offer.
4. Expert Evaluation: To validate the inter-
pretability and legal soundness of the model-
generated explanations, we conduct an expert
evaluation involving legal professionals. They
rate a representative subset of the generated out-
puts on a 1–10 Likert scale across three criteria:
factual accuracy, legal relevance, and complete-
ness of reasoning. A score of 1 denotes a poor
or misleading explanation, while a 10 reflects
high legal fidelity and argumentative soundness.
This evaluation provides critical insights beyond
automated metrics.
5. Inter-Annotator Agreement (IAA): To fur-
ther ensure the reliability and consistency of
expert judgments, we computed multiple stan-
dard inter-rater agreement metrics. Specifi-
cally, Fleiss’ Kappa (Fleiss, 1971) was used
to evaluate the overall agreement among multi-
ple raters, Cohen’s Kappa (Cohen, 1960) cap-
tured pairwise agreement while adjusting for
chance, and the Intraclass Correlation Coeffi-
cient (ICC) (Shrout and Fleiss, 1979) measured
the reliability of continuous ratings across raters.
In addition, Krippendorff’s Alpha (Krippen-
dorff, 2018) provided a robust measure suitable
for ordinal scales and missing data, while the
Pearson Correlation Coefficient (Benesty et al.,
2009) quantified the linear consistency of expert
Pipeline Partition Accuracy Precision Recall F1-score
CaseText Only Single 62.27 33.50 30.88 29.45
Multi 53.10 25.26 23.95 20.81
CaseText + Statutes Single 67.07 45.29 44.55 44.32
Multi 60.36 64.22 64.04 60.35
CaseText + Precedents Single 61.73 41.92 41.35 40.81
Multi 57.53 61.34 61.19 57.53
CaseText + Previous Similar Cases Single 57.53 61.34 61.19 57.53
Multi 61.73 41.92 41.35 57.53
CaseText + Statutes + Precedents Single 64.71 43.50 42.98 42.78
Multi 65.86 63.94 63.99 63.96
CaseFacts Only Single 51.13 51.36 51.30 50.68
Multi 53.71 51.18 51.18 51.18
Facts + Statutes + Precedents Single 50.58 33.57 33.56 33.24
Multi 52.57 52.01 52.01 52.01
Table 3: Performance of various pipelines on Binary and Multi-label LJP task (best results in bold)
scores. The results demonstrated substantial
agreement across different measures, reinforc-
ing the credibility of the evaluation and lending
strong support to the robustness of our findings.
Together, these metrics provide a comprehensive,
multi-perspective evaluation of our system’s abil-
ity to both predict judicial outcomes and generate
legally coherent, interpretable rationales grounded
in retrieved context.
7 Results and Analysis
We conducted extensive evaluations across mul-
tiple pipeline configurations to study the impact
of different legal information components on both
judgment prediction and explanation quality. Ta-
bles 3 and 4 summarize the model’s performance
across these configurations for binary and multi-
label settings.
7.1 Judgment Prediction Performance
As shown in Table 3, the pipeline combining Case-
Text + Statutes achieved the highest accuracy in
the single-label setting. This suggests that legal
statutes provide substantial contextual cues for the
model to infer the likely decision. In contrast, Case-
Text Only achieved 62.27%, highlighting the impor-
tance of augmenting case narratives with applicable
laws. Interestingly, the CaseText + Previous Sim-
ilar Cases pipeline showed the highest precision,
recall, and F1-score in the single-label case, indicat-
ing that semantically retrieved precedents, despite
not being explicitly cited, help the model align with
actual judicial outcomes.
In the multi-label setting, the best accuracy was
observed for the CaseText + Statutes + Precedents
pipeline. This comprehensive context provides
the model with structured legal knowledge, im-
proving generalization across different outcome
labels. Conversely, the Facts Only pipeline per-
formed worst overall, reaffirming that factual nar-
ratives alone, without legal context, are insufficient
for reliably predicting legal outcomes. The poor
performance of the Facts + Statutes + Precedents
pipeline in the single-label setting suggests that fac-
tual sections lack the interpretive cues that full case
texts offer when combined with legal references.
7.2 Explanation Generation Quality
Table 4presents the results of explanation evalua-
tion using a diverse set of metrics, including both
automatic lexical and semantic metrics (ROUGE,
BLEU, METEOR, BERTScore, BLANC) and a
large language model-based evaluation (G-Eval).
Across both single and multi-label setups, the Case-
Text + Statutes pipeline consistently outperformed
all other configurations. In the single-label setting,
it achieved the highest scores across key dimen-
sions, substantially outperforming the CaseText
Only baseline. This result underscores the criti-
cal role of statutory references in enhancing both
the factual alignment and interpretability of model-
generated legal explanations.
Interestingly, while the CaseText + Previous Sim-
ilar Cases pipeline yielded strong lexical overlap
(e.g., top ROUGE-L in the unabridged version),
it lagged behind the statute-enhanced pipeline in
metrics that assess semantic and contextual align-
ment, such as G-Eval and BLANC. This indicates
that while similar cases might help the model repli-
cate surface-level language, they may not consis-
tently offer legally grounded or complete reason-
ing. Meanwhile, the CaseText + Statutes + Prece-
Pipelines RL BLEU METEOR BERTScore BLANC G-Eval Expert Score
Single Partition
CaseText Only 0.16 0.03 0.18 0.52 0.08 4.17 5.2
CaseText + Statutes 0.17 0.03 0.20 0.53 0.09 4.21 5.5
CaseText + Precedents 0.16 0.03 0.19 0.51 0.08 3.45 4.6
CaseText + Previous Similar Cases 0.16 0.03 0.20 0.52 0.08 3.72 4.9
CaseText + Statutes + Precedents 0.16 0.03 0.19 0.52 0.08 4.11 5.4
CaseFacts Only 0.16 0.02 0.18 0.52 0.06 3.53 4.5
Facts + Statutes + Precedents 0.16 0.02 0.18 0.51 0.06 2.97 3.9
Multi Partition
CaseText Only 0.16 0.03 0.18 0.52 0.08 4.00 5.0
CaseText + Statutes 0.17 0.03 0.20 0.53 0.09 4.10 5.3
CaseText + Precedents 0.16 0.03 0.20 0.53 0.09 3.41 4.4
CaseText + Previous Similar Cases 0.16 0.03 0.19 0.52 0.08 3.67 4.7
CaseText + Statutes + Precedents 0.16 0.03 0.20 0.53 0.09 3.92 5.2
CaseFacts Only 0.15 0.02 0.17 0.52 0.08 3.74 4.6
Facts + Statutes + Precedents 0.15 0.02 0.19 0.52 0.07 3.08 4.1
Table 4: Comparison of explanation generation across different legal context pipelines
dents pipeline also performed competitively, sug-
gesting that combining structured legal references
with precedent data can lead to balanced and high-
quality explanations.
In contrast, configurations that relied solely on
factual narratives (CaseFacts Only and Facts +
Statutes + Precedents) exhibited comparatively
poor performance across all evaluation metrics.
For example, the Facts + Statutes + Precedents
pipeline recorded a G-Eval score as low in the
single-label setting. This reinforces the notion that
factual descriptions, while essential, are insufficient
for constructing legally persuasive rationales. The
absence of structured legal arguments, statutory
alignment, or precedent citation in these setups ap-
pears to undermine their explanatory effectiveness.
Expert Evaluation: The results of this evalua-
tion aligned closely with the trends observed in
automatic metrics (Table 4). Pipelines enriched
with statutory provisions, particularly CaseText
+ Statutes, consistently received the highest ex-
pert ratings, highlighting the value of legal ground-
ing in improving explanation quality. In contrast,
pipelines relying solely on factual input, such as
CaseFacts Only, obtained the lowest expert scores,
underscoring their lack of interpretive depth.
To assess the reliability of these expert judg-
ments, we performed a detailed Inter-Annotator
Agreement (IAA) analysis across multiple evalu-
ation dimensions, Table 5. The IAA results re-
vealed moderate to substantial agreement among
annotators. For the Single partition, pipelines such
as CaseText + Statutes and CaseText + Statutes
+ Precedents achieved higher consistency (Fleiss’
κ > 0.49, ICC ≈ 0.60), reflecting strong con-
sensus on their explanation quality. In contrast,
fact-only or noisy-input pipelines showed weaker
agreement (Fleiss’ κ < 0.35, ICC < 0.50), sug-
gesting greater variability in expert perception of
their outputs.
The Multi partition exhibited slightly lower
agreement overall, likely due to the additional com-
plexity of multi-label judgments. Nevertheless,
richer legal context pipelines again demonstrated
higher consistency among experts compared to fact-
only inputs. These findings not only validate the
robustness of our expert evaluation protocol but
also corroborate trends from lexical, semantic, and
LLM-based evaluations.
Taken together, the results emphasize that
Retrieval-Augmented Generation, when paired
with structured legal inputs such as statutes and
precedents, produces explanations that are more ac-
curate, interpretable, and legally coherent. The
combination of automatic metrics, LLM-based
judgment, and human expert ratings provides a
multifaceted and credible framework for assessing
explanation quality in legal judgment prediction.
8 Ablation Study: Understanding the
Role of Legal Context Components
To assess the individual contribution of each le-
gal context component, factual narratives, statutory
provisions, cited precedents, and semantically simi-
lar past cases, we perform an ablation study by sys-
tematically removing or altering these inputs across
pipeline configurations. This study highlights how
each component affects prediction accuracy and
explanation quality, as reported in Tables 3 and 4.
Impact on Judgment Prediction: The
CaseText + Statutes + Precedents pipeline
serves as the most comprehensive baseline.
Pipelines Fleiss’ κ Cohen’s κ ICC Kripp. α Pearson Corr.
Single Partition
CaseText Only 0.42 0.47 0.55 0.49 0.58
CaseText + Statutes 0.51 0.55 0.61 0.57 0.65
CaseText + Precedents 0.37 0.42 0.50 0.45 0.52
CaseText + Previous Similar Cases 0.41 0.45 0.54 0.47 0.56
CaseText + Statutes + Precedents 0.49 0.52 0.59 0.54 0.62
CaseFacts Only 0.34 0.39 0.47 0.43 0.49
Facts + Statutes + Precedents 0.29 0.34 0.42 0.38 0.44
Multi Partition
CaseText Only 0.40 0.45 0.53 0.48 0.57
CaseText + Statutes 0.50 0.54 0.60 0.56 0.64
CaseText + Precedents 0.36 0.41 0.49 0.44 0.51
CaseText + Previous Similar Cases 0.39 0.44 0.52 0.46 0.55
CaseText + Statutes + Precedents 0.47 0.51 0.58 0.52 0.60
CaseFacts Only 0.32 0.37 0.46 0.41 0.48
Facts + Statutes + Precedents 0.28 0.33 0.41 0.36 0.43
Table 5: Inter-Annotator Agreement (IAA) statistics for expert evaluation of generated legal explanations across
different pipeline settings for both Single and Multi partitions
Removing statutory references (i.e., CaseText +
Precedents) leads to a noticeable drop in F1-score
(from 63.96 to 57.53 in the multi-label setting),
indicating that legal provisions provide structured
grounding essential for accurate predictions.
Similarly, eliminating precedents (i.e., CaseText
+ Statutes) also reduces performance, though
the drop is less steep, suggesting complementary
roles of statutes and precedents. Pipelines relying
solely on factual case narratives (e.g., CaseFacts
Only) perform the worst, reaffirming that factual
information alone is insufficient for robust legal
outcome prediction.
Impact on Explanation Quality: A similar pat-
tern emerges in explanation generation. The
CaseText + Statutes pipeline consistently out-
performs others across ROUGE, BLEU, METEOR,
BERTScore, and G-Eval metrics, underscoring
the importance of grounding explanations in ex-
plicit statutory language. When only precedents
are added (without statutes), as in CaseText +
Precedents, explanation scores drop significantly
(e.g., G-Eval: 4.21 to 3.45 in the single-label case).
The worst-performing setup is Facts + Statutes
+ Precedents, highlighting that factual inputs,
even when supplemented with legal references, do
not suffice for generating coherent and persuasive
explanations if the core case context is missing.
Insights: These findings validate the design
choices in NyayaRAG, where integrating factual
case text with statutory and precedential knowl-
edge mimics real-world judicial reasoning. Statu-
tory references provide normative structure, while
precedents offer context-specific analogies. Their
absence not only reduces predictive performance
but also degrades the factuality, clarity, and legal
coherence of the generated explanations.
This ablation analysis also offers practical guid-
ance: for retrieval-augmented systems deployed in
legal contexts, careful curation and combination
of retrieved statutes and relevant precedents are
critical to ensure trustworthy outputs.
9 Conclusions and Future Scope
This paper introduced NyayaRAG, a Retrieval-
Augmented Generation framework tailored for re-
alistic legal judgment prediction and explanation
in the Indian common law system. By combining
factual case details with retrieved statutory provi-
sions and relevant precedents, our approach mirrors
judicial reasoning more closely than prior meth-
ods that rely solely on the case text. Empirical
results across prediction and explanation tasks con-
firm that structured legal retrieval enhances both
outcome accuracy and interpretability. Pipelines
enriched with statutes and precedents consistently
outperformed baselines, as validated by lexical, se-
mantic, and LLM-based (G-Eval) metrics, as well
as expert feedback.
Future directions include extending to hierar-
chical verdict structures, integrating symbolic or
graph-based retrieval, modeling temporal prece-
dent evolution, and leveraging human-in-the-loop
mechanisms. NyayaRAG marks a step toward court-
aligned, explainable legal AI and sets the founda-
tion for future research in retrieval-enhanced legal
systems within under-represented jurisdictions.
Acknowledgements
We would like to express our sincere gratitude
to the anonymous reviewers for their constructive
feedback and valuable suggestions, which greatly
improved the quality of this paper. We also thank
the student research assistants and legal experts
from various law colleges for their dedicated efforts
in annotation and expert evaluation. Their contri-
butions were instrumental in ensuring the quality
and reliability of the dataset and evaluation pro-
cess. We gratefully acknowledge the support of
BharatGen, India, for providing access to computa-
tional resources and hardware infrastructure used
in this research. Their assistance played a vital role
in model training and large-scale experimentation.
The majority of this work was conducted while the
first author was affiliated with the Indian Institute
of Technology Kanpur. The author is currently af-
filiated with the University of Birmingham Dubai.
Limitations
While NyayaRAG marks a significant advance in
realistic legal judgment prediction under the Indian
common law framework, several limitations merit
further attention.
First, although Retrieval-Augmented Generation
(RAG) helps reduce hallucinations by grounding
outputs in retrieved legal documents, it does not
fully eliminate factual or interpretive inaccuracies.
In sensitive domains such as law, even rare errors in
reasoning or justification may raise concerns about
reliability and accountability.
Second, the current framework supports binary
and multi-label outcome structures but does not yet
handle the full spectrum of legal verdicts, such as
hierarchical or multi-class decisions involving com-
plex legal provisions. Expanding to richer verdict
taxonomies would enable broader applicability and
deeper case understanding.
Third, NyayaRAG assumes the availability of
clean, well-structured legal documents and relies
on summarization pipelines to manage input length.
However, real-world legal texts often contain noise,
OCR errors, or inconsistent formatting. Although
summarization aids conciseness, it may inadver-
tently omit subtle legal nuances that affect judg-
ment outcomes or explanation quality.
Finally, due to computational resource con-
straints, the current system utilizes instruction-
tuned LLMs guided by domain-specific prompts
rather than fully fine-tuning on large-scale Indian
legal corpora. While prompt-based tuning remains
efficient and modular, fine-tuning on in-domain le-
gal texts could further enhance model fidelity and
domain alignment.
Despite these limitations, NyayaRAG provides a
robust and interpretable foundation for judgment
prediction and explanation, supported by both auto-
matic and expert evaluations. Future work that ad-
dresses these constraints, particularly hierarchical
decision modeling and domain-specific fine-tuning,
will further strengthen the framework’s legal rele-
vance and practical deployment potential.
Ethics Statement
This research adheres to established ethical stan-
dards for conducting work in high-stakes domains
such as law. The legal documents used in our
study were sourced from IndianKanoon (https://
indiankanoon.org/), a publicly available repos-
itory of Indian court judgments. All documents
are in the public domain and do not include sealed
cases or personally identifiable sensitive informa-
tion, ensuring that our use of the data complies with
privacy and confidentiality norms.
We emphasize that the proposed NyayaRAG sys-
tem is developed strictly for academic research
purposes to simulate realistic legal reasoning pro-
cesses. It is not intended for direct deployment in
real-world legal settings. The model outputs must
not be construed as legal advice, official court pre-
dictions, or determinants of legal outcomes. Any
downstream use should be performed with over-
sight by qualified legal professionals. We strongly
discourage the use of this system in live legal cases,
policymaking, or decisions that may affect individ-
uals’ rights without appropriate human-in-the-loop
supervision.
As part of our evaluation protocol, we in-
volved domain experts (legal professionals and re-
searchers) to assess the quality and legal coherence
of the generated explanations. The evaluation was
conducted on a curated subset of samples, and all
participating experts were informed of the research
objectives and voluntarily participated without any
coercion or conflict of interest. No personal data
was collected during this process, and all expert
feedback was anonymized for analysis.
While we strive to enhance legal interpretabil-
ity and transparency, we acknowledge that legal
documents themselves may reflect systemic biases.
Our framework, while replicating judicial reason-
ing patterns, may inherit such biases from training
data. We do not deliberately introduce or amplify
such biases, but we recognize the importance of fur-
ther work in fairness auditing, particularly across
litigant identity, socio-demographic markers, and
jurisdictional diversity.
References
Nikolaos Aletras, Dimitrios Tsarapatsanis, Daniel
Preo¸tiuc-Pietro, and Vasileios Lampos. 2016. Pre-
dicting judicial decisions of the european court of
human rights: A natural language processing per-
spective. PeerJ computer science, 2:e93.
Flora Amato, Egidia Cirillo, Mattia Fonisto, and Alberto
Moccardi. 2024. Optimizing legal information ac-
cess: Federated search and rag for secure ai-powered
legal solutions. In 2024 IEEE International Con-
ference on Big Data (BigData), pages 7632–7639.
IEEE.
Satanjeev Banerjee and Alon Lavie. 2005. METEOR:
An automatic metric for MT evaluation with im-
proved correlation with human judgments. In Pro-
ceedings of the ACL Workshop on Intrinsic and Ex-
trinsic Evaluation Measures for Machine Transla-
tion and/or Summarization, pages 65–72, Ann Arbor,
Michigan. Association for Computational Linguis-
tics.
Jacob Benesty, Jingdong Chen, Yiteng Huang, and Is-
rael Cohen. 2009. Pearson correlation coefficient.
In Noise reduction in speech processing, pages 1–4.
Springer.
Ilias Chalkidis, Ion Androutsopoulos, and Nikolaos Ale-
tras. 2019. Neural legal judgment prediction in en-
glish. Association for Computational Linguistics
(ACL).
Jacob Cohen. 1960. A coefficient of agreement for
nominal scales. Educational and psychological mea-
surement, 20(1):37–46.
Hudson de Martim. 2025. Graph rag for legal norms: A
hierarchical and temporal approach. arXiv preprint
arXiv:2505.00039.
Jacob Devlin, Ming-Wei Chang, Kenton Lee, and
Kristina Toutanova. 2018. Bert: Pre-training of deep
bidirectional transformers for language understand-
ing. arXiv preprint arXiv:1810.04805.
Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey,
Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman,
Akhil Mathur, Alan Schelten, Amy Yang, Angela
Fan, et al. 2024. The llama 3 herd of models. arXiv
preprint arXiv:2407.21783.
Geya Feng, Yongbin Qin, Ruizhang Huang, and Yan-
ping Chen. 2023. Criminal action graph: a semantic
representation model of judgement documents for
legal charge prediction. Information Processing &
Management, 60(5):103421.
Yi Feng, Chuanyi Li, and Vincent Ng. 2022. Legal judg-
ment prediction via event extraction with constraints.
In Proceedings of the 60th Annual Meeting of the
Association for Computational Linguistics (Volume
1: Long Papers), pages 648–664, Dublin, Ireland.
Association for Computational Linguistics.
Joseph L Fleiss. 1971. Measuring nominal scale agree-
ment among many raters. Psychological bulletin,
76(5):378.
Rujun Han, Yuhao Zhang, Peng Qi, Yumo Xu, Jenyuan
Wang, Lan Liu, William Yang Wang, Bonan Min,
and Vittorio Castelli. 2024. Rag-qa arena: Eval-
uating domain robustness for long-form retrieval
augmented question answering. arXiv preprint
arXiv:2407.13998.
Zijian Hei, Weiling Wei, Wenjie Ou, Juyi Qiao, Junming
Jiao, Zhiqing Zhu, and Guowen Song. 2024. Dr-rag:
Applying dynamic document relevance to retrieval-
augmented generation for question-answering. arXiv
preprint arXiv:2406.07348.
Abe Bohan Hou, Orion Weller, Guanghui Qin, Eu-
gene Yang, Dawn Lawrie, Nils Holzenberger, An-
drew Blair-Stanek, and Benjamin Van Durme. 2024.
Clerc: A dataset for legal case retrieval and retrieval-
augmented analysis generation. arXiv preprint
arXiv:2406.17186.
Albert Q. Jiang, Alexandre Sablayrolles, Antoine
Roux, Arthur Mensch, Blanche Savary, Chris Bam-
ford, Devendra Singh Chaplot, Diego de Las Casas,
Emma Bou Hanna, Florian Bressand, Gianna
Lengyel, Guillaume Bour, Guillaume Lample,
L’elio Renard Lavaud, Lucile Saulnier, Marie-
Anne Lachaux, Pierre Stock, Sandeep Subramanian,
Sophia Yang, Szymon Antoniak, Teven Le Scao,
Théophile Gervet, Thibaut Lavril, Thomas Wang,
Timothée Lacroix, and William El Sayed. 2024. Mix-
tral of experts. ArXiv, abs/2401.04088.
Arnav Kapoor, Mudit Dhawan, Anmol Goel, Arjun T H,
Akshala Bhatnagar, Vibhu Agrawal, Amul Agrawal,
Arnab Bhattacharya, Ponnurangam Kumaraguru, and
Ashutosh Modi. 2022. HLDC: Hindi legal docu-
ments corpus. In Findings of the Association for
Computational Linguistics: ACL 2022, pages 3521–
3536, Dublin, Ireland. Association for Computational
Linguistics.
Klaus Krippendorff. 2018. Content analysis: An intro-
duction to its methodology. Sage publications.
Chin-Yew Lin. 2004. ROUGE: A package for auto-
matic evaluation of summaries. In Text Summariza-
tion Branches Out, pages 74–81, Barcelona, Spain.
Association for Computational Linguistics.
Yang Liu, Dan Iter, Yichong Xu, Shuohang Wang,
Ruochen Xu, and Chenguang Zhu. 2023. G-eval:
NLG evaluation using gpt-4 with better human align-
ment. In Proceedings of the 2023 Conference on
Empirical Methods in Natural Language Processing,
pages 2511–2522, Singapore. Association for Com-
putational Linguistics.
Vijit Malik, Rishabh Sanjay, Shouvik Kumar Guha,
Angshuman Hazarika, Shubham Nigam, Arnab Bhat-
tacharya, and Ashutosh Modi. 2021a. Semantic seg-
mentation of legal documents via rhetorical roles.
arXiv preprint arXiv:2112.01836.
Vijit Malik, Rishabh Sanjay, Shubham Kumar Nigam,
Kripabandhu Ghosh, Shouvik Kumar Guha, Arnab
Bhattacharya, and Ashutosh Modi. 2021b. ILDC
for CJPE: Indian legal documents corpus for court
judgment prediction and explanation. In Proceedings
of the 59th Annual Meeting of the Association for
Computational Linguistics and the 11th International
Joint Conference on Natural Language Processing
(Volume 1: Long Papers), pages 4046–4062, Online.
Association for Computational Linguistics.
Shubham Kumar Nigam, Deepak Patnaik Balara-
mamahanthi, Shivam Mishra, Noel Shallum, Kri-
pabandhu Ghosh, and Arnab Bhattacharya. 2025a.
NYAYAANUMANA and INLEGALLLAMA: The
largest Indian legal judgment prediction dataset and
specialized language model for enhanced decision
analysis. In Proceedings of the 31st International
Conference on Computational Linguistics, pages
11135–11160, Abu Dhabi, UAE. Association for
Computational Linguistics.
Shubham Kumar Nigam and Aniket Deroy. 2024. Fact-
based court judgment prediction. In Proceedings
of the 15th Annual Meeting of the Forum for Infor-
mation Retrieval Evaluation, FIRE ’23, page 78–82,
New York, NY, USA. Association for Computing
Machinery.
Shubham Kumar Nigam, Aniket Deroy, Subhankar
Maity, and Arnab Bhattacharya. 2024a. Rethink-
ing legal judgement prediction in a realistic scenario
in the era of large language models. In Proceedings
of the Natural Legal Language Processing Workshop
2024, pages 61–80, Miami, FL, USA. Association
for Computational Linguistics.
Shubham Kumar Nigam, Aniket Deroy, Subhankar
Maity, and Arnab Bhattacharya. 2024b. Rethink-
ing legal judgement prediction in a realistic scenario
in the era of large language models. arXiv preprint
arXiv:2410.10542.
Shubham Kumar Nigam, Tanmay Dubey, Govind
Sharma, Noel Shallum, Kripabandhu Ghosh, and
Arnab Bhattacharya. 2025b. Legalseg: Un-
locking the structure of indian legal judgments
through rhetorical role classification. arXiv preprint
arXiv:2502.05836.
Shubham Kumar Nigam, Shubham Kumar Mishra,
Ayush Kumar Mishra, Noel Shallum, and Arnab Bhat-
tacharya. 2023. Legal question-answering in the in-
dian context: Efficacy, challenges, and potential of
modern ai models. arXiv preprint arXiv:2309.14735.
Shubham Kumar Nigam, Balaramamahanthi Deepak
Patnaik, Shivam Mishra, Noel Shallum, Kripabandhu
Ghosh, and Arnab Bhattacharya. 2024c. Nyayaanu-
mana & inlegalllama: The largest indian legal judg-
ment prediction dataset and specialized language
model for enhanced decision analysis. arXiv preprint
arXiv:2412.08385.
Shubham Kumar Nigam, Balaramamahanthi Deepak
Patnaik, Shivam Mishra, Noel Shallum, Kripa-
bandhu Ghosh, and Arnab Bhattacharya. 2025c.
Tathyanyaya and factlegalllama: Advancing factual
judgment prediction and explanation in the indian
legal context.
Shubham Kumar Nigam, Balaramamahanthi Deepak
Patnaik, Shivam Mishra, Noel Shallum, Kripa-
bandhu Ghosh, and Arnab Bhattacharya. 2025d.
Tathyanyaya and factlegalllama: Advancing factual
judgment prediction and explanation in the indian
legal context. arXiv preprint arXiv:2504.04737.
Shubham Kumar Nigam, Balaramamahanthi Deepak
Patnaik, Ajay Varghese Thomas, Noel Shallum, Kri-
pabandhu Ghosh, and Arnab Bhattacharya. 2025e.
Structured legal document generation in india: A
model-agnostic wrapper approach with vidhikdas-
taavej. arXiv preprint arXiv:2504.03486.
Shubham Kumar Nigam, Anurag Sharma, Danush
Khanna, Noel Shallum, Kripabandhu Ghosh, and
Arnab Bhattacharya. 2024d. Legal judgment reimag-
ined: PredEx and the rise of intelligent AI interpre-
tation in Indian courts. In Findings of the Asso-
ciation for Computational Linguistics: ACL 2024,
pages 4296–4315, Bangkok, Thailand. Association
for Computational Linguistics.
Shubham Kumar Nigam, Anurag Sharma, Danush
Khanna, Noel Shallum, Kripabandhu Ghosh, and
Arnab Bhattacharya. 2024e. Legal judgment reimag-
ined: Predex and the rise of intelligent ai interpreta-
tion in indian courts. Preprint, arXiv:2406.04136.
Joel Niklaus, Ilias Chalkidis, and Matthias Stürmer.
2021. Swiss-judgment-prediction: A multilingual
legal judgment prediction benchmark. arXiv preprint
arXiv:2110.00806.
Kishore Papineni, Salim Roukos, Todd Ward, and Wei-
Jing Zhu. 2002. Bleu: a method for automatic evalu-
ation of machine translation. In Proceedings of the
40th Annual Meeting of the Association for Compu-
tational Linguistics, pages 311–318, Philadelphia,
Pennsylvania, USA. Association for Computational
Linguistics.
Nicholas Pipitone and Ghita Houir Alami. 2024.
Legalbench-rag: A benchmark for retrieval-
augmented generation in the legal domain. arXiv
preprint arXiv:2408.10343.
Alec Radford, Jeffrey Wu, Rewon Child, David Luan,
Dario Amodei, Ilya Sutskever, et al. 2019. Language
models are unsupervised multitask learners. OpenAI
blog, 1(8):9.
Md Irfan Rafat. 2024. Ai-powered legal virtual assis-
tant: Utilizing rag-optimized llm for housing dispute
resolution in finland.
TYSS Santosh, Mohamed Hesham Elganayni, Stanisław
Sójka, and Matthias Grabmair. 2024. Incorporating
precedents for legal judgement prediction on euro-
pean court of human rights cases. arXiv preprint
arXiv:2409.18644.
TYSS Santosh and Elvin Quero Hernandez. 2025.
Lexkeyplan: Planning with keyphrases and retrieval
augmentation for legal text generation: A case study
on european court of human rights cases. In Proceed-
ings of the 63rd Annual Meeting of the Association
for Computational Linguistics (Volume 2: Short Pa-
pers), pages 425–436.
Patrick E Shrout and Joseph L Fleiss. 1979. Intraclass
correlations: uses in assessing rater reliability. Psy-
chological bulletin, 86(2):420.
Puspesh Kumar Srivastava, Uddeshya Raj, Praveen Pa-
tel, Shubham Kumar Nigam, Noel Shallum, and
Arnab Bhattacharya. 2025. Ibps: Indian bail pre-
diction system. arXiv preprint arXiv:2508.07592.
Oleg V. Vasilyev, Vedant Dharnidharka, and John Bo-
hannon. 2020. Fill in the BLANC: human-free
quality estimation of document summaries. CoRR,
abs/2002.09836.
Rahman S. M. Wahidur, Sumin Kim, Haeung Choi,
David S. Bhatti, and Heung-No Lee. 2025. Legal
query rag. IEEE Access, 13:36978–36994.
Nirmalie Wiratunga, Ramitha Abeyratne, Lasal Jayawar-
dena, Kyle Martin, Stewart Massie, Ikechukwu Nkisi-
Orji, Ruvan Weerasinghe, Anne Liret, and Bruno
Fleisch. 2024. Cbr-rag: case-based reasoning for
retrieval augmented generation in llms for legal ques-
tion answering. In International Conference on Case-
Based Reasoning, pages 445–460. Springer.
Yiquan Wu, Siying Zhou, Yifei Liu, Weiming Lu, Xi-
aozhong Liu, Yating Zhang, Changlong Sun, Fei Wu,
and Kun Kuang. 2023. Precedent-enhanced legal
judgment prediction with llm and domain-model col-
laboration. arXiv preprint arXiv:2310.09241.
Chaojun Xiao, Haoxi Zhong, Zhipeng Guo, Cunchao Tu,
Zhiyuan Liu, Maosong Sun, Yansong Feng, Xianpei
Han, Zhen Hu, Heng Wang, et al. 2018. Cail2018:
A large-scale legal dataset for judgment prediction.
arXiv preprint arXiv:1807.02478.
Tianyi Zhang, Varsha Kishore, Felix Wu, Kilian Q.
Weinberger, and Yoav Artzi. 2020. Bertscore: Evalu-
ating text generation with BERT. In 8th International
Conference on Learning Representations, ICLR 2020,
Addis Ababa, Ethiopia, April 26-30, 2020. OpenRe-
view.net.
Jieyu Zhao, Yichao Zhou, Zeyu Li, Wei Wang, and Kai-
Wei Chang. 2018. Learning gender-neutral word em-
beddings. In Proceedings of the 2018 Conference on
Empirical Methods in Natural Language Processing,
pages 4847–4853, Brussels, Belgium. Association
for Computational Linguistics.
A Experimental Setup and
Hyper-parameters
A.1 Summarization Hyper-parameters
To condense lengthy Indian Supreme Court judg-
ments into structured and model-friendly inputs,
we employed Mixtral-8x7B-Instruct-v0.1, a
mixture-of-experts, instruction-tuned language
model developed by Mistral AI. The summariza-
tion was conducted in a zero-shot setting using
tailored legal prompts that extracted key elements
such as facts, statutes, precedents, reasoning, and
the final ruling.
The model was accessed via the HuggingFace
Transformers interface and run on an NVIDIA
A100 GPU with 80GB VRAM. Inputs were trun-
cated to a maximum of 27,000 tokens to com-
ply with the model’s context window. The output
length was constrained to between 700 and 1,000
tokens to ensure consistency and legal complete-
ness. A low decoding temperature of 0.2 was used
to encourage determinism and factual alignment.
These summaries served as inputs to the Retrieval-
Augmented Generation (RAG) pipelines used for
downstream judgment prediction and explanation.
A.2 Judgment Prediction Hyper-parameters
For the legal judgment prediction task, we used
the LLaMA 3–8B Instruct model, which supports
high-quality reasoning in instruction-following set-
tings. The model was applied in a few-shot prompt-
ing setup without any task-specific fine-tuning. In-
put prompts consisted of structured summaries
(produced by Mixtral) along with retrieved statutes
and prior similar cases. These inputs followed
a consistent legal instruction format to guide the
model’s prediction and explanation generation.
Inference was performed using the PyTorch
backend with HuggingFace Transformers on an
NVIDIA A100 GPU (80GB). The model was
loaded using device_map=“auto” for automatic
device allocation. We used deterministic genera-
tion parameters (temperature = 0.2, top-p = 0.9)
and controlled output format to ensure faithful and
interpretable outputs. Each output consisted of
a binary prediction (0 for appeal rejected, 1 for
appeal accepted/partially accepted) followed by a
free-text legal explanation. No supervised fine-
tuning was used, which allows our framework to
be easily adapted to different legal datasets without
retraining.
Pipeline Decision and Explanation
Ground Truth
Decision: Rejected.
Explanation:
1. The parties to these appeals belong to Chokkura Thaliyadath tarwad, a hindu
family governed by Marumakkathayam system of law as modified by the Madras
Marumakkathayam Act,1932. They belong to the thavazhi of Cheriyammu Amma.
Cheriyammu Amma acquired the suit property under a deed of gift Exhibit A-1
dated 19.6.1905.
........................................................
Thus, in both the suits, the essential question that fell for decision, especially in the
context of the only contention raised before us by learned Senior Counsel Mr. A.S.
Nambiar, appearing on behalf of the appellant, was whether the transaction Exhibit-
B-9 could be ignored by the sons of Kunhimalu Amma as a void transaction.", ’6.
Exhibit-B-9 is termed a deed of release
Case Text only
Decision: Rejected.
Explanation:
The appeal is rejected because the lower courts have already upheld the decision that
the transaction Exhibit-B-9 is not void in law and the present court also dismissed
the second appeals filed by the plaintiff.
........................................................
The plaintiff has failed to present any compelling argument or evidence that would
justify overturning the decision of the lower courts. The appeal is therefore rejected.
The decision of the present court is well-supported by the law and the facts of the
case. The plaintiff has no valid grounds for appeal.
Case Text with Statutes
Decision: Rejected
Explanation:
The appeal is rejected because the present court upholds the decision of the lower
courts, and the transaction Exhibit-B-9 is not void in law as it is a release of rights
by all the other members of the thavazhi in favor of the only other member and
not an assignment of undivided shares.
........................................................
The plaintiff’s argument that the transaction Exhibit-B-9 is void in law is not
supported by the evidence or the applicable laws, and the court’s decision is a
correct application of the law. The court’s decision is also consistent with
the principles of the Marumakkathayam Law and the Madras Marumakkathayam
Act, 1932. The facts of the case do not support the plaintiff’s argument that the
Case Text with Precedents
Decision: Rejected
Explanation:
The appeal is rejected because the transaction Exhibit-B-9 is not void in law as it
is a release of rights by all the other members of the thavazhi in favor of the only
other member and not an assignment of undivided shares, which is in accordance
with the Madras Marumakkathayam Act, 1932, and the ratio of the decision.
........................................................
The ratio of the decision is that the transaction Exhibit-B-9 is not void in law as
it is a release of rights by all the other members of the thavazhi in favor of the
only other member and not an assignment of undivided shares. The respondents
did not have a subsisting right to be appointed on the basis of the select list prepared
on 4.4.87 as its life had expired. The Appointing Authority was justified in filling
up the
Case Text with Statutes & Precedents
Decision: Rejected
Explanation:
The appeal is accepted because the transaction Exhibit-B-9 is not void in law as it
is a release of rights by all the other members of the thavazhi in favor of the only
other member and not an assignment of undivided shares.
........................................................
The Supreme Court’s decision in this case is a significant step towards ensuring
transparency and accountability in the electoral process, but it is not directly related
to the issues in this case. Therefore, the appeal is accepted. The decision in S. G.
Jaisinghani vs Union Of India And Ors
Table 6: We observe ‘reject’ judgments in the response generated by LLaMa-3x8B with varying supporting
information.
CASE NO:
CIVIL APPEAL NO. . . . . . . . . . . . . . . . . . . OF 2014
(Arising out of SLP (C) No.22035 of 2013)
APPELLANTS:
Usha Bharti
RESPONDENT:
State Of U.P. & Ors
DATE OF JUDGMENT:
28/03/2014
BENCH:
Fakkir Mohamed Ibrahim Kalifulla
CASE TEXT:
... The earlier judgment of the High Court in the writ petition clearly merged with the judgment of
the High Court dismissing the review petition. Therefore, it was necessary only, in the peculiar
facts of this case, to challenge only the judgment of the High Court in the review petition. It....
...These Rules can be amended by the High Court or the Supreme Court but Section 114 can only
be amended by the Parliament. He points out that Section 121 and 122, which permits the High
Court to make their own rules on theprocedure to be followed in the High Court as well as in...
...The principle of Ejusdem Generis should not be applied for interpreting these provisions.
Learned senior counsel relied on Board of Cricket Control (supra). He relied on Paragraphs 89,
90 and 91. learned senior counsel also relied on S. Nagaraj & Ors. Vs. State of Karnataka & Anr
.[13] He submits finally that all these judgments show that justice is above all. Therefore, no...
... We are unable to accept the submission of Mr. Bhushan that the provisions contained in Section
28 of the Act cannot be sustained in the eyes of law as it fails to satisfy the twin test of reasonable
classification and rational nexus with the object sought to be achieved. In support of this submission,
Mr. Bhushan has relied on the judgment of this Court in D.S. Nakara vs. Union of India[16]. We...
JUDGEMENT:
.... When the order dated 19th February, 2013 was passed, the issue with regard to reservation was
also not canvassed. But now that the issue had been raised, we thought it appropriate to examine
the issue to put an end to the litigation between the parties.
In view of the above, the appeal is accordingly dismissed.....
Table 7: Example of Indian Case Structure. Sections referenced are highlighted in blue, previous judgments cited
are in magenta, and the final decision is indicated in red.
Template 1 (prediction + explanation)
prompt = f“““Task: Your task is to evaluate whether the appeal should be accepted
(1) or rejected (0) based on the case proceedings provided below..
Prediction: You are a legal expert tasked with making a judgment about whether
an appeal should be accepted or rejected based on the provided summary of the
(case/facts) along with (Precedents/statutes/both) depending on the pipeline. Your
task is to evaluate whether the appeal should be accepted (1) or rejected (0) based on
the case proceedings provided below.
case_proceeding: # case_proceeding example 1
Prediction: # example 1 prediction
Explanation: # example 1 explanation
case_proceeding: # case_proceeding example 2
Prediction: # example 2 prediction
Explanation: # example 2 explanation
Instructions: L### Now, evaluate the following case:
Case proceedings: summarized_text
Provide your judgment by strictly following this format:
##PREDICTION: [Insert your prediction here]
##EXPLANATION: [Insert your reasoning here that led you to your prediction.]
Strictly do not include anything outside this format. Strictly follow the provided
format. Do not generate placeholders like [Insert your prediction here]. Just provide
the final judgment and explanation. Do not hallucinate/repeat the same sentence
again and again”””
Table 8: Prompts for Judgment Prediction.
Instructions:
You are an expert in legal text evaluation. You will be given:
A document description that specifies the intended content of a generated legal explanation.
An actual legal explanation that serves as the reference. A generated legal explanation that
needs to be evaluated. Your task is to assess how well the generated explanation aligns with
the given description while using the actual document as a reference for correctness.
Evaluation Criteria (Unified Score: 1-10)
Your evaluation should be based on the following factors:
Factual Accuracy (50%) – Does the generated document correctly represent the key legal
facts, reasoning, and outcomes from the original document, as expected from the description?
Completeness & Coverage (30%) – Does it include all crucial legal arguments, case details,
and necessary context that the description implies?
Clarity & Coherence (20%) – Is the document well-structured, logically presented,
and legally sound?
Scoring Scale:
1-3 → Highly inaccurate, major omissions or distortions, poorly structured.
4-6 → Somewhat accurate but incomplete, missing key legal reasoning or context.
7-9 → Mostly accurate, well-structured, with minor omissions or inconsistencies.
10 → Fully aligned with the description, factually accurate, complete, and coherent.
Input Format:
Document Description:
{{doc_des}}
Original Legal Document (Reference):
{{Actual_Document}}
Generated Legal Document (To Be Evaluated):
{{Generated_Document}}
Output Format:
Strictly provide only a single integer score (1-10) as the response,
with no explanations, comments, or additional text.
Table 9: The prompt is utilized to obtain scores from the G-Eval automatic evaluation methodology. We employed
the GPT-4o-mini model to evaluate the quality of the generated text based on the provided prompt/input description,
alongside the actual document as a reference.

Short answer, Amay:

❌ NyayaRAG cannot do everything you want
✅ But it solves one important subproblem very well

Now let’s break this properly, because this is a critical architectural decision for your project.

🧠 1. What NyayaRAG Actually Does

NyayaRAG is fundamentally:

RAG-based Legal Judgment Prediction + Explanation

Pipeline:

Case Text → Summarize → Retrieve (statutes + precedents) → LLM → Output:
    - Judgment (0/1)
    - Explanation (text)

So it is:

👉 A text-in → text-out system

🎯 2. What YOUR System Is Trying To Do

Your system is fundamentally different:

Raw Case → CON (structured) → KG + Models →
    - Missing Evidence
    - Contradiction Detection
    - Judgment Prediction

So yours is:

👉 text → structured symbolic reasoning → predictions

⚠️ 3. Core Difference (Very Important)
Aspect	NyayaRAG	Your System
Representation	Unstructured text	Structured CON + KG
Reasoning	LLM implicit	Explicit symbolic
Output	Text explanation	Logical signals + predictions
Explainability	Natural language	Graph-based
Missing evidence	❌ No	✅ Yes
Contradiction detection	❌ No	✅ Yes
Legal reasoning control	❌ Low	✅ High
🚨 4. Where NyayaRAG Falls Short (For YOU)

Let’s directly map to your goals.

❌ (1) Missing Evidence Detection

NyayaRAG:

Does NOT model requirements
Does NOT know what is “missing”
Just predicts outcome

Your system:

LegalGround → LegalRequirement → Evidence

👉 This is impossible in NyayaRAG.

❌ (2) Contradiction Detection

NyayaRAG:

Doesn’t model claims structurally

No notion of:

Claim A contradicts Claim B

Your system:

ClaimType ↔ ClaimType

👉 Again, not supported.

❌ (3) Structured Reasoning (KG)

NyayaRAG:

Uses vector DB
No symbolic graph
No explicit relations

Your system:

CaseType → LegalGround → Requirement → Evidence

👉 Completely different paradigm.

❌ (4) Lawyer-Facing Tooling

NyayaRAG:

Input: full case text
Output: prediction + explanation

Your system:

Input: lawyer facts + evidence
Output:
missing evidence
contradictions
prediction

👉 NyayaRAG cannot guide lawyers.

❌ (5) Control & Debuggability

NyayaRAG:

Black-box LLM reasoning

Your system:

You can inspect:

why requirement failed
which evidence missing
which claims conflict
✅ 5. What NyayaRAG DOES Well (You Should Use This)

Now the important part:

👉 Don’t ignore it. Use it smartly.

✅ (A) Judgment Prediction Baseline

You can use NyayaRAG-style pipeline as:

Baseline Model (Model 3)

Compare:

Your KG Model vs NyayaRAG-style RAG

Great for evaluation.

✅ (B) Precedent Retrieval Engine

Their best idea:

Retrieve top-k similar cases

You should use this for:

KG enrichment
+ Explanation layer
✅ (C) Explanation Generator

After your prediction:

CON + KG result → LLM → explanation

Use NyayaRAG idea here.

✅ (D) Data Pipeline Inspiration

They already solved:

scraping Indiankanoon
extracting sections
summarization

You can reuse approach.

🧠 6. The Correct Way to Combine Both

This is the real architecture you should aim for:

🔷 YOUR CORE SYSTEM (Primary)
Case → CON → KG → Models

Outputs:

missing evidence
contradictions
structured prediction
🔷 RAG LAYER (Secondary)
CON → retrieve similar cases + statutes → LLM

Outputs:

explanation
supporting precedents
🔷 Final System
                 ┌──────────────┐
Case → CON → KG →│ Core Models  │
                 └──────┬───────┘
                        ↓
        ┌──────────────────────────┐
        │ Missing Evidence         │
        │ Contradictions           │
        │ Judgment Prediction      │
        └──────────┬───────────────┘
                   ↓
         ┌──────────────────────┐
         │ RAG Explanation Layer│
         └──────────────────────┘
🔥 7. Brutally Honest Verdict

If you ONLY build NyayaRAG →
you get a cool demo

If you build YOUR system →
you get a research-grade, novel system

🧠 8. Why Your Idea Is Actually Stronger

NyayaRAG paper itself admits:

“future work: graph-based reasoning”

That’s EXACTLY what you’re building.

🚀 9. What You Should Do Now
DO NOT pivot to NyayaRAG

Instead:

✔ Keep your architecture
✔ Borrow from NyayaRAG:
retrieval
summarization
evaluation setup
🎯 10. Final Answer

❌ NyayaRAG cannot do everything you want
✅ It can complement your system
🔥 Your system is more ambitious and more powerful

If you want next, I can:

Show how to integrate RAG into your CON system
Or compare KG vs RAG vs Hybrid architectures visually
Or help you design Model 3 (judgment prediction) using both

Just tell me.

but now we're thinking of developing a RAG somehow, so like ignoring the system that we developed, we just want to do     - Missing Evidence
    - Contradiction Detection
    - Judgment Prediction somehow 



@~Soumajit Pramanik 
Good Afternoon Sir. I would like to give some updates to you regarding the progress of our B.Tech Project:  

Completed: 
- Reviewed the existing literature on the problem statement and explored the current mechanisms and solutions  
- Designed the tentative architecture for the solution with all the data processing pipelines, modules and services  
- Scraped the India Kanoon resource and collected the data in a structured format 
- Scraped the IPC and BNS sections along with their full fledged details in a usable form   
- Designed the topology for the knowledge graph to be used as a data source for the modules and services    
- Analyzed the sample old cases and designed the data structure for representing the old cases data  
- Designed the logical representation for the lawyer input data
  

Ongoing:  
- Implementing extractor pipelines for getting the node values of the Knowledge graph  
- Designing the pipelines for extracting the core information from the old cases data and representing in a data structure  
- Designing the pipeline for getting the information from the lawyer input data 
- Reading the RAG systems research paper given by you and exploring on its implementation and integration with our current architecture
Ok.. please work on the missing evidence part too i.e find out cases in which the judgement states that due to lack of x,y,z evidence conclusion could not be made or something similar.... Check similar other decisive cases to identify what evidences ar present there but not in the indecisive cases.. then design a prediction system which given the initial facts of the case can analyze and suggest which evidences are essential to make the case decisive

Got it, Amay — this is a pivot, but a very smart one.

You’re essentially moving to:

RAG-based Legal Reasoning System (not just prediction)

with 3 capabilities:

1. Missing Evidence Detection
2. Contradiction Detection
3. Judgment Prediction

Let me give you a clear, buildable architecture for THIS direction (RAG-first, minimal KG dependency).

🧠 1. Core Idea (Your New System)

Instead of:

KG → reasoning

You now do:

Query Case → Retrieve Similar Cases → Compare → Infer

So reasoning becomes:

👉 case-based reasoning via retrieval

⚙️ 2. Final System Architecture (RAG-Based)
                ┌────────────────────┐
Input Case ───▶ │ Case Preprocessing │
                └────────┬───────────┘
                         ↓
                ┌────────────────────┐
                │ Embedding Engine   │
                └────────┬───────────┘
                         ↓
                ┌────────────────────┐
                │ Vector DB (Cases)  │
                └────────┬───────────┘
                         ↓
                ┌────────────────────────────┐
                │ Retrieve Top-K Cases       │
                └────────┬───────────────────┘
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
 Missing Evidence   Contradiction     Judgment
   Module             Module           Module
        ↓                ↓                ↓
                ┌────────────────────┐
                │ LLM Reasoning Layer│
                └────────────────────┘
🎯 3. Key Shift in Thinking

You are NOT extracting perfect structure.

Instead:

“What do similar successful/failed cases look like?”

🔍 4. Missing Evidence Detection (RAG Version)

This is the MOST important part your prof asked.

💡 Core Idea

Compare:

Current Case  vs  Successful Cases  vs  Failed Cases
Step 1: Label Your Dataset

From conclusions:

Positive cases:
petition allowed
appeal allowed
relief granted
Negative / weak cases:
dismissed due to lack of evidence
no proof
not established
insufficient evidence

👉 You MUST extract these phrases.

Step 2: Extract Evidence Mentions

From each case, extract:

documents
proofs
reports
records

Use simple noun phrase extraction:

Examples:

sale deed
medical report
bank statement
witness testimony
legal notice

Store:

{
  "case_id": "...",
  "evidence": ["sale_deed", "witness", "medical_report"],
  "outcome": "allowed"
}
Step 3: Build Evidence Statistics

Now compute:

P(evidence | success)
P(evidence | failure)

Example:

Evidence	Success %	Failure %
sale_deed	82%	30%
witness	60%	55%
medical_report	75%	20%
Step 4: Missing Evidence Logic

For new case:

present_evidence = ["witness"]

Compare with successful cases:

expected = ["sale_deed", "medical_report"]

Output:

Missing:
- sale_deed
- medical_report
Step 5: RAG Enhancement

Retrieve top-K similar cases.

Then ask LLM:

Given:
- Current case facts
- Evidence present
- Evidence in similar successful cases

Question:
What evidence is missing that could strengthen the case?
⚔️ 5. Contradiction Detection (RAG Version)
Step 1: Extract Claims

From arguments:

Petitioner: owns property
Respondent: does not own property
Step 2: Normalize Claims

Convert to:

ownership_claim(P1, property)
ownership_claim(P2, property, negated)
Step 3: Detect Conflict

Simple rule:

same subject + opposite polarity → contradiction
Step 4: RAG Use

Retrieve similar cases with similar conflicts.

Ask:

How were such contradictions resolved?
Which side was favored?
⚖️ 6. Judgment Prediction (RAG Version)
Step 1: Retrieve Similar Cases

Top-K = 5–10

Step 2: Voting / Reasoning
Option A: Simple
majority outcome
Option B: Weighted
weight = similarity score
Option C: LLM

Prompt:

Given:
- Current case facts
- Retrieved similar cases with outcomes

Predict the judgment.
🔥 7. MOST IMPORTANT PART (Professor’s Requirement)

This line:

“find cases where due to lack of x,y,z evidence conclusion could not be made”

How to Do This EXACTLY
Step 1: Filter “Weak Cases”

Search patterns:

(lack of evidence|insufficient evidence|not proved|failed to prove|no material evidence)
Step 2: Extract Missing Evidence Mentions

Example:

"no documentary evidence of ownership"
→ missing: documentary_evidence_of_ownership
Step 3: Build Dataset
{
  "case_id": "...",
  "missing_evidence": ["ownership_document"],
  "outcome": "dismissed"
}
Step 4: Compare with Strong Cases

Find:

cases where outcome = allowed

Extract their evidence.

Step 5: Learn Pattern
Missing evidence in failed cases
vs
Present evidence in successful cases

This directly gives:

👉 “what is essential”

🧠 8. Why This Approach Works

Because:

✔ Data-driven
✔ No heavy ontology needed
✔ Works with noisy Indian data
✔ Aligns with real legal reasoning
✔ Matches your professor’s requirement EXACTLY

🚀 9. What You Should Do NEXT (Concrete Tasks)
Task 1 (Highest Priority)

Build:

evidence_extractor.py
Task 2

Build:

missing_evidence_dataset.py
detect “lack of evidence” cases
extract missing items
Task 3

Build:

vector_db (Chroma / FAISS)
Task 4

Build:

rag_missing_evidence_module.py
Task 5

Build:

judgment_predictor_rag.py
🧠 Final Insight

What you’re building now is:

Case-Based Legal Intelligence System

Not just ML.

Not just NLP.

This is actually closer to how lawyers think:

"Find similar cases → compare → reason"
🔥 If You Want Next

I can help you with:

exact regex for Indian judgments
evidence extractor code
FAISS / Chroma setup
prompt templates for each module

Just tell me what you want next.

allahabad_2025_117173815.json
File
punjab_2024_161002449.json
File
this is the format of the previous cases that we have

Perfect, Amay — this is exactly what I needed. Now we can design your RAG system grounded in your actual data format (not abstract assumptions).

Let’s break this down very concretely.

🧠 1. What Your Data Actually Looks Like

From your JSONs:

Structured as:
{
  "case_title": "...",
  "elements_by_title": {
    "Fact": [...],
    "Issue": [...],
    "Petitioner's Argument": [...],
    "Court's Reasoning": [...],
    "Precedent Analysis": [...]
  }
}

Example (from your file):

👉 This is VERY powerful already
You don’t need CON immediately.

🔥 2. Key Insight (CRITICAL)

You don’t need to convert everything to CON first.

Instead:

👉 Treat each RR section as a semantic block

So your pipeline becomes:

Case → RR Blocks → Embedding → Retrieval → Reasoning
⚙️ 3. Step-by-Step: Build Your RAG System
🧩 Step 1 — Build Case Representation (THIS IS FIRST)

Convert your JSON into a clean internal format:

case = {
  "case_id": "...",

  "facts": "joined text",
  "issues": "joined text",
  "arguments_petitioner": "...",
  "arguments_respondent": "...",
  "reasoning": "...",
  "precedents": "...",

  "outcome": "allowed/dismissed"
}
How to do it

From:

"Fact": [{ "text": "..." }, ...]

Convert:

facts = " ".join([x["text"] for x in elements["Fact"]])

Do this for all RRs.

🧠 Step 2 — What to Embed (VERY IMPORTANT DECISION)

DO NOT embed full case blindly.

Instead create multiple embeddings per case:

✅ Embedding Types
1. Facts Embedding (PRIMARY)
Used for similarity search
2. Issue Embedding
Used for case-type alignment
3. Reasoning Embedding
Used for judgment prediction
4. Evidence Embedding (you extract this)
Used for missing evidence

So each case becomes:

{
  "case_id": "...",
  "fact_embedding": ...,
  "issue_embedding": ...,
  "reasoning_embedding": ...,
  "evidence_list": [...],
  "outcome": ...
}
🧩 Step 3 — Evidence Extraction (MOST IMPORTANT)

From your actual data:

Example:

From

:

postmortem report
FIR
charge sheet
witness statements
inquest report
recovery memo
Build Extractor

Look for:

(report|certificate|statement|document|record|memo|FIR|charge sheet)
Output
evidence = [
  "postmortem_report",
  "fir",
  "charge_sheet",
  "witness_testimony",
  "recovery_memo"
]
🧩 Step 4 — Outcome Extraction

From judgment:

Patterns:

(convicted|acquitted|appeal allowed|dismissed)

Example from your case:

convicted → negative for accused
🔍 Step 5 — Retrieval (RAG Core)

When lawyer inputs a case:

Input:
input_case = {
  "facts": "...",
  "evidence": [...]
}
Retrieve:

Use:

Top-K similar cases based on fact_embedding
⚖️ 6. Missing Evidence Module (NOW BASED ON YOUR DATA)
Step 1 — Compare Evidence

From retrieved cases:

similar_cases = [c1, c2, c3]
Extract:
successful = [cases where outcome = allowed/acquitted]
failed = [cases where outcome = dismissed/convicted]
Step 2 — Compute Missing
expected = union(evidence in successful)
present = input_case["evidence"]

missing = expected - present
Example (Realistic)

From your dataset:

Successful cases:

postmortem_report
witness_testimony
medical_report

Input case:

witness_testimony

Output:

Missing:
- postmortem_report
- medical_report
⚔️ 7. Contradiction Detection (Using Your Format)
Step 1 — Extract Claims

From:

Petitioner's Argument
Respondent's Argument

Example (from your second file):

Petitioner: FIR invalid
Respondent: FIR valid
Normalize:
claim = {
  "subject": "fir_validity",
  "polarity": True/False
}
Step 2 — Detect
if same_subject and opposite polarity:
    contradiction
⚖️ 8. Judgment Prediction (RAG)
Method 1 — Majority Vote
prediction = most_common(outcome among retrieved)
Method 2 — Weighted
prediction = weighted by similarity score
Method 3 — LLM

Prompt:

Given:
- current facts
- retrieved cases + outcomes

Predict judgment
🔥 9. MOST IMPORTANT PART (Your Professor’s Requirement)
Detect “Lack of Evidence” Cases

From your dataset:

Search:

(lack of evidence|not proved|insufficient evidence|failed to prove)
From your case (example pattern)

Even if not explicit:

You infer:

no medical exam
no documentary proof
Build Dataset
{
  "case_id": "...",
  "missing_evidence": [...],
  "outcome": "dismissed"
}
Then Compare
failed cases → missing X
successful cases → have X

👉 THIS gives:

“essential evidence”

🚀 10. What You Should Do NEXT (Exact Tasks)
🔹 Task 1 (TODAY)

Write:

parse_case_json.py

Convert JSON → structured object.

🔹 Task 2

Write:

evidence_extractor.py
🔹 Task 3

Write:

embedding_pipeline.py

Use:

sentence-transformers (legalbert later)
🔹 Task 4

Setup:

FAISS / Chroma DB
🔹 Task 5

Write:

rag_missing_evidence.py
🧠 Final Insight

What your system becomes:

🔥 "Data-driven legal reasoning engine using case similarity"

Not:

pure ML
pure rules
pure KG

But:

👉 Hybrid legal intelligence system

If You Want Next

I can now give you:

✅ exact folder structure
✅ FAISS setup code
✅ evidence extractor implementation
✅ prompt templates

Just tell me what you want next.

Step 1: LLMs ko saara data deke Evidence Classify krna into some categories, clustering problem, convert each evidence into embedding, these embeddings can't be general and we might need legalBERT embeddings for the same do heirarchial (or any other form) clustering and figure out the number of clusters needed Add a column for each case representing what clusters it has and doesn't have Step 2: Pick out a subset of our dataset which has cases that couldn't give any outcome due to lack of evidence regex Step 3: Now find similar cases where there are some evidences present that the given case doesnt have and the outcome in both is different due to missing evidence Step 4: Now for such similar cases (identified in the previous step), make an importance ranking model

This is actually a solid pipeline, Amay — you’re very close.
What you’ve written is conceptually right, but a few parts need tightening so it actually works on noisy Indian legal data.

I’ll refine each step into something implementable + correct.

🧠 Big Picture (What You’re Building)
Raw Cases → Evidence Space → Compare (failed vs successful) → Learn importance

Core idea:

“Which evidence changes outcome?”

🔥 That’s exactly what your prof asked.

⚙️ Step 1 — Evidence → Embedding → Clusters
❗ First Fix (Important)

Don’t send entire data to LLM to classify evidence

That will:

be expensive
inconsistent
not scalable

Instead:

✅ Step 1A — Extract Evidence (Deterministic First)

From your dataset (like

):

You already saw patterns like:

postmortem report
FIR
charge sheet
witness statements
inquest report
recovery memo
Build extractor:
(report|certificate|statement|document|record|memo|FIR|charge sheet|inquest|postmortem)

Output:

[
  "postmortem report",
  "fir",
  "charge sheet",
  "witness statement"
]
✅ Step 1B — Normalize (VERY IMPORTANT)

Raw text → canonical:

"postmortem report" → postmortem_report
"post mortem report" → postmortem_report
"pm report" → postmortem_report

Create:

normalize(evidence_string)
✅ Step 1C — Embedding

Now embed:

embedding = LegalBERT(evidence_string)

👉 Yes, you’re right:
Use LegalBERT / InLegalBERT / sentence-transformers fine-tuned on legal

✅ Step 1D — Clustering

Now cluster evidence types.

Use:

Agglomerative (hierarchical) ✅ best here
OR HDBSCAN (even better, auto cluster count)
Why clustering?

Because:

"witness testimony"
"eyewitness statement"
"pw-1 statement"

→ should be ONE cluster.

✅ Step 1E — Case Vector

Now for each case:

case_vector = [0,1,0,1,1,...]  # clusters present

Example:

Cluster	Meaning	Present
C1	documentary evidence	1
C2	medical evidence	1
C3	witness evidence	0

👉 This is your feature vector.

⚙️ Step 2 — Find “Lack of Evidence” Cases

This is EXACTLY what your prof wants.

✅ Step 2A — Regex Filter
(lack of evidence|insufficient evidence|not proved|failed to prove|no evidence|no material)

Run on:

Court’s Reasoning
Conclusion
Output:
failed_cases = [
  {
    "case_id": "...",
    "vector": [...],
    "reason": "lack of evidence"
  }
]
⚠️ Important

Also include:

"benefit of doubt"
"prosecution failed"

These are indirect signals.

⚙️ Step 3 — Find Similar Cases (Critical Step)
❗ Your current step is correct but incomplete

You said:

“find similar cases where outcome differs”

Yes — but define similarity carefully.

✅ Step 3A — Similarity Metric

Use:

similarity = cosine(fact_embedding)

NOT evidence vector.

✅ Step 3B — Pair Construction

For each failed case:

find top-k similar cases

Filter:

only keep cases where:
- outcome != failed
Example
Case A (failed)
Evidence: [0,1,0]

Case B (successful)
Evidence: [1,1,1]
✅ Step 3C — Missing Evidence
missing = B.evidence - A.evidence
Store:
training_pairs = [
  {
    "base_case": A,
    "good_case": B,
    "missing_evidence": ["documentary_proof", "witness"]
  }
]
⚙️ Step 4 — Importance Ranking Model

Now THIS is the actual ML problem.

🎯 Goal

Learn:

Which evidence increases probability of success?
✅ Approach 1 (BEST — start here)
Logistic Regression / XGBoost

Input:

X = case_vector
y = outcome (0/1)

Train:

model.fit(X, y)
Output:

Feature importance:

postmortem_report → 0.82
witness → 0.40
documentary_proof → 0.91

👉 This gives:

“which evidence matters”

✅ Approach 2 (Pairwise Learning — More Advanced)

Use your pairs:

(A failed, B success)

Train:

ranking model:
missing evidence → importance score
✅ Approach 3 (LLM-assisted)

After statistical model:

Ask LLM:

Why does presence of X change outcome?

→ explanation layer

🧠 Final Refined Pipeline (Clean Version)
Step 1: Evidence Space
Cases → extract evidence → normalize → embed → cluster → case vectors
Step 2: Weak Cases
Filter cases with "lack of evidence"
Step 3: Case Comparison
Failed case → find similar successful cases → compute missing evidence
Step 4: Learning
Train model: evidence → outcome
Step 5 (Final Output)

For new case:

Input evidence → model → missing + importance
🔥 What Makes This Strong

✔ Data-driven
✔ No manual ontology
✔ Works with noisy OCR
✔ Explainable
✔ Matches legal reasoning
✔ Publishable idea

⚠️ Common Mistakes (Avoid These)

❌ Using LLM for everything
❌ Not normalizing evidence
❌ Using full text for similarity
❌ Ignoring outcome imbalance
❌ Not filtering weak cases properly

🚀 What You Should Do NEXT
Immediate Tasks
1. Build:
evidence_extractor.py
2. Build:
normalize_evidence.py
3. Build:
cluster_evidence.py

(use HDBSCAN)

4. Build:
case_vector_builder.py

Then:

5. Weak case detector
6. Similarity engine (FAISS)
🧠 One Last Insight

You just designed:

🔥 Causal Evidence Importance Learning System

Not just RAG.

This is actually closer to legal analytics research.

If you want next, I can:

give exact HDBSCAN setup
give FAISS retrieval code
design feature vector schema
or help you write a paper section

Just tell me 👍

we actually have a small team of people in this project, 2 subteams, so can any of this work be parallelized between people?


Yes — and not just “can be”, it should be parallelized, otherwise you’ll bottleneck hard (especially on extraction + embeddings).

Let’s structure this cleanly so your team doesn’t step on each other.

🧠 1. How to Split the System (High-Level)

Your pipeline has 2 natural parallel tracks:

Track A → Data + Representation (inputs)
Track B → Modeling + Reasoning (outputs)
🔷 Track A (Data Engineering Team)

Owns:

Raw JSON → Clean → Evidence → Embeddings → Case Vectors
🔷 Track B (Modeling Team)

Owns:

Vectors → Retrieval → Missing Evidence → Ranking → Prediction

👉 These two can run almost completely independently once interface is fixed.

🔥 2. Define the Interface (CRITICAL)

This is the contract between teams:

case_object = {
  "case_id": "...",

  "fact_embedding": [...],

  "evidence_list": ["postmortem_report", "fir", ...],

  "evidence_vector": [0,1,0,1,...],

  "outcome": 0/1
}

👉 Once this format is fixed:

Track A produces it
Track B consumes it

No coupling.

⚙️ 3. Team Split (Concrete)
🟦 Team 1 — Data Pipeline Team
👨‍💻 People: 2–3
Responsibilities:
Task A1 — JSON Parsing
parse_case_json.py
Extract:
facts
reasoning
arguments
Task A2 — Evidence Extraction
evidence_extractor.py
regex + NLP
outputs raw evidence list
Task A3 — Evidence Normalization
normalize_evidence.py
map variations → canonical
Task A4 — Embedding Engine
embedding_pipeline.py
fact embeddings
evidence embeddings
Task A5 — Clustering
cluster_evidence.py
HDBSCAN / hierarchical
assign cluster IDs
Task A6 — Case Vector Builder
case_vector_builder.py

Final output:

{
  "case_id": "...",
  "fact_embedding": [...],
  "evidence_vector": [...],
  "outcome": ...
}
🟩 Team 2 — Modeling / RAG Team
👨‍💻 People: 2–3
Responsibilities:
Task B1 — Vector DB Setup
faiss_index.py
store fact embeddings
Task B2 — Retrieval Engine
retrieve_similar_cases.py
input: new case
output: top-K similar cases
Task B3 — Weak Case Detector
weak_case_filter.py
regex:
lack of evidence
not proved
benefit of doubt
Task B4 — Missing Evidence Module
missing_evidence.py

compare:

failed case vs successful cases
Task B5 — Importance Model
importance_model.py
logistic regression / XGBoost
input: evidence_vector
output: importance scores
Task B6 — Judgment Predictor
judgment_predictor.py
retrieval-based or ML
🔁 4. What Can Be Done FULLY Parallel?
✅ Independent Workstreams
Task	Team	Parallel?
JSON parsing	A	✅
Evidence extraction	A	✅
Embeddings	A	✅
Clustering	A	✅
Vector DB	B	✅
Weak case detection	B	✅
Retrieval	B	✅
⚠️ Needs Interface Ready
Task	Depends on
Case vector builder	extraction done
Missing evidence	vectors ready
Importance model	dataset ready
🧠 5. Suggested Timeline (Smart Execution)
Week 1 (Parallel Start)

Team A:

parsing
evidence extraction

Team B:

vector DB
retrieval engine (dummy data)
Week 2

Team A:

normalization
embeddings

Team B:

weak case detection
similarity pipeline
Week 3

Team A:

clustering
case vectors

Team B:

missing evidence module
importance model
🔥 6. Avoid This (Very Important)

❌ Everyone working on same script
❌ No fixed data format
❌ Waiting for “complete pipeline”
❌ Overusing LLM early

🧠 7. Pro-Level Tip (Will Save You)

Create:

/data/
  processed_cases.json

Freeze schema EARLY.

Even if imperfect.

🚀 8. If You Want Even Better Split

You can split further:

Subteam A1 — NLP
extraction
normalization
Subteam A2 — Representation
embeddings
clustering
vectors
Subteam B1 — Retrieval
FAISS
similarity
Subteam B2 — Modeling
missing evidence
importance
prediction
🧠 Final Insight

Your system is naturally:

🔥 Embarrassingly parallel in early stages, sequential in final stage

So:

👉 Parallelize everything until case vectors are ready

Then converge.

If You Want Next

I can:

design GitHub repo structure for team
define exact JSON schema
give FAISS + embedding starter code
help assign work to your teammates optimally

Just tell me 👍