/**
 * Literature Search - Core Module
 * 文献检索核心模块
 * 
 * 提供多源文献检索能力：
 * - arXiv API
 * - Semantic Scholar API
 * - Web Search (通过z-ai-web-dev-sdk)
 */

import ZAI from 'z-ai-web-dev-sdk';
import type { SearchOptions, SearchResult, SearchResponse, ArxivPaper, SemanticScholarPaper } from './types';

// arXiv API 基础URL
const ARXIV_API_URL = 'http://export.arxiv.org/api/query';

// Semantic Scholar API 基础URL
const S2_API_URL = 'https://api.semanticscholar.org/graph/v1';

export default class LiteratureSearch {
  private zai: Awaited<ReturnType<typeof ZAI.create>> | null = null;

  /**
   * 初始化搜索器
   */
  async initialize(): Promise<void> {
    if (!this.zai) {
      this.zai = await ZAI.create();
    }
  }

  /**
   * 综合搜索入口
   */
  async search(query: string, options: SearchOptions = {}): Promise<SearchResponse> {
    await this.initialize();

    const {
      sources = ['arxiv', 'semantic_scholar', 'web'],
      limit = 10,
      sortBy = 'relevance',
      filters
    } = options;

    const allResults: SearchResult[] = [];
    const usedSources: string[] = [];

    // 并行搜索多个数据源
    const searchPromises: Promise<SearchResult[]>[] = [];

    if (sources.includes('arxiv')) {
      searchPromises.push(this.searchArxiv(query, limit));
      usedSources.push('arxiv');
    }

    if (sources.includes('semantic_scholar')) {
      searchPromises.push(this.searchSemanticScholar(query, limit));
      usedSources.push('semantic_scholar');
    }

    if (sources.includes('web')) {
      searchPromises.push(this.searchWeb(query, limit));
      usedSources.push('web');
    }

    const results = await Promise.allSettled(searchPromises);

    // 合并结果
    results.forEach((result) => {
      if (result.status === 'fulfilled') {
        allResults.push(...result.value);
      }
    });

    // 应用过滤
    let filtered = this.applyFilters(allResults, filters);

    // 排序
    filtered = this.sortResults(filtered, sortBy);

    // 限制结果数量
    filtered = filtered.slice(0, limit * sources.length);

    // 去重（基于标题相似度）
    filtered = this.deduplicateResults(filtered);

    return {
      query,
      totalResults: filtered.length,
      results: filtered.slice(0, limit),
      sources: usedSources,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * arXiv 搜索
   */
  private async searchArxiv(query: string, limit: number): Promise<SearchResult[]> {
    try {
      const searchQuery = encodeURIComponent(`all:${query}`);
      const url = `${ARXIV_API_URL}?search_query=${searchQuery}&max_results=${limit}&sortBy=relevance`;

      const response = await fetch(url);
      const text = await response.text();

      return this.parseArxivResponse(text);
    } catch (error) {
      console.error('arXiv search error:', error);
      return [];
    }
  }

  /**
   * 解析 arXiv API 响应
   */
  private parseArxivResponse(xml: string): SearchResult[] {
    const results: SearchResult[] = [];

    // 简单的XML解析（生产环境建议使用专业XML解析器）
    const entries = xml.split('<entry>').slice(1);

    for (const entry of entries) {
      try {
        const title = this.extractXmlContent(entry, 'title');
        const abstract = this.extractXmlContent(entry, 'summary');
        const published = this.extractXmlContent(entry, 'published');
        const id = this.extractXmlContent(entry, 'id');

        // 提取作者
        const authorMatches = entry.match(/<author>[\s\S]*?<name>([^<]+)<\/name>[\s\S]*?<\/author>/g) || [];
        const authors = authorMatches.map(a => {
          const match = a.match(/<name>([^<]+)<\/name>/);
          return match ? match[1].trim() : '';
        }).filter(Boolean);

        // 提取分类
        const categoryMatches = entry.match(/category term="([^"]+)"/g) || [];
        const categories = categoryMatches.map(c => {
          const match = c.match(/term="([^"]+)"/);
          return match ? match[1] : '';
        }).filter(Boolean);

        results.push({
          id: id.split('/abs/')[1] || id,
          title: title.trim(),
          authors,
          abstract: abstract.trim(),
          publishDate: published.split('T')[0],
          source: 'arxiv',
          url: id,
          pdfUrl: id.replace('/abs/', '/pdf/') + '.pdf',
          keywords: categories
        });
      } catch (e) {
        continue;
      }
    }

    return results;
  }

  /**
   * 提取XML内容
   */
  private extractXmlContent(xml: string, tag: string): string {
    const match = xml.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, 'i'));
    return match ? match[1].trim() : '';
  }

  /**
   * Semantic Scholar 搜索
   */
  private async searchSemanticScholar(query: string, limit: number): Promise<SearchResult[]> {
    try {
      const fields = 'paperId,title,abstract,authors,year,citationCount,venue,url,openAccessPdf';
      const url = `${S2_API_URL}/paper/search?query=${encodeURIComponent(query)}&limit=${limit}&fields=${fields}`;

      const response = await fetch(url);
      const data = await response.json() as { data?: SemanticScholarPaper[] };

      if (!data.data) return [];

      return data.data.map((paper) => ({
        id: paper.paperId,
        title: paper.title,
        authors: paper.authors.map(a => a.name),
        abstract: paper.abstract || '',
        publishDate: paper.year?.toString() || '',
        source: 'semantic_scholar',
        url: paper.url,
        pdfUrl: paper.openAccessPdf?.url,
        citations: paper.citationCount,
        venue: paper.venue
      }));
    } catch (error) {
      console.error('Semantic Scholar search error:', error);
      return [];
    }
  }

  /**
   * Web 搜索（通过 z-ai-web-dev-sdk）
   */
  private async searchWeb(query: string, limit: number): Promise<SearchResult[]> {
    if (!this.zai) {
      await this.initialize();
    }

    try {
      // 构建学术搜索查询
      const academicQuery = `${query} research paper arxiv OR scholar OR "paper" OR "publication"`;

      const results = await this.zai!.functions.invoke('web_search', {
        query: academicQuery,
        num: limit
      });

      return results.map((item: any, index: number) => ({
        id: `web_${index}`,
        title: item.name,
        authors: [],
        abstract: item.snippet || '',
        publishDate: item.date || '',
        source: 'web',
        url: item.url,
        snippet: item.snippet
      }));
    } catch (error) {
      console.error('Web search error:', error);
      return [];
    }
  }

  /**
   * 按作者搜索
   */
  async searchByAuthor(authorName: string, options: SearchOptions = {}): Promise<SearchResponse> {
    const query = `author:"${authorName}"`;
    return this.search(query, { ...options, sources: ['arxiv', 'semantic_scholar'] });
  }

  /**
   * 应用过滤条件
   */
  private applyFilters(results: SearchResult[], filters?: SearchOptions['filters']): SearchResult[] {
    if (!filters) return results;

    let filtered = [...results];

    // 年份过滤
    if (filters.yearRange) {
      const [start, end] = filters.yearRange;
      filtered = filtered.filter(r => {
        const year = parseInt(r.publishDate.split('-')[0]);
        return year >= start && year <= end;
      });
    }

    // 最小引用数过滤
    if (filters.minCitations) {
      filtered = filtered.filter(r =>
        !r.citations || r.citations >= filters.minCitations!
      );
    }

    // 分类过滤
    if (filters.categories?.length) {
      filtered = filtered.filter(r =>
        r.keywords?.some(k => filters.categories!.includes(k))
      );
    }

    return filtered;
  }

  /**
   * 排序结果
   */
  private sortResults(results: SearchResult[], sortBy: string): SearchResult[] {
    const sorted = [...results];

    switch (sortBy) {
      case 'citations':
        return sorted.sort((a, b) => (b.citations || 0) - (a.citations || 0));
      case 'date':
        return sorted.sort((a, b) =>
          new Date(b.publishDate).getTime() - new Date(a.publishDate).getTime()
        );
      default:
        return sorted; // 按相关性（API默认顺序）
    }
  }

  /**
   * 去重（基于标题相似度）
   */
  private deduplicateResults(results: SearchResult[]): SearchResult[] {
    const seen = new Set<string>();
    const deduped: SearchResult[] = [];

    for (const result of results) {
      // 简单的标题标准化用于去重
      const normalizedTitle = result.title.toLowerCase()
        .replace(/[^a-z0-9]/g, '')
        .substring(0, 50);

      if (!seen.has(normalizedTitle)) {
        seen.add(normalizedTitle);
        deduped.push(result);
      }
    }

    return deduped;
  }
}

// CLI 支持
if (import.meta.main) {
  const args = process.argv.slice(2);
  const query = args[0];

  if (!query) {
    console.error('Usage: bun run search.ts <query> [--limit N] [--source <arxiv|semantic_scholar|web>]');
    process.exit(1);
  }

  const limit = parseInt(args[args.indexOf('--limit') + 1]) || 10;
  const sourceIndex = args.indexOf('--source');
  const source = sourceIndex > -1 ? args[sourceIndex + 1] as any : undefined;

  const searcher = new LiteratureSearch();

  searcher.search(query, {
    limit,
    sources: source ? [source] : undefined
  }).then(response => {
    console.log(JSON.stringify(response, null, 2));
  }).catch(console.error);
}
