/**
 * Knowledge Gap Detector - Core Module
 * 知识盲区检测核心模块
 * 
 * 主动识别知识缺口：
 * - 基于领域知识图谱分析
 * - 识别相关但未探索的方向
 * - 发现跨学科交叉点
 * - 推荐学习优先级
 */

import ZAI from 'z-ai-web-dev-sdk';
import type {
  DetectOptions,
  GapReport,
  KnowledgeGap,
  GapSummary,
  EstimatedEffort,
  KnowledgeProfile,
  LearningPathAnalysisOptions,
  CrossDisciplinaryOptions
} from './types';

// 领域知识图谱（简化版，实际应用可扩展）
const DOMAIN_GRAPHS: Record<string, string[]> = {
  'Natural Language Processing': [
    'tokenization', 'word embeddings', 'language models', 'sequence modeling',
    'RNN', 'LSTM', 'GRU', 'attention mechanism', 'transformer',
    'BERT', 'GPT', 'text classification', 'named entity recognition',
    'sentiment analysis', 'machine translation', 'question answering',
    'text generation', 'summarization', 'coreference resolution',
    'dependency parsing', 'constituency parsing', 'part-of-speech tagging',
    'word2vec', 'GloVe', 'FastText', 'ELMo', 'positional encoding',
    'self-attention', 'multi-head attention', 'encoder-decoder',
    'pre-training', 'fine-tuning', 'prompt engineering', 'RAG',
    'semantic search', 'knowledge graphs for NLP', 'dialogue systems'
  ],
  'Machine Learning': [
    'supervised learning', 'unsupervised learning', 'reinforcement learning',
    'regression', 'classification', 'clustering', 'dimensionality reduction',
    'decision trees', 'random forests', 'gradient boosting', 'XGBoost',
    'SVM', 'naive bayes', 'k-nearest neighbors', 'logistic regression',
    'neural networks', 'CNN', 'RNN', 'deep learning',
    'backpropagation', 'optimization', 'regularization', 'cross-validation',
    'feature engineering', 'feature selection', 'hyperparameter tuning',
    'ensemble methods', 'bagging', 'boosting', 'stacking',
    'overfitting', 'underfitting', 'bias-variance tradeoff',
    'data preprocessing', 'normalization', 'standardization',
    'model evaluation', 'precision', 'recall', 'F1 score', 'AUC-ROC',
    'transfer learning', 'meta-learning', 'few-shot learning'
  ],
  'Deep Learning': [
    'neural network fundamentals', 'activation functions', 'loss functions',
    'optimizers', 'gradient descent', 'backpropagation',
    'CNN', 'RNN', 'LSTM', 'GRU', 'transformer',
    'attention mechanism', 'self-attention', 'multi-head attention',
    'batch normalization', 'layer normalization', 'dropout',
    'weight initialization', 'residual connections', 'skip connections',
    'autoencoders', 'VAE', 'GANs', 'diffusion models',
    'transfer learning', 'fine-tuning', 'domain adaptation',
    'computer vision', 'image classification', 'object detection',
    'semantic segmentation', 'instance segmentation',
    'natural language processing', 'text classification', 'sequence labeling',
    'speech recognition', 'time series analysis',
    'model compression', 'quantization', 'pruning', 'knowledge distillation'
  ],
  'Computer Vision': [
    'image processing fundamentals', 'feature detection', 'edge detection',
    'CNN architectures', 'AlexNet', 'VGG', 'ResNet', 'Inception', 'EfficientNet',
    'object detection', 'YOLO', 'R-CNN', 'Faster R-CNN', 'SSD',
    'semantic segmentation', 'instance segmentation', 'panoptic segmentation',
    'image classification', 'transfer learning for vision',
    'object tracking', 'optical flow', 'pose estimation',
    'face recognition', 'face detection', 'facial landmark detection',
    'OCR', 'text detection', 'text recognition',
    'image generation', 'GANs', 'diffusion models', 'VAE',
    'video analysis', 'action recognition', 'video segmentation',
    '3D vision', 'point clouds', 'depth estimation', 'SLAM',
    'vision transformers', 'ViT', 'Swin Transformer',
    'multimodal learning', 'vision-language models', 'CLIP'
  ]
};

export default class KnowledgeGapDetector {
  private zai: Awaited<ReturnType<typeof ZAI.create>> | null = null;

  async initialize(): Promise<void> {
    if (!this.zai) {
      this.zai = await ZAI.create();
    }
  }

  /**
   * 检测知识盲区
   */
  async detect(options: DetectOptions): Promise<GapReport> {
    await this.initialize();

    const {
      domain,
      knownConcepts,
      targetLevel = 'intermediate',
      focusAreas,
      excludeConcepts = []
    } = options;

    // 获取领域知识图谱
    const domainGraph = this.getDomainGraph(domain);

    // 识别未掌握的概念
    const unknownConcepts = this.findUnknownConcepts(
      domainGraph,
      knownConcepts,
      excludeConcepts
    );

    // 分类知识缺口
    const classifiedGaps = await this.classifyGaps(
      unknownConcepts,
      knownConcepts,
      domain,
      targetLevel
    );

    // 发现新兴主题
    const emergingTopics = await this.discoverEmergingTopics(domain, knownConcepts);

    // 发现跨学科机会
    const crossDisciplinary = await this.findCrossDisciplinary(
      domain,
      knownConcepts
    );

    // 生成建议学习顺序
    const suggestedOrder = this.generateSuggestedOrder([
      ...classifiedGaps.critical,
      ...classifiedGaps.recommended
    ]);

    // 计算摘要
    const summary = this.calculateSummary(
      classifiedGaps,
      domainGraph,
      knownConcepts
    );

    // 估算学习工作量
    const estimatedEffort = this.estimateEffort(classifiedGaps);

    return {
      domain,
      analysisDate: new Date().toISOString(),
      summary,
      criticalGaps: classifiedGaps.critical,
      recommendedGaps: classifiedGaps.recommended,
      optionalGaps: classifiedGaps.optional,
      crossDisciplinary,
      emergingTopics,
      suggestedOrder,
      estimatedEffort
    };
  }

  /**
   * 从知识档案检测
   */
  async detectFromProfile(options: { profilePath: string; domain: string }): Promise<GapReport> {
    // 读取档案（简化实现）
    const profile: KnowledgeProfile = {
      domain: options.domain,
      knownConcepts: [],
      skillLevel: {},
      learningGoals: [],
      lastUpdated: new Date().toISOString()
    };

    return this.detect({
      domain: options.domain,
      knownConcepts: profile.knownConcepts
    });
  }

  /**
   * 分析学习路径缺口
   */
  async analyzeLearningPath(options: LearningPathAnalysisOptions): Promise<GapReport> {
    await this.initialize();

    const { currentPath, targetRole } = options;

    // 获取目标角色所需技能
    const requiredSkills = await this.getRoleRequiredSkills(targetRole);

    // 识别缺口
    const gaps = requiredSkills.filter(skill => !currentPath.includes(skill));

    return this.detect({
      domain: targetRole,
      knownConcepts: currentPath
    });
  }

  /**
   * 发现跨学科机会
   */
  async discoverCrossDisciplinary(options: CrossDisciplinaryOptions): Promise<KnowledgeGap[]> {
    await this.initialize();

    const { primaryDomain, relatedDomains, knownConcepts = [] } = options;

    const prompt = `作为一个跨学科研究专家，分析以下领域的交叉机会：

主领域: ${primaryDomain}
相关领域: ${relatedDomains.join(', ')}
已知概念: ${knownConcepts.join(', ')}

请识别：
1. 主领域与相关领域的交叉点
2. 可迁移的技术和方法
3. 有研究价值的跨学科方向

返回JSON格式：
{
  "crossDisciplinaryGaps": [
    {
      "concept": "交叉概念名称",
      "category": "cross-disciplinary",
      "reason": "为什么重要",
      "importance": 1-5,
      "prerequisites": ["前置知识"],
      "relatedKnown": ["相关已知知识"],
      "estimatedTime": "学习时间估计",
      "impactIfLearned": "学会后的影响"
    }
  ]
}`;

    const completion = await this.zai!.chat.completions.create({
      messages: [
        { role: 'system', content: '你是一位跨学科研究专家，擅长发现学科交叉创新机会。' },
        { role: 'user', content: prompt }
      ],
      temperature: 0.4
    });

    const responseText = completion.choices[0]?.message?.content || '{}';
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);

    if (jsonMatch) {
      try {
        const parsed = JSON.parse(jsonMatch[0]);
        return parsed.crossDisciplinaryGaps || [];
      } catch (e) {
        console.error('Failed to parse cross-disciplinary response');
      }
    }

    return [];
  }

  /**
   * 获取领域知识图谱
   */
  private getDomainGraph(domain: string): string[] {
    // 查找匹配的领域图谱
    for (const [key, concepts] of Object.entries(DOMAIN_GRAPHS)) {
      if (domain.toLowerCase().includes(key.toLowerCase()) ||
          key.toLowerCase().includes(domain.toLowerCase())) {
        return concepts;
      }
    }

    // 如果没有找到，返回基础ML概念
    return DOMAIN_GRAPHS['Machine Learning'];
  }

  /**
   * 查找未掌握概念
   */
  private findUnknownConcepts(
    domainGraph: string[],
    knownConcepts: string[],
    excludeConcepts: string[]
  ): string[] {
    const normalizedKnown = new Set(
      knownConcepts.map(c => c.toLowerCase().trim())
    );
    const normalizedExclude = new Set(
      excludeConcepts.map(c => c.toLowerCase().trim())
    );

    return domainGraph.filter(concept => {
      const normalized = concept.toLowerCase().trim();
      return !normalizedKnown.has(normalized) && !normalizedExclude.has(normalized);
    });
  }

  /**
   * 分类知识缺口
   */
  private async classifyGaps(
    unknownConcepts: string[],
    knownConcepts: string[],
    domain: string,
    targetLevel: string
  ): Promise<{
    critical: KnowledgeGap[];
    recommended: KnowledgeGap[];
    optional: KnowledgeGap[];
  }> {
    const prompt = `作为知识体系专家，分析以下知识缺口并分类：

领域: ${domain
    }
未知概念: ${unknownConcepts.join(', ')
    }
已知概念: ${knownConcepts.join(', ')
    }
目标水平: ${targetLevel

    }

请将每个未知概念分类为：
- critical: 必须掌握的基础或核心概念
- recommended: 建议学习的扩展概念
- optional: 可选的高级概念

返回JSON格式：
{
  "gaps": [
    {
      "concept": "概念名",
      "category": "critical|recommended|optional",
      "reason": "分类原因",
      "importance": 1-5,
      "prerequisites": ["前置知识"],
      "relatedKnown": ["相关已知概念"],
      "estimatedTime": "学习时间",
      "impactIfLearned": "学习后的影响"
    }
  ]
}`;

    const completion = await this.zai!.chat.completions.create({
      messages: [
        { role: 'system', content: '你是一位知识体系分析专家。' },
        { role: 'user', content: prompt }
      ],
      temperature: 0.2
    });

    const responseText = completion.choices[0]?.message?.content || '{}';
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);

    const critical: KnowledgeGap[] = [];
    const recommended: KnowledgeGap[] = [];
    const optional: KnowledgeGap[] = [];

    if (jsonMatch) {
      try {
        const parsed = JSON.parse(jsonMatch[0]);
        for (const gap of (parsed.gaps || [])) {
          gap.resources = [];
          if (gap.category === 'critical') {
            critical.push(gap);
          } else if (gap.category === 'recommended') {
            recommended.push(gap);
          } else {
            optional.push(gap);
          }
        }
      } catch (e) {
        console.error('Failed to classify gaps');
      }
    }

    return { critical, recommended, optional };
  }

  /**
   * 发现新兴主题
   */
  private async discoverEmergingTopics(
    domain: string,
    knownConcepts: string[]
  ): Promise<KnowledgeGap[]> {
    try {
      const results = await this.zai!.functions.invoke('web_search', {
        query: `${domain} emerging trends 2024 new techniques`,
        num: 5
      });

      return results.map((item: any) => ({
        concept: item.name,
        category: 'emerging' as const,
        reason: '该主题是近期新兴的研究方向',
        importance: 3 as const,
        prerequisites: [],
        relatedKnown: [],
        resources: [{
          type: 'paper' as const,
          title: item.name,
          url: item.url,
          description: item.snippet,
          difficulty: 'advanced' as const
        }],
        estimatedTime: '2-4周',
        impactIfLearned: '掌握前沿技术，保持竞争力'
      }));
    } catch (error) {
      console.error('Failed to discover emerging topics:', error);
      return [];
    }
  }

  /**
   * 发现跨学科机会
   */
  private async findCrossDisciplinary(
    domain: string,
    knownConcepts: string[]
  ): Promise<KnowledgeGap[]> {
    // 获取相关领域
    const relatedDomains = this.getRelatedDomains(domain);

    if (relatedDomains.length === 0) return [];

    return this.discoverCrossDisciplinary({
      primaryDomain: domain,
      relatedDomains,
      knownConcepts
    });
  }

  /**
   * 获取相关领域
   */
  private getRelatedDomains(domain: string): string[] {
    const domainRelations: Record<string, string[]> = {
      'Natural Language Processing': ['Machine Learning', 'Deep Learning', 'Knowledge Graphs', 'Speech Recognition'],
      'Machine Learning': ['Statistics', 'Deep Learning', 'Optimization', 'Data Science'],
      'Deep Learning': ['Machine Learning', 'Computer Vision', 'NLP', 'Reinforcement Learning'],
      'Computer Vision': ['Deep Learning', 'Image Processing', 'Robotics', 'Graphics']
    };

    for (const [key, related] of Object.entries(domainRelations)) {
      if (domain.toLowerCase().includes(key.toLowerCase())) {
        return related;
      }
    }

    return [];
  }

  /**
   * 生成建议学习顺序
   */
  private generateSuggestedOrder(gaps: KnowledgeGap[]): string[] {
    // 按重要性和前置关系排序
    const sorted = [...gaps].sort((a, b) => {
      // 先按重要性排序
      if (a.importance !== b.importance) {
        return b.importance - a.importance;
      }
      // 再按前置知识数量排序（少的先学）
      return a.prerequisites.length - b.prerequisites.length;
    });

    return sorted.map(g => g.concept);
  }

  /**
   * 计算摘要
   */
  private calculateSummary(
    classifiedGaps: { critical: KnowledgeGap[]; recommended: KnowledgeGap[]; optional: KnowledgeGap[] },
    domainGraph: string[],
    knownConcepts: string[]
  ): GapSummary {
    const criticalCount = classifiedGaps.critical.length;
    const recommendedCount = classifiedGaps.recommended.length;
    const optionalCount = classifiedGaps.optional.length;
    const totalGaps = criticalCount + recommendedCount + optionalCount;

    const coveragePercentage = Math.round(
      (knownConcepts.length / (knownConcepts.length + totalGaps)) * 100
    );

    return {
      totalGaps,
      criticalCount,
      recommendedCount,
      optionalCount,
      coveragePercentage
    };
  }

  /**
   * 估算学习工作量
   */
  private estimateEffort(
    classifiedGaps: { critical: KnowledgeGap[]; recommended: KnowledgeGap[]; optional: KnowledgeGap[] }
  ): EstimatedEffort {
    const criticalHours = classifiedGaps.critical.length * 10; // 每个关键概念约10小时
    const recommendedHours = classifiedGaps.recommended.length * 5; // 每个推荐概念约5小时

    return {
      critical: `约 ${Math.ceil(criticalHours / 10)} 周 (每周10小时)`,
      recommended: `约 ${Math.ceil(recommendedHours / 10)} 周 (每周10小时)`,
      total: `约 ${Math.ceil((criticalHours + recommendedHours) / 10)} 周 (每周10小时)`
    };
  }

  /**
   * 获取角色所需技能
   */
  private async getRoleRequiredSkills(role: string): Promise<string[]> {
    const completion = await this.zai!.chat.completions.create({
      messages: [
        {
          role: 'system',
          content: '你是一位职业发展专家，了解各类技术岗位的技能要求。'
        },
        {
          role: 'user',
          content: `列出${role}需要掌握的核心技能，返回JSON数组格式：["skill1", "skill2", ...]`
        }
      ],
      temperature: 0.2
    });

    const responseText = completion.choices[0]?.message?.content || '[]';
    const jsonMatch = responseText.match(/\[[\s\S]*\]/);

    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[0]);
      } catch (e) {
        return [];
      }
    }

    return [];
  }

  /**
   * 导出为Markdown报告
   */
  toMarkdown(report: GapReport): string {
    return `# ${report.domain} 知识盲区分析报告

## 📊 总览

- 分析时间: ${report.analysisDate}
- 知识覆盖率: ${report.summary.coveragePercentage}%
- 发现缺口总数: ${report.summary.totalGaps}

| 类型 | 数量 |
|------|------|
| 关键缺口 | ${report.summary.criticalCount} |
| 建议学习 | ${report.summary.recommendedCount} |
| 可选扩展 | ${report.summary.optionalCount} |

## 🚨 关键缺口 (必须掌握)

${report.criticalGaps.map(g => `
### ${g.concept}
- **重要性**: ${'⭐'.repeat(g.importance)}
- **原因**: ${g.reason}
- **前置知识**: ${g.prerequisites.join(', ') || '无'}
- **预计时间**: ${g.estimatedTime}
- **学习影响**: ${g.impactIfLearned}
`).join('\n')}

## 📚 建议学习

${report.recommendedGaps.map(g => `
### ${g.concept}
- **重要性**: ${'⭐'.repeat(g.importance)}
- **原因**: ${g.reason}
- **预计时间**: ${g.estimatedTime}
`).join('\n')}

## 🔗 跨学科机会

${report.crossDisciplinary.map(g => `
### ${g.concept}
- **原因**: ${g.reason}
- **影响**: ${g.impactIfLearned}
`).join('\n')}

## 📈 新兴主题

${report.emergingTopics.map(g => `
- **${g.concept}**: ${g.reason}
`).join('\n')}

## 🎯 建议学习顺序

1. ${report.suggestedOrder.join('\n2. ')}

## ⏱️ 预计学习工作量

- 补齐关键缺口: ${report.estimatedEffort.critical}
- 完成建议学习: ${report.estimatedEffort.recommended}
- **总计**: ${report.estimatedEffort.total}

---
*由知识盲区检测器生成*
`;
  }
}

// CLI 支持
if (import.meta.main) {
  const args = process.argv.slice(2);

  const domainIndex = args.indexOf('--domain');
  const knownIndex = args.indexOf('--known');
  const outputIndex = args.indexOf('--output');

  const domain = domainIndex > -1 ? args[domainIndex + 1] : 'Machine Learning';
  const known = knownIndex > -1 ? args[knownIndex + 1].split(',') : [];
  const outputFile = outputIndex > -1 ? args[outputIndex + 1] : null;

  const detector = new KnowledgeGapDetector();

  detector.detect({ domain, knownConcepts: known }).then(report => {
    if (outputFile) {
      const fs = require('fs');
      fs.writeFileSync(outputFile, detector.toMarkdown(report));
      console.log(`Gap report saved to ${outputFile}`);
    } else {
      console.log(JSON.stringify(report, null, 2));
    }
  }).catch(console.error);
}
