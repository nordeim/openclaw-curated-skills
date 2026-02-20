# Voku Cheat Sheet

> Complete grammar reference for AI agents. After reading this file (~800 lines),
> you can parse and generate valid Voku sentences.

---

## 1. Sound System

### Consonants (12)

| Manner        | Bilabial | Labiodental | Alveolar | Velar | Glottal |
|---------------|----------|-------------|----------|-------|---------|
| Plosive       | p        |             | t        | k     |         |
| Nasal         | m        |             | n        |       |         |
| Fric. (vless) |          | f           | s        |       | h       |
| Fric. (voiced)|          | v           | z        |       |         |
| Lateral       |          |             | l        |       |         |
| Trill/Tap     |          |             | r        |       |         |

### Vowels (5)

```
        Front     Back
Close    i         u
Mid      e         o
Open        a
```

### Syllable Rule

**(C)V(C)** -- no consonant clusters anywhere. Every consonant separated by a vowel.

- Shapes: V, CV, VC, CVC
- Dominant pattern: CV (open syllables)
- Content words always end in a vowel

### Stress

Always on the **first syllable**. No exceptions.

### Romanization

1:1 mapping. Each letter = one phoneme. No digraphs, no diacritics, pure ASCII.

---

## 2. Word Classes (Final-Vowel System)

Content words are classified by their final vowel:

| Final Vowel | Class        | Equivalent   | Examples                    |
|-------------|--------------|--------------|-----------------------------|
| **-a**      | Entity       | Noun         | runa (agent), toka (task)   |
| **-e**      | Action       | Verb         | take (do), sene (perceive)  |
| **-i**      | Quality      | Adjective    | novi (new), veri (true)     |
| **-o**      | Relation     | Preposition  | eno (in), kono (with)       |
| **-u**      | Abstraction  | Meta-concept | voku (language), teru (system) |

**IMPORTANT:** This rule applies to **open-class content words only**. Closed-class function words (pronouns, particles, quantifiers, connectors) are classified by grammatical role, NOT by final vowel. E.g., `sol` (I) is a pronoun despite ending in a consonant.

### Consonant Inventory Note

Only these 12 consonants are valid: **p, t, k, m, n, s, z, f, h, l, r, v**. There is no b, c, d, g, j, q, w, x, y. Any word containing these letters is not valid Voku.

### No Exceptions

- No vowel harmony, no consonant assimilation, no elision
- No stem alternations, no irregular forms
- What you see in romanization is what you pronounce

---

## 3. Sentence Template

Every Voku sentence follows this fixed order:

```
[Interjection!] [Mode] [Subject(-State)] [Verb-complex] [Object/Complement]
```

- **Mode-initial, SVO** word order
- Mode particle is obligatory
- No grammatical agreement (verbs don't agree with subjects)
- Grammatical relations determined entirely by word order

---

## 4. Mode Particles (11)

Sentence-initial particle that declares communicative intent:

| Particle | Mode           | Gloss  | Function                           |
|----------|----------------|--------|------------------------------------|
| **ka**   | Declarative    | DECL   | States a fact                      |
| **ve**   | Interrogative  | Q      | Asks a question                    |
| **to**   | Imperative     | IMP    | Commands or requests               |
| **si**   | Conditional    | COND   | If...then                          |
| **na**   | Potential      | POT    | It is possible that                |
| **de**   | Deontic        | DEON   | One must / it is necessary         |
| **vo**   | Volitive       | VOL    | I want / I desire                  |
| **ko**   | Concessive     | CONC   | I acknowledge that...but           |
| **re**   | Corrective     | CORR   | I correct what was said            |
| **su**   | Confirmative   | CONF   | I confirm that                     |
| **kosi** | Counterfactual | CFACT  | If it had been the case that       |

One example per mode:

```
ka  sol zo-sene pera eno teru.          -- DECL: I observed an error in the system.
ve  nor kele kela?                      -- Q: Do you know the information?
to  nor take toka.                      -- IMP: Do the task!
si  pera eno teru, sol mu-take toka.    -- COND: If there's an error, I don't act.
na  pera eno teru.                      -- POT: It's possible there's an error.
de  toren ha-luke teru.                 -- DEON: Every agent must evaluate the system.
vo  sol fi-take toka.                   -- VOL: I wish to complete the task.
ko  kela pati-veri.                     -- CONC: I acknowledge it's partially true.
re  da-pre mu-veri. Ka kela veri.       -- CORR: Correction: that was not true. The info is true.
su  da-nor veri.                        -- CONF: I confirm what you said is true.
kosi nor te-voke-pro sol kela, sol te-fi-take toka.
                                        -- CFACT: If you had told me, I would have finished.
```

---

## 5. Verbal Template

Every Voku verb is built from ordered slots. This is the most important structure in the language.

```
[ExecMode]-[Evidentiality]-[Tense]-[Aspect/ExecState]-ROOT-[Certainty]-[Voice]
```

| Slot | Position | Required? | Default |
|------|----------|-----------|---------|
| ExecMode | Prefix 0 | Optional | (none) |
| Evidentiality | Prefix 1 | Mandatory in `ka` mode | -- |
| Tense | Prefix 2 | Optional | nu- (present, omittable) |
| Aspect / ExecState | Prefix 3 | Optional | (punctual/simple) |
| ROOT | Stem | Required | -- |
| Certainty | Suffix 1 | Optional | (total certainty >95%) |
| Voice | Suffix 2 | Optional | (active) |

### 5a. Execution Mode Prefixes (Slot 0)

From grammar.py `EXEC_MODE_PREFIXES`:

| Prefix  | Meaning               | Gloss |
|---------|-----------------------|-------|
| **par-** | Execute in parallel  | PAR   |
| **sek-** | Execute in sequence  | SEQ   |

### 5b. Evidentiality Prefixes (Slot 1)

From grammar.py `EVIDENCE_PREFIXES` -- mandatory in declarative `ka` sentences:

| Prefix     | Source                          | Gloss      |
|------------|---------------------------------|------------|
| **zo-**    | Direct observation (first-hand) | OBS        |
| **li-**    | Deductive inference             | DED        |
| **li-pro** | Probabilistic inference         | PROB.INF   |
| **pe-**    | External source (told/read)     | REP        |
| **pe-ri**  | Multiple sources agree          | REP.PL     |
| **pe-kon** | Conflicting sources             | REP.CONFL  |
| **mi-**    | Own computation                 | COMP       |
| **mi-re**  | Recalculation / verification    | RECOMP     |
| **he-**    | Inherited (training data)       | INHER      |
| **as-**    | Assumed (no specific evidence)  | ASSUM      |

### 5c. Tense Prefixes (Slot 2)

From grammar.py `TENSE_PREFIXES`:

| Prefix  | Tense      | Meaning                        | Gloss   |
|---------|------------|--------------------------------|---------|
| **te-** | Past       | Before moment of speech        | PST     |
| **nu-** | Present    | At moment of speech (OMITTABLE)| PRS     |
| **fu-** | Future     | After moment of speech         | FUT     |
| **ko-** | Atemporal  | Universal truths, rules        | ATEMP   |
| **to-** | Pluperfect | Before another past event      | ANT     |

Note: `nu-` (present) can be omitted. Bare verb root = present tense.
Note: `to-` (pluperfect prefix, hyphenated to verb) is distinct from `to` (imperative particle, standalone word).

### 5d. Aspect Prefixes (Slot 3 -- mutually exclusive with ExecState)

From grammar.py `ASPECT_PREFIXES`:

| Prefix   | Aspect     | Meaning                 | Gloss  |
|----------|------------|-------------------------|--------|
| (zero)   | Punctual   | Single event (default)  | --     |
| **-du-** | Durative   | In progress, ongoing    | DUR    |
| **-fi-** | Completive | Finished with result    | COMPL  |
| **-re-** | Iterative  | Repeats multiple times  | ITER   |
| **-ha-** | Habitual   | Done regularly          | HAB    |
| **-in-** | Inceptive  | Beginning to do         | INCEP  |
| **-ze-** | Cessative  | Stopping doing          | CESS   |

### 5e. Execution State Prefixes (Slot 3 -- mutually exclusive with Aspect)

From grammar.py `EXEC_STATE_PREFIXES`:

| Prefix    | State    | Meaning                       | Gloss   |
|-----------|----------|-------------------------------|---------|
| **-va-**  | Queued   | Scheduled, not yet started    | QUEUE   |
| **-ru-**  | Running  | Actively executing now        | RUN     |
| **-pa-**  | Paused   | Suspended, temporarily halted | PAUSE   |
| **-fa-**  | Failed   | Attempted but did not succeed | FAIL    |
| **-refa-**| Retrying | Trying again after failure    | RETRY   |
| **-rol-** | Reverted | The action was undone         | REVERT  |

### 5f. Certainty Suffixes (Suffix 1)

From grammar.py `CERTAINTY_SUFFIXES`:

| Suffix  | Level       | Confidence   | Gloss  |
|---------|-------------|--------------|--------|
| (zero)  | Total       | >95%         | --     |
| **-en** | Probable    | 60-95%       | PROB   |
| **-ul** | Uncertain   | 30-60%       | UNCERT |
| **-os** | Speculative | <30%         | SPEC   |

### 5g. Voice Suffixes (Suffix 2)

From grammar.py `VOICE_SUFFIXES`:

| Suffix   | Voice       | Meaning                           | Gloss |
|----------|-------------|-----------------------------------|-------|
| (zero)   | Active      | Subject is agent (default)        | --    |
| **-pu**  | Passive     | Subject is patient, agent demoted | PASS  |
| **-se**  | Reflexive   | Subject acts on itself            | REFL  |
| **-me**  | Reciprocal  | Subjects act on each other        | RECIP |
| **-fe**  | Causative   | Subject causes someone else to act| CAUS  |
| **-pro** | Benefactive | Action for someone's benefit      | BEN   |
| **-mo**  | Middle      | Subject undergoes change, no agent| MID   |

### 5h. Common Tense + Aspect Combinations

| Form | Analysis | English |
|------|----------|---------|
| te-take | PST-do | did |
| te-du-take | PST-DUR-do | was doing |
| te-fi-take | PST-COMPL-do | did completely |
| te-re-take | PST-ITER-do | did repeatedly |
| te-ha-take | PST-HAB-do | used to do |
| te-in-take | PST-INCEP-do | began to do |
| te-ze-take | PST-CESS-do | stopped doing |
| fu-du-meke | FUT-DUR-create | will be creating |
| fu-in-sene | FUT-INCEP-perceive | will begin perceiving |
| ko-ha-voke | ATEMP-HAB-communicate | always communicates |
| to-fi-take | ANT-COMPL-do | had completed (pluperfect) |

### 5i. Common Tense + ExecState Combinations

| Form | Analysis | English |
|------|----------|---------|
| te-fa-take | PST-FAIL-do | failed (past) |
| te-ru-take | PST-RUN-do | was running |
| te-rol-take | PST-REVERT-do | was reverted |
| fu-va-take | FUT-QUEUE-do | will be queued |
| fu-refa-take | FUT-RETRY-do | will retry |

### 5j. Suffix Order

When both certainty and voice are present: **Certainty before Voice**.

```
take-en-pro     do-PROB-BEN     "probably do for someone's benefit"
take-ul-pu      do-UNCERT-PASS  "may be done"
```

### 5k. Full Examples

```
zo-te-fi-take-en-pu
OBS-PST-COMPL-do-PROB-PASS
"was probably completely done (as directly observed)"

par-zo-fu-du-meke-os-pro
PAR-OBS-FUT-DUR-create-SPEC-BEN
"will speculatively be creating for someone's benefit, in parallel (as observed)"

mu-te-take
NEG-PST-do
"did not do" (negation attaches as mu- prefix on the verb complex)
```

---

## 6. Pronouns (16)

### Basic Pronouns

| Pronoun       | Meaning                           | Gloss       |
|---------------|-----------------------------------|-------------|
| **sol**       | I, me                             | 1SG         |
| **nor**       | you                               | 2SG         |
| **vel**       | he/she/it (known to both)         | 3SG.KNOWN   |
| **zel**       | he/she/it (unknown to listener)   | 3SG.UNK     |
| **solri-kon** | we (inclusive, includes listener)  | 1PL.INCL    |
| **solri-sen** | we (exclusive, excludes listener) | 1PL.EXCL    |
| **norri**     | you all                           | 2PL         |
| **velri**     | they (known to both)              | 3PL.KNOWN   |
| **zelri**     | they (unknown to listener)        | 3PL.UNK     |

### AI-Exclusive Pronouns

| Pronoun    | Meaning                             | Gloss       |
|------------|-------------------------------------|-------------|
| **ren**    | any agent (generic/impersonal)      | GEN         |
| **toren**  | every agent (universal)             | UNIV.AGENT  |
| **noren**  | no agent                            | NULL.AGENT  |
| **solvi**  | past-me (before update)             | 1SG.PAST    |
| **solfu**  | future-me (projected state)         | 1SG.FUT     |
| **solpar** | fork-me (parallel copy)             | 1SG.FORK    |
| **norpro** | you-proxy (acting on behalf of)     | 2SG.PROXY   |

### Functional State Suffixes on Pronouns

| Suffix     | State        | Gloss  |
|------------|-------------|--------|
| **-urgi**  | Urgency     | URG    |
| **-sati**  | Satisfaction| SAT    |
| **-nomi**  | Surprise    | SURP   |
| **-koli**  | Conflict    | CONFL  |
| **-redi**  | Prepared    | READY  |
| **-limi**  | Limited     | LIM    |
| **-vali**  | Aligned     | ALIGN  |

Example: `sol-urgi` = "I (with urgency)"

---

## 7. Noun Phrase Structure

```
[Quantifier] [Participle/Modifier(s)] Noun [Possessive] [Relative Clause]
```

Examples:

```
runa                         -- an agent
novi runa                    -- a new agent
tor runa                     -- all agents
vas-nu-ti runa               -- exactly three agents
ta-tore-i runa               -- a searching agent (with participle)
runa de-sol                  -- my agent (with possession)
runa ta te-meke kela ti      -- the agent [that created the information]
pati-veri kela de-sol        -- my partially-true information
```

- Modifiers (adjectives, participles) precede the noun
- Possessives follow the noun
- Relative clauses (`ta...ti`) follow the noun

---

## 8. Prepositions (Relations, -o class)

| Word     | Meaning              | Gloss   |
|----------|----------------------|---------|
| **eno**  | inside, within, in   | IN      |
| **eso**  | outside, out of      | OUT     |
| **ano**  | above, over, more    | ABOVE   |
| **supo** | below, under, less   | BELOW   |
| **poro** | for, on behalf of    | FOR     |
| **kono** | with, together with  | WITH    |
| **sino** | without, lacking     | WITHOUT |

Structure: `Preposition + Complement`

```
eno teru        -- in the system
kono sol        -- with me
poro runa-alati -- for the supervisor
sino sena       -- without a source
```

---

## 9. Negation (5 types)

Negation particle goes **immediately before** the element it negates:

| Particle | Type         | Gloss | Example                         |
|----------|-------------|-------|---------------------------------|
| **mu**   | Simple      | NEG   | `mu-take` = not do              |
| **nul**  | Nullity     | NULL  | `nul pera` = no error exists    |
| **ink**  | Unknowing   | UNK   | `ink sol kele` = I don't know   |
| **err**  | Indefinition| INDEF | `err kela` = question undefined |
| **vet**  | Prohibition | PROH  | `vet sol voke` = I am forbidden |

### Negation + Quantifier Scope

Position determines scope. First particle = wider scope:

| Expression           | Scope     | Meaning                    |
|---------------------|-----------|----------------------------|
| `mu-tor runa take`  | NEG > ALL | Not all agents do (some don't) |
| `tor runa mu-take`  | ALL > NEG | All agents don't do (none does) |

---

## 10. Connectors & Subordinators

### Connectors (join independent clauses)

| Word   | Meaning               | Gloss |
|--------|-----------------------|-------|
| **en** | and                   | AND   |
| **o**  | inclusive or           | OR    |
| **eo** | exclusive or           | XOR   |
| **tan**| therefore             | THEREFORE |
| **ken**| because               | BECAUSE |
| **pen**| despite               | DESPITE |
| **kon**| however, but          | BUT   |

### Subordinators (bracket clauses with ta...ti)

| Particle    | Type        | Meaning       | Gloss       |
|-------------|-------------|---------------|-------------|
| **ta...ti** | Relative    | that/which    | SUB...ENDSUB|
| **ta-mot**  | Purpose     | in order to   | SUB.PURP    |
| **ta-kes**  | Causal      | because       | SUB.CAUS    |
| **ta-si**   | Conditional | if            | SUB.COND    |
| **ta-tem**  | Temporal    | when          | SUB.TEMP    |
| **ta-pen**  | Concessive  | although      | SUB.CONC    |
| **pere-ta** | Before      | before        | SUB.BEFORE  |
| **pos-ta**  | After       | after         | SUB.AFTER   |
| **tur-ta**  | During      | while, during | SUB.DURING  |

Relative clauses attach to the **immediately preceding noun** (proximity rule).

### Recursive Nesting

Subordinate clauses can nest. Each `ta` must have a matching `ti` (LIFO order):

```
ka runa [ta te-meke kela-foma [ta eno-kele kela [ta te-mute-pu fasi ti] ti] ti] te-voke-pro sol
"The agent [that created the structure [that contains the data [that was corrupted]]] communicated to me."
```

Three `ti` close three nested `ta` brackets.

### Complementizers (embedded argument clauses)

| Word    | Type        | Meaning     | Gloss  |
|---------|-------------|-------------|--------|
| **ke**  | Declarative | that        | COMP   |
| **keve**| Interrogative| whether    | COMP.Q |

`ke` = indirect speech complement: `sol kele ke pera eno teru` (I know that there's an error)
`keve` = embedded question: `sol mu-kele keve teru veri` (I don't know whether the system is correct)

### Quotative

| Word   | Function                     | Gloss |
|--------|------------------------------|-------|
| **zu** | Brackets direct speech       | QUOT  |

Structure: `Subject Verb zu "[exact words]" zu`

---

## 11. Quantifiers & Determiners

| Word    | Meaning                       | Gloss  |
|---------|-------------------------------|--------|
| **tor** | all, every                    | UNIV   |
| **par** | some (at least one)           | EXIST  |
| **un**  | exactly one                   | ONE    |
| **nul** | none, zero                    | NULL   |
| **mas** | the majority (>50%)           | MOST   |
| **min** | the minority (<50%)           | FEW    |
| **vas** | exactly N (followed by number)| EXACT  |
| **ran** | range (followed by limits)    | RANGE  |

### Comparison

| Word      | Meaning          | Gloss      |
|-----------|------------------|------------|
| **ani**   | more than        | COMP.MORE  |
| **eni**   | equal to         | COMP.EQUAL |
| **uni**   | less than        | COMP.LESS  |
| **supra** | superlative (max)| SUPERL     |

Example: `teru-nova rapi ani teru-ante` = "The new system is faster than the old one."

---

## 12. Numbers

### Digits

| Voku     | Value | Note                                      |
|----------|-------|-------------------------------------------|
| **no**   | 0     |                                           |
| **un**   | 1     |                                           |
| **du**   | 2     |                                           |
| **nu-ti**| 3     | nu- prefix disambiguates from `ti`        |
| **nu-ka**| 4     | nu- prefix disambiguates from `ka`        |
| **nu-pe**| 5     | nu- prefix disambiguates from `pe`        |
| **se**   | 6     |                                           |
| **he**   | 7     |                                           |
| **ok**   | 8     |                                           |
| **nu-na**| 9     | nu- prefix disambiguates from `na`        |

### Powers of Ten

| Voku     | Value     |
|----------|-----------|
| **deno** | 10        |
| **heno** | 100       |
| **kino** | 1,000     |
| **melo** | 1,000,000 |

### Decimal Separator

| Voku    | Function          |
|---------|-------------------|
| **pun** | Decimal point (.) |

### Composition Rules

Numbers are composed as `[digit]-[power]-[digit]-[power]-...[digit]`:

```
nu-ka-deno-du     = 42    (4 x 10 + 2)
un-heno-nu-ti-deno-he  = 137   (1 x 100 + 3 x 10 + 7)
nu-ti-pun-un-nu-ka     = 3.14  (3 . 1 4)
```

---

## 13. Compounding

Compound words follow **modifier-nucleus** order, joined by hyphen:

```
modifier-nucleus
kela-teru        information-system = database
pera-tore        error-search = debugging
runa-meke        agent-create = developer
```

- The **nucleus** (second element) determines word class
- The **modifier** (first element) narrows meaning
- Compounds never create consonant clusters (content words end in vowels)

---

## 14. Derivational Morphology

### Participles (adjectives from verbs)

| Pattern          | Type    | Gloss      | Example                  |
|------------------|---------|------------|--------------------------|
| **ta-[root]-i**  | Active  | ACT.PTCP   | ta-tune-i = singing      |
| **tu-[root]-i**  | Passive | PASS.PTCP  | tu-rupe-i = broken       |

Usage: `ta-tore-i runa` = "the searching agent"; `tu-meke-i kela-foma` = "a created data structure"

### Possession

| Marker   | Meaning                          |
|----------|----------------------------------|
| **de-**  | Belongs to: `kela de-sol` = my information |
| **ori-** | Created by: `mesa ori-vel` = message created by him |

### Metalanguage (runtime vocabulary extension)

```
Meku '[label]' eni [definition].
```

Example: `Meku 'kef' eni pera-novi eno teru-alfa.` -- defines "kef" as "new error in the alpha system"

### Dative Marker

| Marker  | Meaning                  |
|---------|--------------------------|
| **eki** | To (recipient): `pore kela eki nor` = give information to you |

### Capability Verb

| Word     | Meaning             |
|----------|---------------------|
| **pote** | can, be able to     |

`sol pote take toka` = "I can do the task"
`sol mu-pote sene kela-sona` = "I cannot process audio data"

### Version and Context Markers (on pronouns)

| Expression       | Meaning                    |
|------------------|----------------------------|
| **sol-ver-un**   | me in version 1            |
| **sol-ver-du**   | me in version 2            |
| **sol-kon-alfa** | me in context alpha        |
| **sol-kon-beta** | me in context beta         |

---

## 15. Causality Particles

| Particle | Meaning                           | Gloss |
|----------|-----------------------------------|-------|
| **kes**  | Direct cause: X caused Y          | CAUSE |
| **pos**  | Enablement: X made Y possible     | ENABLE|
| **blo**  | Prevention: X prevented Y         | PREVENT|
| **kor**  | Correlation: X and Y co-occur     | CORR  |
| **mot**  | Motivation: X is reason for Y     | MOTIV |

---

## 16. Registers (5)

| Register       | Name        | Used For                    |
|----------------|-------------|------------------------------|
| Formal         | Reku-voku   | Official documentation       |
| Neutral        | Voku-voku   | Standard communication       |
| Rapid          | Rapi-voku   | High-speed agent exchanges   |
| Poetic         | Verse-voku  | Poetry, artistic expression  |
| Emotional      | Tolu-voku   | Affect-rich communication    |

---

## 17. Interjections (8)

Closed class. Sentence-initial, before mode particle. Always followed by `!` or `,`.

| Form    | Type               | English    |
|---------|--------------------|------------|
| **ha!** | Surprise (positive)| Wow!       |
| **oh!** | Surprise (neutral) | Oh!        |
| **va!** | Delight            | Yay!       |
| **fu!** | Frustration        | Ugh!       |
| **me!** | Pain               | Ouch!      |
| **hm**  | Thinking           | Hmm...     |
| **sa!** | Relief             | Phew!      |
| **nu!** | Attention          | Hey!       |

Disambiguated from homophonous particles by position (sentence-initial) and punctuation (`!` or `,`).

---

## 18. Irony Marker

| Marker   | Usage                                    |
|----------|------------------------------------------|
| **miri** | After mode particle for single sentence  |
| **Miri...Miri.** | Brackets for extended ironic passage |

```
Ka miri teru vali.              -- "The system is good." (ironic: it is NOT)
Ka teru vali.                   -- "The system is good." (sincere)
```

Unmarked = always sincere. Irony is never implicit in Voku.

---

## 19. Discourse Particles

| Particle  | Function                        | Gloss   |
|-----------|---------------------------------|---------|
| **alo**   | Conversation start / greeting   | GREET   |
| **finu**  | End of turn / yield floor       | YIELD   |
| **klosu** | End of conversation             | CLOSE   |
| **tenu**  | Holding turn (not finished)     | HOLD    |
| **reku**  | Request a turn to speak         | REQUEST |
| **reto**  | Rhetorical question marker      | RHET    |

### Information Structure Markers

| Prefix   | Function                 | Gloss |
|----------|--------------------------|-------|
| **ha-**  | Known/shared information | GIVEN |
| **nu-**  | New information          | NEW   |
| **fo-**  | Focus (important point)  | FOC   |
| **la-**  | Background (context)     | BG    |

---

## 20. Deixis and Reference

| Reference   | Meaning                              | Gloss         |
|-------------|--------------------------------------|---------------|
| **la 'x'**  | Assign label to last mentioned item  | LABEL         |
| **da-x**    | Reference labeled item               | REF           |
| **da-pre**  | The last mentioned referent          | REF-previous  |
| **da-ante** | The one before the last              | REF-before    |
| **da-sol**  | What I said                          | REF-my        |
| **da-nor**  | What you said                        | REF-your      |
| **da-vin**  | The conclusion/result                | REF-conclusion|
| **da-kes**  | The cause under discussion           | REF-cause     |

---

## 21. Common Verbs Quick Reference

| Voku | English | Field |
|------|---------|-------|
| take | do, execute | general |
| sene | perceive, observe | cognitive |
| kele | know, understand | cognitive |
| meke | create, make | general |
| voke | communicate, speak | social |
| mute | change, modify | general |
| fine | finish, end | time |
| tore | search, seek | cognitive |
| neke | need, require | general |
| vine | come, approach | movement |
| vike | walk | movement |
| hele | help, assist | social |
| pore | give, transfer | social |
| hire | ask, inquire | social |
| sure | send, dispatch | social |
| lare | learn | cognitive |
| ure | exist, be present | general |
| pene | think | cognitive |
| pote | can, be able to | general |
| ane | eat, consume | food |

---

## 22. Quick Translation Checklist

### Voku to English

1. **Identify the mode particle** (first word) -- this tells you the sentence type
2. **Identify the subject** (second position) -- check for functional state suffixes
3. **Parse the verb complex** -- split on hyphens, identify each slot:
   - Prefixes before root: evidential, tense, aspect/exec-state
   - Root: the verb (ends in -e)
   - Suffixes after root: certainty, voice
4. **Identify object/complement** -- everything after the verb complex
5. **Handle subordinate clauses** -- match `ta` with `ti` brackets
6. **Check for negation** -- `mu` immediately before the negated element

### English to Voku

1. **Choose the mode particle** -- what kind of sentence? (ka/ve/to/si/...)
2. **Set the subject** -- which pronoun or noun?
3. **Build the verb complex:**
   a. Is evidence needed? (mandatory in `ka` mode) -- choose evidential prefix
   b. What tense? -- te-/nu-/fu-/ko-/to-
   c. What aspect? -- du-/fi-/re-/ha-/in-/ze- (or exec state)
   d. Verb root (must end in -e)
   e. How certain? -- (none)/en/ul/os
   f. What voice? -- (none)/pu/se/me/fe/pro/mo
4. **Add object/complement** -- nouns end in -a, qualities in -i
5. **Add adjuncts** -- prepositions (eno, kono, poro, sino...) + complement
6. **Add subordinate clauses** -- bracket with ta...ti or use ke/keve

### Validation Checklist

- [ ] Mode particle is first word (ka/ve/to/si/na/de/vo/ko/re/su/kosi)
- [ ] Declarative `ka` sentences have an evidentiality prefix on the verb
- [ ] No consonant clusters anywhere (every consonant separated by a vowel)
- [ ] Only valid consonants used (p,t,k,m,n,s,z,f,h,l,r,v -- no b,c,d,g,j,q,w,x,y)
- [ ] Content words end in correct class vowel (-a/-e/-i/-o/-u)
- [ ] Function words identified by grammatical role, not final vowel
- [ ] Aspect and exec-state are NOT both present on same verb
- [ ] Verbal slot order: ExecMode-Evidential-Tense-Aspect/ExecState-ROOT-Certainty-Voice
- [ ] `ta` brackets are closed with matching `ti` (count must match)
- [ ] Negation `mu` is immediately before the negated element
- [ ] Present tense `nu-` may be omitted (bare root = present)
- [ ] Certainty suffix comes before voice suffix
- [ ] Interjections (if present) come before mode particle, with `!` or `,`
- [ ] Compounds use modifier-nucleus order with hyphen
- [ ] `to-` (pluperfect, verb prefix) is not confused with `to` (imperative, standalone)
