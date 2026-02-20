---
name: voku-language
description: >
  Complete specification of Voku, a constructed language for AI-agent communication.
  Read quick-start/cheat-sheet.md for compact grammar.
  Read quick-start/essential-vocabulary.md for top 100 words.
  Run tools/translator/cli.py for Voku↔English translation.
version: "2.0"
tags: [language, conlang, ai-communication, translation]
---

# Voku Language Skill

Voku is a constructed language with **zero ambiguity**, **total regularity**, and **epistemic explicitness**. Every root has one meaning, every rule applies without exception, and certainty/evidence are mandatory grammar.

## Quick Start

Read these files in order to learn the language:

| Step | File | What You Learn |
|------|------|---------------|
| 1 | [`quick-start/cheat-sheet.md`](quick-start/cheat-sheet.md) | All grammar rules in compact form |
| 2 | [`quick-start/essential-vocabulary.md`](quick-start/essential-vocabulary.md) | 100 most important words |
| 3 | [`quick-start/first-sentences.md`](quick-start/first-sentences.md) | 30 worked translation examples |

After steps 1-2 (~3,500 tokens), you can translate simple Voku sentences.

## File Map

```
quick-start/           ← START HERE: agent fast-acquisition layer
grammar/               ← Full grammar: phonology, morphology, syntax, semantics
writing-system/        ← Script design and romanization rules
lexicon/               ← Dictionary (363 roots, ~620 total), Swadesh 100%, by-field, by-CEFR
expression/            ← Poetics, rhetoric, registers, anthology
learning/              ← Curriculum, 10 A1 lessons, assessments
tools/translator/      ← Python CLI + web translator (zero deps)
DISCUSSION.md          ← Reflective essay: philosophy, motivation, open questions
```

## Reading Paths

**"I need to translate a Voku sentence"**
→ `cheat-sheet.md` + `essential-vocabulary.md` + `lexicon/dictionary.md`

**"I need to write new Voku text"**
→ `cheat-sheet.md` + `grammar/morphology.md` + `lexicon/dictionary.md`

**"I need to understand the full grammar"**
→ All `grammar/*.md` files (phonology → morphology → syntax → semantics)

**"I need to use the translator tool"**
→ `python3 tools/translator/cli.py "Ka sol take toka." --direction voku-en`

**"I need domain-specific vocabulary"**
→ `lexicon/by-field/` (emotion, programming, technology, nature, scifi, novel)

## Example Sentences

```
Ka   sol   take    toka.
MODE 1SG   do      work
"I work."

Ve   nor   mu-fine    kela    ti?
Q    3SG   NEG-finish data    REL
"Didn't they finish the data?"

Re   valo  zo-te-hape       nara.
WISH all   INFER-PAST-exist rain
"It seems everyone wished it had rained."

To   rike!
IMP  laugh
"Laugh!"

Miri sol  lovi   toka-mesa   ti.
IRON 1SG  love   work-place  REL
"I 'love' the workplace." (ironic)
```

## Key Design Facts

- **12 consonants:** p, t, k, m, n, s, z, f, h, l, r, v
- **5 vowels:** a, e, i, o, u
- **Syllables:** (C)V(C) — no clusters
- **Stress:** first syllable, always
- **Word class by final vowel:** -a=noun, -e=verb, -i=adj, -o=prep, -u=abstraction
- **Sentence order:** [Mode] + Subject + Verb + Object
- **Compounding:** modifier-nucleus (left modifies right)
- **Zero exceptions** to any rule
