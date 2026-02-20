# Literature Search Skill

## Overview

文献检索引擎，提供多源学术文献搜索与聚合能力。支持arXiv、Semantic Scholar、以及通用网络搜索，帮助用户快速找到相关领域的高质量文献资源。

## Core Capabilities

### 1. 多源检索
- **arXiv**: 预印本论文检索，获取最新研究动态
- **Semantic Scholar**: 学术搜索，获取引用关系和论文质量指标
- **Web Search**: 扩展检索，覆盖更多资源

### 2. 智能排序
- 按引用数排序
- 按发布时间排序
- 按相关性排序

### 3. 信息提取
- 论文标题、作者、摘要
- 发布时间、期刊/会议
- 引用数、影响力指标

## CLI Usage

### 基础检索
```bash
# 使用CLI快速搜索
z-ai function -n web_search -a '{"query": "transformer attention mechanism site:arxiv.org", "num": 10}'

# 搜索最新进展
z-ai function -n web_search -a '{"query": "large language models recent advances", "num": 10, "recency_days": 30}'
```

### 使用脚本
```bash
# 运行文献检索脚本
bun run skills/literature-search/scripts/search.ts "attention mechanism"

# 指定数据源
bun run skills/literature-search/scripts/search.ts "transformer" --source arxiv

# 限制结果数量
bun run skills/literature-search/scripts/search.ts "GPT" --limit 20
```

## API Usage

### 简单搜索
```typescript
import LiteratureSearch from './scripts/search';

const searcher = new LiteratureSearch();
await searcher.initialize();

// 搜索文献
const results = await searcher.search("transformer attention", {
  sources: ['arxiv', 'semantic_scholar'],
  limit: 10,
  sortBy: 'relevance'
});

console.log(results);
```

### 高级搜索
```typescript
// 带过滤条件的搜索
const filtered = await searcher.search("machine learning", {
  sources: ['arxiv'],
  limit: 20,
  filters: {
    yearRange: [2022, 2024],
    categories: ['cs.LG', 'cs.AI'],
    minCitations: 10
  },
  sortBy: 'citations'
});

// 按作者搜索
const byAuthor = await searcher.searchByAuthor("Yann LeCun", {
  limit: 15,
  sortBy: 'date'
});
```

## Output Format

### SearchResult 类型
```typescript
interface SearchResult {
  id: string;              // 论文唯一标识
  title: string;           // 标题
  authors: string[];       // 作者列表
  abstract: string;        // 摘要
  publishDate: string;     // 发布日期
  source: string;          // 数据源
  url: string;             // 论文链接
  pdfUrl?: string;         // PDF链接
  citations?: number;      // 引用数
  venue?: string;          // 期刊/会议
  keywords?: string[];     // 关键词
  doi?: string;            // DOI
}
```

## Integration Examples

### 与AI分析结合
```typescript
import LiteratureSearch from './scripts/search';
import ZAI from 'z-ai-web-dev-sdk';

async function searchAndAnalyze(query: string) {
  const searcher = new LiteratureSearch();
  await searcher.initialize();
  
  // 搜索文献
  const results = await searcher.search(query, { limit: 5 });
  
  // 使用AI分析结果
  const zai = await ZAI.create();
  const summary = await zai.chat.completions.create({
    messages: [{
      role: 'user',
      content: `分析以下文献搜索结果，总结研究趋势:\n${JSON.stringify(results, null, 2)}`
    }]
  });
  
  return { results, analysis: summary.choices[0].message.content };
}
```

## Best Practices

1. **明确检索词**: 使用具体的技术术语而非模糊概念
2. **组合数据源**: 不同数据源覆盖不同范围的文献
3. **合理排序**: 根据目的选择排序方式 (引用数/时间/相关性)
4. **缓存结果**: 避免重复检索相同内容
5. **定期更新**: 关注新发表论文，保持知识更新

## Troubleshooting

### 问题：检索结果太少
- 尝试扩大检索词范围
- 增加数据源数量
- 检查拼写是否正确

### 问题：结果质量不高
- 使用引用数排序
- 添加时间过滤
- 指定高质量期刊/会议

### 问题：API限制
- 实现请求缓存
- 使用合理的请求间隔
- 合并相似请求

## File Structure

```
skills/literature-search/
├── skill.md           # 本说明文档
├── scripts/
│   ├── search.ts      # 核心搜索脚本
│   └── types.ts       # 类型定义
└── examples/
    ├── basic.ts       # 基础用法示例
    └── advanced.ts    # 高级用法示例
```
