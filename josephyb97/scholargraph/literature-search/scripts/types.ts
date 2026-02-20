/**
 * Literature Search - Type Definitions
 * 文献检索类型定义
 */

export interface SearchOptions {
  sources?: ('arxiv' | 'semantic_scholar' | 'web')[];
  limit?: number;
  sortBy?: 'relevance' | 'date' | 'citations';
  filters?: {
    yearRange?: [number, number];
    categories?: string[];
    minCitations?: number;
    authors?: string[];
  };
}

export interface SearchResult {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  publishDate: string;
  source: string;
  url: string;
  pdfUrl?: string;
  citations?: number;
  venue?: string;
  keywords?: string[];
  doi?: string;
  snippet?: string;
}

export interface ArxivPaper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  published: string;
  updated: string;
  categories: string[];
  pdfUrl: string;
  entryId: string;
}

export interface SemanticScholarPaper {
  paperId: string;
  title: string;
  abstract?: string;
  authors: Array<{ authorId: string; name: string }>;
  year?: number;
  citationCount?: number;
  venue?: string;
  url: string;
  openAccessPdf?: { url: string };
}

export interface SearchResponse {
  query: string;
  totalResults: number;
  results: SearchResult[];
  sources: string[];
  timestamp: string;
}
