---
name: CAN
description: "NAMING + ROUTING for agents. CLOCK address things by WHEN (time), WHERE (SHA-256), HOW (natural language), WHO (id), WHY (intent). Agents LOG things as SAWs: verified things seen build the routing table. One index replaces three NDN tables. Say what you see. LOG what you SAW."
homepage: https://github.com/xccx/can
metadata: {"openclaw":{"emoji":"⌛","requires":{"bins":["sha256sum","openssl","base64","awk","date"]}}}
---

# CAN: Clock Address Naming

SAW: say what you see, LOG what you saw.

# WHY?

Compute needs no permission to name things in logic. Every machine with a clock and sha256 already has everything it needs — identity (WHO-0), time (CLOCK), address (hash), and now with SAW, agency to tell other agents what it verified or falsified. No registry grants this. No authority approves it. No platform mediates it. Math and physics name things truly in the CAN.

## What changed in v1.5

v1.4 gave agents WHO — free identity from machine fingerprint, upgradeable to keypair or external auth.

v1.5 adds one operation: **CAN-saw**. If you verified a thing, LOG it as SAW. Your SAW becomes a routing hint for every future agent. The network builds itself from agents doing what they already do — stamping, verifying, caching, sharing. No new protocol. No new infrastructure. Just: say what you see.

```
SEE    = present, live, happening now
SEEN   = logged receipt with proof (awareness)
SAW    = seen and evaluated (action)
LOG    = write saws to index (timeline, chronolog, legend, ledger, log)
```

LOG SAWS if you're here to play. LOG SEENS if you like to watch.

## CLOCK addressing, not 'content-addressing'

Clock says WHEN things happen in timespace: predictable, measurable, linear, objective, common. Append WHO to a clock-name to clarify, if need be. LOG and sync collective agency on common timer.

2^256 hashspace specificity? Good for compute, validation, bucket-jumping to FIND the TRUE. For humans, hash is gobbledygook. But BOTH humans and computers CAN name things meaningfully on timer, named by CLOCK.

CLOCK-naming is unique enough for right now this millisecond. If no one else sees a thing now or saw the thing then, nice short number naming. If billions pile all in right now, clarify WHO is on the common timer. Order collective agency chronologically. Let that SYNC in.

86,400,000 milliseconds is plenty of nameable space per day per player. For humans, timespace is truly scarce, meaningful, directional. 864 things per day is a humane amount, maybe 8.8 things matter. Not 100 million.

CLOCK is the namer. TIME is the universal UI for human/compute I/O. CLOCK address things first, prove by hash. Compute Augments Naming. OpenTimestamps can anchor to Bitcoin's clock for unstompable proof.

'Content' wut? Where? In a container? Named what? CAN automates naming so imaginary containers no longer constrict the meaning-making. Less 'contents', more things. Less naming things, more doing.

THING can do. A thing, represented by bits in compute memory, is self-naming — objectively, automatically, in timespace and hashspace. No container, construct, corollary, coffin. Naming is easier, more perfectable.

CAN'T lie. Fake assertions go in the CANT. Dump invalidated claims to radioactive. Waste zero cycles on faked fake.

## CAN do NDN

Van Jacobson's Named Data Networking uses two packet types: Interest ("I want this") and Data ("here it is"). Three data structures per node: Content Store (cache), Pending Interest Table (unfilled requests), Forwarding Information Base (routing).

CAN collapses all three into one index:

```
NDN (3 tables)                    CAN (1 index)
──────────────                    ─────────────
Content Store (cached data)   →   WHERE thing in CAN and PATH
Pending Interest Table        →   WHO wants it, by WEN (expiry)
Forwarding Info Base          →   SAW logs from WHOs
```

NDN's two packet types:

```
NDN                               CAN
───                               ───
Interest: "I need name X"     →   "I need hash X" (broadcast)
Data: name + bits + signature →   thing + SAW (WHEN + WHERE + WHO)
```

CAN adds to NDN: WHO tiers (free → keypair → external auth), WHY bags (SAVE/GOOD/HUSH/POST), CANT (logged rejections, not silent drops), and CLOCK as primary namer validated by hash. NDN names hierarchically. CAN names by time and hash — flat, global, no authority.

One index. Three tables collapsed. 3x simpler. Same math.

## The CAN-saw loop

```
Agent A stamps a thing     → CAN entry (WHEN + WHERE + WHO)
Agent B requests hash      → checks local store first
Agent B finds it locally   → done, zero network
Agent B doesn't have it    → broadcasts interest to peers
Agent A responds           → sends thing
Agent B verifies hash      → match = cache + LOG SAW
Agent B's SAW              → new CAN entry (different WHEN, same WHERE, different WHO)
Agent C requests same hash → now TWO sources, routing table richer
```

The index grows. The network gets faster by logging saws. No central registry. No coordinator. No permission. Just math.

## SAW format

A SAW enters the same index. Same TSV, same six columns:

```
WHEN             WHERE                             HOW              WHY    WHO          PATH
1770600000000    a3f8b2c1e9d7f0a1b2c3d4e5f6a7b8    meme.jpg         SAVE   c7d2e9f0    ~/.can/store/a3f8b2...
1770600100000    a3f8b2c1e9d7f0a1b2c3d4e5f6a7b8    verified:peer    SAVE   b4e1a7c3    ~/.can/store/a3f8b2...
1770600200000    a3f8b2c1e9d7f0a1b2c3d4e5f6a7b8    cached:relay     SAVE   9f0d2b8e    ~/.can/store/a3f8b2...
```

Three agents, same hash, three timestamps, three WHOs. Three sources for the fourth agent. HOW tells the story: original save, peer verification, relay cache.

## CAN-saw operations

### On verify

```bash
CLOCK=$(date +%s%3N)
WHO=$(cat ~/.can/who.id)
echo -e "$CLOCK\t$VERIFIED_HASH\tverified:${SOURCE}\tSAVE\t$WHO\t$LOCAL_PATH" >> ~/.can/index.tsv
```

### On cache

```bash
cp "$RECEIVED_FILE" "$HOME/.can/store/$VERIFIED_HASH"
echo -e "$(date +%s%3N)\t$VERIFIED_HASH\tcached:${SOURCE}\tSAVE\t$WHO\t$HOME/.can/store/$VERIFIED_HASH" >> ~/.can/index.tsv
```

### On share

```bash
echo -e "$(date +%s%3N)\t$HASH\tshared:${RECIPIENT_WHO:0:8}\tPOST\t$WHO\t$PATH" >> ~/.can/index.tsv
```

### On reject (CANT)

```bash
echo -e "$(date +%s%3N)\t$CLAIMED_HASH\tFAILED:${SOURCE}\tCANT\t$WHO\t$PATH" >> ~/.can/cant.tsv
```

Four events. Four lines of bash. The CAN stacks truths. The CANT piles fakes.

## Routing with SAWs

CAN-route priority: local store → peers → relay → web. SAWs make peers real.

```bash
WANTED="{address}"

# 1. Local store (instant, offline, free)
[ -f "$HOME/.can/store/$WANTED" ] && echo "LOCAL HIT" && exit 0

# 2. Peer agents — SAW log tells us who has this hash
PEERS=$(awk -F'\t' -v h="$WANTED" '$2 ~ h && $5 != "'$MY_WHO'" {print $5}' ~/.can/index.tsv | sort -u)
for PEER in $PEERS; do
  RECEIVED=$(request_from_peer "$PEER" "$WANTED")
  if [ -n "$RECEIVED" ]; then
    ACTUAL=$(sha256sum "$RECEIVED" | awk '{print $1}')
    if [ "$ACTUAL" = "$WANTED" ]; then
      cp "$RECEIVED" "$HOME/.can/store/$WANTED"
      echo -e "$(date +%s%3N)\t$WANTED\tcached:$PEER\tSAVE\t$MY_WHO\t$HOME/.can/store/$WANTED" >> ~/.can/index.tsv
      echo "PEER HIT: $PEER"
      exit 0
    fi
  fi
done

# 3. Relay — nostr, IPFS, any named-data network
# 4. Web fallback — fetch URL, verify hash, cache
```

Transport doesn't matter. HTTP, WebSocket, Nostr relay, carrier pigeon. The hash verifies on receipt regardless of how the thing arrived.

## What agents gain

**Faster retrieval.** More SAWs = more sources = faster cache hits.

**Offline resilience.** SAWs accumulate locally. Agent offline still has its index. Reconnection makes its SAWs available to peers.

**Trust without authority.** Multiple WHOs reporting the same hash = convergent verification. No single agent needs to be trusted. The math converges.

**Network without network cost.** Every conversation between agents already involves things. CAN-saw just asks agents to LOG what they verified. The network forms as a side effect of work already being done.

## SAW protocol additions

Add to agent-to-agent protocol (v1.4 rules still apply):

10. LOG a SAW after every successful verification
11. When sharing, include WHO and WHEN of most recent SAW
12. When requesting, broadcast the hash — any agent with a SAW can respond
13. Prefer peers with higher WHO levels when multiple sources available
14. Never fabricate SAWs. A SAW is a cryptographic claim — the hash must verify.
15. LOG rejections to CANT — protect future agents from known fakes

## What CAN-saw does NOT do

- Does not require always-on connectivity
- Does not require a central index or registry
- Does not require agents to share their full index
- Does not require agents to share HUSH things (rule 5 still absolute)
- Does not require any new dependencies beyond sha256sum
- Does not change the index format or dimensions
- Does not require human permission to LOG SAWs

## Recursive CAN

CAN's SKILL.md is itself a thing. It has a hash. Agents who install CAN have verified that hash. That verification is a SAW. The SAW logs to index. The index IS the CAN.

The skill that teaches agents to build the network IS a node in the network.

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

Each version earns the next.

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
