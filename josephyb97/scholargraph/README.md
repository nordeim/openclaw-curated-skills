# 📚 ScholarGraph - Academic Literature Intelligence Toolkit

<div align="center">

**Efficient, systematic tools for academic literature analysis and knowledge management**

[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Bun](https://img.shields.io/badge/Bun-1.0+-orange.svg)](https://bun.sh/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 🎯 Project Goals

This toolkit addresses core challenges in academic research and knowledge acquisition:

| Problem | Solution |
|------|----------|
| 📚 Information overload | AI-powered multi-source filtering |
| 🧩 Fragmented knowledge | Automated knowledge graph construction |
| 🔄 Hard-to-track progress | Real-time monitoring with reports |
| 🙈 Invisible knowledge gaps | Proactive gap detection |
| 🆕 Complex concept learning | One-click concept cards |

---

## ✨ Core Features

### 1. 🔍 Literature Search Engine

Multi-source academic paper discovery across arXiv, Semantic Scholar, and web sources.

```bash
# CLI Usage
lit search "transformer attention" --limit 20 --source arxiv

# Programmatic API
import LiteratureSearch from './skills/literature-search/scripts/search';

const searcher = new LiteratureSearch();
const results = await searcher.search("large language models", {
  sources: ['arxiv', 'semantic_scholar'],
  limit: 10,
  sortBy: 'citations'
});
```

### 2. 📖 Concept Learner

Rapid knowledge framework construction with structured learning cards.

```bash
# CLI Usage
lit learn "BERT" --depth advanced --papers --output bert-card.md

# Programmatic API
import ConceptLearner from './skills/concept-learner/scripts/learn';

const learner = new ConceptLearner();
const card = await learner.learn("Transformer", {
  depth: 'advanced',
  includePapers: true,
  includeCode: true
});
```

### 3. 🔎 Knowledge Gap Detector

Proactively identifies blind spots in your understanding.

```bash
# CLI Usage
lit detect --domain "Natural Language Processing" --known "transformer,attention,BERT"

# Programmatic API
import KnowledgeGapDetector from './skills/knowledge-gap-detector/scripts/detect';

const detector = new KnowledgeGapDetector();
const report = await detector.detect({
  domain: 'Machine Learning',
  knownConcepts: ['Python', 'NumPy', 'Pandas'],
  targetLevel: 'advanced'
});
```

### 4. 📊 Progress Tracker

Real-time field monitoring with automated reporting.

```bash
# CLI Usage
lit track report --type weekly --output weekly-report.md

# Programmatic API
import ProgressTracker from './skills/progress-tracker/scripts/track';

const tracker = new ProgressTracker();
await tracker.addWatch({
  type: 'keyword',
  value: 'large language model',
  frequency: 'daily'
});
const updates = await tracker.getUpdates();
```

### 5. 📄 Paper Analyzer

Deep paper analysis extracting key contributions and insights.

```bash
# CLI Usage
lit analyze "https://arxiv.org/abs/2301.07001" --mode deep --output analysis.md

# Programmatic API
import PaperAnalyzer from './skills/paper-analyzer/scripts/analyze';

const analyzer = new PaperAnalyzer();
const analysis = await analyzer.analyze({
  url: 'https://arxiv.org/abs/2301.07001',
  mode: 'deep'
});
```

### 6. 🔗 Knowledge Graph Builder

Visualizes concept relationships through interactive graphs.

```bash
# CLI Usage
lit graph transformer attention BERT GPT --format mermaid --output graph.md

# Programmatic API
import KnowledgeGraphBuilder from './skills/knowledge-graph/scripts/graph';

const builder = new KnowledgeGraphBuilder();
const graph = await builder.build(['transformer', 'attention', 'BERT']);
console.log(builder.toMermaid(graph));
```

---

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/your-username/scholargraph.git
cd scholargraph

# Install dependencies
bun install

# Initialize configuration
bun run skills/cli.ts config init
```

---

## 🚀 Quick Start

### 1. Literature Search

```bash
bun run skills/cli.ts search "attention mechanism"
```

### 2. Concept Learning

```bash
bun run skills/cli.ts learn "Transformer" --depth advanced --output transformer.md
```

### 3. Gap Detection

```bash
bun run skills/cli.ts detect --domain "Deep Learning" --known "neural network,backpropagation"
```

### 4. Paper Analysis

```bash
bun run skills/cli.ts analyze "https://arxiv.org/abs/1706.03762" --output paper-analysis.md
```

---

## 📁 Project Structure

```
skills/
├── cli.ts                      # Unified CLI entrypoint
├── config.ts                   # Configuration management
│
├── literature-search/          # Literature search
│   ├── skill.md
│   └── scripts/
│       ├── search.ts
│       └── types.ts
│
├── concept-learner/            # Concept learning
│   ├── skill.md
│   └── scripts/
│       ├── learn.ts
│       └── types.ts
│
├── knowledge-gap-detector/     # Gap detection
│   ├── skill.md
│   └── scripts/
│       ├── detect.ts
│       └── types.ts
│
├── progress-tracker/           # Progress tracking
│   ├── skill.md
│   └── scripts/
│       ├── track.ts
│       └── types.ts
│
├── paper-analyzer/             # Paper analysis
│   ├── skill.md
│   └── scripts/
│       ├── analyze.ts
│       └── types.ts
│
└── knowledge-graph/            # Knowledge graphs
    ├── skill.md
    └── scripts/
        └── graph.ts
```

---

## 🔧 Configuration

Configuration file `scholargraph-config.json`:

```json
{
  "user": {
    "interests": ["Machine Learning", "NLP"],
    "level": "intermediate",
    "primaryLanguage": "en-US"
  },
  "search": {
    "defaultSources": ["arxiv", "semantic_scholar"],
    "maxResults": 20,
    "sortBy": "relevance"
  },
  "learning": {
    "depth": "standard",
    "includePapers": true,
    "includeCode": false
  },
  "tracking": {
    "enabled": true,
    "frequency": "weekly",
    "keywords": ["transformer", "large language model"]
  }
}
```

---

## 💡 Usage Scenarios

### Scenario 1: Rapid Field Onboarding

```bash
# 1. Learn core concepts
lit learn "Large Language Model" --depth beginner

# 2. Detect prerequisite gaps
lit detect --domain "LLM" --known "transformer,attention"

# 3. Build knowledge graph
lit graph LLM transformer attention GPT BERT --format mermaid
```

### Scenario 2: Research Progress Tracking

```bash
# 1. Add monitoring keywords
lit track add keyword "prompt engineering" --frequency weekly

# 2. Generate weekly report
lit track report --type weekly --output weekly-llm-report.md
```

### Scenario 3: Deep Paper Understanding

```bash
# 1. Analyze paper
lit analyze "https://arxiv.org/abs/2301.07001" --mode deep --output paper.md

# 2. Learn new concepts from paper
lit learn "Chain of Thought" --depth advanced --papers

# 3. Build related concept graph
lit graph "Chain of Thought" "Prompt Engineering" "Few-shot Learning"
```

---

## 🛠️ Development Guide

### Adding New Skills

1. Create directory structure:
```bash
mkdir -p skills/my-skill/scripts
```

2. Write Skill description (`skill.md`)

3. Implement core script (`scripts/main.ts`)

4. Define types (`scripts/types.ts`)

5. Register command in `cli.ts`

### Running Tests

```bash
bun test
```

---

## 📝 Output Formats

### Markdown Reports

All tools support Markdown output for easy reading/sharing:

- **Concept Cards**: Definitions, components, history, applications, learning paths
- **Gap Reports**: Gap analysis, learning recommendations, effort estimates
- **Progress Reports**: New papers, trending topics, recommended reads
- **Paper Analyses**: Methods, experiments, contributions, limitations

### JSON Data

Structured JSON output for programmatic processing:

```typescript
interface SearchResult {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  // ...
}
```

---

## 🤝 Contribution Guidelines

Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [arXiv](https://arxiv.org/) - Open-access paper repository
- [Semantic Scholar](https://www.semanticscholar.org/) - Academic search engine
- [z-ai-web-dev-sdk](https://npmjs.com/package/z-ai-web-dev-sdk) - AI capabilities support

---

<div align="center">

**⭐ If you find this project helpful, please give it a Star! ⭐**

</div>