/**
 * Paper Analyzer - Core Module
 * 论文分析核心模块
 * 
 * 提供论文深度分析能力：
 * - 智能阅读与结构提取
 * - 方法学分析
 * - 实验结果解读
 * - 引用关系梳理
 */

import ZAI from 'z-ai-web-dev-sdk';
import type {
  AnalyzeOptions,
  PaperAnalysis,
  PaperMetadata,
  KeyPoint,
  MethodologyAnalysis,
  ExperimentAnalysis,
  Contribution,
  Limitation,
  CitationAnalysis,
  RelatedWork,
  ReproducibilityAnalysis,
  AnalysisRecommendations,
  ComparisonResult,
  CritiqueResult
} from './types';

export default class PaperAnalyzer {
  private zai: Awaited<ReturnType<typeof ZAI.create>> | null = null;

  async initialize(): Promise<void> {
    if (!this.zai) {
      this.zai = await ZAI.create();
    }
  }

  /**
   * 分析论文
   */
  async analyze(options: AnalyzeOptions): Promise<PaperAnalysis> {
    await this.initialize();

    const {
      url,
      text,
      mode = 'standard',
      depth = 'standard',
      includeCitations = false,
      includeRelatedWork = false,
      focusAreas,
      language = 'zh-CN'
    } = options;

    // 获取论文内容
    let paperContent = text;
    let metadata: Partial<PaperMetadata> = { url };

    if (url && !text) {
      const fetched = await this.fetchPaperContent(url);
      paperContent = fetched.content;
      metadata = { ...metadata, ...fetched.metadata };
    }

    if (!paperContent) {
      throw new Error('No paper content available for analysis');
    }

    // 根据模式执行分析
    const analysisMode = mode || depth;
    const analysis = await this.performAnalysis(
      paperContent,
      metadata,
      analysisMode,
      { includeCitations, includeRelatedWork, focusAreas, language }
    );

    return analysis;
  }

  /**
   * 获取论文内容
   */
  private async fetchPaperContent(url: string): Promise<{
    content: string;
    metadata: Partial<PaperMetadata>;
  }> {
    try {
      // 尝试从web搜索获取相关信息
      const searchResults = await this.zai!.functions.invoke('web_search', {
        query: `${url} abstract summary`,
        num: 5
      });

      // 提取信息
      let content = '';
      const metadata: Partial<PaperMetadata> = { url };

      for (const result of searchResults) {
        content += result.snippet + '\n\n';
        if (!metadata.title && result.name) {
          metadata.title = result.name;
        }
      }

      // 如果是arXiv链接，提取ID
      const arxivMatch = url.match(/arxiv\.org\/abs\/(\d+\.\d+)/);
      if (arxivMatch) {
        metadata.arxivId = arxivMatch[1];
      }

      return { content, metadata };
    } catch (error) {
      console.error('Error fetching paper content:', error);
      return { content: '', metadata: { url } };
    }
  }

  /**
   * 执行分析
   */
  private async performAnalysis(
    content: string,
    metadata: Partial<PaperMetadata>,
    mode: string,
    options: {
      includeCitations: boolean;
      includeRelatedWork: boolean;
      focusAreas?: string[];
      language: string;
    }
  ): Promise<PaperAnalysis> {
    const { includeCitations, includeRelatedWork, focusAreas, language } = options;

    const langPrompt = language === 'zh-CN' ? '请用中文回答' : 'Please answer in English';

    // 构建分析prompt
    const analysisPrompt = this.buildAnalysisPrompt(content, mode, langPrompt, focusAreas);

    const completion = await this.zai!.chat.completions.create({
      messages: [
        {
          role: 'system',
          content: '你是一位资深的学术研究分析专家，擅长深入分析学术论文的结构、方法、实验和贡献。'
        },
        { role: 'user', content: analysisPrompt }
      ],
      temperature: 0.2
    });

    const responseText = completion.choices[0]?.message?.content || '{}';

    // 解析响应
    const parsed = this.parseAnalysisResponse(responseText);

    // 补充引用分析
    let citations: CitationAnalysis = { keyReferences: [] };
    if (includeCitations) {
      citations = await this.analyzeCitations(content);
    }

    // 补充相关工作
    let relatedWork: RelatedWork[] = [];
    if (includeRelatedWork) {
      relatedWork = await this.analyzeRelatedWork(content);
    }

    return {
      metadata: {
        title: metadata.title || parsed.title || 'Unknown',
        authors: metadata.authors || parsed.authors || [],
        venue: metadata.venue || parsed.venue,
        year: metadata.year || parsed.year || new Date().getFullYear().toString(),
        doi: metadata.doi || parsed.doi,
        arxivId: metadata.arxivId,
        url: metadata.url || '',
        keywords: parsed.keywords || []
      },
      abstract: parsed.abstract || '',
      summary: parsed.summary || '',
      keyPoints: parsed.keyPoints || [],
      methodology: parsed.methodology || this.getDefaultMethodology(),
      experiments: parsed.experiments || this.getDefaultExperiments(),
      contributions: parsed.contributions || [],
      limitations: parsed.limitations || [],
      futureWork: parsed.futureWork || [],
      citations,
      relatedWork,
      reproducibility: parsed.reproducibility || this.getDefaultReproducibility(),
      recommendations: parsed.recommendations || this.getDefaultRecommendations(),
      generatedAt: new Date().toISOString()
    };
  }

  /**
   * 构建分析prompt
   */
  private buildAnalysisPrompt(
    content: string,
    mode: string,
    langPrompt: string,
    focusAreas?: string[]
  ): string {
    const focusPrompt = focusAreas
      ? `\n重点关注领域: ${focusAreas.join(', ')}`
      : '';

    const depthInstruction = mode === 'quick'
      ? '提供简洁的分析，专注于核心要点。'
      : mode === 'deep'
        ? '提供深入详细的分析，包括方法细节、实验设计、引用关系等。'
        : '提供标准深度的分析。';

    return `${langPrompt}

分析以下论文内容:

${content.substring(0, 5000)}${content.length > 5000 ? '...(内容已截断)' : ''}

${depthInstruction}
${focusPrompt}

请返回JSON格式的分析结果:
{
  "title": "论文标题",
  "authors": ["作者1", "作者2"],
  "venue": "发表期刊/会议",
  "year": "年份",
  "keywords": ["关键词1", "关键词2"],
  "abstract": "摘要",
  "summary": "整体摘要（3-5句话）",
  "keyPoints": [
    {
      "point": "关键点",
      "importance": "critical|important|supporting",
      "location": "在论文中的位置",
      "explanation": "解释"
    }
  ],
  "methodology": {
    "overview": "方法概述",
    "approach": "具体方法",
    "novelty": "创新点",
    "assumptions": ["假设条件"],
    "strengths": ["优点"],
    "weaknesses": ["缺点"]
  },
  "experiments": {
    "datasets": ["数据集"],
    "metrics": ["评估指标"],
    "baselines": ["基线方法"],
    "mainResults": "主要结果",
    "ablations": ["消融实验"],
    "analysis": "结果分析"
  },
  "contributions": [
    {
      "description": "贡献描述",
      "type": "methodological|empirical|theoretical|dataset|tool",
      "significance": "major|moderate|minor"
    }
  ],
  "limitations": [
    {
      "description": "局限性描述",
      "impact": "high|medium|low",
      "potentialSolution": "可能的解决方案"
    }
  ],
  "futureWork": ["未来工作方向"],
  "reproducibility": {
    "score": 0-100,
    "codeAvailable": true|false,
    "datasetAvailable": true|false,
    "detailsAvailable": true|false,
    "notes": "备注"
  },
  "recommendations": {
    "forResearchers": ["对研究者的建议"],
    "forPractitioners": ["对实践者的建议"],
    "furtherReading": ["推荐阅读"]
  }
}`;
  }

  /**
   * 解析分析响应
   */
  private parseAnalysisResponse(responseText: string): any {
    try {
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      console.error('Error parsing analysis response:', error);
    }
    return {};
  }

  /**
   * 分析引用
   */
  private async analyzeCitations(content: string): Promise<CitationAnalysis> {
    const prompt = `分析以下论文内容的引用关系，提取关键引用:

${content.substring(0, 2000)}

返回JSON格式:
{
  "keyReferences": ["关键引用论文1", "关键引用论文2"],
  "influentialCitations": ["有影响力的引用"]
}`;

    try {
      const completion = await this.zai!.chat.completions.create({
        messages: [
          { role: 'system', content: '你是一位学术引用分析专家。' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.2
      });

      const responseText = completion.choices[0]?.message?.content || '{}';
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);

      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      console.error('Error analyzing citations:', error);
    }

    return { keyReferences: [] };
  }

  /**
   * 分析相关工作
   */
  private async analyzeRelatedWork(content: string): Promise<RelatedWork[]> {
    const prompt = `分析以下论文的相关工作，识别相关研究领域:

${content.substring(0, 2000)}

返回JSON格式:
{
  "relatedWork": [
    {
      "category": "相关领域名称",
      "papers": ["相关论文"],
      "comparison": "与本论文的对比"
    }
  ]
}`;

    try {
      const completion = await this.zai!.chat.completions.create({
        messages: [
          { role: 'system', content: '你是一位学术领域分析专家。' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.2
      });

      const responseText = completion.choices[0]?.message?.content || '{}';
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);

      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        return parsed.relatedWork || [];
      }
    } catch (error) {
      console.error('Error analyzing related work:', error);
    }

    return [];
  }

  /**
   * 比较多篇论文
   */
  async compare(urls: string[]): Promise<ComparisonResult> {
    await this.initialize();

    // 分析每篇论文
    const analyses = await Promise.all(
      urls.map(url => this.analyze({ url, mode: 'standard' }))
    );

    // 生成比较分析
    const comparisonPrompt = `比较以下论文:

${analyses.map((a, i) => `
论文${i + 1}: ${a.metadata.title}
摘要: ${a.summary}
主要贡献: ${a.contributions.map(c => c.description).join(', ')}
方法: ${a.methodology.overview}
`).join('\n')}

返回JSON格式的比较分析:
{
  "commonThemes": ["共同主题"],
  "differences": ["主要差异"],
  "methodologicalComparison": "方法学比较",
  "performanceComparison": "性能比较（如有）",
  "synthesis": "综合分析"
}`;

    const completion = await this.zai!.chat.completions.create({
      messages: [
        { role: 'system', content: '你是一位学术论文比较分析专家。' },
        { role: 'user', content: comparisonPrompt }
      ],
      temperature: 0.2
    });

    const responseText = completion.choices[0]?.message?.content || '{}';
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);

    let comparisonData = {
      commonThemes: [],
      differences: [],
      methodologicalComparison: '',
      performanceComparison: '',
      synthesis: ''
    };

    if (jsonMatch) {
      comparisonData = JSON.parse(jsonMatch[0]);
    }

    return {
      papers: analyses.map(a => a.metadata),
      ...comparisonData
    };
  }

  /**
   * 批判性分析
   */
  async critique(options: AnalyzeOptions & { focusAreas?: string[] }): Promise<CritiqueResult> {
    const analysis = await this.analyze({ ...options, mode: 'deep' });

    const critiquePrompt = `对以下论文进行批判性分析:

标题: ${analysis.metadata.title}
摘要: ${analysis.summary}
方法: ${analysis.methodology.overview}
主要贡献: ${analysis.contributions.map(c => c.description).join(', ')}
局限性: ${analysis.limitations.map(l => l.description).join(', ')}

${options.focusAreas ? `重点关注: ${options.focusAreas.join(', ')}` : ''}

返回JSON格式:
{
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["缺点1", "缺点2"],
  "gaps": ["研究空白"],
  "suggestions": ["改进建议"],
  "overallAssessment": "总体评价"
}`;

    const completion = await this.zai!.chat.completions.create({
      messages: [
        { role: 'system', content: '你是一位批判性思维专家，能够客观评价学术研究。' },
        { role: 'user', content: critiquePrompt }
      ],
      temperature: 0.3
    });

    const responseText = completion.choices[0]?.message?.content || '{}';
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);

    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }

    return {
      strengths: [],
      weaknesses: [],
      gaps: [],
      suggestions: [],
      overallAssessment: ''
    };
  }

  /**
   * 默认方法学分析
   */
  private getDefaultMethodology(): MethodologyAnalysis {
    return {
      overview: '',
      approach: '',
      novelty: '',
      assumptions: [],
      strengths: [],
      weaknesses: []
    };
  }

  /**
   * 默认实验分析
   */
  private getDefaultExperiments(): ExperimentAnalysis {
    return {
      datasets: [],
      metrics: [],
      baselines: [],
      mainResults: '',
      ablations: [],
      analysis: ''
    };
  }

  /**
   * 默认可复现性分析
   */
  private getDefaultReproducibility(): ReproducibilityAnalysis {
    return {
      score: 50,
      codeAvailable: false,
      datasetAvailable: false,
      detailsAvailable: false,
      notes: '无法确定'
    };
  }

  /**
   * 默认推荐
   */
  private getDefaultRecommendations(): AnalysisRecommendations {
    return {
      forResearchers: [],
      forPractitioners: [],
      furtherReading: []
    };
  }

  /**
   * 导出为Markdown
   */
  toMarkdown(analysis: PaperAnalysis): string {
    return `# ${analysis.metadata.title}

## 📋 基本信息

- **作者**: ${analysis.metadata.authors.join(', ') || '未知'}
- **年份**: ${analysis.metadata.year}
- **来源**: ${analysis.metadata.venue || '未知'}
- **关键词**: ${analysis.metadata.keywords.join(', ') || '无'}
- **链接**: ${analysis.metadata.url}

## 📖 摘要

${analysis.abstract || analysis.summary}

## 🎯 关键要点

${analysis.keyPoints.map(k => `
### ${k.point}
- **重要性**: ${k.importance}
- **说明**: ${k.explanation}
`).join('\n')}

## 🔬 方法分析

### 概述
${analysis.methodology.overview}

### 创新点
${analysis.methodology.novelty}

### 优点
${analysis.methodology.strengths.map(s => `- ${s}`).join('\n')}

### 缺点
${analysis.methodology.weaknesses.map(w => `- ${w}`).join('\n')}

## 📊 实验结果

- **数据集**: ${analysis.experiments.datasets.join(', ') || '未指定'}
- **评估指标**: ${analysis.experiments.metrics.join(', ') || '未指定'}
- **基线方法**: ${analysis.experiments.baselines.join(', ') || '未指定'}

### 主要结果
${analysis.experiments.mainResults}

## 🏆 贡献

${analysis.contributions.map(c => `
- **${c.description}** (${c.significance} - ${c.type})
`).join('\n')}

## ⚠️ 局限性

${analysis.limitations.map(l => `
- **${l.description}** (影响程度: ${l.impact})
${l.potentialSolution ? `  - 可能的解决方案: ${l.potentialSolution}` : ''}
`).join('\n')}

## 🔮 未来工作

${analysis.futureWork.map(f => `- ${f}`).join('\n')}

## 🔄 可复现性

- **评分**: ${analysis.reproducibility.score}/100
- **代码可用**: ${analysis.reproducibility.codeAvailable ? '是' : '否'}
- **数据可用**: ${analysis.reproducibility.datasetAvailable ? '是' : '否'}
- **备注**: ${analysis.reproducibility.notes}

## 💡 建议

### 对研究者
${analysis.recommendations.forResearchers.map(r => `- ${r}`).join('\n') || '暂无'}

### 对实践者
${analysis.recommendations.forPractitioners.map(r => `- ${r}`).join('\n') || '暂无'}

---
*分析时间: ${analysis.generatedAt}*
`;
  }
}

// CLI 支持
if (import.meta.main) {
  const args = process.argv.slice(2);

  const urlIndex = args.indexOf('--url');
  const fileIndex = args.indexOf('--file');
  const outputIndex = args.indexOf('--output');
  const modeIndex = args.indexOf('--mode');

  const url = urlIndex > -1 ? args[urlIndex + 1] : undefined;
  const file = fileIndex > -1 ? args[fileIndex + 1] : undefined;
  const outputFile = outputIndex > -1 ? args[outputIndex + 1] : null;
  const mode = modeIndex > -1 ? args[modeIndex + 1] as any : 'standard';

  if (!url && !file) {
    console.error('Usage: analyze.ts --url <url> [--mode quick|standard|deep] [--output <file>]');
    console.error('       analyze.ts --file <path> [--mode quick|standard|deep] [--output <file>]');
    process.exit(1);
  }

  const analyzer = new PaperAnalyzer();

  analyzer.analyze({ url, file, mode }).then(analysis => {
    if (outputFile) {
      const fs = require('fs');
      fs.writeFileSync(outputFile, analyzer.toMarkdown(analysis));
      console.log(`Analysis saved to ${outputFile}`);
    } else {
      console.log(JSON.stringify(analysis, null, 2));
    }
  }).catch(console.error);
}
