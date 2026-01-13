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
    // Nature & Organic
    'nature', 'floral', 'botanical', 'ocean', 'forest', 'mountain', 'desert', 'tropical',
    'wildlife', 'marine life', 'birds', 'butterflies', 'celestial', 'cosmic', 'galaxy',

    // Art Movements & Styles
    'abstract', 'geometric', 'minimalist', 'vintage', 'retro', 'art deco', 'art nouveau',
    'bauhaus', 'pop art', 'grunge', 'punk', 'gothic', 'baroque', 'renaissance',

    // Modern & Contemporary
    'modern', 'contemporary', 'futuristic', 'cyberpunk', 'steampunk', 'vaporwave',
    'synthwave', 'y2k', 'streetwear', 'urban', 'industrial', 'brutalist',

    // Fantasy & Sci-Fi
    'fantasy', 'sci-fi', 'mystical', 'magical', 'mythological', 'anime', 'manga',
    'comic book', 'superhero', 'dystopian', 'post-apocalyptic', 'alien',

    // Cultural & Regional
    'japanese', 'chinese', 'aztec', 'egyptian', 'greek', 'norse', 'celtic',
    'tribal', 'ethnic', 'oriental', 'western', 'african', 'native american',

    // Themes & Concepts
    'horror', 'dark', 'light', 'zen', 'spiritual', 'religious', 'philosophical',
    'music', 'sports', 'gaming', 'tech', 'science', 'space', 'time',
    'typography', 'calligraphy', 'graffiti', 'street art'
  ];

  private styles = [
    // Traditional Art
    'watercolor', 'oil painting', 'acrylic painting', 'pastel', 'charcoal', 'ink drawing',
    'pencil sketch', 'gouache', 'tempera', 'fresco',

    // Digital Art
    'vector art', 'digital painting', 'pixel art', '3D render', 'photorealistic',
    'cel shading', 'flat design', 'gradient art', 'glitch art', 'generative art',

    // Illustration Styles
    'line art', 'cartoon', 'comic book', 'manga style', 'anime style', 'chibi',
    'caricature', 'editorial illustration', 'children\'s book style', 'concept art',

    // Print & Design
    'screen print', 'linocut', 'woodblock print', 'etching', 'lithograph',
    'risograph', 'letterpress', 'stencil art', 'collage', 'mixed media',

    // Modern & Experimental
    'abstract expressionism', 'geometric abstraction', 'minimalism', 'maximalism',
    'surrealism', 'impressionism', 'pointillism', 'cubism', 'futurism',

    // Pop Culture
    'pop art', 'psychedelic', 'vaporwave', 'synthwave', 'retro wave', 'outrun',
    'cyberpunk', 'steampunk', 'dieselpunk', 'solarpunk',

    // Special Techniques
    'grunge', 'distressed', 'vintage halftone', 'dot matrix', 'ascii art',
    'glowing neon', 'stained glass', 'mosaic', 'mandala', 'zentangle',
    'double exposure', 'silhouette', 'negative space', 'optical illusion'
  ];

  private subjects = [
    // Landscapes & Nature
    'mountain landscape', 'ocean waves', 'forest scene', 'sunset', 'sunrise', 'desert dunes',
    'tropical beach', 'waterfall', 'canyon', 'volcano', 'northern lights', 'rainbow',
    'storm clouds', 'lightning', 'fog', 'mist', 'snow', 'rain', 'wind',

    // Flora & Fauna
    'flowers', 'roses', 'lotus', 'cherry blossoms', 'sunflowers', 'tropical plants',
    'trees', 'leaves', 'vines', 'mushrooms', 'crystals', 'minerals',
    'animals', 'birds', 'butterflies', 'dragonflies', 'fish', 'dolphins', 'whales',
    'lions', 'tigers', 'wolves', 'bears', 'eagles', 'owls', 'hummingbirds',
    'cats', 'dogs', 'horses', 'deer', 'foxes', 'rabbits',

    // Celestial & Space
    'galaxy', 'nebula', 'stars', 'constellations', 'planets', 'moon', 'sun',
    'meteor shower', 'black hole', 'cosmic clouds', 'space station', 'astronaut',

    // Abstract & Geometric
    'geometric shapes', 'sacred geometry', 'mandala', 'fractals', 'tessellation',
    'abstract patterns', 'swirls', 'spirals', 'circles', 'triangles', 'hexagons',
    'polygons', 'lines', 'dots', 'grids', 'waves', 'ripples',

    // Urban & Architecture
    'city skyline', 'skyscrapers', 'streets', 'bridges', 'tunnels', 'buildings',
    'architecture', 'monuments', 'towers', 'castles', 'temples', 'ruins',

    // Fantasy & Mythology
    'dragons', 'phoenixes', 'unicorns', 'mermaids', 'fairies', 'angels', 'demons',
    'mythical creatures', 'gods', 'goddesses', 'warriors', 'wizards', 'sorcerers',
    'knights', 'samurai', 'ninjas', 'pirates', 'vikings',

    // Modern & Pop Culture
    'skulls', 'robots', 'cyborgs', 'aliens', 'spaceships', 'cars', 'motorcycles',
    'guitars', 'music notes', 'headphones', 'cameras', 'books', 'coffee',
    'skateboards', 'surfboards', 'gaming', 'technology', 'circuits',

    // Symbols & Icons
    'yin yang', 'infinity symbol', 'hearts', 'stars', 'crowns', 'anchors',
    'arrows', 'feathers', 'keys', 'locks', 'clocks', 'compass', 'maps',
    'eyes', 'hands', 'wings', 'flames', 'water drops', 'lightning bolts'
  ];

  private colors = [
    // Basic Palettes
    'vibrant colors', 'pastel tones', 'muted colors', 'bold colors', 'soft colors',
    'monochrome', 'black and white', 'grayscale', 'sepia tones',

    // Specific Hues
    'neon colors', 'neon pink and blue', 'neon green', 'electric blue',
    'warm colors', 'cool colors', 'earth tones', 'jewel tones', 'metallic colors',
    'gold and black', 'silver and blue', 'rose gold', 'copper tones',

    // Color Combinations
    'blue and purple', 'pink and orange', 'teal and coral', 'mint and peach',
    'red and black', 'blue and gold', 'purple and gold', 'green and gold',
    'rainbow colors', 'sunset colors', 'ocean colors', 'forest colors',
    'autumn colors', 'spring colors', 'summer colors', 'winter colors',

    // Special Effects
    'gradient', 'ombre', 'iridescent', 'holographic', 'chromatic',
    'complementary colors', 'analogous colors', 'triadic colors',
    'duotone', 'tritone', 'high contrast', 'low contrast',

    // Advanced Palettes
    'cyberpunk neon', 'vaporwave aesthetic', 'synthwave sunset', 'retrowave colors',
    'dark academia', 'light academia', 'cottagecore pastels', 'gothic dark tones',
    'kawaii colors', 'y2k bright colors', 'grunge muted tones'
  ];

  private moods = [
    // Positive & Uplifting
    'peaceful', 'serene', 'tranquil', 'calm', 'relaxing', 'soothing',
    'joyful', 'happy', 'cheerful', 'optimistic', 'uplifting', 'inspiring',
    'playful', 'whimsical', 'fun', 'lighthearted', 'carefree',

    // Energetic & Dynamic
    'energetic', 'dynamic', 'vibrant', 'lively', 'exciting', 'intense',
    'powerful', 'strong', 'bold', 'confident', 'fierce', 'aggressive',

    // Elegant & Sophisticated
    'elegant', 'sophisticated', 'refined', 'luxurious', 'classy', 'stylish',
    'graceful', 'delicate', 'subtle', 'minimalistic', 'clean', 'modern',

    // Dark & Mysterious
    'mysterious', 'enigmatic', 'mystical', 'magical', 'ethereal', 'otherworldly',
    'dark', 'moody', 'brooding', 'ominous', 'eerie', 'haunting',
    'gothic', 'dramatic', 'intense', 'melancholic', 'nostalgic',

    // Creative & Artistic
    'artistic', 'creative', 'imaginative', 'expressive', 'innovative',
    'abstract', 'surreal', 'dreamlike', 'fantastical', 'visionary',
    'edgy', 'rebellious', 'unconventional', 'avant-garde', 'experimental',

    // Nature & Organic
    'natural', 'organic', 'earthy', 'rustic', 'wild', 'raw',
    'fresh', 'crisp', 'breezy', 'flowing', 'fluid', 'dynamic',

    // Retro & Vintage
    'retro', 'vintage', 'nostalgic', 'classic', 'timeless', 'traditional',
    'antique', 'weathered', 'aged', 'distressed'
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

  private qualityEnhancers = [
    'high quality', 'detailed', 'intricate details', 'ultra detailed', '8k resolution',
    '4k quality', 'sharp focus', 'crisp', 'professional', 'masterpiece',
    'award winning', 'trending on artstation', 'featured on behance',
    'highly detailed', 'perfect composition', 'stunning', 'breathtaking',
    'photorealistic', 'hyperrealistic', 'cinematic', 'dramatic lighting',
    'perfect for print', 'commercial quality', 'premium quality', 'HD'
  ];

  private techniques = [
    'symmetrical', 'asymmetrical', 'centered composition', 'rule of thirds',
    'golden ratio', 'dynamic composition', 'balanced', 'layered',
    'textured', 'smooth gradients', 'bold outlines', 'soft edges',
    'high contrast', 'low contrast', 'atmospheric perspective', 'depth of field',
    'bokeh effect', 'lens flare', 'rim lighting', 'ambient occlusion'
  ];

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
    const quality = this.randomElement(this.qualityEnhancers);
    const quality2 = this.randomElement(this.qualityEnhancers);
    const technique = this.randomElement(this.techniques);

    const templates = [
      `${style} of ${subject}, ${color}, ${mood} atmosphere, ${technique}, ${quality}, ${quality2}`,
      `${theme} inspired ${subject} in ${style}, ${color}, ${mood} mood, ${technique}, ${quality}, perfect for t-shirt design`,
      `beautiful ${subject}, ${style}, ${color} palette, ${mood} vibes, ${quality}, ${technique}, ideal for apparel`,
      `${mood} ${subject} design, ${style}, ${color}, ${theme} aesthetic, ${quality}, ${technique}`,
      `professional ${style} depicting ${subject}, ${color}, ${mood} feeling, ${quality}, ${technique}, print ready`,
      `stunning ${subject} artwork, ${style}, ${theme} theme, ${color}, ${mood} energy, ${quality}, ${technique}`,
      `${subject} illustration, ${style}, ${color} scheme, ${mood} vibe, ${theme} inspiration, ${quality}, clean vector style`,
      `${theme} ${subject}, rendered in ${style}, ${color}, ${mood} atmosphere, ${technique}, ${quality}, scalable design`,
      `artistic ${subject}, ${style} technique, ${color}, ${mood} mood, ${theme} elements, ${quality}, ${technique}`,
      `${subject} composition, ${style}, ${color} tones, ${mood} aesthetic, ${theme} inspired, ${technique}, ${quality}`
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

  /**
   * Get all available themes
   */
  getAvailableThemes(): string[] {
    return [...this.themes];
  }

  /**
   * Get all available styles
   */
  getAvailableStyles(): string[] {
    return [...this.styles];
  }

  /**
   * Get all available subjects
   */
  getAvailableSubjects(): string[] {
    return [...this.subjects];
  }

  /**
   * Get themes by category
   */
  getThemesByCategory(): { [key: string]: string[] } {
    return {
      'Nature & Organic': this.themes.slice(0, 15),
      'Art Movements': this.themes.slice(15, 29),
      'Modern & Contemporary': this.themes.slice(29, 41),
      'Fantasy & Sci-Fi': this.themes.slice(41, 53),
      'Cultural & Regional': this.themes.slice(53, 66),
      'Themes & Concepts': this.themes.slice(66)
    };
  }

  /**
   * Get styles by category
   */
  getStylesByCategory(): { [key: string]: string[] } {
    return {
      'Traditional Art': ['watercolor', 'oil painting', 'acrylic painting', 'pastel', 'charcoal', 'ink drawing', 'pencil sketch', 'gouache', 'tempera', 'fresco'],
      'Digital Art': ['vector art', 'digital painting', 'pixel art', '3D render', 'photorealistic', 'cel shading', 'flat design', 'gradient art', 'glitch art', 'generative art'],
      'Illustration': ['line art', 'cartoon', 'comic book', 'manga style', 'anime style', 'chibi', 'caricature', 'editorial illustration', 'children\'s book style', 'concept art'],
      'Print & Design': ['screen print', 'linocut', 'woodblock print', 'etching', 'lithograph', 'risograph', 'letterpress', 'stencil art', 'collage', 'mixed media'],
      'Modern & Experimental': ['abstract expressionism', 'geometric abstraction', 'minimalism', 'maximalism', 'surrealism', 'impressionism', 'pointillism', 'cubism', 'futurism'],
      'Pop Culture': ['pop art', 'psychedelic', 'vaporwave', 'synthwave', 'retro wave', 'outrun', 'cyberpunk', 'steampunk', 'dieselpunk', 'solarpunk'],
      'Special Techniques': ['grunge', 'distressed', 'vintage halftone', 'dot matrix', 'ascii art', 'glowing neon', 'stained glass', 'mosaic', 'mandala', 'zentangle']
    };
  }

  /**
   * Generate random prompts from a specific category
   */
  async generateByCategory(
    category: 'nature' | 'fantasy' | 'abstract' | 'modern' | 'vintage' | 'anime',
    count: number
  ): Promise<PromptResult[]> {
    const categoryThemes: { [key: string]: string[] } = {
      nature: ['nature', 'floral', 'botanical', 'ocean', 'forest', 'mountain', 'wildlife'],
      fantasy: ['fantasy', 'mystical', 'magical', 'mythological', 'dragons', 'unicorns'],
      abstract: ['abstract', 'geometric', 'minimalist', 'psychedelic', 'surreal'],
      modern: ['modern', 'contemporary', 'urban', 'streetwear', 'tech', 'futuristic'],
      vintage: ['vintage', 'retro', 'art deco', 'art nouveau', 'classic', 'antique'],
      anime: ['anime', 'manga', 'kawaii', 'chibi', 'japanese', 'oriental']
    };

    const themes = categoryThemes[category] || this.themes;
    const prompts: PromptResult[] = [];

    for (let i = 0; i < count; i++) {
      const theme = this.randomElement(themes);
      const prompt = this.generateSinglePrompt({ theme });
      prompts.push(prompt);
    }

    return prompts;
  }

  /**
   * Generate a prompt with specific parameters
   */
  async generateCustomPrompt(params: {
    theme?: string;
    style?: string;
    subject?: string;
    color?: string;
    mood?: string;
  }): Promise<PromptResult> {
    const theme = params.theme || this.randomElement(this.themes);
    const style = params.style || this.randomElement(this.styles);
    const subject = params.subject || this.randomElement(this.subjects);
    const color = params.color || this.randomElement(this.colors);
    const mood = params.mood || this.randomElement(this.moods);

    const prompt = this.buildPrompt(theme, style, subject, color, mood);
    const title = this.generateTitle(theme, subject);
    const tags = this.generateTags(theme, style, subject);
    const description = this.generateDescription(theme, style, subject, mood);

    return { prompt, title, tags, description };
  }
}

/**
 * Factory function to create the service
 */
export function createLocalPromptingService(): LocalPromptingService {
  return new LocalPromptingService();
}
