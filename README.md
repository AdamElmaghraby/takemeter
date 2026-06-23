# TakeMeter: Discourse Quality Classifier for r/stocks

## 1. Community Choice & Reasoning
The chosen community is `r/stocks`, a public Reddit forum dedicated to discussions surrounding individual equities, macroeconomic trends, and retail portfolio strategies. I selected this space because its discourse exists on a wildly volatile spectrum—ranging from institutional-grade, data-dense fundamental analysis to unhinged, reactionary panic-selling rants. 

Dissecting these distinctions matters profoundly to this community because retail investing is an exercise in information filtering. For a casual reader on `r/stocks`, the ability to separate genuine evidentiary signal from unverified speculative narratives and emotional herd noise is the literal difference between making a calculated, profitable position or suffering a catastrophic liquidation.

---

## 2. Label Taxonomy

Our classification objective measures **epistemic rigor** (how a user proves what they claim to know). Every post is assigned strictly one of three mutually exclusive labels based on the core thesis of the text:

### `evidenced_analysis`
* **Definition:** The post supports its core investment thesis using verifiable quantitative data, historical market precedents, SEC filings, official analyst coverage, or specific fundamental metrics (e.g., P/E ratios, forward guidance, revenue growth).
* **Example 1:** *"Company: Klaviyo | Ticker: KVYO | Market cap: $4 billion USD... 2025 revenue: Roughly $1.2 billion | 2026 revenue guidance: Roughly $1.55 billion... Non-GAAP operating margins at roughly 14-15%, while gross margins are at 75%... Q1 results (28% growth)..."*
* **Example 2:** *"A Citi analyst initiated coverage on Figma today with a Buy rating and a $36 price target, implying roughly 80% upside... FIG is down over 50% YTD despite accelerating growth. Q1 revenue grew 46% YoY and guidance was raised."*

### `logical_speculation`
* **Definition:** The post presents a structured, internally coherent financial narrative or macro argument that sounds logical, but relies primarily on personal assumptions, broad industry narratives, or technical chart patterns rather than verifiable accounting data.
* **Example 1:** *"This stock is headed to $300 soon. Co pilot is a failure, openAI is sketchy and very unprofitable... To me, MSFT is now in that value trap territory, similar to NKE or PYPL in that sense. P/E ratio is low, sure! But the street also knows that growth is likely to slow..."*
* **Example 2:** *"It’s not just new load growth, most of the North American power grid was built in the 1960s. Regardless of data centres and electrification, the baseline case still requires massive grid investments."*

### `emotional_sentiment`
* **Definition:** The post expresses raw feelings, momentum bias (FOMO/panic), personal lifestyle anecdotes, or immediate psychological reactions to market action with minimal analytical structure.
* **Example 1:** *"I know I’m gonna get so much shit for this but I don’t care. I was 70% VT 30% SGOV and I sold my market positions... I just see splinters everywhere... when I dump it all back once we enter the 30-40% correction I think is coming, it will pay off... sometimes your gut is overwhelming."*
* **Example 2:** *"NVDA to the moon baby 🚀🚀 completely unhinged green day, bears are absolutely crying in shambles right now, doubling down on my calls at open tomorrow!"*

---

## 3. Data Curation, Culling, & Annotation

### The "Speculation Monopoly" Discovery
Raw ingestion was performed via an automated read-only script using PRAW (Python Reddit API Wrapper). Initially, the script scraped 320 active posts and top-level comments. 

Upon conducting an initial exploratory human audit of the 320 raw items, I uncovered a severe real-world data skew: **nearly 200 of the 320 scraped items fell under `logical_speculation`.** Because `r/stocks` is dominated by retail "armchair CEOs," the raw data threatened to create an extreme 62% majority class. Recognizing that feeding an imbalanced distribution to a small 66-million parameter model would induce severe prediction drag (teaching the weights to just default to Speculation when confused), **I actively culled 120 speculative rows from the dataset**, locking down a tight, hand-balanced 200-item ground truth.

### Final Locked Dataset Distribution (200 Total)
* `emotional_sentiment`: **82 examples** (41.0%)
* `logical_speculation`: **73 examples** (36.5%)
* `evidenced_analysis`: **45 examples** (22.5%) 

*(Note: This distribution satisfies the project safety constraints: every class sits safely above the 20% minimum floor, and no class breaches the 50% majority cap).*

### Two-Stage Annotation & Human Overrides
To annotate the locked 200 rows, I utilized a **Machine-Assisted Human-Audited** workflow:
1. **Stage 1 (LLM Pre-Pass):** The raw text of all 200 rows was passed to Gemini 1.5 Pro via a strict zero-shot classification prompt containing the taxonomy definitions.
2. **Stage 2 (Human Audit):** I manually audited 100% of the pre-labeled rows. During this audit, I encountered several complex semantic traps where the machine's logic failed, requiring human overrides. 

**Three genuinely difficult annotation examples from this audit included:**

* **Difficult Example A:** *"I made $500,000 trading stocks and options in 18 months. These are the 15 things I did that worked best.. I failed a lot while trading before, during, and after succeeding..."*
  * *The Trap:* The LLM labeled this `logical_speculation` because it read like a retrospective personal story. 
  * *Human Decision:* Overridden to **`evidenced_analysis`**. The core claim is the literal acquisition of $500k; because the "15 things" listed tangible trading rules that substantiated the math, the monetary figure acted as verifiable proof rather than a casual boast.

* **Difficult Example B:** *"I forgot I bought AMD and now its most of my portfolio, it's stressing me out. I'm going to be honest, I have no idea what I'm doing when it comes to stocks..."*
  * *The Trap:* The LLM labeled this `logical_speculation` because the author used calm, standard, well-punctuated "indoor syntax."
  * *Human Decision:* Overridden to **`emotional_sentiment`**. Despite the polite grammar, the core thesis contains zero market mechanics and is entirely an expression of personal psychological paralysis.

* **Difficult Example C:** *"No. Survivorship bias. Those who made losses betting on wrong ones do not post here."*
  * *The Trap:* The LLM flagged this as `emotional_sentiment` due to the blunt, fragmented, one-word opening sentence.
  * *Human Decision:* Overridden to **`logical_speculation`**. Bluntness is not an emotion; the author is invoking a formal epistemological concept (survivorship bias) to logically dismantle an assumption.

---

## 4. AI Usage Disclosure (Part 1: Data & Setup)

* **Automated Scraper Generation (Claude Code):** Directed the agent to write a minimal, read-only PRAW script to fetch top-level comments from `r/stocks`. *Human Override:* Modified the output script manually to insert an explicit filter that dropped stickied Auto-Moderator comments.
* **Dataset Pre-Labeling (Gemini 1.5 Pro):** Prompted the model to act as a zero-shot classifier across my 200 culled CSV rows. *Human Override:* Conducted a 100% manual review pass, overriding approximately 20% of the machine's generated labels where it fell into superficial syntax and vocabulary traps.

## 5. Fine-Tuning Pipeline & Architecture

### Base Model Selection
The specialized classifier was fine-tuned atop `distilbert-base-uncased`. DistilBERT was selected because it represents an optimal architectural compromise: via knowledge distillation, it retains 97% of standard BERT’s language understanding capabilities while reducing the total parameter count by 40% (down to roughly 66 million parameters). This allowed the entire custom training loop to execute natively on a free Google Colab Nvidia T4 GPU in approximately 120 seconds.

### Hyperparameter Strategy
Training was executed using the following stable configuration:
* **Number of Epochs:** `3`
* **Batch Size:** `16`
* **Learning Rate:** `2e-5`

**Engineering Justification:** With a locked training split of only 140 items (post train/val/test split), parameter restraint is paramount. Altering the learning rate to a more aggressive posture (e.g., `5e-5`) on a small text pool risks violently overshooting the local minima. Conversely, increasing the epoch count beyond `3` on a 140-item ground truth inevitably induces severe memorization (overfitting), stripping the small model of its ability to generalize unseen test prose.

---

## 6. Baseline Zero-Shot Comparison

To establish a defensible performance floor, the held-out test split (30 items) was evaluated against a zero-shot baseline prior to fine-tuning. 

### Baseline LLM & Prompt Architecture
The baseline evaluation utilized Groq's cloud inference engine running `llama-3.3-70b-versatile`. The model was supplied with a strict, system-level Few-Shot classification prompt containing:
1. The explicit contextual role (*"expert financial discourse classifier analyzing r/stocks"*).
2. The locked one-sentence definitions from the taxonomy spec.
3. High-contrast, truncated examples for each class.
4. Strict programmatic output constraints forbidding conversational filler, markdown, or punctuation.

**Parsing Success:** The zero-shot baseline achieved a **100% parse rate** (0 unparseable strings out of 30 requests), proving the validity of the prompt guardrails.

---

## 7. Comprehensive Evaluation Report & Autopsy

### Comparative Scoreboard (Evaluated on Locked Test Split)

| Metric | Groq Zero-Shot (`llama-3.3-70b`) | Fine-Tuned (`distilbert-base`) | Delta / Impact |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy** | **76.7%** | 46.7% | `-30.0%` |
| **Macro Avg F1** | **0.76** | 0.34 | `-0.42` |
| **Evidenced Analysis (F1)** | **0.80** | 0.00 | `-0.80` (Collapse) |
| **Logical Speculation (F1)** | **0.67** | 0.52 | `-0.15` |
| **Emotional Sentiment (F1)** | **0.83** | 0.50 | `-0.33` |

### Forensic Autopsy: Why the Custom Model Underperformed

In standard software development, a 46.7% accuracy represents a pipeline failure. In artificial intelligence engineering, a 46.7% accuracy featuring a literal `0.00` class score represents a textbook diagnostic case study in **model parameter capacity versus zero-shot semantic reasoning.**

Pitting a 66-million parameter model against a 70-billion parameter cloud behemoth on a 140-item training set exposed three systemic failure modes:

#### 1. Complete Minority Class Collapse (`evidenced_analysis` F1 = 0.00)
DistilBERT completely failed to predict `evidenced_analysis` a single time across the test split. Because this class represented only 22.5% of the overall dataset, DistilBERT was exposed to roughly **23 total training examples** of it. Learning the visual structures of quantitative fundamental metrics embedded inside noisy Reddit text requires a dense parameter map; lacking sufficient data depth, DistilBERT’s optimizer simply deleted the complex boundary from its internal weights to minimize overall cross-entropy loss, defaulting entirely to the two majority classes.

#### 2. The "Syntactic Posture" Trap (Grammar over Grief)
* **Directional Error:** True `emotional_sentiment` misclassified as `logical_speculation`.
* **Example Failure:** *"I forgot I bought AMD and now its most of my portfolio, it's stressing me out... I have no idea what I'm doing..."*
* **Analysis:** DistilBERT overfit to **superficial punctuation heuristics**. It learned that long, grammatically standard, multi-sentence lowercase paragraphs equal `logical_speculation`. Because this user typed their financial anxiety in a polite, highly structured voice rather than screaming in ALL CAPS with rocket emojis, the small model completely missed the underlying psychological paralysis.

#### 3. Blunt Brevity Confused for Rage
* **Directional Error:** True `logical_speculation` misclassified as `emotional_sentiment`.
* **Example Failure:** *"No. Survivorship bias. Those who made losses betting on wrong ones do not post here."*
* **Analysis:** This post is an exceptional, high-level logical argument invoking an academic concept. However, DistilBERT cannot grasp the high-level epistemological definition of "survivorship bias." Instead, it looked at the aggressive syntactic structure—a blunt one-word sentence followed by hard stops—and mapped the abruptness to its internal trigger definition of *An Emotional Internet Argument*.

#### 4. Narrative Camouflage Drowning Out Numerical Tokens
* **Directional Error:** True `evidenced_analysis` misclassified as `logical_speculation`.
* **Example Failure:** *"McDonald's - An expensive real-estate company (value $150.90 vs price $248.74). I went through the annual reports..."*
* **Analysis:** This post contains exact fundamental DCF intrinsic value math (`$150.90`). However, DistilBERT parses semantic meaning heavily via surrounding verb tokens. Because the author wrapped the math inside first-person conversational storytelling (*"I went through...", "I'll describe it as..."*), the conversational narrative tokens drowned out the literal numerical tokens, convincing the model it was reading an opinion piece rather than a balance sheet audit.


## 8. Sample Classifications & Inference Proof

Below is an audited sample of held-out test prose processed through the fine-tuned DistilBERT inference pipeline:

| Post Snippet (Truncated) | Predicted Label | Confidence | True Label | Status |
| :--- | :---: | :---: | :---: | :---: |
| *"Everyone is talking about AI causing the continued fall. It's not. It's the September jobs report.. If it was only the AI trade cracking, you'd see much more rotation into other sectors..."* | `logical_speculation` | `0.40` | `logical_speculation` | **CORRECT** |
| *"McDonald's - An expensive real-estate company (value $150.90 vs price $248.74). I went through the annual reports of Mcdonald's for the first time..."* | `logical_speculation` | `0.41` | `evidenced_analysis` | **INCORRECT** |
| *"I forgot I bought AMD and now its most of my portfolio, it's stressing me out. I'm going to be honest, I have no idea what I'm doing..."* | `logical_speculation` | `0.39` | `emotional_sentiment` | **INCORRECT** |
| *"No. Survivorship bias. Those who made losses betting on wrong ones do not post here."* | `emotional_sentiment` | `0.39` | `logical_speculation` | **INCORRECT** |

**Correct Prediction Justification:** DistilBERT correctly captured the September jobs report snippet because the author utilized formal propositional logic (*"If X cracking, you'd see Y"*), completely omitting first-person emotional posture or high-arousal vocabulary.

---

## 9. Intended vs. Learned Behavior & Higher Reflections

### Intended vs. Learned Behavior
A profound semantic gap exists between my design intent and DistilBERT's actual learned heuristics. I intended the model to evaluate the **epistemic rigor** of a post (Hard Quantitative Proof vs. Structured Propositional Logic vs. Unfiltered Psychological Arousal). 

Instead, DistilBERT overfit to **superficial syntactic posture**:
1. **The Polite Panic Heuristic:** It assumed that soft-spoken, well-punctuated, lowercase sentences automatically indicate `logical_speculation`, misclassifying polite expressions of severe financial depression as valid market theses.
2. **The Bluntness Heuristic:** It mapped short, highly fragmented, hard-stopped sentences to its internal trigger for *Internet Conflict*, misclassifying high-level epistemological concepts like "survivorship bias" as raw emotion simply because the author delivered the counter-argument abruptly.
3. **Narrative Token Flooding:** When an author introduced legitimate Discounted Cash Flow math ($150.90 intrinsic value) via first-person storytelling (*"I went through the reports and I'll describe it as"*), the narrative verb tokens completely overwhelmed the isolated numerical tokens, tricking the model into categorizing a balance sheet audit as mere opinion.

### Specification vs. Implementation Reflection
* **How the Spec Guided Me:** Drafting strict precedence rules in `planning.md` prior to data collection prevented me from succumbing to label drift during the human annotation phase. When reviewing chaotic Reddit prose that contained both specific partial share counts and defensive personal venting, I was able to strictly anchor to my written rule—*classify strictly by what carries the core thesis*—to override the LLM's flawed initial guesses.
* **How Implementation Diverged:** My initial planning spec operated on the naive assumption that a standard top-level scrape of `r/stocks` would yield a roughly balanced natural distribution. In practice, implementation heavily diverged during the initial ingestion pass: out of 320 raw scraped items, nearly 200 were trapped inside `logical_speculation`. This required an unplanned, manual data-engineering intervention where I actively discarded 120 speculative rows to protect the 66M parameter model from developing an extreme majority-class prediction bias.

---

## 10. AI Usage Disclosure (Part 2: Post-Mortem Analysis)

* **Error Pattern Autopsy (Claude 3.5 Sonnet):** Fed the raw text printout of DistilBERT's 16 misclassified test entries into the LLM, directing it to act as a linguistic forensic investigator to identify common semantic denominators across the failures. *Human Verification:* I manually audited 100% of the model's suggested themes against my source CSV, confirming the finding that standard indoor syntax heavily induced a false Speculation bias across genuine sentiment entries.