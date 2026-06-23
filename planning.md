# TakeMeter — Planning Spec

A fine-tuned text classifier that grades the *type of discourse* in r/stocks posts: is a take backed by evidence, built on logic, or driven by emotion?

---

## 1. Community

**The community is [r/stocks](https://www.reddit.com/r/stocks/)**, a large public forum where retail investors gather to discuss equity markets and portfolio strategies. I chose it because it features a highly volatile mix of discourse, ranging from data-heavy, institutional-grade research to reactionary panic-selling rants. Distinguishing between these styles matters deeply to members of this community because separating actual evidentiary signal from unverified speculative narratives and emotional market noise is the direct difference between making calculated, profitable investments or suffering catastrophic financial losses.

**Why it's a good fit for a classification task:** the quality of takes on r/stocks varies enormously and along a meaningful axis — *how* a claim is justified, not just *what* it claims. The same ticker (say NVDA) will appear in a 1,000-word DD post citing revenue guidance and margins, in a structured-but-unsourced "this is headed to $300" technical argument, and in a one-line "🚀 to the moon, bears crying" comment. That spread gives me three genuinely distinct discourse styles that co-occur on the same topics, which is exactly what makes the boundary learnable but non-trivial. The subreddit is also high-volume and fully public, so collecting 200+ real examples is feasible without touching private or authenticated content.

---

## 2. Labels

Three mutually exclusive labels. A post gets **exactly one**. When a post mixes styles, I apply this **precedence rule**: classify by what carries the *core thesis*, with **evidence > logic > emotion** — i.e., scattered data points do not make a post `evidenced_analysis` unless that data directly validates the main claim; intense tone does not make a post `emotional_sentiment` if a valid structural argument is doing the real work.

### `evidenced_analysis`
The post supports its core investment thesis using verifiable quantitative data, historical market precedents, SEC filings, analyst ratings, or specific fundamental metrics.

- **Example A (Klaviyo deep dive):** "Company: Klaviyo | Ticker: KVYO | Market cap: $4 billion... 2025 revenue: Roughly $1.2 billion | 2026 revenue guidance: Roughly $1.55 billion... Non-GAAP operating margins at roughly 14-15%, while gross margins are at 75%... In q1 they reported 38% YoY growth in their enterprise segment..."
- **Example B (Citi Figma coverage):** "A Citi analyst initiated coverage on Figma today with a Buy rating and a $36 price target, implying roughly 80% upside... FIG is down over 50% YTD despite accelerating growth. Q1 revenue grew 46% YoY and guidance was raised."

### `logical_speculation`
The post presents a structured, internally coherent financial narrative or structural argument that sounds logical, but relies primarily on personal assumptions, macro theories, or chart technicals rather than verifiable accounting data or external sources.

- **Example A (MSFT value trap):** "This stock is headed to $300 soon. Co pilot is a failure, openAI is sketchy and very unprofitable... Chart also look really bad on daily weekly and monthly timeframes... To me, MSFT is now in that value trap territory, similar to NKE or PYPL... P/E ratio is low, sure! But the street also knows that growth is likely to slow..."
- **Example B (power grid macro reply):** "It's not just new load growth, most of the North American power grid was built in the 1960s... Regardless of data centres and electrification, the baseline case still requires massive grid investments."

### `emotional_sentiment`
The post expresses raw feelings, momentum bias (FOMO/panic), personal lifestyle anecdotes, or immediate psychological reactions to market moves with minimal analytical structure.

- **Example A (gut panic):** "I know I'm gonna get so much shit for this but I don't care. I was 70% VT 30% SGOV and I sold my market positions... I just see splinters everywhere... when I dump it all back once we enter the 30-40% correction I think is coming, it will pay off... sometimes your gut is overwhelming and you should listen."
- **Example B (short-form hype):** "NVDA to the moon baby 🚀🚀 completely unhinged green day, bears are absolutely crying in shambles right now, doubling down on my calls at open tomorrow!"

---

## 3. Hard Edge Cases

Three post *types* that genuinely sit between two labels, with the rule I'll apply when annotating.

- **Scattered data anchoring an unverified thesis** (e.g., the $RDDT post: cites 50M DAU, Twitter's $500M 2021 data-licensing revenue, a $33B valuation — but the actual argument rests on subjective claims like "ads look and feel spammy" and "subreddit visits don't equate to purchase intent"). *This straddles `evidenced_analysis` ↔ `logical_speculation`.* **Rule:** to be `evidenced_analysis`, the data must directly validate the core thesis. When numbers are decorative and the thesis hangs on qualitative judgment, label it **`logical_speculation`**.

- **Valid structural argument wrapped in high-intensity prose** (e.g., the $MU/Micron post: a real supply/demand case about HBM contracted capacity through 2027, but written with hyperbole — "$1500 by Q4," "traumatized by historical boom and bust," "math staring them in the face"). *This straddles `logical_speculation` ↔ `emotional_sentiment`.* **Rule:** tone alone doesn't disqualify logic. If valid macro/industry-level structural reasoning is carrying the post, it stays **`logical_speculation`**.

- **Post dominated by ego/identity defense rather than the security** (e.g., the user tracking exact partial shares but spending the post defending their background — "graduate student at MIT to be more specific since it seems that certain people care about whether I come from a prestigious institution"). *This straddles `emotional_sentiment` ↔ `evidenced_analysis` (the share counts look like data).* **Rule:** when the post's primary real estate defends the author's ego/intelligence/emotional state rather than evaluating the security, it fails the structural threshold of an argument → **`emotional_sentiment`**.

I'll keep a running list of every real example that gives me pause during annotation (what it was, the two candidate labels, what I decided), appended here.

---

## 4. Data Collection Plan

- **Where:** public posts and top-level comments from r/stocks, pulled via Reddit's **public JSON endpoints** (append `.json` to any public listing, e.g. `r/stocks/top.json?t=month`). No app, credentials, or authentication required — read-only public content only. A small script with a custom `User-Agent` header collects candidates; I keep it minimal so collection doesn't turn into a coding project.
- **How many:** **200 labeled examples**, saved as a single CSV with columns `text`, `label`, `notes` (the notebook does the 70/15/15 train/val/test split — I will *not* pre-split).
- **Per-label target:** natural-ish distribution but **capped** — **no label above 50%, every label at least 20%** of the 200 (≥40 examples each). I expect `emotional_sentiment` and `logical_speculation` to be common in the wild and `evidenced_analysis` to be the scarcest.
- **If a label is underrepresented after the first pass:** run a **targeted second pass** — sort/search r/stocks for DD-flaired and long-form posts to boost `evidenced_analysis`, and pull from comment threads / daily discussion for whichever class is short — until every label clears the 20% floor. I'd rather collect more than carry a lopsided set, since heavy imbalance teaches the model to just predict the majority class.

---

## 5. Evaluation Metrics

**Accuracy alone is not enough** because the dataset is intentionally imbalanced (up to ~50% one class): a model that ignores the input and always predicts the majority label could post a deceptively high accuracy while being useless on the minority classes. So I'll use:

- **Macro-F1 (primary).** The unweighted mean of per-class F1. It weights all three classes equally regardless of size, which matches my goal of getting *every* discourse type right, not just the common one. This is my headline number and the basis of my success criterion.
- **Per-class precision, recall, and F1.** To see *which* class is failing and *how* — e.g., high precision / low recall on `evidenced_analysis` means the model is too conservative about calling something evidenced.
- **Confusion matrix.** To expose *directional* errors — which boundary the model hasn't learned (e.g., true `evidenced_analysis` predicted as `logical_speculation`). This directly tests whether my hard edge cases are where the model breaks.

I'll report all of these for **both** the fine-tuned DistilBERT model and the Groq `llama-3.3-70b-versatile` zero-shot baseline on the same locked test set.

---

## 6. Definition of Success

**Numeric bar:** the fine-tuned model is a success if it reaches **macro-F1 ≥ 0.70** on the held-out test set **and clearly beats the Groq `llama-3.3-70b-versatile` zero-shot baseline** on macro-F1. Beating the baseline is what proves fine-tuning actually added value; the 0.70 floor is a defensible target for a hard, subjective 3-class task on 200 examples.

**What would make it genuinely useful / "good enough for deployment":** TakeMeter could power three real r/stocks tools at once —

1. an **auto-flair suggester** that tags new posts `[Evidenced]` / `[Speculation]` / `[Sentiment]` (low-stakes, editable);
2. a **signal filter** that surfaces `evidenced_analysis` and downranks `emotional_sentiment` noise; and
3. a **discourse-health dashboard** tracking the label mix over time.

For those uses, "good enough" means: hitting the bar above, **no dead class** (every class F1 meaningfully above zero), and that the model's mistakes are **between adjacent labels** (evidence↔logic, logic↔emotion) rather than between the extremes (evidence↔emotion). Adjacent confusions mirror the genuinely fuzzy human boundary and are tolerable for a suggester/filter; extreme confusions would mean the model never learned the core distinction and isn't deployable.

---

## AI Tool Plan

This project has no implementation code to generate, so AI tools help in three specific places:

- **Label stress-testing (before annotating 200).** I'll give an LLM my label definitions and edge-case rules above and ask it to generate 5–10 posts that sit on the boundary between two labels. If it produces posts I *can't* classify cleanly with my rules, my definitions need tightening — I'll fix them here before committing to annotation.
- **Annotation assistance.** I will use an LLM to **pre-label** each collected post (given the definitions in this doc), then **review and correct every single label myself** — no skimming. Pre-labeled rows are tracked (a marker in the `notes` column) so I can disclose exactly which examples were machine-assisted in the README's AI usage section.
- **Failure analysis (after fine-tuning).** I'll paste the list of misclassified test examples into an LLM and ask it to surface systematic patterns (a specific confused label pair, short/low-info posts, sarcasm, etc.). I'll then **verify each suggested pattern by re-reading the examples myself** before it goes in the evaluation report — the LLM surfaces candidates, I confirm them.
