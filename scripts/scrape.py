#!/usr/bin/env python3
"""Legge il menu di pizzamari.it e scrive menu.json.

Uso: scrape.py [file_html_locale] [--out menu.json]
Senza file scarica la pagina.
"""
import json, re, sys, urllib.request, datetime, unicodedata
from html.parser import HTMLParser

URL = "https://www.pizzamari.it/menu/"
PRICE = re.compile(r"€\s*(\d+[.,]\d{2})")
BLOCK = {"p", "li"}
HEAD = {"h1", "h2", "h3", "h4", "h5"}


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.events = []          # ("head", level, text) | ("block", [lines])
        self.cur = None           # current block or heading collector
        self.kind = None
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        elif tag in HEAD:
            self.flush(); self.kind = ("head", int(tag[1])); self.cur = [""]
        elif tag in BLOCK:
            self.flush(); self.kind = ("block",); self.cur = [""]
        elif tag == "br" and self.cur is not None:
            self.cur.append("")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.skip = max(0, self.skip - 1)
        elif tag in HEAD or tag in BLOCK:
            self.flush()

    def handle_data(self, d):
        if self.skip or self.cur is None:
            return
        self.cur[-1] += d

    def flush(self):
        if self.cur is None:
            return
        lines = [re.sub(r"\s+", " ", l).strip() for l in self.cur]
        lines = [l for l in lines if l]
        if lines:
            if self.kind[0] == "head":
                self.events.append(("head", self.kind[1], " ".join(lines)))
            else:
                self.events.append(("block", lines))
        self.cur = None; self.kind = None


def nice(name):
    return name[:1].upper() + name[1:].lower() if name.isupper() else name


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def num(s):
    return float(s.replace(",", "."))


def parse(html):
    p = P(); p.feed(html); p.flush()
    sezione, sotto = None, None
    pizze, viste = [], set()
    for ev in p.events:
        if ev[0] == "head":
            lvl, txt = ev[1], ev[2]
            if lvl <= 2:
                sezione, sotto = txt, None
            else:
                sotto = txt
            continue
        lines = ev[1]
        if sezione is None or len(lines) < 2:
            continue
        pidx = next((i for i, l in enumerate(lines) if PRICE.search(l)), None)
        if pidx is None or pidx == 0:
            continue
        nome = nice(lines[0].strip(" :-"))
        ingredienti = ", ".join(lines[1:pidx]).strip()
        prezzi = [num(x) for x in PRICE.findall(" ".join(lines[pidx:]))]
        maxi = None
        m = re.search(r"maxi\s*€\s*(\d+[.,]\d{2})", " ".join(lines[pidx:]), re.I)
        if m:
            maxi = num(m.group(1))
        key = (sezione, nome.lower())
        if key in viste:
            continue
        viste.add(key)
        pizze.append({
            "id": slug(f"{sezione}-{nome}"),
            "nome": nome,
            "sezione": sezione,
            "sottosezione": sotto,
            "ingredienti": ingredienti,
            "prezzo": prezzi[0] if prezzi else None,
            "maxi": maxi,
        })
    return pizze


def main():
    args = sys.argv[1:]
    out = "menu.json"
    if "--out" in args:
        i = args.index("--out"); out = args[i + 1]; del args[i:i + 2]
    if args:
        html = open(args[0], encoding="utf-8", errors="replace").read()
    else:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (pizza-random)"})
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    pizze = parse(html)
    if len(pizze) < 20:
        sys.exit(f"Trovate solo {len(pizze)} voci: la pagina e' cambiata? Non sovrascrivo menu.json")
    data = {
        "aggiornato": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "fonte": URL,
        "pizze": pizze,
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"OK: {len(pizze)} voci scritte in {out}")


if __name__ == "__main__":
    main()
