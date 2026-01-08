/**
 * StaticWaves POD Engine - Enhanced Designs Tab
 * Advanced design management with search, filters, and bulk operations
 */

import React, { useState, useEffect } from 'react'
import {
  Search, Filter, Download, Trash2, Package, Eye,
  CheckCircle, XCircle, Clock, AlertCircle, Upload,
  Grid, List, SlidersHorizontal, X, Check
} from 'lucide-react'

interface Design {
  id: string
  filename: string
  width: number
  height: number
  status: string
  created_at: string
  tags: string[]
  prompt?: string
}

export default function EnhancedDesigns() {
  const [designs, setDesigns] = useState<Design[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedDesigns, setSelectedDesigns] = useState<Set<string>>(new Set())
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [showFilters, setShowFilters] = useState(false)

  const API_BASE = 'http://localhost:8188/api'
  const token = localStorage.getItem('token')

  useEffect(() => {
    fetchDesigns()
  }, [])

  const fetchDesigns = async () => {
    try {
      const response = await fetch(`${API_BASE}/designs?limit=100`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setDesigns(data)
      }
    } catch (error) {
      console.error('Failed to fetch designs:', error)
    } finally {
      setLoading(false)
    }
  }

  // Filter and search logic
  const filteredDesigns = designs.filter(design => {
    // Search filter
    const matchesSearch = searchQuery === '' ||
      design.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      design.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())) ||
      design.prompt?.toLowerCase().includes(searchQuery.toLowerCase())

    // Status filter
    const matchesStatus = statusFilter === 'all' || design.status === statusFilter

    return matchesSearch && matchesStatus
  })

  // Selection handlers
  const handleSelectAll = () => {
    if (selectedDesigns.size === filteredDesigns.length) {
      setSelectedDesigns(new Set())
    } else {
      setSelectedDesigns(new Set(filteredDesigns.map(d => d.id)))
    }
  }

  const handleSelectDesign = (id: string) => {
    const newSelected = new Set(selectedDesigns)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedDesigns(newSelected)
  }

  // Bulk operations
  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${selectedDesigns.size} designs?`)) return

    // Implement bulk delete
    console.log('Deleting:', Array.from(selectedDesigns))
    setSelectedDesigns(new Set())
  }

  const handleBulkCreateProducts = async () => {
    console.log('Creating products for:', Array.from(selectedDesigns))
    // Implement bulk product creation
  }

  const handleBulkDownload = async () => {
    console.log('Downloading:', Array.from(selectedDesigns))
    // Implement bulk download
  }

  const getStatusColor = (status: string) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-800',
      processing: 'bg-blue-100 text-blue-800',
      published: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'published':
        return <CheckCircle className="w-4 h-4" />
      case 'processing':
        return <Clock className="w-4 h-4 animate-spin" />
      case 'failed':
        return <XCircle className="w-4 h-4" />
      default:
        return <AlertCircle className="w-4 h-4" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header with Search and Actions */}
      <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Designs</h2>
          <p className="text-gray-600">
            {filteredDesigns.length} design{filteredDesigns.length !== 1 ? 's' : ''}
            {selectedDesigns.size > 0 && ` • ${selectedDesigns.size} selected`}
          </p>
        </div>

        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => {/* Open upload modal */}}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
          >
            <Upload className="w-4 h-4" />
            Upload Design
          </button>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search designs by name, tags, or prompt..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-4 py-2 border rounded-lg flex items-center gap-2 ${
              showFilters ? 'bg-blue-50 border-blue-300 text-blue-700' : 'border-gray-300 hover:bg-gray-50'
            }`}
          >
            <SlidersHorizontal className="w-4 h-4" />
            Filters
          </button>

          {/* View Mode Toggle */}
          <div className="flex border border-gray-300 rounded-lg">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-2 ${viewMode === 'grid' ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-50'}`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 border-l ${viewMode === 'list' ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-50'}`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="all">All Statuses</option>
                  <option value="draft">Draft</option>
                  <option value="processing">Processing</option>
                  <option value="published">Published</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Bulk Actions Bar */}
      {selectedDesigns.size > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <span className="font-medium text-blue-900">
                {selectedDesigns.size} design{selectedDesigns.size !== 1 ? 's' : ''} selected
              </span>
              <button
                onClick={() => setSelectedDesigns(new Set())}
                className="text-blue-700 hover:text-blue-900 text-sm underline"
              >
                Clear selection
              </button>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleBulkCreateProducts}
                className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-green-700"
              >
                <Package className="w-4 h-4" />
                Create Products
              </button>
              <button
                onClick={handleBulkDownload}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
              <button
                onClick={handleBulkDelete}
                className="bg-red-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-red-700"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Select All Checkbox */}
      {filteredDesigns.length > 0 && (
        <div className="flex items-center gap-2 bg-gray-50 px-4 py-2 rounded-lg">
          <input
            type="checkbox"
            checked={selectedDesigns.size === filteredDesigns.length}
            onChange={handleSelectAll}
            className="w-4 h-4 text-blue-600 rounded"
          />
          <label className="text-sm text-gray-700">
            Select all {filteredDesigns.length} design{filteredDesigns.length !== 1 ? 's' : ''}
          </label>
        </div>
      )}

      {/* Designs Grid/List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading designs...</p>
        </div>
      ) : filteredDesigns.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <Package className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600">
            {searchQuery || statusFilter !== 'all'
              ? 'No designs match your filters'
              : 'No designs yet. Upload your first design to get started!'}
          </p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredDesigns.map((design) => (
            <div
              key={design.id}
              className={`bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition ${
                selectedDesigns.has(design.id) ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              {/* Selection Checkbox */}
              <div className="absolute top-2 left-2 z-10">
                <input
                  type="checkbox"
                  checked={selectedDesigns.has(design.id)}
                  onChange={() => handleSelectDesign(design.id)}
                  className="w-5 h-5 text-blue-600 rounded shadow-lg"
                />
              </div>

              {/* Image Preview */}
              <div className="aspect-square bg-gray-200 relative">
                <img
                  src={`${API_BASE}/designs/${design.id}/preview?width=400`}
                  alt={design.filename}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-2 right-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1 ${getStatusColor(design.status)}`}>
                    {getStatusIcon(design.status)}
                    {design.status}
                  </span>
                </div>
              </div>

              {/* Info */}
              <div className="p-4">
                <h3 className="font-semibold truncate">{design.filename}</h3>
                <p className="text-sm text-gray-600">{design.width} × {design.height}</p>
                {design.tags.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {design.tags.slice(0, 3).map((tag, i) => (
                      <span key={i} className="px-2 py-1 bg-gray-100 text-xs rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                <div className="mt-4 flex gap-2">
                  <button className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 text-sm">
                    Create Product
                  </button>
                  <button className="p-2 border rounded hover:bg-gray-50">
                    <Eye className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        // List View
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left w-12">
                  <input
                    type="checkbox"
                    checked={selectedDesigns.size === filteredDesigns.length}
                    onChange={handleSelectAll}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dimensions</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tags</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredDesigns.map((design) => (
                <tr
                  key={design.id}
                  className={`hover:bg-gray-50 ${selectedDesigns.has(design.id) ? 'bg-blue-50' : ''}`}
                >
                  <td className="px-4 py-4">
                    <input
                      type="checkbox"
                      checked={selectedDesigns.has(design.id)}
                      onChange={() => handleSelectDesign(design.id)}
                      className="w-4 h-4 text-blue-600 rounded"
                    />
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-medium">{design.filename}</div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {design.width} × {design.height}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {design.tags.slice(0, 2).map((tag, i) => (
                        <span key={i} className="px-2 py-1 bg-gray-100 text-xs rounded">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${getStatusColor(design.status)}`}>
                      {getStatusIcon(design.status)}
                      {design.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {new Date(design.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      <button className="text-blue-600 hover:underline text-sm">
                        View
                      </button>
                      <button className="text-gray-600 hover:underline text-sm">
                        Edit
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
