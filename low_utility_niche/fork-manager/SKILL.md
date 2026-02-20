---
name: fork-manager
description: Manage forks with open PRs - sync upstream, rebase branches, track PR status, and maintain production branches with pending contributions. Use when syncing forks, rebasing PR branches, building production branches that combine all open PRs, reviewing closed/rejected PRs, or managing local patches kept outside upstream. Requires Git and GitHub CLI (gh).
metadata: {"openclaw": {"requires": {"bins": ["git", "gh"]}}}
---

# Fork Manager Skill

Manage forks where you contribute PRs but also use improvements before they're merged upstream. Includes support for local patches — fixes kept in the production branch even when the upstream PR was closed/rejected.

## When to use

- Sync a fork with upstream
- Check status of open PRs
- Rebase PR branches onto latest upstream
- Build a production branch combining all open PRs + local patches
- Review recently closed/rejected PRs and decide whether to keep locally
- Manage local patches (fixes not submitted or rejected upstream)

## When NOT to use

- General GitHub queries (issues, PRs, CI status on any repo) → use `github` skill instead
- Triaging/ranking/prioritizing issues → use `issue-prioritizer` skill instead
- Reviewing code changes before publishing a PR → use `pr-review` skill instead
- Creating new PRs from scratch (not fork sync) → use `gh pr create` directly

## Cron Mode

When invoked by a cron job (automated recurring sync), follow these guidelines for efficient execution:

1. **Skip interactive prompts** — auto-resolve decisions that don't require human input:
   - Rebases: attempt automatically, report failures
   - Closed PRs: report but defer decision (don't drop or keep without human input)
   - Audit findings: report but don't act
2. **Compact output** — use the summary format, not full verbose report:
   ```
   🍴 Fork Sync Complete — <repo>
   Main: synced N commits (old_sha → new_sha)
   PRs: X open, Y changed state
   - Rebased: A/B clean (C conflicts)
   Production: rebuilt clean | N conflicts
   Notable upstream: [1-3 bullet highlights]
   ```
3. **Checkpoint on failure** — if a rebase fails or production build has conflicts, write state to `repos/<name>/checkpoint.json` so the next run (or manual invocation) can resume
4. **Time budget** — target <10 minutes total. If rebasing 20+ PRs, batch push at the end instead of per-branch

## Configuration

Configs are organized per repository in `repos/<repo-name>/config.json` relative to the skill directory:

```
fork-manager/
├── SKILL.md
└── repos/
    ├── project-a/
    │   └── config.json
    └── project-b/
        └── config.json
```

Formato do `config.json`:

```json
{
  "repo": "owner/repo",
  "fork": "your-user/repo",
  "localPath": "/path/to/local/clone",
  "mainBranch": "main",
  "productionBranch": "main-with-all-prs",
  "upstreamRemote": "upstream",
  "forkRemote": "origin",
  "openPRs": [123, 456],
  "prBranches": {
    "123": "fix/issue-123",
    "456": "feat/feature-456"
  },
  "localPatches": {
    "local/my-custom-fix": {
      "description": "Breve descrição do que o patch faz",
      "originalPR": 789,
      "closedReason": "rejected|superseded|duplicate|wontfix",
      "keepReason": "Motivo pelo qual mantemos localmente",
      "addedAt": "2026-02-07T00:00:00Z",
      "reviewDate": "2026-03-07T00:00:00Z"
    }
  },
  "lastSync": "2026-01-28T12:00:00Z",
  "notes": {
    "mergedUpstream": {},
    "closedWithoutMerge": {},
    "droppedPatches": {}
  }
}
```

### Campos de `localPatches`

Cada entry em `localPatches` é uma branch local mantida na production branch mas **sem PR aberto** no upstream.

| Campo | Descrição |
|-------|-----------|
| `description` | O que o patch faz |
| `originalPR` | Número do PR original que foi fechado (opcional se criado direto como patch) |
| `closedReason` | Por que o PR foi fechado: `rejected` (mantenedor recusou), `superseded` (outro PR resolve parcialmente mas não totalmente), `duplicate` (fechamos nós mesmos), `wontfix` (upstream não vai resolver) |
| `keepReason` | Por que precisamos manter localmente |
| `addedAt` | Data em que foi convertido para local patch |
| `reviewDate` | Data para reavaliar se ainda é necessário (upstream pode ter resolvido) |

## Histórico de Execuções

Cada repositório gerenciado tem um arquivo `history.md` que registra todas as execuções da skill como um livro de registro append-only:

```
fork-manager/
└── repos/
    ├── project-a/
    │   ├── config.json
    │   └── history.md
    └── project-b/
        ├── config.json
        └── history.md
```

### Regra: Ler último output antes de começar

**Antes de qualquer operação**, ler o `history.md` do repositório alvo e extrair a **última entrada** (último bloco `---`). Isso dá contexto sobre:
- O que foi feito na última execução
- Quais PRs tinham problemas
- Quais decisões foram tomadas
- Se ficou alguma ação pendente

```bash
# Ler última entrada do history (tudo após o último "---")
tail -n +$(grep -n '^---$' "$SKILL_DIR/repos/<repo-name>/history.md" | tail -1 | cut -d: -f1) "$SKILL_DIR/repos/<repo-name>/history.md"
```

Se o arquivo não existir, criar com o header e prosseguir normalmente.

### Regra: Registrar output ao finalizar

**Ao final de toda execução**, fazer append ao `history.md` com o resultado completo. Formato:

```markdown
---
## YYYY-MM-DD HH:MM UTC | <comando>
**Operator:** <claude-code | openclaw-agent | manual>

### Summary
- Main: <status do sync>
- PRs: <X open, Y merged, Z closed, W reopened>
- Local Patches: <N total, M com review vencida>
- Production: <rebuilt OK | not rebuilt | build failed>

### Actions Taken
- <lista de ações executadas, ex: "Synced main (was 12 commits behind)">
- <"Rebased 21/21 branches clean">
- <"PR #999 closed → kept as local patch local/my-fix">
- <"PR #777 reopened → restored to openPRs (was in droppedPatches)">

### Pending
- <ações que ficaram pendentes, ex: "PR #456 has conflicts — needs manual resolution">
- <"3 local patches with expired reviewDate — run review-patches">

### Full Report
<o relatório completo que seria mostrado ao usuário, colado aqui na íntegra>
```

**Importante:** O bloco `Full Report` contém o relatório completo sem abreviação. Isso garante que o próximo agente que ler o history tenha toda a informação, não apenas o resumo.

## Fluxo de Análise

### 1. Carregar config e histórico

Resolve the skill directory (where SKILL.md lives):

```bash
# SKILL_DIR is the directory containing this SKILL.md
# Resolve it relative to the agent's workspace or skill install path
SKILL_DIR="<path-to-fork-manager-skill>"

# Load config for the target repo
cat "$SKILL_DIR/repos/<repo-name>/config.json"

# Ler último output do history para contexto
HISTORY="$SKILL_DIR/repos/<repo-name>/history.md"
if [ -f "$HISTORY" ]; then
  # Extrair última entrada (após último ---)
  LAST_SEP=$(grep -n '^---$' "$HISTORY" | tail -1 | cut -d: -f1)
  if [ -n "$LAST_SEP" ]; then
    tail -n +"$LAST_SEP" "$HISTORY"
  fi
fi
```

### 2. Navegar para o repositório

```bash
cd <localPath>
```

### 3. Fetch de ambos remotes

```bash
git fetch <upstreamRemote>
git fetch <originRemote>
```

### 4. Analisar estado do main

```bash
# Commits que upstream tem e origin/main não tem
git log --oneline <originRemote>/<mainBranch>..<upstreamRemote>/<mainBranch>

# Contar commits atrás
git rev-list --count <originRemote>/<mainBranch>..<upstreamRemote>/<mainBranch>
```

### 5. Verificar PRs abertos via GitHub CLI

```bash
# Listar PRs abertos do usuário
gh pr list --state open --author @me --json number,title,headRefName,state

# Verificar status de um PR específico
gh pr view <number> --json state,mergedAt,closedAt,title
```

### 6. Classificar cada PR

Para cada PR no config, verificar:

| Estado       | Condição                          | Ação                                    |
| ------------ | --------------------------------- | --------------------------------------- |
| **open**     | PR aberto no GitHub               | Manter, verificar se precisa rebase     |
| **merged**   | PR foi mergeado                   | Remover do config, deletar branch local |
| **closed**   | PR fechado sem merge              | **Acionar `review-closed`** (ver abaixo) |
| **conflict** | Branch tem conflitos com upstream | Precisa rebase manual                   |
| **outdated** | Branch está atrás do upstream     | Precisa rebase                          |

Comando para verificar se branch precisa rebase:

```bash
git log --oneline <upstreamRemote>/<mainBranch>..<originRemote>/<branch> | wc -l  # commits à frente
git log --oneline <originRemote>/<branch>..<upstreamRemote>/<mainBranch> | wc -l  # commits atrás
```

### 7. Revisar PRs recém-fechados (`review-closed`)

Quando um PR é detectado como fechado sem merge, **NÃO remover automaticamente**. Iniciar um fluxo de revisão interativo:

#### 7.1. Coletar contexto do fechamento

```bash
# Buscar comentários e motivo do fechamento
gh pr view <number> --repo <repo> --json title,closedAt,state,comments,labels

# Verificar se upstream resolveu o problema de outra forma
# (procurar PRs mergeados recentes que toquem os mesmos arquivos)
gh pr list --state merged --repo <repo> --json number,title,mergedAt --limit 30
```

#### 7.2. Classificar o motivo do fechamento

| Categoria | Descrição | Ação padrão |
|-----------|-----------|-------------|
| **resolved_upstream** | Upstream corrigiu o problema por outro caminho | `drop` — não precisamos mais |
| **superseded_by_ours** | Fechamos nós mesmos em favor de outro PR nosso | `drop` — o substituto já está em `openPRs` |
| **rejected_approach** | Mantenedor não gostou da abordagem, mas o bug/feature existe | `review` — considerar resubmeter com abordagem diferente |
| **rejected_need** | Mantenedor não concorda que é um problema | `review` — avaliar se precisamos localmente |
| **wontfix** | Upstream marcou como wontfix | `review` — provável candidato a local patch |

#### 7.3. Apresentar ao usuário para decisão

Para cada PR fechado, apresentar:

```markdown
### PR #<number> — <title>
- **Fechado em:** <data>
- **Motivo:** <categoria>
- **Comentários do mantenedor:** <resumo>
- **O fix ainda é relevante pra nós?** Análise: <o que o patch faz e se upstream resolve>

**Opções:**
1. 🗑️ **Drop** — remover completamente (branch local + remote)
2. 📌 **Keep as local patch** — mover para `localPatches`, manter na production branch
3. 🔄 **Resubmit** — retrabalhar e abrir novo PR com abordagem diferente
4. ⏸️ **Defer** — manter no limbo por agora, revisitar depois
```

#### 7.4. Executar a decisão

**Drop:**
```bash
git branch -D <branch> 2>/dev/null
git push <originRemote> --delete <branch> 2>/dev/null
# Mover para notes.droppedPatches no config
```

**Keep as local patch:**
```bash
# Branch continua existindo, mas sai de openPRs/prBranches
# Entra em localPatches com metadata completa
# Renomear branch de fix/xxx para local/xxx (opcional, para clareza)
```

**Resubmit:**
```bash
# Manter branch, criar novo PR com descrição atualizada
gh pr create --title "<novo titulo>" --body "<nova descrição com contexto>"
# Atualizar config com novo número de PR
```

**Defer:**
```bash
# Mover para uma seção notes.deferred no config
# Será apresentado novamente no próximo full-sync
```

### 8. Auditar PRs abertos (`audit-open`)

Análise proativa dos PRs **ainda abertos** para detectar redundâncias e obsolescência. Deve rodar no `full-sync` depois do `update-config`.

#### 8.1. Resolved upstream

Verificar se o upstream já resolveu o problema que nosso PR corrige, sem mergear nosso PR:

```bash
# Para cada PR aberto, buscar os arquivos que ele toca
gh pr view <number> --repo <repo> --json files --jq '[.files[].path]'

# Verificar se upstream alterou esses mesmos arquivos recentemente
# (commits no upstream/main que não estão no nosso PR branch)
git log --oneline upstream/main --since="<lastSync>" -- <files>

# Se houve mudanças upstream nos mesmos arquivos, verificar se o diff
# do nosso PR ainda faz diferença (pode ter sido absorvido)
git diff upstream/main..origin/<branch> -- <files>
```

**Se o diff do PR estiver vazio** (upstream absorveu as mudanças): marcar como `resolved_upstream`.
**Se o diff for parcial** (upstream resolveu parte): marcar como `partially_resolved` para revisão.

#### 8.2. Duplicate externo

Verificar se outra pessoa abriu um PR que resolve o mesmo problema:

```bash
# Buscar PRs abertos no upstream que tocam os mesmos arquivos
gh pr list --state open --repo <repo> --json number,title,headRefName,files --limit 50

# Buscar PRs mergeados recentes que tocam os mesmos arquivos
gh pr list --state merged --repo <repo> --json number,title,mergedAt,files --limit 30 \
  | jq '[.[] | select(.mergedAt >= "<lastSync>")]'
```

Para cada PR encontrado que toca os mesmos arquivos, comparar:
- Mesmo issue referenciado?
- Mesma área de código?
- Mesmo tipo de fix?

Se houver match forte: marcar como `duplicate_external` ou `superseded_external`.

#### 8.3. Self-duplicate

Detectar sobreposição entre nossos próprios PRs abertos:

```bash
# Coletar files de todos os nossos PRs abertos
for pr in <openPRs>; do
  gh pr view $pr --repo <repo> --json number,files --jq '{number, files: [.files[].path]}'
done

# Cruzar: se dois PRs tocam os mesmos arquivos, são candidatos a duplicata
```

Para cada par com overlap de arquivos:
- Verificar se o diff é similar ou complementar
- Se similar: recomendar fechar o mais antigo/menos limpo
- Se complementar: ok, apenas nota informativa

#### 8.4. Apresentar resultados

```markdown
### Audit de PRs Abertos

#### Possivelmente resolvidos upstream
| # | Titulo | Arquivos em comum | Status |
|---|--------|-------------------|--------|
| 123 | fix(foo): bar | foo.ts (changed upstream 3 days ago) | ⚠️ Verificar |

#### Possíveis duplicatas externas
| Nosso PR | PR externo | Overlap | Recomendação |
|----------|-----------|---------|--------------|
| #123 | #456 (@user) | foo.ts, bar.ts | ⚠️ Mesmo issue, verificar |

#### Self-duplicates (nossos PRs que se sobrepõem)
| PR A | PR B | Arquivos em comum | Recomendação |
|------|------|-------------------|--------------|
| #6471 | #8386 | skills/refresh.ts | 🗑️ Fechar #6471 (duplicata) |

**Opções por PR flagged:**
1. 🗑️ **Close** — fechar o PR no upstream e drop
2. ✅ **Keep** — falso positivo, manter aberto
3. 🔄 **Merge into** — combinar com outro PR
4. ⏸️ **Defer** — revisitar depois
```

## Comandos do Agente

### `status` - Verificar estado atual

1. Carregar config
2. Fetch remotes
3. Contar commits atrás do upstream
4. Listar PRs e seus estados
5. Reportar ao usuário

### `sync` - Sincronizar main com upstream

```bash
cd <localPath>
git fetch <upstreamRemote>
git checkout <mainBranch>
git merge <upstreamRemote>/<mainBranch>
git push <originRemote> <mainBranch>
```

### `rebase <branch>` - Rebase de uma branch específica

```bash
git checkout <branch>
git fetch <upstreamRemote>
git rebase <upstreamRemote>/<mainBranch>
# Se conflito: resolver e git rebase --continue
git push <originRemote> <branch> --force-with-lease
```

### `rebase-all` - Rebase de todas as branches de PR

Para cada branch em `prBranches`:

1. Checkout da branch
2. Rebase no upstream/main
3. Push com --force-with-lease
4. Reportar sucesso/falha

### `update-config` - Atualizar config com PRs atuais

```bash
# Buscar PRs abertos
gh pr list --state open --author @me --repo <repo> --json number,headRefName

# Atualizar o arquivo $SKILL_DIR/repos/<repo-name>/config.json com os PRs atuais
# Usar jq ou editar manualmente o JSON
```

#### Detecção de PRs reabertos

Ao comparar a lista do GitHub (`gh pr list --state open`) com o config local, detectar **três cenários**:

| Cenário | Condição | Ação |
|---------|----------|------|
| **PR novo** | No GitHub mas não em `openPRs`, `localPatches`, nem `notes` | Adicionar a `openPRs` + `prBranches` normalmente |
| **PR reaberto (dropped)** | No GitHub como open, encontrado em `notes.closedWithoutMerge` ou `notes.droppedPatches` | **Restaurar**: mover de volta para `openPRs` + `prBranches`, remover da seção `notes`. Fetch da branch: `git fetch <originRemote> <branch>`. Logar no relatório como "🔄 Reopened" |
| **PR reaberto (local patch)** | No GitHub como open, encontrado em `localPatches` (via campo `originalPR`) | **Promover**: mover de `localPatches` para `openPRs` + `prBranches`. Logar no relatório como "🔄 Reopened (was local patch)" |

**Implementação:**

```bash
# Para cada PR open no GitHub que NÃO está em openPRs:
# 1. Checar se o número está em notes.closedWithoutMerge ou notes.droppedPatches
#    → Se sim: PR foi reaberto. Restaurar automaticamente.
# 2. Checar se algum entry em localPatches tem originalPR == número
#    → Se sim: PR foi reaberto. Promover de volta a openPRs.
# 3. Se não encontrado em lugar nenhum: PR genuinamente novo.

# Restaurar branch se foi deletada:
git fetch <originRemote> <branch> 2>/dev/null || git fetch <originRemote> pull/<number>/head:<branch>
```

**Nota:** A restauração é automática (sem interação) porque o mantenedor reabrir um PR é sinal claro de que ele deve voltar ao tracking. O relatório sempre lista os PRs restaurados para visibilidade.

### `build-production` - Criar branch de produção com todos os PRs + local patches

```bash
cd <localPath>
git fetch <upstreamRemote>
git fetch <originRemote>

# ⚠️ SEMPRE preservar arquivos não-commitados antes de trocar de branch
if [ -n "$(git status --porcelain)" ]; then
  git stash push --include-untracked -m "fork-manager: pre-build-production $(date -u +%Y%m%dT%H%M%S)"
  STASHED=1
fi

# Deletar branch antiga se existir
git branch -D <productionBranch> 2>/dev/null || true

# Criar nova branch a partir do upstream
git checkout -b <productionBranch> <upstreamRemote>/<mainBranch>

# 1. Mergear cada PR branch (contribuições upstream pendentes)
for branch in <prBranches>; do
  git merge <originRemote>/$branch -m "Merge PR #<number>: <title>"
  # Se conflito, resolver
done

# 2. Mergear cada local patch (fixes mantidos localmente)
for branch in <localPatches>; do
  git merge <originRemote>/$branch -m "Merge local patch: <description>"
  # Se conflito, resolver
done

# Push
git push <originRemote> <productionBranch> --force

# Restaurar arquivos não-commitados
if [ "$STASHED" = "1" ]; then
  git stash pop
fi
```

**After rebuilding the production branch, remind the user to run their project's build command if needed.**

**Ordem de merge:** PRs abertos primeiro (ordem crescente por número), local patches depois. Isso garante que patches locais se aplicam sobre a base mais completa possível.

### `audit-open` - Auditar PRs abertos por redundância/obsolescência

Análise proativa de todos os PRs abertos (seção 8 acima):

1. Para cada PR aberto, coletar arquivos tocados
2. **Resolved upstream**: verificar se upstream alterou os mesmos arquivos desde último sync; se diff do PR ficou vazio, flaggar
3. **Duplicate externo**: buscar PRs upstream (open + recently merged) que tocam mesmos arquivos
4. **Self-duplicate**: cruzar arquivos entre nossos próprios PRs abertos
5. Apresentar findings ao usuário com opções: close / keep / merge-into / defer
6. Executar decisões
7. Atualizar config

### `review-closed` - Revisar PRs recém-fechados

Detecta PRs que foram fechados/mergeados desde o último sync e guia o usuário na decisão:

1. Buscar todos os PRs do config no GitHub
2. Identificar os que mudaram de estado (merged ou closed)
3. Para **merged**: mover para `notes.mergedUpstream`, deletar branches
4. Para **closed sem merge**: iniciar fluxo de revisão interativo (seção 7 acima)
5. Para cada closed, apresentar contexto e opções ao usuário
6. Executar decisão: drop / keep as local patch / resubmit / defer
7. Atualizar config

### `review-patches` - Reavaliar patches locais existentes

Para cada entry em `localPatches` cuja `reviewDate` já passou:

1. Verificar se upstream resolveu o problema desde a última revisão
2. Verificar se o patch ainda aplica limpo (sem conflitos)
3. Apresentar ao usuário com opções: manter / drop / resubmit / estender reviewDate
4. Atualizar config

### `full-sync` - Sincronização completa

1. **Stash** - `git stash --include-untracked` se houver arquivos não-commitados
2. `sync` - Atualizar main
3. `update-config` - Atualizar lista de PRs
4. **`review-closed`** - Revisar PRs recém-fechados/mergeados (interativo)
5. **`audit-open`** - Auditar PRs abertos por redundância/obsolescência (interativo)
6. **`review-patches`** - Reavaliar local patches com reviewDate vencida (interativo)
7. `rebase-all` - Rebase de todas as branches (PRs + local patches)
8. `build-production` - Recriar branch de produção (PRs + local patches)
9. **Pop stash** - `git stash pop` para restaurar arquivos locais
10. Remind user to run their project's build command if needed

**Nota sobre ordem:** `update-config` roda **antes** de `review-closed` porque é ali que PRs reabertos são detectados e restaurados automaticamente. Depois, `review-closed` processa PRs que foram genuinamente fechados. Por fim, `audit-open` roda por último, já com a lista de PRs abertos atualizada (incluindo os reabertos).

## Relatório para o Usuário

Após qualquer operação, gerar relatório:

```markdown
## 🍴 Fork Status: <repo>

### Upstream Sync

- **Main branch:** X commits behind upstream
- **Last sync:** <date>

### Open PRs (Y total)

| #   | Branch        | Status           | Action Needed     |
| --- | ------------- | ---------------- | ----------------- |
| 123 | fix/issue-123 | ✅ Up to date    | None              |
| 456 | feat/feature  | ⚠️ Needs rebase  | Run rebase        |
| 789 | fix/bug       | ❌ Has conflicts | Manual resolution |

### Local Patches (Z total)

| Branch             | Original PR | Motivo          | Review em  |
| ------------------ | ----------- | --------------- | ---------- |
| local/my-fix       | #321        | rejected_need   | 2026-03-07 |
| local/custom-tweak | —           | wontfix         | 2026-04-01 |

### Audit de PRs Abertos

| #   | Título           | Flag                | Detalhe                          |
| --- | ---------------- | ------------------- | -------------------------------- |
| 123 | fix(foo): bar    | ⚠️ resolved_upstream | upstream changed foo.ts 3d ago   |
| 456 | fix(baz): qux    | ⚠️ duplicate_external | similar to #789 by @user         |
| 111 | fix(a): b        | ⚠️ self_duplicate    | overlaps with our #222           |

### PRs Reabertos (restaurados automaticamente)

| #   | Título           | Origem              | Ação                    |
| --- | ---------------- | ------------------- | ----------------------- |
| 777 | fix(foo): bar    | notes.droppedPatches | 🔄 Restored to openPRs |
| 888 | feat(baz): qux   | localPatches         | 🔄 Promoted to openPRs |

_Seção presente apenas quando há PRs reabertos no ciclo atual._

### PRs Recém-Fechados (aguardando decisão)

| #   | Título           | Fechado em | Motivo              | Recomendação     |
| --- | ---------------- | ---------- | ------------------- | ---------------- |
| 999 | fix(foo): bar    | 2026-02-05 | resolved_upstream   | 🗑️ Drop          |
| 888 | feat(baz): qux   | 2026-02-06 | rejected_need       | 📌 Local patch   |

### Production Branch

- **Branch:** main-with-all-prs
- **Contains:** PRs #123, #456 + Local patches: local/my-fix, local/custom-tweak
- **Status:** ✅ Up to date / ⚠️ Needs rebuild

### Recommended Actions

1. ...
2. ...
```

## Notas Importantes

- Sempre usar `--force-with-lease` em vez de `--force` para push
- Sempre fazer backup antes de operações destrutivas
- Use the project's package manager for build commands (bun/npm/yarn/pnpm)
- Manter o config atualizado após cada operação
- **Local patches são cidadãos de primeira classe:** rebase, build e relatório incluem tanto PRs abertos quanto local patches
- **Nunca remover automaticamente um PR fechado sem merge.** Sempre passar pelo fluxo `review-closed` para decisão do usuário
- **Review dates em local patches:** ao criar um local patch, definir uma data de revisão (default: 30 dias). No `full-sync`, patches com review vencida são apresentados ao usuário para reavaliação
- **Naming convention para local patches:** prefixo `local/` para distinguir de branches de PR (ex: `local/my-custom-fix`). A branch original pode ser renomeada ou mantida — o importante é que o config rastreie a branch correta

### ⚠️ Proteger arquivos não-commitados antes de operações destrutivas

Antes de qualquer operação que troca de branch ou deleta/recria branches (especialmente `build-production` e `full-sync`), **sempre** verificar e preservar arquivos unstaged, untracked e staged:

```bash
cd <localPath>

# 1. Checar se há arquivos em risco
git status --porcelain

# 2. Se houver arquivos modificados/untracked, fazer stash com untracked
git stash push --include-untracked -m "fork-manager: pre-sync stash $(date -u +%Y%m%dT%H%M%S)"

# 3. Executar a operação (rebase, checkout, merge, etc.)
# ...

# 4. Após concluir, restaurar o stash
git stash pop
```

**Por quê?** Ao deletar e recriar a branch de produção (`git branch -D <productionBranch>`), arquivos que existiam apenas no working directory (não commitados) são perdidos permanentemente. Isso inclui:

- Arquivos gerados (dashboards, history, state)
- Arquivos de configuração local (serve.ts, .env)
- Dados acumulados (JSON, SQLite)

**Regra:** Se `git status --porcelain` retornar qualquer saída, fazer `git stash --include-untracked` antes de prosseguir. Restaurar com `git stash pop` ao final.

## Security Notice

This skill performs operations that require broad filesystem and network access by design:

- **Git operations**: fetch, checkout, merge, rebase, push across multiple remotes and branches
- **GitHub CLI**: reads PR status, creates PRs, queries repo metadata
**Before using this skill on a repository:**
- All git push operations use `--force-with-lease` (not `--force`) to prevent data loss
- The skill always stashes uncommitted files before destructive branch operations

These capabilities are inherent to fork management and cannot be removed without breaking core functionality.

## Usage Example

User: "sync my fork of project-x"

Agent:

1. Load config from `$SKILL_DIR/repos/project-x/config.json`
2. Run `status` to assess current state
3. If main is behind, run `sync`
4. If PRs need rebase, run `rebase-all`
5. Update `productionBranch` if needed
6. Remind user to rebuild if needed
7. Report results to user
