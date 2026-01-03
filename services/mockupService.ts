/**
 * Mockup Generator Service
 * TypeScript wrapper for Python mockup generator
 */

import { exec } from 'child_process'
import { promisify } from 'util'
import * as path from 'path'
import * as fs from 'fs'

const execAsync = promisify(exec)

interface MockupConfig {
  templatesDir: string
  outputDir: string
}

interface MockupResult {
  tshirt?: string
  hoodie?: string
}

export class MockupService {
  private config: MockupConfig
  private scriptPath: string

  constructor(config: MockupConfig) {
    this.config = config
    this.scriptPath = path.join(__dirname, 'mockup.py')

    // Ensure output directory exists
    if (!fs.existsSync(config.outputDir)) {
      fs.mkdirSync(config.outputDir, { recursive: true })
    }
  }

  /**
   * Generate mockups for a design
   */
  async generateMockups(
    designPath: string,
    productTypes: ('tshirt' | 'hoodie')[],
    designId: string
  ): Promise<MockupResult> {
    const result: MockupResult = {}

    for (const productType of productTypes) {
      const templatePath = path.join(
        this.config.templatesDir,
        `${productType}_base.png`
      )

      // Skip if template doesn't exist
      if (!fs.existsSync(templatePath)) {
        console.warn(`Mockup template not found: ${templatePath}`)
        continue
      }

      const outputPath = path.join(
        this.config.outputDir,
        `${designId}_${productType}_mockup.png`
      )

      try {
        // Generate mockup using Python script
        const { stdout, stderr } = await execAsync(
          `python "${this.scriptPath}" "${templatePath}" "${designPath}" "${outputPath}" 0.7 0.45`
        )

        if (stderr) {
          console.warn(`Mockup stderr: ${stderr}`)
        }

        if (fs.existsSync(outputPath)) {
          result[productType] = outputPath
          console.log(`Generated ${productType} mockup: ${outputPath}`)
        }
      } catch (error) {
        console.error(`Failed to generate ${productType} mockup:`, error)
      }
    }

    return result
  }

  /**
   * Check if templates exist
   */
  hasTemplates(productTypes: ('tshirt' | 'hoodie')[]): boolean {
    return productTypes.every(type => {
      const templatePath = path.join(
        this.config.templatesDir,
        `${type}_base.png`
      )
      return fs.existsSync(templatePath)
    })
  }

  /**
   * Get available template types
   */
  getAvailableTemplates(): string[] {
    if (!fs.existsSync(this.config.templatesDir)) {
      return []
    }

    const files = fs.readdirSync(this.config.templatesDir)
    return files
      .filter(f => f.endsWith('_base.png'))
      .map(f => f.replace('_base.png', ''))
  }
}
