"""
Apply Claude's first-pass (pre-)labels to candidates.csv -> candidates_prelabeled.csv.

These labels were assigned by Claude in-session by reading each candidate and
applying the planning.md rubric (precedence: evidence > logic > emotion). They
are a PROVISIONAL first pass; every label is to be reviewed/corrected by the
human annotator. The `notes` column records "prelabeled:claude" for disclosure.

Code -> label:
  ea   = evidenced_analysis
  ls   = logical_speculation
  es   = emotional_sentiment
  skip = not a take (pure news repost / automod / off-topic) -> excluded from the
         labeled set; kept in the CSV with label "skip" so the human can override.
"""

import csv

CODE2LABEL = {
    "ea": "evidenced_analysis",
    "ls": "logical_speculation",
    "es": "emotional_sentiment",
    "skip": "skip",
}

PRELABELS = {
    # ---- posts ----
    "1u287z4": "skip", "1tx30lf": "ea", "1ub1qvj": "skip", "1trm7oc": "es",
    "1tvud2t": "ls", "1u33yms": "es", "1u9hqcu": "es", "1txr3nd": "ls",
    "1u417vx": "ls", "1u3g4s9": "ea", "1u80mp7": "es", "1tv5ykp": "ea",
    "1u3vcow": "ea", "1txtobk": "es", "1u7eoli": "skip", "1tn0giy": "ls",
    "1tyc3dq": "es", "1todfhu": "skip", "1u7jhyx": "ls", "1u5xqoa": "skip",
    "1tod7ce": "ls", "1u6payq": "ls", "1u2ozc6": "ls", "1tn8pcy": "ea",
    "1u3hylp": "ls", "1u1ms9n": "ls", "1u8sr16": "ls", "1u9x42q": "ea",
    "1tp80yw": "ea", "1u90d1y": "ls", "1typ4hv": "skip", "1u4v5va": "ls",
    "1u15r8v": "ls", "1txa2d2": "skip", "1u5yjg5": "ea", "1u1arec": "ls",
    "1trzt9l": "ea", "1tupsgk": "ls", "1twvxhq": "skip", "1u63g6o": "skip",
    "1u2cbzm": "es", "1ts88sd": "skip", "1tzj0i5": "ls", "1tqgvb5": "ls",
    "1tm9qu6": "ls", "1tu5v0n": "skip", "1tttxjr": "skip", "1tufw5a": "skip",
    "1tqq8vh": "es", "1ub8yux": "ls", "1tvswrl": "es", "1tqhnwo": "ea",
    "1u6rxoq": "ea", "1u9ag33": "ea", "1tyqb8t": "ls", "1u09ymq": "ls",
    "1toqa3x": "skip", "1tv4t55": "skip", "1tq7dbq": "es", "1tzxxvu": "ls",
    "1u5ct14": "es", "1tw27pr": "skip", "1u6wzx7": "ls", "1u36ain": "skip",
    "1ts1765": "es", "1u1aual": "skip", "1u4adsn": "skip", "1tyudcz": "skip",
    "1u6f1cc": "skip", "1tqlm5o": "ls", "1ty1916": "ls", "1u3y0eb": "skip",
    "1u08349": "ls", "1twd71e": "ls", "1tpz97p": "ls", "1u0f262": "skip",
    "1tzb2f6": "ls", "1toewek": "ls", "1tucwha": "skip", "1u7nuyb": "skip",
    "1uc1hwn": "ea", "1tob8md": "ls", "1tnx461": "ls", "1u0q7b0": "skip",
    "1uaacua": "skip", "1ttccux": "ls", "1tpqfg0": "skip", "1u3gvs5": "skip",
    "1tomixx": "es", "1u8l1z2": "skip", "1tufk7m": "skip", "1touet5": "ls",
    "1u45ebg": "skip", "1u1faxs": "ls", "1ubo4yf": "ls", "1trk1a8": "es",
    "1u4q9wf": "es", "1u38c7y": "ls", "1u9i1kz": "skip", "1twq323": "skip",
    "1qivvl0": "skip", "1th6vv8": "skip", "1qkcgws": "skip", "1mjhjv6": "skip",
    "1r9xpm4": "skip", "1ohn70r": "es", "1pidr40": "es", "1nm9pun": "skip",
    "1o3d10v": "skip", "1mf49mh": "skip", "1rpabjj": "skip", "1oen217": "skip",
    "1qi1y6p": "skip", "1nxbr66": "skip", "1qnowp0": "skip", "1r3vrja": "skip",
    "1rjgwsz": "es", "1qai9nf": "es", "1o4weu2": "es", "1slqarf": "ea",
    "1s07g52": "skip", "1m1frce": "skip", "1ou3xj9": "skip", "1pa7fpl": "es",
    "1of85md": "skip", "1q33k1v": "ls", "1qlop6t": "skip", "1nm33ll": "ls",
    "1sofb6a": "ls", "1ncp6wl": "skip", "1sry062": "skip", "1qr4xcl": "ls",
    "1octyv8": "skip", "1ra3xio": "skip", "1sfz9ct": "es", "1sry5dm": "es",
    "1rlqxo4": "skip", "1ooi0vb": "ls", "1mnlj21": "skip", "1lvjd1q": "skip",
    "1sjf29j": "skip", "1q7i3am": "skip", "1s7ppni": "ls", "1q6yzus": "skip",
    "1s1l6s9": "es", "1s90075": "skip", "1mevctp": "skip", "1rs76f8": "es",
    "1o7pjzr": "skip", "1lu5g5m": "ls", "1nyz3nz": "ls", "1oaf6tg": "skip",
    "1p39cmr": "skip", "1lo8vug": "skip", "1rfjeq4": "skip", "1qel32s": "skip",
    "1nhnjwm": "skip", "1o1ioby": "ls", "1qdd0iu": "ls", "1ojf9mj": "skip",
    "1m8q42q": "ls", "1n47cuu": "es", "1lriebt": "skip", "1ny7ylt": "skip",
    "1p5mo6h": "skip", "1nhm2n2": "ls", "1rz6h5y": "ls", "1oic1z0": "skip",
    "1mcbijm": "ls", "1qwxret": "skip", "1sle4si": "ls", "1s883ul": "ls",
    "1r72nva": "skip", "1sewljl": "ls", "1ohfc9l": "skip", "1q6o0na": "skip",
    "1qj84vr": "skip", "1nlmydw": "es", "1s5dtzs": "es", "1rh0u8r": "skip",
    "1qhhuh3": "skip", "1opw2ee": "es", "1nsrmnk": "ls", "1mewdtd": "skip",
    "1n6ukgk": "skip", "1rzdjiv": "ls", "1pcsjmc": "skip", "1qwkyvn": "es",
    "1q058cv": "es", "1s1ivqi": "es", "1lm0jch": "skip", "1q14hbk": "ea",
    "1p2dl13": "ls", "1odbs83": "skip", "1ucvuqt": "skip", "1ucqxip": "ls",
    "1ucj1kk": "skip", "1ucmier": "ls", "1ud0ya3": "ls", "1ucp36c": "ls",
    "1ucv4fr": "skip", "1uckw79": "ls", "1uczxy4": "ls", "1uca77q": "skip",
    "1ubzl4l": "ls", "1ucylw6": "ls", "1ucs046": "ls", "1ucky2y": "ls",
    "1ubw0yf": "ls", "1ucn34p": "skip", "1ucwnml": "ls", "1uclno1": "ls",
    "1ucabem": "ls", "1ubpphg": "skip", "1uberrm": "ls", "1uch4xu": "ls",
    "1uch9ck": "skip",
    # ---- comments ----
    "nt5a2ka": "es", "nt5c3v9": "ls", "nt5bhsk": "ls", "nt5anjg": "ls",
    "nt5d0pz": "ls", "nt5exvs": "ls", "nt5b6eq": "es", "nt5f771": "ls",
    "n7bmbik": "skip", "n7b3pk2": "ls", "n7b5414": "es", "n7b3xlv": "ls",
    "n7b5qnu": "ls", "n7b4pux": "es", "n7b49wb": "es", "n7b9f4q": "ls",
    "o8d3s8x": "ls", "o8d3v8d": "ls", "o8d53nt": "ls", "o8d3l9x": "ls",
    "o8d70vd": "es", "o8d7ds3": "ls", "o8f9nrb": "es", "o8d7nsx": "ls",
    "os4ltkx": "ls", "os4kc7n": "ls", "os4jzjp": "ls", "os4jzkl": "ls",
    "os4kb9p": "ls", "os4kebu": "ls", "os4qms7": "ls", "os4n7eq": "ls",
    "niv3yga": "skip", "niuakhw": "es", "niu9ab1": "ls", "niuafco": "es",
    "niu967i": "es", "niui9g3": "es", "niu9b0g": "es", "niu9nog": "skip",
    "nlp51id": "ls", "nlp4g90": "ls", "nlsvdzz": "es", "nlp4eo4": "ls",
    "nlp4muq": "skip", "nlp7v2p": "ls", "nlp7rje": "ls", "nlsvyu6": "es",
    "omlmfr6": "skip", "oml714k": "es", "oml18di": "es", "oml740z": "ls",
    "oml1n87": "es", "oml1jtl": "ls", "oml3jjv": "es", "oml7hta": "ls",
    "nxhosku": "skip", "nxhpsut": "es", "nxhr1af": "ls", "nxhvmz4": "ls",
    "nxhrrhp": "ls", "nxhpr9u": "ls", "nxhrjmu": "ls", "nxhqkt4": "ls",
    "o9krddu": "skip", "o9jnfjz": "es", "o9jkocv": "ls", "o9jlka4": "ls",
    "o9jlmis": "ls", "o9jns5s": "es", "o9jmnym": "es", "o9jnq62": "es",
    "ooonxbm": "ls", "ooopcy6": "ls", "ooopktz": "ls", "oooqveb": "ls",
    "ooozmlf": "ls", "oooo607": "es", "ooopaot": "ls", "ooooio4": "ls",
    "or2a4q3": "es", "or2bmcc": "es", "or2q6ye": "ls", "or2edui": "ls",
    "or2bwwv": "ls", "or2d9vb": "es", "or2cacg": "ls", "or29z96": "es",
    "o0ulfwd": "skip", "o0ul58g": "es", "o0ucqzi": "es", "o0u9qn6": "ls",
    "o0ugu7a": "ls", "o0ucck7": "es", "o0ulmvi": "ls", "o0ufnf6": "ls",
    "octsuu4": "es", "octv3bb": "ls", "octtd1s": "ls", "octwyw5": "es",
    "octsi8v": "es", "octtaat": "ls", "ocuii47": "ls", "octw6al": "ls",
    "nzouwgo": "skip", "nzowc9y": "ls", "nzpjbcg": "ls", "nzoyh3r": "ls",
    "nzovk1p": "es", "nzp7rif": "ls", "nzpyy14": "ls", "nzp3c5v": "ls",
    "og8lpbo": "ls", "og8kmdb": "ls", "og8oxzs": "ls", "ogbee8y": "es",
    "og8opov": "ls", "og8n92w": "es", "og8n5nc": "es", "og8n0yv": "ls",
    "o1fka7g": "skip", "o1fkyra": "es", "o1fltk6": "es", "o1fl6sh": "es",
    "o1fmsbg": "ls", "o1fldyh": "es", "o1flrrk": "ls", "o1fn4u2": "es",
    "opyel7r": "ls", "opyij7h": "es", "opydhlo": "ls", "opyeki3": "es",
    "opyesuv": "ls", "opyf89i": "es", "opyfcod": "ls", "opyegli": "ls",
    "osgeurb": "es", "osgcqyj": "ls", "osgc1gr": "ls", "osgeu8o": "es",
    "osgcwh1": "ls", "osgemgq": "es", "osgcv7o": "ea", "osgc1s5": "ls",
}


def main():
    rows = list(csv.DictReader(open("candidates.csv", encoding="utf-8")))
    missing = [r["id"] for r in rows if r["id"] not in PRELABELS]
    if missing:
        print(f"WARNING: {len(missing)} ids have no prelabel: {missing[:10]}")

    counts = {}
    with open("candidates_prelabeled.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "type", "score", "permalink", "text", "label", "notes"])
        w.writeheader()
        for r in rows:
            code = PRELABELS.get(r["id"], "skip")
            label = CODE2LABEL[code]
            counts[label] = counts.get(label, 0) + 1
            r["label"] = label
            r["notes"] = "prelabeled:claude"
            w.writerow(r)

    total_takes = sum(v for k, v in counts.items() if k != "skip")
    print("Pre-label distribution:")
    for k in ("evidenced_analysis", "logical_speculation", "emotional_sentiment", "skip"):
        n = counts.get(k, 0)
        if k == "skip":
            print(f"  {k:<22} {n}")
        else:
            pct = 100 * n / total_takes if total_takes else 0
            print(f"  {k:<22} {n:>3}  ({pct:.0f}% of {total_takes} takes)")


if __name__ == "__main__":
    main()
