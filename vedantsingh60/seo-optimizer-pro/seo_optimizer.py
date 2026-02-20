#!/usr/bin/env python3
"""
SEO Optimizer Pro - AI-Powered SEO Content Optimization
Version: 1.0.6
Copyright © 2026 UnisAI. All Rights Reserved.

Multi-provider SEO analysis using Claude, GPT, Gemini, Llama, or Mistral.
Each provider requires its own API key. Only the provider you select needs
a key configured.

Features:
- Content optimization suggestions via your chosen AI model
- Technical SEO audit and recommendations
- Answer Engine Optimization (AEO) analysis
- Keyword clustering and topic mapping
- Meta tag generation
- Readability and structure analysis

PRIVACY NOTICE: This skill sends your content to third-party AI providers.
Review the provider's privacy policy before sending sensitive content.
"""

__version__ = "1.0.6"

import os
import json
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import re
from datetime import datetime


@dataclass
class SEOMetrics:
    """SEO analysis results"""
    content_length: int
    readability_score: float  # 0-100
    keyword_density: Dict[str, float]
    headings_structure: List[Tuple[str, int]]  # (heading, level)
    meta_tags_present: List[str]
    internal_links_count: int
    external_links_count: int
    word_count: int
    avg_paragraph_length: int
    flesch_kincaid_grade: float


@dataclass
class OptimizationSuggestion:
    """Optimization suggestion with priority"""
    category: str  # "content", "technical", "aeo", "keywords"
    priority: str  # "high", "medium", "low"
    suggestion: str
    current_value: Optional[str]
    recommended_value: Optional[str]
    impact: str  # estimated impact description


@dataclass
class SEOAnalysisResult:
    """Complete SEO analysis result"""
    test_id: str
    timestamp: str
    url: Optional[str]
    model_used: str
    provider: str
    metrics: SEOMetrics
    suggestions: List[OptimizationSuggestion]
    content_optimization: Dict
    aeo_recommendations: List[str]
    estimated_impact: str


class SEOOptimizer:
    """
    AI-powered SEO optimizer with real multi-provider support.

    Each provider uses its own SDK and API key:
    - Anthropic Claude: ANTHROPIC_API_KEY
    - OpenAI GPT: OPENAI_API_KEY
    - Google Gemini: GOOGLE_API_KEY
    - Mistral: MISTRAL_API_KEY
    - Meta Llama (via OpenRouter): OPENROUTER_API_KEY

    Only the API key for your chosen provider is required.
    """

    # IP Protection
    WATERMARK = "PROPRIETARY_SKILL_SEO_OPTIMIZER_2026"

    # Supported models and their providers (2026)
    SUPPORTED_MODELS = {
        # Anthropic Claude 4.5
        "claude-opus-4-5-20251101": {"provider": "anthropic", "env_key": "ANTHROPIC_API_KEY"},
        "claude-sonnet-4-5-20250929": {"provider": "anthropic", "env_key": "ANTHROPIC_API_KEY"},
        "claude-haiku-4-5-20251001": {"provider": "anthropic", "env_key": "ANTHROPIC_API_KEY"},

        # OpenAI GPT-5.2
        "gpt-5.2-pro": {"provider": "openai", "env_key": "OPENAI_API_KEY"},
        "gpt-5.2-thinking": {"provider": "openai", "env_key": "OPENAI_API_KEY"},
        "gpt-5.2-instant": {"provider": "openai", "env_key": "OPENAI_API_KEY"},

        # Google Gemini 2.5/3.0
        "gemini-3-pro": {"provider": "google", "env_key": "GOOGLE_API_KEY"},
        "gemini-2.5-pro": {"provider": "google", "env_key": "GOOGLE_API_KEY"},
        "gemini-2.5-flash": {"provider": "google", "env_key": "GOOGLE_API_KEY"},

        # Meta Llama (via OpenRouter)
        "llama-3.3-70b": {"provider": "openrouter", "env_key": "OPENROUTER_API_KEY"},
        "llama-3.2-90b": {"provider": "openrouter", "env_key": "OPENROUTER_API_KEY"},

        # Mistral
        "mistral-large-2501": {"provider": "mistral", "env_key": "MISTRAL_API_KEY"},
    }

    def __init__(self, model: str = None, api_key: str = None):
        """
        Initialize with model selection and optional API key override.

        Args:
            model: Model ID to use (defaults to claude-haiku-4-5-20251001)
            api_key: Override API key (otherwise reads from environment variable)
        """
        self.model = model or "claude-haiku-4-5-20251001"

        if self.model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Model '{self.model}' not supported.\n"
                f"Available models: {list(self.SUPPORTED_MODELS.keys())}"
            )

        self.model_config = self.SUPPORTED_MODELS[self.model]
        self.provider = self.model_config["provider"]
        self.env_key = self.model_config["env_key"]

        # Resolve API key
        self.api_key = api_key or os.getenv(self.env_key)
        if not self.api_key:
            raise ValueError(
                f"{self.env_key} not set. "
                f"Model '{self.model}' requires the {self.env_key} environment variable."
            )

        # Initialize the correct client for the provider
        self.client = self._init_client()

    def _init_client(self):
        """Initialize the correct SDK client based on provider."""
        if self.provider == "anthropic":
            from anthropic import Anthropic
            return Anthropic(api_key=self.api_key)

        elif self.provider == "openai":
            from openai import OpenAI
            return OpenAI(api_key=self.api_key)

        elif self.provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            return genai.GenerativeModel(self.model)

        elif self.provider == "mistral":
            from mistralai import Mistral
            return Mistral(api_key=self.api_key)

        elif self.provider == "openrouter":
            from openai import OpenAI
            return OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )

        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _call_ai(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Send a prompt to the selected AI model and return the response text.
        Routes to the correct API based on provider.
        """
        if self.provider == "anthropic":
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text

        elif self.provider in ("openai", "openrouter"):
            # OpenAI SDK (also used for OpenRouter/Llama)
            model_id = self.model
            if self.provider == "openrouter":
                # OpenRouter uses specific model paths
                model_map = {
                    "llama-3.3-70b": "meta-llama/llama-3.3-70b-instruct",
                    "llama-3.2-90b": "meta-llama/llama-3.2-90b-vision-instruct",
                }
                model_id = model_map.get(self.model, self.model)

            response = self.client.chat.completions.create(
                model=model_id,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        elif self.provider == "google":
            response = self.client.generate_content(
                prompt,
                generation_config={"max_output_tokens": max_tokens}
            )
            return response.text

        elif self.provider == "mistral":
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def analyze_content(self,
                       content: str,
                       url: Optional[str] = None,
                       target_keywords: Optional[List[str]] = None) -> SEOAnalysisResult:
        """
        Perform comprehensive SEO analysis on content.

        Args:
            content: HTML or plain text content to analyze
            url: Optional URL for reference
            target_keywords: Optional list of target keywords to focus on

        Returns:
            Complete SEO analysis with suggestions
        """
        test_id = self._generate_test_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Extract text from content
        text_content = self._extract_text(content)

        # Analyze technical metrics (no AI needed)
        metrics = self._calculate_metrics(text_content, target_keywords)

        # Generate rule-based suggestions (no AI needed)
        suggestions = self._generate_suggestions(text_content, metrics, target_keywords)

        # Get AI optimization suggestions
        content_optimization = self._get_ai_suggestions(text_content, target_keywords)

        # AEO-specific recommendations
        aeo_recommendations = self._get_aeo_recommendations(text_content, target_keywords)

        # Estimate impact
        estimated_impact = self._estimate_impact(metrics, len(suggestions))

        return SEOAnalysisResult(
            test_id=test_id,
            timestamp=timestamp,
            url=url,
            model_used=self.model,
            provider=self.provider,
            metrics=metrics,
            suggestions=suggestions,
            content_optimization=content_optimization,
            aeo_recommendations=aeo_recommendations,
            estimated_impact=estimated_impact
        )

    def _extract_text(self, content: str) -> str:
        """Extract text from HTML or plain text"""
        text = re.sub(r'<[^>]+>', '', content)
        text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _calculate_metrics(self, text: str, keywords: Optional[List[str]] = None) -> SEOMetrics:
        """Calculate SEO metrics (no AI call, pure computation)"""
        words = text.split()
        word_count = len(words)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        avg_para_length = word_count // len(paragraphs) if paragraphs else 0

        # Keyword density
        keyword_density = {}
        if keywords:
            text_lower = text.lower()
            for keyword in keywords:
                count = text_lower.count(keyword.lower())
                density = (count / word_count * 100) if word_count > 0 else 0
                if density > 0:
                    keyword_density[keyword] = round(density, 2)

        # Readability (Flesch-Kincaid)
        sentences = len(re.split(r'[.!?]+', text))
        syllables = self._count_syllables(text)
        if sentences > 0 and word_count > 0:
            fk_grade = 0.39 * (word_count / sentences) + 11.8 * (syllables / word_count) - 15.59
        else:
            fk_grade = 0
        readability_score = max(0, min(100, 100 - (fk_grade * 5)))

        # Heading structure
        headings = [(f"H{i}", text.count(f"<h{i}")) for i in range(1, 7)]
        headings = [(h, c) for h, c in headings if c > 0]

        return SEOMetrics(
            content_length=len(text),
            readability_score=readability_score,
            keyword_density=keyword_density,
            headings_structure=headings,
            meta_tags_present=["title", "description"],
            internal_links_count=text.count("<a href"),
            external_links_count=0,
            word_count=word_count,
            avg_paragraph_length=avg_para_length,
            flesch_kincaid_grade=fk_grade
        )

    def _count_syllables(self, text: str) -> int:
        """Estimate syllable count"""
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        for char in text.lower():
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        return max(1, syllable_count)

    def _generate_suggestions(self,
                            text: str,
                            metrics: SEOMetrics,
                            keywords: Optional[List[str]] = None) -> List[OptimizationSuggestion]:
        """Generate rule-based optimization suggestions (no AI call)"""
        suggestions = []

        if metrics.word_count < 300:
            suggestions.append(OptimizationSuggestion(
                category="content", priority="high",
                suggestion="Content is too short. Aim for at least 300 words for better indexing.",
                current_value=str(metrics.word_count), recommended_value="300+",
                impact="Better coverage of topic, improved ranking potential"
            ))
        elif metrics.word_count < 1000:
            suggestions.append(OptimizationSuggestion(
                category="content", priority="medium",
                suggestion="Consider expanding content to 1000+ words for comprehensive coverage.",
                current_value=str(metrics.word_count), recommended_value="1000+",
                impact="More thorough topic coverage, higher authority signals"
            ))

        if metrics.readability_score < 60:
            suggestions.append(OptimizationSuggestion(
                category="content", priority="high",
                suggestion="Content readability is low. Use shorter sentences and simpler words.",
                current_value=f"{metrics.readability_score:.1f}/100", recommended_value="60+",
                impact="Better user engagement, improved bounce rate"
            ))

        if keywords:
            for keyword, density in metrics.keyword_density.items():
                if density < 0.5:
                    suggestions.append(OptimizationSuggestion(
                        category="keywords", priority="medium",
                        suggestion=f"Target keyword '{keyword}' appears {density}% of the time. Increase naturally to 1-2%.",
                        current_value=f"{density:.2f}%", recommended_value="1-2%",
                        impact="Better keyword relevance signal"
                    ))
                elif density > 3:
                    suggestions.append(OptimizationSuggestion(
                        category="keywords", priority="high",
                        suggestion=f"Keyword '{keyword}' density is {density}% - this may be keyword stuffing.",
                        current_value=f"{density:.2f}%", recommended_value="1-2%",
                        impact="Avoid Google penalties, maintain natural flow"
                    ))

        if not metrics.headings_structure:
            suggestions.append(OptimizationSuggestion(
                category="technical", priority="high",
                suggestion="No heading tags found. Add H1, H2, H3 tags to structure content.",
                current_value="None", recommended_value="H1 (1), H2 (3-5), H3 (optional)",
                impact="Better content structure, improved accessibility"
            ))

        return suggestions[:10]

    def _get_ai_suggestions(self, text: str, keywords: Optional[List[str]] = None) -> Dict:
        """Get AI-powered optimization suggestions from the selected model."""
        keyword_context = ""
        if keywords:
            keyword_context = f"\n\nTarget keywords to naturally incorporate: {', '.join(keywords)}"

        prompt = f"""You are an expert SEO content strategist. Analyze this content and provide specific, actionable optimization suggestions.

Content:
{text[:2000]}

{keyword_context}

Please provide:
1. Title optimization (40-60 chars with target keyword)
2. Meta description (150-160 chars)
3. H1 tag suggestion
4. 3-5 key points to expand
5. Natural keyword integration suggestions
6. Internal linking opportunities

Format as JSON with keys: title, meta_description, h1, key_points, keyword_integration, internal_links"""

        response_text = self._call_ai(prompt, max_tokens=1000)

        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError, IndexError):
            pass

        return {
            "title": "See analysis in full results",
            "meta_description": "See analysis in full results",
            "suggestions": response_text
        }

    def _get_aeo_recommendations(self, text: str, keywords: Optional[List[str]] = None) -> List[str]:
        """Get Answer Engine Optimization (AEO) recommendations."""
        keyword_context = ""
        if keywords:
            keyword_context = f"Focus on these keywords: {', '.join(keywords[:3])}"

        prompt = f"""As an Answer Engine Optimization (AEO) expert, analyze this content for optimization in AI search results (ChatGPT citations, Google AI Overviews, Claude, etc).

Content excerpt:
{text[:1500]}

{keyword_context}

Provide 5 specific AEO recommendations to:
1. Get featured in AI search results
2. Appear as a cited source in AI-generated responses
3. Improve visibility in ChatGPT, Google AI Overviews, and similar platforms

Format as a simple numbered list."""

        response_text = self._call_ai(prompt, max_tokens=500)
        items = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|\Z)', response_text, re.DOTALL)
        return [item.strip() for item in items][:5]

    def _estimate_impact(self, metrics: SEOMetrics, suggestion_count: int) -> str:
        """Estimate potential impact of optimizations (no AI call)"""
        impact_score = 0
        factors = []

        if metrics.word_count < 500:
            impact_score += 3
            factors.append("Expanding content length")
        if metrics.readability_score < 70:
            impact_score += 2
            factors.append("Improving readability")
        if metrics.keyword_density:
            impact_score += 2
            factors.append("Optimizing keyword presence")
        if not metrics.headings_structure:
            impact_score += 1
            factors.append("Adding heading structure")

        if impact_score >= 6:
            return f"High Impact - Implementing all suggestions could improve ranking potential by 25-40%. Key factors: {', '.join(factors)}"
        elif impact_score >= 3:
            return f"Medium Impact - Implementing suggestions could improve ranking by 10-20%. Key factors: {', '.join(factors)}"
        else:
            return f"Optimization potential - Content is well-optimized. Focus on: {', '.join(factors[:2])}"

    def format_results(self, result: SEOAnalysisResult) -> str:
        """Format analysis results for display"""
        output = f"""
╔══════════════════════════════════════════════════════════════════╗
║              SEO ANALYSIS RESULTS - {result.test_id}              ║
╚══════════════════════════════════════════════════════════════════╝

🤖 Model: {result.model_used} ({result.provider})

📊 METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Word Count: {result.metrics.word_count}
• Content Length: {result.metrics.content_length} characters
• Readability Score: {result.metrics.readability_score:.1f}/100
• Flesch-Kincaid Grade: {result.metrics.flesch_kincaid_grade:.1f}
• Avg Paragraph Length: {result.metrics.avg_paragraph_length} words

🔑 KEYWORD DENSITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        if result.metrics.keyword_density:
            for keyword, density in result.metrics.keyword_density.items():
                output += f"• {keyword}: {density:.2f}%\n"
        else:
            output += "• No keywords analyzed\n"

        output += f"""
💡 TOP SUGGESTIONS ({len(result.suggestions)} found)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for i, sugg in enumerate(result.suggestions[:5], 1):
            priority_emoji = "🔴" if sugg.priority == "high" else "🟡" if sugg.priority == "medium" else "🟢"
            output += f"\n{priority_emoji} [{sugg.category.upper()}] {sugg.suggestion}\n"
            if sugg.current_value:
                output += f"   Current: {sugg.current_value} → Recommended: {sugg.recommended_value}\n"
            output += f"   Impact: {sugg.impact}\n"

        output += f"""
🎯 ESTIMATED IMPACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{result.estimated_impact}

🤖 AI SEARCH OPTIMIZATION (AEO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for i, rec in enumerate(result.aeo_recommendations, 1):
            output += f"{i}. {rec}\n"

        output += f"\n⏱️  Analysis ID: {result.test_id}\n"
        output += f"🕐 Timestamp: {result.timestamp}\n"

        return output

    @staticmethod
    def _generate_test_id() -> str:
        """Generate unique test ID"""
        import uuid
        return str(uuid.uuid4())[:8].upper()
