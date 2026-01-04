#!/usr/bin/env node
/**
 * Push Printify Products Script
 * Reads images from /home/static/ComfyUI/output/images/failed and creates T-shirt and Hoodie products in Printify
 */

import { readdir, readFile } from 'fs/promises'
import { join, basename, extname } from 'path'
import { PrintifyService } from '../services/printify.ts'
import dotenv from 'dotenv'

// Load environment variables
dotenv.config()

interface ProcessedImage {
  filename: string
  path: string
  base64: string
}

interface ProductResult {
  filename: string
  tshirt?: {
    id: string
    title: string
    url: string
  }
  hoodie?: {
    id: string
    title: string
    url: string
  }
  error?: string
}

class PrintifyPusher {
  private printify: PrintifyService
  private imageDir: string
  private results: ProductResult[] = []

  constructor() {
    const apiKey = process.env.PRINTIFY_API_KEY
    const shopId = process.env.PRINTIFY_SHOP_ID

    if (!apiKey || !shopId) {
      throw new Error('Missing PRINTIFY_API_KEY or PRINTIFY_SHOP_ID in .env file')
    }

    this.printify = new PrintifyService({ apiKey, shopId })
    this.imageDir = process.env.COMFYUI_FAILED_DIR || '/home/static/ComfyUI/output/images/failed'
  }

  /**
   * Get all image files from the directory
   */
  async getImageFiles(): Promise<string[]> {
    try {
      const files = await readdir(this.imageDir)
      const imageExtensions = ['.png', '.jpg', '.jpeg', '.webp', '.gif']

      return files.filter(file => {
        const ext = extname(file).toLowerCase()
        return imageExtensions.includes(ext)
      })
    } catch (error) {
      console.error(`Error reading directory ${this.imageDir}:`, error)
      return []
    }
  }

  /**
   * Read and convert image to base64
   */
  async processImage(filename: string): Promise<ProcessedImage | null> {
    try {
      const filePath = join(this.imageDir, filename)
      const imageBuffer = await readFile(filePath)
      const base64 = imageBuffer.toString('base64')
      const ext = extname(filename).toLowerCase().replace('.', '')

      // Create data URL
      const mimeType = ext === 'jpg' ? 'jpeg' : ext
      const dataUrl = `data:image/${mimeType};base64,${base64}`

      return {
        filename,
        path: filePath,
        base64: dataUrl
      }
    } catch (error) {
      console.error(`Error processing image ${filename}:`, error)
      return null
    }
  }

  /**
   * Generate product title from filename
   */
  generateTitle(filename: string): string {
    const nameWithoutExt = basename(filename, extname(filename))

    // Convert filename to title case
    // Example: my-awesome-design.png -> My Awesome Design
    return nameWithoutExt
      .replace(/[-_]/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  /**
   * Generate product description
   */
  generateDescription(title: string): string {
    return `High-quality ${title} design on premium apparel. Comfortable, durable, and stylish.`
  }

  /**
   * Upload image and create products
   */
  async createProductsForImage(image: ProcessedImage): Promise<ProductResult> {
    const title = this.generateTitle(image.filename)
    const description = this.generateDescription(title)

    console.log(`\n📦 Processing: ${image.filename}`)
    console.log(`   Title: ${title}`)

    const result: ProductResult = {
      filename: image.filename
    }

    try {
      // Create T-shirt
      console.log('   👕 Creating T-Shirt...')
      const tshirt = await this.printify.createTShirt(
        image.base64,
        `${title} - T-Shirt`,
        description,
        {
          price: parseFloat(process.env.DEFAULT_TSHIRT_PRICE || '19.99'),
          tags: ['ai-generated', 'pod', 'custom-design']
        }
      )

      result.tshirt = {
        id: tshirt.id,
        title: tshirt.title,
        url: tshirt.printifyUrl
      }

      console.log(`   ✅ T-Shirt created: ${tshirt.printifyUrl}`)

      // Publish T-shirt if AUTO_PUBLISH is enabled
      if (process.env.AUTO_PUBLISH === 'true') {
        console.log('   📤 Publishing T-Shirt...')
        await this.printify.publishProduct(tshirt.id)
        console.log('   ✅ T-Shirt published')
      }

      // Create Hoodie
      console.log('   🧥 Creating Hoodie...')
      const hoodie = await this.printify.createHoodie(
        image.base64,
        `${title} - Hoodie`,
        description,
        {
          price: parseFloat(process.env.DEFAULT_HOODIE_PRICE || '34.99'),
          tags: ['ai-generated', 'pod', 'custom-design']
        }
      )

      result.hoodie = {
        id: hoodie.id,
        title: hoodie.title,
        url: hoodie.printifyUrl
      }

      console.log(`   ✅ Hoodie created: ${hoodie.printifyUrl}`)

      // Publish Hoodie if AUTO_PUBLISH is enabled
      if (process.env.AUTO_PUBLISH === 'true') {
        console.log('   📤 Publishing Hoodie...')
        await this.printify.publishProduct(hoodie.id)
        console.log('   ✅ Hoodie published')
      }

    } catch (error) {
      console.error(`   ❌ Error creating products:`, error)
      result.error = error instanceof Error ? error.message : String(error)
    }

    return result
  }

  /**
   * Run the main process
   */
  async run(): Promise<void> {
    console.log('🚀 Printify Product Push Started')
    console.log(`📁 Image Directory: ${this.imageDir}`)
    console.log(`🏪 Shop ID: ${this.printify['config'].shopId}`)
    console.log('')

    // Get all image files
    const imageFiles = await this.getImageFiles()

    if (imageFiles.length === 0) {
      console.log('⚠️  No images found in the directory')
      return
    }

    console.log(`📸 Found ${imageFiles.length} image(s)`)

    // Process each image
    for (const filename of imageFiles) {
      const image = await this.processImage(filename)

      if (!image) {
        this.results.push({
          filename,
          error: 'Failed to process image'
        })
        continue
      }

      const result = await this.createProductsForImage(image)
      this.results.push(result)

      // Add delay between requests to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 2000))
    }

    // Print summary
    this.printSummary()
  }

  /**
   * Print summary of results
   */
  printSummary(): void {
    console.log('\n' + '='.repeat(60))
    console.log('📊 SUMMARY')
    console.log('='.repeat(60))

    const successful = this.results.filter(r => !r.error)
    const failed = this.results.filter(r => r.error)

    console.log(`\n✅ Successful: ${successful.length}`)
    console.log(`❌ Failed: ${failed.length}`)

    if (successful.length > 0) {
      console.log('\n📦 Created Products:')
      successful.forEach(result => {
        console.log(`\n   ${result.filename}`)
        if (result.tshirt) {
          console.log(`   👕 T-Shirt: ${result.tshirt.url}`)
        }
        if (result.hoodie) {
          console.log(`   🧥 Hoodie: ${result.hoodie.url}`)
        }
      })
    }

    if (failed.length > 0) {
      console.log('\n❌ Failed Products:')
      failed.forEach(result => {
        console.log(`   ${result.filename}: ${result.error}`)
      })
    }

    console.log('\n' + '='.repeat(60))
  }
}

// Main execution
async function main() {
  try {
    const pusher = new PrintifyPusher()
    await pusher.run()
  } catch (error) {
    console.error('Fatal error:', error)
    process.exit(1)
  }
}

main()
