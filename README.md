# Pizza Random 🍕 #YOLO

Sito che sceglie a caso una pizza dal [menu di Pizza Marì](https://www.pizzamari.it/menu/), con voti e preferiti condivisi.

**Sito:** https://breight-code.github.io/pizza-random/

## Come funziona

- `menu.json` contiene la lista delle pizze. La aggiorna il workflow **Aggiorna menu** (`.github/workflows/aggiorna-menu.yml`), che parte **solo a mano**: dal pulsante "Aggiorna pizze" del sito o da GitHub → Actions. Si può avviare al massimo una volta ogni 24 ore.
- `scripts/scrape.py` legge la pagina del menu (sezioni, pizze del mese, ingredienti, prezzi, MAXI). Se la pagina cambia struttura e trova meno di 20 voci, si ferma senza toccare `menu.json`.
- `voti.json` contiene stelle e preferiti di ogni persona. Il sito lo aggiorna tramite l'API di GitHub, quindi ogni voto è un commit: la cronologia fa anche da backup.

## Chiave (token) per votare e aggiornare

1. GitHub → Settings → Developer settings → [Fine-grained tokens → Generate new token](https://github.com/settings/personal-access-tokens/new)
2. *Repository access*: **Only select repositories** → `pizza-random`
3. *Permissions*: **Contents** → Read and write, **Actions** → Read and write
4. Sul sito: ⚙️ Impostazioni → nome + token.

Il token resta solo nel browser di chi lo inserisce. Se si cancella la cache basta reincollarlo: i voti sono su GitHub.
