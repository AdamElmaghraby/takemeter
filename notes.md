# Planning Notes

## Community Context

The chosen community is r/stocks, a public forum where retail investors gather to discuss equity markets and portfolio strategies. This space features a highly volatile mix of discourse, ranging from data-heavy institutional-grade research to reactionary panic-selling rants. Distinguishing between these styles matters deeply to members of this community because separating actual evidentiary signal from unverified speculative narratives and emotional market noise is the direct difference between making calculated, profitable investments or suffering catastrophic financial losses.

## Label Taxonomies and Specifications

### 1. evidenced_analysis

**One-Sentence Definition:** The post supports its core investment thesis using verifiable quantitative data, historical market precedents, SEC filings, analyst ratings, or specific fundamental metrics.

**Clear Example A (Klaviyo Deep Dive)**
> "Company: Klaviyo | Ticker: KVYO | Market cap: $4 billion USD... 2025 revenue: Roughly $1.2 billion | 2026 revenue guidance: Roughly $1.55 billion... Non-GAAP operating margins at roughly 14-15%, while gross margins are at 75%... Q1 results (28% growth)... In q1 they reported 38% YoY growth in their enterprise segment..."

**Clear Example B (Citi Figma Analyst Coverage)**
> "A Citi analyst initiated coverage on Figma today with a Buy rating and a $36 price target, implying roughly 80% upside from current levels... FIG is down over 50% TYD despite accelerating growth. Q1 revenue grew 46% YoY and guidance was raised."

**The Uncertain Case (The $RDDT Post)**
- *The Text:* The long post analyzing Reddit's business model, mentioning 50 million DAU, a historical reference to Twitter's $500 million data licensing revenue in 2021, and its current $33 billion valuation.
- *Why it's ambiguous:* It includes specific figures ($500M, 50M DAU, $33B valuation), which flirts with evidenced_analysis. However, the core of the argument relies on qualitative, subjective assessments of ad aesthetics ("ads look and feel spammy") and user behavior patterns ("subreddit visits do not equate to purchase intent").
- *The Decision Rule:* To qualify as evidenced_analysis, the quantitative data must directly validate the core thesis via financial metrics or official reports. Because this post uses a few scattered data points to anchor a broader, unverified thesis on advertiser psychology, it is classified as logical_speculation.

---

### 2. logical_speculation

**One-Sentence Definition:** The post presents a structured, internally coherent financial narrative or structural argument that sounds logical, but relies primarily on personal assumptions, macro theories, or chart technicals rather than verifiable accounting data or external sources.

**Clear Example A (MSFT/SaaS Value Trap)**
> "This stock is headed to $300 soon. Co pilot is a failure, openAI is sketchy and very unprofitable... Chart also look really bad on daily weekly and monthly timeframes... To me, MSFT is now in that value trap territory, similar to NKE or PYPL in that sense. P/E ratio is low, sure! But the street also knows that growth is likely to slow..."

**Clear Example B (Power Grid Macro Reply)**
> "It's not just new load growth, most of the North American power grid was built in the 1960s and 1960s. Regardless of data centres and electrification... the baseline case still requires massive grid investments."

**The Uncertain Case (The Micron/$MU Dynamic)**
- *The Text:* The post asserting that Micron will hit $1500 by Q4 due to an HBM supply crunch, referencing contracted capacity through 2027, but heavily interwoven with high-intensity prose ("traumatized by historical boom and bust", "math staring them in the face").
- *Why it's ambiguous:* It makes a valid structural point about supply-demand dynamics and contracted revenue, but the tone is incredibly intense and borders on hyperbole ($1500 target on an active $1100 range).
- *The Decision Rule:* If a post presents valid macroeconomic or industry-level structural logic (like the physical constraints of HBM production), it remains speculation rather than pure emotion. Tone alone does not disqualify logic. Therefore, it is classified as logical_speculation.

---

### 3. emotional_sentiment

**One-Sentence Definition:** The post expresses raw feelings, momentum bias (FOMO/panic), personal lifestyle anecdotes, or immediate psychological reactions to market moves with minimal analytical structure.

**Clear Example A (The Overwhelming Gut Panic)**
> "I know I'm gonna get so much shit for this but I don't care. I was 70% VT 30% SGOV and I sold my market positions... I just see splinters everywhere. The cap gain hit will suck but when I dump it all back once we enter the 30-40% correction I think is coming, it will pay off... sometimes your gut is overwhelming and you should listen."

**Clear Example B (Standard Short-Form Hype/Fear)**
> "NVDA to the moon baby 🚀🚀 completely unhinged green day, bears are absolutely crying in shambles right now, doubling down on my calls at open tomorrow!"

**The Uncertain Case (The Aggressive Venting Post)**
- *The Text:* A user tracking their exact partial shares while heavily defensive about their personal background ("bear in mind that I am a graduate student... graduate student at MIT to be more specific since it seems that certain people care about whether I come from a prestigious institution or not").
- *Why it's ambiguous:* The text tracking exact portfolio stakes looks like data, and the defensive context is entirely a personal social critique rather than financial data.
- *The Decision Rule:* When a post's primary real estate is spent defending the author's ego, intelligence, or emotional state rather than evaluating the security itself, it fails the structural threshold of a logical argument. It is classified as emotional_sentiment.
