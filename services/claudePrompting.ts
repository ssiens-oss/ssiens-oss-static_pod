/**
 * Claude Prompting Service
 * Generates creative prompts for POD designs using Claude API
 */

interface ClaudeConfig {
  apiKey: string
  model?: string
}

interface PromptGenerationRequest {
  theme?: string
  style?: string
  niche?: string
  count?: number
  productType?: 'tshirt' | 'hoodie' | 'both'
}

interface GeneratedPrompt {
  prompt: string
  title: string
  tags: string[]
  description: string
}

export class ClaudePromptingService {
  private config: ClaudeConfig
  private baseUrl = 'https://api.anthropic.com/v1/messages'

  constructor(config: ClaudeConfig) {
    this.config = {
      model: 'claude-3-5-sonnet-20241022',
      ...config
    }
  }

  /**
   * Generate creative prompts for POD designs
   */
  async generatePrompts(request: PromptGenerationRequest): Promise<GeneratedPrompt[]> {
    const {
      theme = 'general',
      style = 'modern',
      niche = 'general audience',
      count = 1,
      productType = 'tshirt'
    } = request

    const systemPrompt = this.buildSystemPrompt(productType)
    const userPrompt = this.buildUserPrompt(theme, style, niche, count)

    try {
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': this.config.apiKey,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: this.config.model,
          max_tokens: 4000,
          temperature: 1.0,
          system: systemPrompt,
          messages: [
            {
              role: 'user',
              content: userPrompt
            }
          ]
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(`Claude API error: ${error.error?.message || response.statusText}`)
      }

      const data = await response.json()
      const content = data.content[0].text

      // Parse JSON response
      const prompts = this.parsePromptsFromResponse(content)

      return prompts
    } catch (error) {
      console.error('Error generating prompts:', error)
      throw error
    }
  }

  /**
   * Build system prompt for Claude
   */
  private buildSystemPrompt(productType: string): string {
    return `You are an expert POD (Print-on-Demand) designer and AI art prompt engineer. Your role is to create highly effective prompts for AI image generation that will be used on ${productType}s.

Key requirements for POD designs:
- Designs must be visually striking and stand out in online marketplaces
- Prompts should generate images suitable for apparel printing
- Focus on clean, bold graphics that work well on fabric
- Avoid overly complex details that don't translate well to print
- Consider popular trends in POD marketplaces (minimalism, vintage, abstract, typography, nature, etc.)

Your output should be in JSON format with the following structure:
{
  "prompts": [
    {
      "prompt": "Detailed AI art generation prompt",
      "title": "Product title for marketplace",
      "tags": ["tag1", "tag2", "tag3"],
      "description": "Product description for customers"
    }
  ]
}

Make prompts specific, creative, and optimized for commercial appeal.`
  }

  /**
   * Build user prompt
   */
  private buildUserPrompt(theme: string, style: string, niche: string, count: number): string {
    return `Generate ${count} creative and commercially viable POD design prompt${count > 1 ? 's' : ''} with the following criteria:

Theme: ${theme}
Style: ${style}
Target Niche: ${niche}

Each prompt should:
1. Be detailed enough for AI image generation (ComfyUI/Stable Diffusion)
2. Include artistic style, composition, colors, and mood
3. Be optimized for print-on-demand apparel
4. Have commercial appeal for the target niche
5. Include a catchy product title
6. Include relevant marketplace tags
7. Include a compelling product description

Return the prompts in JSON format as specified in the system prompt.`
  }

  /**
   * Parse prompts from Claude response
   */
  private parsePromptsFromResponse(content: string): GeneratedPrompt[] {
    try {
      // Extract JSON from markdown code blocks if present
      const jsonMatch = content.match(/```json\n([\s\S]*?)\n```/) || content.match(/```\n([\s\S]*?)\n```/)
      const jsonStr = jsonMatch ? jsonMatch[1] : content

      const parsed = JSON.parse(jsonStr)
      return parsed.prompts || []
    } catch (error) {
      console.error('Error parsing Claude response:', error)
      // Fallback: try to extract manually
      return this.fallbackParse(content)
    }
  }

  /**
   * Fallback parsing if JSON parsing fails
   */
  private fallbackParse(content: string): GeneratedPrompt[] {
    // Simple fallback: treat entire content as a single prompt
    return [{
      prompt: content,
      title: 'AI Generated Design',
      tags: ['ai art', 'unique', 'creative'],
      description: 'Unique AI-generated design for your wardrobe'
    }]
  }

  /**
   * Generate prompts for trending topics
   */
  async generateTrendingPrompts(trends: string[], count: number = 5): Promise<GeneratedPrompt[]> {
    const trendStr = trends.join(', ')

    return this.generatePrompts({
      theme: `trending topics: ${trendStr}`,
      style: 'modern and trending',
      niche: 'trend-conscious consumers',
      count
    })
  }

  /**
   * Refine an existing prompt
   */
  async refinePrompt(originalPrompt: string, improvements: string): Promise<GeneratedPrompt> {
    const userPrompt = `Refine this POD design prompt to ${improvements}:

Original prompt: ${originalPrompt}

Return a single improved prompt in the same JSON format as before.`

    const systemPrompt = this.buildSystemPrompt('tshirt')

    try {
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': this.config.apiKey,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: this.config.model,
          max_tokens: 2000,
          temperature: 0.8,
          system: systemPrompt,
          messages: [
            {
              role: 'user',
              content: userPrompt
            }
          ]
        })
      })

      const data = await response.json()
      const content = data.content[0].text
      const prompts = this.parsePromptsFromResponse(content)

      return prompts[0] || {
        prompt: originalPrompt,
        title: 'Refined Design',
        tags: ['refined', 'improved'],
        description: 'Refined AI-generated design'
      }
    } catch (error) {
      console.error('Error refining prompt:', error)
      throw error
    }
  }

  /**
   * Generate seasonal/themed collections
   */
  async generateCollection(collectionTheme: string, count: number = 10): Promise<GeneratedPrompt[]> {
    return this.generatePrompts({
      theme: collectionTheme,
      style: 'cohesive collection',
      niche: 'collection buyers',
      count
    })
  }
}
