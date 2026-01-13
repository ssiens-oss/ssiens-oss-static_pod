/**
 * Local Prompt Generation Service
 * Free alternative to Claude API - generates prompts locally
 * No API costs - 100% free!
 */

interface LocalPromptConfig {
  theme?: string;
  style?: string;
  niche?: string;
  count?: number;
  productType?: 'tshirt' | 'hoodie';
}

interface PromptResult {
  prompt: string;
  title: string;
  tags: string[];
  description: string;
}

/**
 * Local Prompt Generator - No API Required
 * Uses template-based generation with randomization
 */
export class LocalPromptingService {
  private themes = [
    'nature', 'abstract', 'geometric', 'minimalist', 'vintage',
    'modern', 'retro', 'artistic', 'sci-fi', 'fantasy',
    'urban', 'cosmic', 'floral', 'animal', 'typography'
  ];

  private styles = [
    'vector art', 'watercolor', 'line art', 'grunge',
    'psychedelic', 'pop art', 'art deco', 'cartoon',
    'illustration', 'sketch', 'digital painting', 'pixel art'
  ];

  private subjects = [
    'mountain landscape', 'ocean waves', 'forest scene', 'sunset',
    'geometric shapes', 'mandala', 'abstract patterns', 'galaxy',
    'city skyline', 'animals', 'flowers', 'trees',
    'clouds', 'stars', 'moon', 'crystals', 'fractals'
  ];

  private colors = [
    'vibrant colors', 'pastel tones', 'monochrome', 'neon',
    'earth tones', 'blue and purple', 'warm colors', 'cool colors',
    'black and white', 'gradient', 'complementary colors'
  ];

  private moods = [
    'peaceful', 'energetic', 'mysterious', 'playful',
    'serene', 'dramatic', 'whimsical', 'bold',
    'elegant', 'edgy', 'dreamy', 'powerful'
  ];

  /**
   * Generate prompts locally without API calls
   */
  async generatePrompts(config: LocalPromptConfig): Promise<PromptResult[]> {
    const count = config.count || 1;
    const prompts: PromptResult[] = [];

    for (let i = 0; i < count; i++) {
      const prompt = this.generateSinglePrompt(config);
      prompts.push(prompt);
    }

    return prompts;
  }

  /**
   * Generate a single prompt with random elements
   */
  private generateSinglePrompt(config: LocalPromptConfig): PromptResult {
    // Use provided config or pick random elements
    const theme = config.theme || this.randomElement(this.themes);
    const style = config.style || this.randomElement(this.styles);
    const subject = this.randomElement(this.subjects);
    const color = this.randomElement(this.colors);
    const mood = this.randomElement(this.moods);

    // Build the prompt
    const prompt = this.buildPrompt(theme, style, subject, color, mood);

    // Generate title
    const title = this.generateTitle(theme, subject);

    // Generate tags
    const tags = this.generateTags(theme, style, subject, config.niche);

    // Generate description
    const description = this.generateDescription(theme, style, subject, mood);

    return {
      prompt,
      title,
      tags,
      description
    };
  }

  /**
   * Build the actual image generation prompt
   */
  private buildPrompt(
    theme: string,
    style: string,
    subject: string,
    color: string,
    mood: string
  ): string {
    const templates = [
      `${style} of ${subject}, ${color}, ${mood} atmosphere, high quality, detailed, professional design`,
      `${theme} inspired ${subject} in ${style}, ${color}, ${mood} mood, trending design, 4k quality`,
      `beautiful ${subject}, ${style}, ${color} palette, ${mood} vibes, perfect for print, high resolution`,
      `${mood} ${subject} design, ${style}, ${color}, ${theme} aesthetic, commercial quality`,
      `professional ${style} depicting ${subject}, ${color}, ${mood} feeling, suitable for ${theme} products`
    ];

    return this.randomElement(templates);
  }

  /**
   * Generate a catchy title
   */
  private generateTitle(theme: string, subject: string): string {
    const adjectives = [
      'Stunning', 'Beautiful', 'Magnificent', 'Elegant', 'Bold',
      'Vibrant', 'Serene', 'Mystical', 'Dynamic', 'Classic',
      'Modern', 'Artistic', 'Creative', 'Unique', 'Premium'
    ];

    const titleFormats = [
      `${this.randomElement(adjectives)} ${this.capitalize(subject)}`,
      `${this.capitalize(theme)} ${this.capitalize(subject)}`,
      `The ${this.randomElement(adjectives)} ${this.capitalize(subject.split(' ')[0])}`,
      `${this.capitalize(subject)} ${this.capitalize(theme)}`,
    ];

    return this.randomElement(titleFormats);
  }

  /**
   * Generate relevant tags
   */
  private generateTags(
    theme: string,
    style: string,
    subject: string,
    niche?: string
  ): string[] {
    const tags = [
      theme,
      style.replace(' ', '-'),
      subject.split(' ')[0],
      'ai-art',
      'print-design',
      'graphic-tee',
      'unique-design'
    ];

    if (niche) {
      tags.push(niche);
    }

    // Add some random popular tags
    const popularTags = [
      'trending', 'cool-design', 'artistic', 'modern',
      'minimalist', 'vintage', 'aesthetic', 'creative'
    ];

    tags.push(this.randomElement(popularTags));
    tags.push(this.randomElement(popularTags));

    return [...new Set(tags)]; // Remove duplicates
  }

  /**
   * Generate product description
   */
  private generateDescription(
    theme: string,
    style: string,
    subject: string,
    mood: string
  ): string {
    const templates = [
      `This ${mood} ${theme} design features a ${subject} in beautiful ${style}. Perfect for those who appreciate unique artistic expressions.`,
      `Express your style with this ${mood} ${subject} design. Created with ${style} techniques, this ${theme}-inspired piece is both eye-catching and meaningful.`,
      `A ${mood} take on ${subject}, rendered in stunning ${style}. This ${theme} design adds personality and flair to any wardrobe.`,
      `Discover this ${theme}-inspired ${subject} design, crafted with ${style} artistry. The ${mood} aesthetic makes it a standout piece.`,
      `Unique ${style} artwork featuring ${subject}. This ${mood} ${theme} design is perfect for making a statement.`
    ];

    return this.randomElement(templates);
  }

  /**
   * Get a random element from an array
   */
  private randomElement<T>(array: T[]): T {
    return array[Math.floor(Math.random() * array.length)];
  }

  /**
   * Capitalize first letter
   */
  private capitalize(text: string): string {
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  /**
   * Generate a batch of themed prompts
   */
  async generateThemedBatch(
    theme: string,
    count: number,
    niche?: string
  ): Promise<PromptResult[]> {
    return this.generatePrompts({ theme, count, niche });
  }

  /**
   * Generate prompts for a specific style
   */
  async generateStyleBatch(
    style: string,
    count: number
  ): Promise<PromptResult[]> {
    return this.generatePrompts({ style, count });
  }
}

/**
 * Factory function to create the service
 */
export function createLocalPromptingService(): LocalPromptingService {
  return new LocalPromptingService();
}
