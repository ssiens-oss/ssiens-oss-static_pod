#!/usr/bin/env node
/**
 * TikTok Storefront Preflight Checker
 * Validates products before publish to prevent silent blocks
 */

const fs = require('fs')
const path = require('path')

// TikTok Storefront Rules
const RULES = {
  PRICE_FLOORS: {
    'tshirt': 12.00,
    'hoodie': 22.00,
    'poster': 14.00,
    'sticker': 3.99
  },
  MIN_INVENTORY: 10,
  IMAGE_MIN_SIZE: 1000,
  REQUIRED_ASPECT_RATIO: 1, // 1:1 square
  FORBIDDEN_TEXT: ['mockup', 'sample', 'watermark', 'demo']
}

class TikTokPreflight {
  constructor() {
    this.issues = []
    this.fixes = []
  }

  /**
   * Main preflight check
   */
  check(product) {
    this.issues = []
    this.fixes = []

    this.checkPrice(product)
    this.checkInventory(product)
    this.checkImages(product)
    this.checkVariants(product)

    const blockers = this.issues.filter(i => i.severity === 'BLOCKER')
    const warnings = this.issues.filter(i => i.severity === 'WARNING')

    return {
      pass: blockers.length === 0,
      canPublishLive: true, // LIVE always allowed
      canPublishStorefront: blockers.length === 0,
      blockers,
      warnings,
      fixes: this.fixes,
      recommendation: this.getRecommendation(blockers.length)
    }
  }

  /**
   * Check price floor
   */
  checkPrice(product) {
    const productType = this.detectProductType(product.title)
    const minPrice = RULES.PRICE_FLOORS[productType]

    if (minPrice && product.price < minPrice) {
      this.issues.push({
        type: 'PRICE',
        severity: 'BLOCKER',
        message: `Price $${product.price} below TikTok floor $${minPrice}`,
        fix: `Raise to $${minPrice}`
      })
    }
  }

  /**
   * Check inventory
   */
  checkInventory(product) {
    const variants = product.variants || []
    const lowStock = variants.filter(v => (v.inventory || 0) < RULES.MIN_INVENTORY)

    if (lowStock.length > 0) {
      this.issues.push({
        type: 'INVENTORY',
        severity: 'WARNING',
        message: `${lowStock.length} variants below ${RULES.MIN_INVENTORY} stock`,
        fix: `Auto-set to ${RULES.MIN_INVENTORY}`
      })
    }
  }

  /**
   * Check images
   */
  checkImages(product) {
    const images = product.images || []

    if (images.length === 0) {
      this.issues.push({
        type: 'IMAGE',
        severity: 'BLOCKER',
        message: 'No images provided',
        fix: 'Add product images'
      })
      return
    }

    // Check image dimensions (if file path available)
    images.forEach((img, idx) => {
      if (typeof img === 'string' && fs.existsSync(img)) {
        // Simple check - real impl would use sharp/jimp
        const stats = fs.statSync(img)
        if (stats.size < 50000) { // < 50KB probably too small
          this.issues.push({
            type: 'IMAGE',
            severity: 'WARNING',
            message: `Image ${idx + 1} may be too small (${stats.size} bytes)`,
            fix: 'Use high-res images (min 1000x1000px)'
          })
        }
      }
    })
  }

  /**
   * Check variants completeness
   */
  checkVariants(product) {
    const variants = product.variants || []

    const incomplete = variants.filter(v => !v.id || !v.price)
    if (incomplete.length > 0) {
      this.issues.push({
        type: 'VARIANT',
        severity: 'BLOCKER',
        message: `${incomplete.length} variants missing ID or price`,
        fix: 'Complete all variant data'
      })
    }
  }

  /**
   * Auto-fix issues
   */
  autoFix(product) {
    this.fixes = []

    // Fix inventory
    if (product.variants) {
      product.variants.forEach(v => {
        if ((v.inventory || 0) < RULES.MIN_INVENTORY) {
          v.inventory = RULES.MIN_INVENTORY
          this.fixes.push({
            type: 'INVENTORY',
            message: `Set variant ${v.id} inventory to ${RULES.MIN_INVENTORY}`
          })
        }
      })
    }

    // Fix price
    const productType = this.detectProductType(product.title)
    const minPrice = RULES.PRICE_FLOORS[productType]
    if (minPrice && product.price < minPrice) {
      product.price = minPrice
      this.fixes.push({
        type: 'PRICE',
        message: `Raised price to $${minPrice}`
      })
    }

    return this.fixes.length > 0
  }

  /**
   * Detect product type from title
   */
  detectProductType(title = '') {
    const lower = title.toLowerCase()
    if (lower.includes('hoodie')) return 'hoodie'
    if (lower.includes('tee') || lower.includes('shirt')) return 'tshirt'
    if (lower.includes('poster')) return 'poster'
    if (lower.includes('sticker')) return 'sticker'
    return 'unknown'
  }

  /**
   * Get recommendation
   */
  getRecommendation(blockerCount) {
    if (blockerCount === 0) {
      return 'PUBLISH_STOREFRONT'
    }
    return 'PUBLISH_LIVE_ONLY'
  }

  /**
   * Generate report
   */
  generateReport(result, product) {
    const report = {
      product_id: product.id || 'unknown',
      product_title: product.title,
      timestamp: new Date().toISOString(),
      status: result.pass ? 'PASS' : 'FAIL',
      storefront_eligible: result.canPublishStorefront,
      live_eligible: result.canPublishLive,
      recommendation: result.recommendation,
      blockers: result.blockers,
      warnings: result.warnings,
      fixes_applied: result.fixes
    }

    return report
  }
}

module.exports = TikTokPreflight
