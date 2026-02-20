/**
 * Literature Skills - Configuration
 * 文献检索总结工具配置系统
 */

export interface LiteratureSkillConfig {
  // 用户配置
  user: {
    name?: string;
    interests: string[];
    level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
    primaryLanguage: 'zh-CN' | 'en-US';
  };

  // 检索配置
  search: {
    defaultSources: ('arxiv' | 'semantic_scholar' | 'web')[];
    maxResults: number;
    sortBy: 'relevance' | 'date' | 'citations';
    cacheResults: boolean;
    cacheDuration: number; // 毫秒
  };

  // 学习配置
  learning: {
    depth: 'quick' | 'standard' | 'deep';
    includePapers: boolean;
    includeCode: boolean;
    focusAreas: string[];
  };

  // 追踪配置
  tracking: {
    enabled: boolean;
    frequency: 'daily' | 'weekly' | 'monthly';
    keywords: string[];
    authors: string[];
    conferences: string[];
  };

  // 输出配置
  output: {
    format: 'json' | 'markdown' | 'html';
    savePath: string;
    generateReports: boolean;
    reportFrequency: 'daily' | 'weekly' | 'monthly';
  };
}

export const defaultConfig: LiteratureSkillConfig = {
  user: {
    interests: [],
    level: 'intermediate',
    primaryLanguage: 'zh-CN'
  },

  search: {
    defaultSources: ['arxiv', 'semantic_scholar', 'web'],
    maxResults: 20,
    sortBy: 'relevance',
    cacheResults: true,
    cacheDuration: 3600000 // 1小时
  },

  learning: {
    depth: 'standard',
    includePapers: true,
    includeCode: false,
    focusAreas: []
  },

  tracking: {
    enabled: true,
    frequency: 'weekly',
    keywords: [],
    authors: [],
    conferences: []
  },

  output: {
    format: 'markdown',
    savePath: './output',
    generateReports: true,
    reportFrequency: 'weekly'
  }
};

/**
 * 配置管理器
 */
export class ConfigManager {
  private config: LiteratureSkillConfig;
  private configPath: string;

  constructor(configPath: string = './literature-config.json') {
    this.configPath = configPath;
    this.config = { ...defaultConfig };
  }

  /**
   * 加载配置
   */
  load(): LiteratureSkillConfig {
    try {
      const fs = require('fs');
      if (fs.existsSync(this.configPath)) {
        const loaded = JSON.parse(fs.readFileSync(this.configPath, 'utf-8'));
        this.config = { ...defaultConfig, ...loaded };
      }
    } catch (error) {
      console.warn('Failed to load config, using defaults:', error);
    }
    return this.config;
  }

  /**
   * 保存配置
   */
  save(): void {
    try {
      const fs = require('fs');
      fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 2));
    } catch (error) {
      console.error('Failed to save config:', error);
    }
  }

  /**
   * 更新配置
   */
  update(partial: Partial<LiteratureSkillConfig>): void {
    this.config = {
      ...this.config,
      ...partial,
      user: { ...this.config.user, ...partial.user },
      search: { ...this.config.search, ...partial.search },
      learning: { ...this.config.learning, ...partial.learning },
      tracking: { ...this.config.tracking, ...partial.tracking },
      output: { ...this.config.output, ...partial.output }
    };
    this.save();
  }

  /**
   * 获取当前配置
   */
  get(): LiteratureSkillConfig {
    return this.config;
  }

  /**
   * 重置为默认配置
   */
  reset(): void {
    this.config = { ...defaultConfig };
    this.save();
  }
}

// CLI 支持
if (import.meta.main) {
  const args = process.argv.slice(2);
  const command = args[0];

  const manager = new ConfigManager();

  switch (command) {
    case 'init':
      manager.save();
      console.log('Configuration initialized at ./literature-config.json');
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
          console.log(`Set ${key} = ${value}`);
        } catch {
          manager.update({ [key]: value });
          console.log(`Set ${key} = "${value}"`);
        }
      }
      break;

    case 'reset':
      manager.reset();
      console.log('Configuration reset to defaults');
      break;

    default:
      console.log(`
Usage:
  config.ts init              - Initialize configuration file
  config.ts show              - Show current configuration
  config.ts set <key> <value> - Set configuration value
  config.ts reset             - Reset to defaults
`);
  }
}
