"""Dopisuje dzienny zrzut radaru i przebudowuje zbiorcze pliki CSV.

Użycie:  python3 narzedzia/dopisz.py <radar.json> [RRRR-MM-DD]
- zapisuje dni/<dzień>.json (ten sam dzień nadpisuje poprzedni zrzut z tego dnia),
- przebudowuje sygnaly.csv i wiadomosci.csv ze WSZYSTKICH plików w dni/.
Dzień domyślnie z pola "updated" (DD.MM.RRRR, GG:MM). Tylko biblioteka standardowa.
"""
import csv, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIG_KEYS = ["hy", "krzywa", "bezrobocie", "brent"]
CTX_KEYS = ["fed", "us10y", "btc", "zloto", "nbp"]


def day_of(d):
    m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", d.get("updated", ""))
    if not m:
        sys.exit("Brak poprawnego pola 'updated' (DD.MM.RRRR, GG:MM)")
    return f"{m[3]}-{m[2]}-{m[1]}"


def check(d):
    assert len(d["signals"]) == 4, "signals musi mieć 4 pozycje"
    assert len(d["context"]) == 5, "context musi mieć 5 pozycji"
    assert 1 <= len(d["news"]) <= 10, "news: 1–10 pozycji"
    for n in d["news"]:
        for k in ("date", "region", "title", "summary", "impact", "source", "url"):
            assert k in n, f"wiadomość bez pola {k}"


def main():
    src = sys.argv[1]
    d = json.load(open(src, encoding="utf-8"))
    check(d)
    day = sys.argv[2] if len(sys.argv) > 2 else day_of(d)
    os.makedirs(os.path.join(ROOT, "dni"), exist_ok=True)
    with open(os.path.join(ROOT, "dni", f"{day}.json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")

    days = sorted(glob.glob(os.path.join(ROOT, "dni", "*.json")))
    sig_rows, news = [], {}
    for p in days:
        dd = os.path.basename(p)[:-5]
        x = json.load(open(p, encoding="utf-8"))
        row = {"dzien": dd, "odswiezono": x.get("updated", "")}
        for k, s in zip(SIG_KEYS, x["signals"]):
            row[f"{k}_wartosc"] = s["value"]
            row[f"{k}_data"] = s["date"]
            row[f"{k}_stan"] = s["status"]
        for k, c in zip(CTX_KEYS, x["context"]):
            row[f"{k}"] = c["value"]
        row["alarmy"] = sum(s["status"] == "alarm" for s in x["signals"])
        sig_rows.append(row)
        for n in x["news"]:
            key = (n.get("url") or "").strip() or n["title"].strip().lower()
            if key not in news:
                news[key] = {"pierwszy_raz": dd, "ostatni_raz": dd, "dni_na_radarze": 0, **{
                    "data": n["date"], "region": n["region"], "tytul": n["title"],
                    "streszczenie": n["summary"], "wplyw": n["impact"], "zrodlo": n["source"], "url": n["url"]}}
            news[key]["ostatni_raz"] = dd
            news[key]["dni_na_radarze"] += 1

    with open(os.path.join(ROOT, "sygnaly.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sig_rows[0].keys()))
        w.writeheader(); w.writerows(sig_rows)
    cols = ["pierwszy_raz", "ostatni_raz", "dni_na_radarze", "data", "region", "tytul",
            "streszczenie", "wplyw", "zrodlo", "url"]
    with open(os.path.join(ROOT, "wiadomosci.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(sorted(news.values(), key=lambda r: (r["pierwszy_raz"], r["tytul"])))
    print(f"OK {day}: dni {len(days)}, wiadomości {len(news)}, alarmy dziś {sig_rows[-1]['alarmy']}")


if __name__ == "__main__":
    main()
