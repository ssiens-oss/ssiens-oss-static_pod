/**
 * Proofing Service
 * Manages content review and approval workflow
 */

export interface ProofingConfig {
  autoApprove: boolean
  requireManualReview: boolean
}

export interface ProofItem {
  id: string
  url: string
  metadata: {
    title: string
    description: string
    tags: string[]
    timestamp: string
  }
  proofStatus: 'pending' | 'approved' | 'rejected'
  proofNotes?: string
}

export interface ProofResult {
  approved: boolean
  notes?: string
}

export class ProofingService {
  private config: ProofingConfig
  private proofQueue: ProofItem[] = []
  private reviewCallback?: (item: ProofItem) => Promise<ProofResult>

  constructor(config: ProofingConfig) {
    this.config = config
  }

  /**
   * Set manual review callback
   */
  setReviewCallback(callback: (item: ProofItem) => Promise<ProofResult>): void {
    this.reviewCallback = callback
  }

  /**
   * Submit asset for review
   */
  async submitForReview(asset: any): Promise<ProofResult> {
    const proofItem: ProofItem = {
      id: asset.id,
      url: asset.url,
      metadata: asset.metadata,
      proofStatus: 'pending'
    }

    this.proofQueue.push(proofItem)

    // Auto-approve if enabled
    if (this.config.autoApprove && !this.config.requireManualReview) {
      proofItem.proofStatus = 'approved'
      return { approved: true }
    }

    // Manual review required
    if (this.reviewCallback) {
      const result = await this.reviewCallback(proofItem)
      proofItem.proofStatus = result.approved ? 'approved' : 'rejected'
      proofItem.proofNotes = result.notes
      return result
    }

    // Default: pending (will be reviewed later)
    return { approved: false, notes: 'Pending manual review' }
  }

  /**
   * Approve an item
   */
  async approve(itemId: string, notes?: string): Promise<void> {
    const item = this.proofQueue.find(i => i.id === itemId)
    if (item) {
      item.proofStatus = 'approved'
      item.proofNotes = notes
    }
  }

  /**
   * Reject an item
   */
  async reject(itemId: string, notes: string): Promise<void> {
    const item = this.proofQueue.find(i => i.id === itemId)
    if (item) {
      item.proofStatus = 'rejected'
      item.proofNotes = notes
    }
  }

  /**
   * Get all items pending review
   */
  getPendingItems(): ProofItem[] {
    return this.proofQueue.filter(i => i.proofStatus === 'pending')
  }

  /**
   * Get all approved items
   */
  getApprovedItems(): ProofItem[] {
    return this.proofQueue.filter(i => i.proofStatus === 'approved')
  }

  /**
   * Get all rejected items
   */
  getRejectedItems(): ProofItem[] {
    return this.proofQueue.filter(i => i.proofStatus === 'rejected')
  }

  /**
   * Get proofing statistics
   */
  getStats() {
    return {
      total: this.proofQueue.length,
      pending: this.proofQueue.filter(i => i.proofStatus === 'pending').length,
      approved: this.proofQueue.filter(i => i.proofStatus === 'approved').length,
      rejected: this.proofQueue.filter(i => i.proofStatus === 'rejected').length
    }
  }
}
