#!/usr/bin/env bun
/**
 * Literature Skills - Unified CLI
 * 文献检索总结工具统一命令行入口
 * 
 * 用法:
 *   lit <command> [options]
 * 
 * 命令:
 *   search <query>          检索文献
 *   learn <concept>         学习概念
 *   detect <domain>         检测知识盲区
 *   track <action>          进展追踪
 *   analyze <url>           分析论文
 *   graph <concepts...>     构建知识图谱
 *   config <action>         配置管理
 */

import LiteratureSearch from './literature-search/scripts/search';
import ConceptLearner from './concept-learner/scripts/learn';
import KnowledgeGapDetector from './knowledge-gap-detector/scripts/detect';
import ProgressTracker from './progress-tracker/scripts/track';
import PaperAnalyzer from './paper-analyzer/scripts/analyze';
import KnowledgeGraphBuilder from './knowledge-graph/scripts/graph';
import { ConfigManager, defaultConfig } from './config';

const COMMANDS = {
  search: '检索文献',
  learn: '学习概念',
  detect: '检测知识盲区',
  track: '进展追踪',
  analyze: '分析论文',
  graph: '构建知识图谱',
  config: '配置管理'
};

function showHelp() {
  console.log(`
📚 Literature Skills - 文献检索总结工具
==========================================

用法:
  lit <command> [options]

命令:
  search <query>              检索相关文献
    --limit <n>               结果数量 (默认: 10)
    --source <s>              数据源 (arxiv|semantic_scholar|web)
    --sort <by>               排序方式 (relevance|date|citations)

  learn <concept>             学习概念并生成知识卡片
    --depth <d>               学习深度 (beginner|intermediate|advanced)
    --papers                  包含相关论文
    --code                    包含代码示例
    --output <file>           输出文件

  detect --domain <d>         检测知识盲区
    --known <list>            已知概念 (逗号分隔)
    --output <file>           输出报告文件

  track <action>              进展追踪
    add <type> <value>        添加监控项
    report                    生成报告
    --type <t>                报告类型 (daily|weekly|monthly)
    --output <file>           输出文件

  analyze <url>               分析论文
    --mode <m>                分析模式 (quick|standard|deep)
    --output <file>           输出文件

  graph <concepts...>         构建知识图谱
    --format <f>              输出格式 (mermaid|json)
    --output <file>           输出文件

  config <action>             配置管理
    init                      初始化配置文件
    show                      显示当前配置
    set <key> <value>         设置配置项
    reset                     重置为默认配置

示例:
  lit search "transformer attention" --limit 20
  lit learn "BERT" --depth advanced --output bert-card.md
  lit detect --domain "NLP" --known "transformer,attention"
  lit track report --type weekly --output weekly-report.md
  lit analyze "https://arxiv.org/abs/2301.07001" --output analysis.md
  lit graph transformer attention BERT GPT --format mermaid
`);
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    showHelp();
    process.exit(0);
  }

  const command = args[0];
  const cmdArgs = args.slice(1);

  try {
    switch (command) {
      case 'search':
        await handleSearch(cmdArgs);
        break;

      case 'learn':
        await handleLearn(cmdArgs);
        break;

      case 'detect':
        await handleDetect(cmdArgs);
        break;

      case 'track':
        await handleTrack(cmdArgs);
        break;

      case 'analyze':
        await handleAnalyze(cmdArgs);
        break;

      case 'graph':
        await handleGraph(cmdArgs);
        break;

      case 'config':
        handleConfig(cmdArgs);
        break;

      default:
        console.error(`Unknown command: ${command}`);
        console.log('Run "lit --help" for usage information.');
        process.exit(1);
    }
  } catch (error: any) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

async function handleSearch(args: string[]) {
  const query = args[0];
  if (!query) {
    console.error('Error: Please provide a search query');
    process.exit(1);
  }

  const limitIndex = args.indexOf('--limit');
  const limit = limitIndex > -1 ? parseInt(args[limitIndex + 1]) : 10;

  const sourceIndex = args.indexOf('--source');
  const source = sourceIndex > -1 ? args[sourceIndex + 1] as any : undefined;

  const sortIndex = args.indexOf('--sort');
  const sortBy = sortIndex > -1 ? args[sortIndex + 1] as any : 'relevance';

  const searcher = new LiteratureSearch();
  await searcher.initialize();

  console.log(`🔍 Searching for "${query}"...`);

  const results = await searcher.search(query, {
    limit,
    sources: source ? [source] : undefined,
    sortBy
  });

  console.log(`\n📚 Found ${results.totalResults} results:\n`);

  results.results.forEach((paper, i) => {
    console.log(`${i + 1}. ${paper.title}`);
    console.log(`   Authors: ${paper.authors.slice(0, 3).join(', ')}${paper.authors.length > 3 ? '...' : ''}`);
    console.log(`   Source: ${paper.source} | Date: ${paper.publishDate}`);
    console.log(`   URL: ${paper.url}`);
    console.log('');
  });
}

async function handleLearn(args: string[]) {
  const concept = args[0];
  if (!concept) {
    console.error('Error: Please provide a concept to learn');
    process.exit(1);
  }

  const depthIndex = args.indexOf('--depth');
  const depth = depthIndex > -1 ? args[depthIndex + 1] as any : 'intermediate';

  const includePapers = args.includes('--papers');
  const includeCode = args.includes('--code');

  const outputIndex = args.indexOf('--output');
  const outputFile = outputIndex > -1 ? args[outputIndex + 1] : null;

  const learner = new ConceptLearner();
  await learner.initialize();

  console.log(`📖 Learning "${concept}"...`);

  const card = await learner.learn(concept, {
    depth,
    includePapers,
    includeCode
  });

  if (outputFile) {
    const fs = require('fs');
    fs.writeFileSync(outputFile, learner.toMarkdown(card));
    console.log(`\n✅ Concept card saved to ${outputFile}`);
  } else {
    console.log('\n📋 Concept Card:\n');
    console.log(`Title: ${card.concept}`);
    console.log(`Definition: ${card.definition}`);
    console.log(`\nCore Components: ${card.coreComponents.length}`);
    console.log(`Applications: ${card.applications.length}`);
    console.log(`Related Concepts: ${card.relatedConcepts.length}`);
  }
}

async function handleDetect(args: string[]) {
  const domainIndex = args.indexOf('--domain');
  const domain = domainIndex > -1 ? args[domainIndex + 1] : 'Machine Learning';

  const knownIndex = args.indexOf('--known');
  const known = knownIndex > -1 ? args[knownIndex + 1].split(',') : [];

  const outputIndex = args.indexOf('--output');
  const outputFile = outputIndex > -1 ? args[outputIndex + 1] : null;

  const detector = new KnowledgeGapDetector();
  await detector.initialize();

  console.log(`🔍 Detecting knowledge gaps in "${domain}"...`);

  const report = await detector.detect({
    domain,
    knownConcepts: known
  });

  if (outputFile) {
    const fs = require('fs');
    fs.writeFileSync(outputFile, detector.toMarkdown(report));
    console.log(`\n✅ Gap report saved to ${outputFile}`);
  } else {
    console.log('\n📊 Gap Analysis Summary:\n');
    console.log(`Domain: ${report.domain}`);
    console.log(`Coverage: ${report.summary.coveragePercentage}%`);
    console.log(`Total Gaps: ${report.summary.totalGaps}`);
    console.log(`  - Critical: ${report.summary.criticalCount}`);
    console.log(`  - Recommended: ${report.summary.recommendedCount}`);
    console.log(`  - Optional: ${report.summary.optionalCount}`);

    if (report.criticalGaps.length > 0) {
      console.log('\n🚨 Critical Gaps:');
      report.criticalGaps.slice(0, 5).forEach(gap => {
        console.log(`  - ${gap.concept}: ${gap.reason}`);
      });
    }
  }
}

async function handleTrack(args: string[]) {
  const action = args[0];

  const tracker = new ProgressTracker();
  await tracker.initialize();

  if (action === 'report') {
    const typeIndex = args.indexOf('--type');
    const type = typeIndex > -1 ? args[typeIndex + 1] as any : 'daily';

    const outputIndex = args.indexOf('--output');
    const outputFile = outputIndex > -1 ? args[outputIndex + 1] : null;

    console.log(`📊 Generating ${type} report...`);

    const report = await tracker.generateReport({ type });

    if (outputFile) {
      const fs = require('fs');
      fs.writeFileSync(outputFile, tracker.toMarkdown(report));
      console.log(`\n✅ Report saved to ${outputFile}`);
    } else {
      console.log('\n📈 Progress Report:\n');
      console.log(`Period: ${report.period.start} ~ ${report.period.end}`);
      console.log(`Total Papers: ${report.summary.totalPapers}`);
      console.log(`Highlighted: ${report.summary.highlightedPapers}`);
      console.log(`Trending: ${report.summary.trendingTopics.slice(0, 5).join(', ')}`);
    }
  } else {
    console.error('Error: Unknown track action. Use "report".');
    process.exit(1);
  }
}

async function handleAnalyze(args: string[]) {
  const url = args[0];
  if (!url) {
    console.error('Error: Please provide a paper URL');
    process.exit(1);
  }

  const modeIndex = args.indexOf('--mode');
  const mode = modeIndex > -1 ? args[modeIndex + 1] as any : 'standard';

  const outputIndex = args.indexOf('--output');
  const outputFile = outputIndex > -1 ? args[outputIndex + 1] : null;

  const analyzer = new PaperAnalyzer();
  await analyzer.initialize();

  console.log(`📄 Analyzing paper...`);

  const analysis = await analyzer.analyze({ url, mode });

  if (outputFile) {
    const fs = require('fs');
    fs.writeFileSync(outputFile, analyzer.toMarkdown(analysis));
    console.log(`\n✅ Analysis saved to ${outputFile}`);
  } else {
    console.log('\n📑 Paper Analysis:\n');
    console.log(`Title: ${analysis.metadata.title}`);
    console.log(`Authors: ${analysis.metadata.authors.join(', ')}`);
    console.log(`Year: ${analysis.metadata.year}`);
    console.log(`\nSummary: ${analysis.summary}`);
    console.log(`\nKey Points: ${analysis.keyPoints.length}`);
    console.log(`Contributions: ${analysis.contributions.length}`);
    console.log(`Limitations: ${analysis.limitations.length}`);
  }
}

async function handleGraph(args: string[]) {
  const concepts = args.filter(a => !a.startsWith('--'));

  if (concepts.length < 2) {
    console.error('Error: Please provide at least 2 concepts');
    process.exit(1);
  }

  const formatIndex = args.indexOf('--format');
  const format = formatIndex > -1 ? args[formatIndex + 1] : 'mermaid';

  const outputIndex = args.indexOf('--output');
  const outputFile = outputIndex > -1 ? args[outputIndex + 1] : null;

  const builder = new KnowledgeGraphBuilder();
  await builder.initialize();

  console.log(`🔗 Building knowledge graph...`);

  const graph = await builder.build(concepts);

  let output: string;
  if (format === 'json') {
    output = builder.toJSON(graph);
  } else {
    output = builder.toMermaid(graph);
  }

  if (outputFile) {
    const fs = require('fs');
    fs.writeFileSync(outputFile, output);
    console.log(`\n✅ Graph saved to ${outputFile}`);
  } else {
    console.log('\n📈 Knowledge Graph:\n');
    console.log(output);
  }
}

function handleConfig(args: string[]) {
  const action = args[0];
  const manager = new ConfigManager();

  switch (action) {
    case 'init':
      manager.save();
      console.log('✅ Configuration initialized at ./literature-config.json');
      break;

    case 'show':
      const config = manager.load();
      console.log(JSON.stringify(config, null, 2));
      break;

    case 'set':
      const key = args[1];
      const value = args[2];
      if (key && value) {
        try {
          const parsed = JSON.parse(value);
          manager.update({ [key]: parsed });
        } catch {
          (manager as any).config[key] = value;
          manager.save();
        }
        console.log(`✅ Set ${key}`);
      }
      break;

    case 'reset':
      manager.reset();
      console.log('✅ Configuration reset to defaults');
      break;

    default:
      console.error('Error: Unknown config action. Use init|show|set|reset.');
      process.exit(1);
  }
}

main().catch(console.error);
