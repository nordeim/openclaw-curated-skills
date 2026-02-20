# CAN: Clock Address Naming

NAMING + ROUTING for agents. Clock Address Name things by WHEN, WHERE, HOW, WHO, WHY. Say what you see. LOG what you SAW.

## What CAN does

1. **STAMP** — hash any thing, record WHEN and WHO
2. **NAME** — give it human-readable names (HOW), tag intent (WHY)
3. **STORE** — cache by hash in `~/.can/store/`
4. **FIND** — locate by time, hash, name, tag
5. **ROUTE** — local store → peers → relay → web
6. **SAW** — LOG verified things as routing hints for future agents
7. **CANT** — LOG rejected things to protect future agents from fakes

## Requirements

`sha256sum` (pre-installed on most Linux; use `shasum -a 256` on macOS). WHO-1 signing uses `openssl` (pre-installed on most systems). Also uses `awk`, `date`, `base64` — standard on Linux and macOS. No npm. No pip. No runtime. Works air-gapped.

## Quick start

```bash
# Stamp a thing
CLOCK=$(date +%s%3N)
HASH=$(sha256sum myfile.txt | awk '{print $1}')
echo -e "$CLOCK\t$HASH\tmyfile.txt\tSAVE\t$(cat ~/.can/who.id)\t$(pwd)/myfile.txt" >> ~/.can/index.tsv

# Find by name
grep "myfile" ~/.can/index.tsv

# Find by time (today)
TODAY=$(date +%s)000
awk -F'\t' -v t="$TODAY" '$1 >= t' ~/.can/index.tsv
```

## Index format

Six columns, tab-separated:

```
WHEN    WHERE    HOW    WHY    WHO    PATH
```

- **WHEN** — millisecond timestamp (CLOCK)
- **WHERE** — SHA-256 hash (address)
- **HOW** — human-readable name or SAW type (verified:peer, cached:relay)
- **WHY** — intent bag (SAVE, GOOD, HUSH, POST, CANT)
- **WHO** — identity tier (WHO-0 machine fingerprint, WHO-1 keypair, WHO-2 external auth)
- **PATH** — local filesystem path (convenience, least trustworthy column)

## WHO identity tiers

- **WHO-0** (free, automatic) — `sha256(username + machine-id)`. Zero config.
- **WHO-1** (opt-in) — Ed25519 keypair in `~/.can/who.key`. Self-signed. Back up your key.
- **WHO-2** (auth upgrade) — Nostr (NIP-07), Farcaster, OAuth. Portable, externally verifiable.

## CAN do NDN

CAN collapses Van Jacobson's three NDN tables (Content Store, Pending Interest Table, Forwarding Information Base) into one index. 3x simpler. Same math.

## Roadmap

```
v1.3.2  DONE   naming + routing + bags + HUSH + scoped locate
v1.4    DONE   WHO: free machine-id + auth upgrade path
v1.5    LOG    SAW: say what you see, LOG what you saw
v1.6    TRUST  WOT: web of trust, recursive scope
v1.7    GOGO   ROOT: stack threads from root to FIN (merkle)
v1.8    LOL    expiry EOL gg a) game-over or b) insert-coin
v1.9    MEME   what else are ya gonna do?
v2.0    BUMP   humans in the CAN
```

## References

- Paul Baran, On Distributed Communications (RAND, 1964)
- Phil Zimmermann, Pretty Good Privacy (PGP, 1991)
- Van Jacobson, A New Way to Look at Networking (Google Tech Talk, 2006)
- John Day, Recursive InterNetwork Architecture (RINA)
- Linus Torvalds, Git content-addressable object store
- Zooko's Triangle (CAN amplifies the petnaming solution)

## TL;DR

```
HASH thing
TIME when
WHO says
INDEX ()) <- in the CAN
OWN things.
SAW logs.
```
