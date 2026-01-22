# 🎨 POD Gateway - Feature Documentation

## Overview

The POD Gateway is a powerful, modern web interface for managing your Print-on-Demand (POD) workflow. It provides a comprehensive approval system for generated images with advanced features like batch operations, search, and one-click publishing to Printify.

## 🚀 Key Features

### 1. **Smart Auto-Titling System** ✨ NEW

Automatically generate intelligent, SEO-friendly titles for your designs.

**How it works:**
- Extracts keywords from your prompt
- Includes style and genre tags
- Uses customizable templates
- Date-based naming options
- Fallback to safe defaults

**Default Template:** `{style} {prompt} Design`

**Example Output:**
- Prompt: "majestic mountain landscape sunset"
- Style: "watercolor"
- Result: "Watercolor Majestic Mountain Landscape Design"

**Customization:**
- Click "⚙ Settings" in toolbar
- Edit title template with available tokens
- Choose from preset templates (Default, Descriptive, Date-Based, Simple)
- Settings saved automatically in browser

**Available Tokens:**
- `{style}` - Design style (minimalist, vintage, etc.)
- `{genre}` - Design genre (nature, fantasy, etc.)
- `{prompt}` - First 3 keywords from prompt
- `{date}` - Current date (YYYY-MM-DD)
- `{id}` - Short image ID (6 characters)
- `{filename}` - Original filename without extension

---

### 2. **Batch Selection & Multi-Select**

Select multiple images at once for bulk operations.

**How to use:**
- Click the checkbox on any image card to select it
- Use "✓ Select All" to select all visible images
- Use "✗ Deselect All" to clear selection
- **Keyboard shortcut:** `Ctrl/Cmd + A` to select all

**Visual feedback:**
- Selected images have a glowing purple border
- Bulk actions bar appears when items are selected
- Counter shows how many items are selected

---

### 3. **Bulk Operations** 🚀 ENHANCED

Perform actions on multiple images simultaneously with real-time progress tracking.

#### Available Bulk Actions:

**✓ Bulk Approve** ✨ NEW: Progress Indicators
- Approves all selected images
- Shows confirmation dialog before execution
- Real-time progress bar during execution
- Displays success/fail count after completion
- Can be undone with Undo button

**✗ Bulk Reject** ✨ NEW: Progress Indicators
- Rejects all selected images
- Useful for quickly clearing unwanted designs
- Confirmation required
- Real-time progress tracking
- Can be undone with Undo button

**→ Bulk Publish (One-Click Publish)** ✨ NEW: Smart Titles & Preview
- **Smart filtering:** Only publishes approved images
- **Smart titles:** Uses title template with context (style, genre, keywords)
- **Title Preview:** Shows generated titles before publishing (first 5 images)
- Publishes to Printify sequentially with progress bar
- Shows individual error messages if any fail
- Perfect for publishing multiple approved designs at once
- Can be undone with Undo button

**⬇ Bulk Download** ✨ NEW: Progress Indicators
- Downloads all selected images to your computer
- Downloads happen sequentially with real-time progress bar
- Files keep their original names
- Small delays prevent browser blocking

**🗑 Bulk Delete**
- Delete multiple images at once
- **Note:** Currently shows "not yet implemented" - backend support needed
- Requires confirmation to prevent accidental deletion

#### Progress Indicators ✨ NEW

All bulk operations now show a live progress indicator:
- Appears in bottom-right corner
- Shows current progress: "X / Total"
- Visual progress bar with percentage
- Auto-dismisses when complete
- Non-blocking: Can continue using the interface

---

### 4. **Undo System** ✨ NEW

Safely reverse bulk operations with a multi-level undo system.

**Features:**
- Undo up to 10 recent bulk actions
- Shows undo count in button: "↶ Undo (3)"
- Restores previous status for all affected images
- Works for: Bulk Approve, Bulk Reject, Bulk Publish
- Displays success/failure count after undo

**How to use:**
1. Perform a bulk operation (approve, reject, or publish)
2. Click "↶ Undo" button in toolbar (if you change your mind)
3. Confirm the undo action
4. All images restored to previous state

**Limitations:**
- Cannot undo individual image actions (only bulk)
- Stack limited to 10 most recent actions
- Published images on Printify remain published (local status only)

---

### 5. **Search & Filter** 🚀 ENHANCED

Find images quickly with powerful search and filtering.

**Search Box:**
- Real-time search as you type
- Searches both filename and image ID
- Case-insensitive
- Works with active filters

**Sort Options:** ✨ NEW: True Timestamp Sorting
- **Newest first** (default) - Uses actual creation timestamp
- **Oldest first** - Uses actual creation timestamp
- **Name (A-Z)** - Alphabetical by filename
- **Name (Z-A)** - Reverse alphabetical

**Improved Sorting:**
- Now uses `created_at` field when available for accurate temporal sorting
- Fallback to filename comparison for older images without timestamps
- Faster and more accurate than filename-based date sorting

**Status Filters:**
- All (shows everything)
- Pending (newly generated, awaiting approval)
- Approved (ready to publish)
- Published (live on Printify)
- Rejected (not approved)
- Failed (publish attempt failed)

---

### 6. **Image Preview & Download**

**Image Preview Modal:**
- Click any image to open full-size preview
- Shows filename
- Download button in preview
- **Keyboard shortcut:** `Escape` to close

**Download Options:**
- Individual download button on each card (⬇)
- Download from preview modal
- Bulk download for multiple images

---

### 7. **Auto-Refresh & Notifications**

**Auto-Refresh Toggle:**
- Located in toolbar settings
- Refreshes image gallery every 10 seconds
- Default: ON
- Toggle off to save bandwidth or when working offline
- Shows notification when toggled

**Toast Notifications:**
- Appear in top-right corner
- Auto-dismiss after 3 seconds
- Color-coded:
  - **Green border:** Success
  - **Red border:** Error
  - **Blue border:** Info

**Notification Types:**
- Action confirmations (approve, reject, etc.)
- Bulk operation results
- Generation completion alerts
- Error messages
- Setting changes

---

### 8. **ComfyUI Prompter**

Generate new images directly from the gateway.

**Features:**
- Text prompt input
- Style dropdown (minimalist, vintage, retro, etc.)
- Genre dropdown (nature, fantasy, sci-fi, etc.)
- Real-time status indicator
- Auto-polling for generation completion
- Automatic image refresh when complete

**Status Indicators:**
- Idle: Ready to accept prompts
- Queued: Submitted to RunPod
- Generation in progress: Shows prompt ID
- Complete: Shows download count
- Failed: Shows error message

---

### 9. **Smart Publishing Modal** 🚀 ENHANCED

Fine-tune product details before publishing with intelligent title pre-fill.

**Features:**
- **Smart title pre-fill** ✨ NEW: Auto-generates context-aware title using template
- Product title (required, editable)
- Optional description
- Price override (leave blank for default)
- Product presets:
  - T-Shirt (Blueprint 3, Provider 99)
  - Hoodie (Blueprint 165, Provider 99)
  - Custom (manual blueprint/provider entry)
  - Use gateway defaults

**Smart Title Pre-fill:**
- Uses your custom title template
- Includes prompt keywords, style, and genre
- Fully editable before publishing
- Balances speed and customization

**Workflow:**
1. Click "→ Publish" on any approved image
2. Review auto-generated title (edit if desired)
3. Add description, price, product type (optional)
4. Click "Publish Now"
5. Modal closes and image updates to "published"

---

### 10. **Settings Panel** ✨ NEW

Customize gateway behavior with persistent settings.

**How to access:**
- Click "⚙ Settings" button in toolbar
- Modal opens with customization options

**Available Settings:**

**Title Template:**
- Customize how titles are generated
- Use tokens for dynamic content
- Real-time preview of available tokens
- Preset templates for quick setup

**Template Presets:**
- **Default:** `{style} {prompt} Design`
- **Descriptive:** `{genre} {style} {prompt} - {date}`
- **Date-Based:** `Design {date} {id}`
- **Simple:** `{prompt} {id}`

**Persistence:**
- Settings saved to browser localStorage
- Persists across sessions
- Per-browser configuration

---

### 11. **Keyboard Shortcuts**

Boost productivity with keyboard shortcuts:

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + A` | Select all visible images |
| `Escape` | Close modal OR deselect all |

---

### 12. **Statistics Dashboard**

Real-time counters at the top of the page:

- **Total:** All images in gallery
- **Pending:** Awaiting approval
- **Approved:** Ready to publish
- **Published:** Live on Printify

---

### 13. **Responsive Design**

Works on all devices:
- Desktop (optimal experience)
- Tablet (responsive toolbar and grid)
- Mobile (single column layout, touch-friendly)

---

## 🎯 Common Workflows

### Workflow 1: Generate and Publish Single Design

1. Enter prompt in ComfyUI Prompter
2. Select style and genre (optional)
3. Click "Generate with ComfyUI"
4. Wait for generation to complete (status updates automatically)
5. Review the generated image
6. Click "✓ Approve"
7. Click "→ Publish"
8. Review product details, click "Publish Now"
9. ✅ Image is now live on Printify!

---

### Workflow 2: Bulk Approve and Publish Multiple Designs ✨ ENHANCED

1. Filter by "Pending" to see only unapproved images
2. Review images visually
3. Click checkboxes on images you want to approve
4. Click "✓ Approve" in bulk actions bar
5. Watch real-time progress bar as images are approved
6. All selected images are now approved
7. Keep them selected (or reselect)
8. Click "→ Publish All" in bulk actions bar
9. **NEW:** Preview generated titles in confirmation dialog
10. Confirm bulk publish
11. **NEW:** Watch progress bar show publishing status
12. ✅ All approved images published to Printify with smart titles!
13. **Optional:** Click "↶ Undo" if you need to reverse the action

---

### Workflow 3: Batch Download for Backup

1. Search or filter images you want to download
2. Click "✓ Select All"
3. Click "⬇ Download" in bulk actions bar
4. All selected images download to your computer
5. ✅ Backup complete!

---

### Workflow 4: Customize Title Templates ✨ NEW

1. Click "⚙ Settings" button in toolbar
2. Review current title template
3. **Option A:** Choose a preset template (Default, Descriptive, Date-Based, Simple)
4. **Option B:** Create custom template using available tokens
5. Click "Save Settings"
6. Generate new images and see smart titles automatically
7. All future bulk publishes use your custom template

**Example Custom Template:**
- Template: `{date} {genre} {style} - {prompt}`
- Result: "2026-01-22 Nature Watercolor - Mountain Landscape Sunset"

---

### Workflow 5: Clean Up Rejected Designs

1. Filter by "Rejected"
2. Review rejected images
3. **Option A:** Reset to pending (click "↺ Reset" per image)
4. **Option B:** Select unwanted images and use "🗑 Delete" when implemented

---

## 🎨 UI Elements Explained

### Image Cards

Each card shows:
- Checkbox for selection (top-left)
- Image preview (click to enlarge)
- Filename
- Status badge (color-coded)
- Action buttons based on status

### Status Badge Colors

- **Gray (Pending):** Newly generated
- **Green (Approved):** Ready to publish
- **Blue (Published):** Live on Printify
- **Red (Rejected):** Not approved
- **Dark Red (Failed):** Publish error
- **Orange (Publishing):** Currently uploading

### Toolbar Sections

- **Search:** Find specific images
- **Sort:** Change display order
- **Settings:** Auto-refresh toggle
- **Selection:** Select/deselect all buttons

---

## 🔧 Configuration

### Constants (New in v1.1)

All timing constants are now defined at the top of the script for easy customization:

```javascript
const AUTO_REFRESH_INTERVAL = 10000; // 10 seconds
const POLL_INTERVAL = 2000; // 2 seconds (ComfyUI status polling)
const RUNPOD_POLL_INTERVAL = 4000; // 4 seconds (RunPod status polling)
const NOTIFICATION_DURATION = 3000; // 3 seconds
```

To change any interval, edit these constants in `gateway/templates/gallery.html` at line ~845.

### Title Template

Default: `{style} {prompt} Design`

**Via UI (Recommended):**
1. Click "⚙ Settings" in toolbar
2. Edit title template
3. Click "Save Settings"

**Via Code:**
Edit `gateway/templates/gallery.html` at line ~860:
```javascript
let titleTemplate = '{style} {prompt} Design'; // Change default template
```

### Undo Stack Size

Default: 10 actions

To change, edit `gateway/templates/gallery.html` in the `saveUndoState` function:
```javascript
// Keep only last 10 undo states
if (undoStack.length > 10) {  // Change 10 to desired size
    undoStack.shift();
}
```

---

## 💡 Tips & Tricks

1. **Use Search + Filters Together:** Search for specific terms within filtered status groups

2. **Keyboard Shortcuts Save Time:** Use `Ctrl+A` and `Escape` frequently

3. **Bulk Publish Approved Only:** The system automatically skips non-approved images when bulk publishing

4. **Monitor Generation:** The prompter status updates every 2 seconds automatically

5. **Preview Before Publishing:** Click any image to see it full-size before approving

6. **One-Click Publishing:** For rapid workflows, select multiple approved images and hit "→ Publish All"

7. **Organize with Filters:** Use the "Failed" filter to find and retry errored publishes

8. **Download for Backup:** Regularly bulk download your approved images for safekeeping

9. **Mobile-Friendly:** Access the gateway from your phone to approve/reject on the go

10. **Auto-Refresh Off:** Turn off auto-refresh when reviewing images carefully to prevent UI jumps

11. **✨ NEW - Customize Title Templates:** Set up your preferred title format once in Settings, use forever

12. **✨ NEW - Preview Titles Before Publishing:** Check the title preview in bulk publish confirmation to ensure quality

13. **✨ NEW - Use Undo for Safety:** Made a mistake? The Undo button has you covered (up to 10 actions)

14. **✨ NEW - Watch Progress:** Progress bars show exactly where you are in bulk operations

15. **✨ NEW - Include Keywords in Prompts:** The first 3 significant words from your prompt become part of titles

16. **✨ NEW - Style Matters:** Always select a style and genre when generating for better auto-titles

17. **✨ NEW - True Time Sorting:** "Newest" and "Oldest" now use actual timestamps, not filenames

18. **✨ NEW - Template Presets:** Don't want to create templates? Use the built-in presets

---

## 🐛 Troubleshooting

### Images Not Showing

**Solution:**
- Check that `/gateway/data/images/` directory exists
- Verify images were generated successfully
- Check browser console for errors
- Ensure gateway is running and accessible

### Bulk Publish Fails

**Possible causes:**
1. Printify API key not configured
2. Images not in "approved" status (bulk publish skips these)
3. Network connectivity issues
4. Invalid blueprint or provider IDs

**Solution:**
- Check gateway logs for detailed error messages
- Verify Printify credentials in `.env`
- Try publishing single image first to test connection

### Search Not Working

**Solution:**
- Ensure you're typing the correct filename or ID
- Check that images exist with that name
- Clear search box and try again
- Refresh the page

### Auto-Refresh Stopped

**Solution:**
- Check if auto-refresh toggle is ON
- Browser may have throttled background timers (check console)
- Manually click refresh by toggling auto-refresh off then on

---

## 🔮 Future Enhancements

Planned features:

- [ ] Bulk delete with backend API support
- [ ] Image metadata editing (rename, tags)
- [ ] Advanced filters (date range, size)
- [ ] Drag-and-drop reordering
- [ ] Favorites/bookmarking
- [ ] Export gallery report (CSV/JSON)
- [ ] Batch image editing (crop, resize)
- [ ] Collections/albums
- [ ] Scheduled publishing
- [ ] Analytics dashboard
- [ ] AI-powered title suggestions based on image analysis
- [ ] Title templates with conditional logic
- [ ] Batch rename with pattern matching

## ✅ Recently Completed (v1.1)

- [x] Smart auto-titling with customizable templates
- [x] Progress indicators for all bulk operations
- [x] Undo functionality for bulk actions
- [x] Title preview before bulk publish
- [x] True timestamp-based sorting
- [x] Settings panel with persistent configuration
- [x] Template presets for quick setup
- [x] Configurable constants for all intervals

---

## 📚 API Reference

### Bulk Operations Endpoints

These endpoints are called by the bulk operations:

```
POST /api/approve/{image_id}
POST /api/reject/{image_id}
POST /api/publish/{image_id}
POST /api/reset/{image_id}
```

### Data Format

**Request (publish):**
```json
{
  "title": "Design Title",
  "description": "Optional description",
  "price_cents": 2999,
  "blueprint_id": 3,
  "provider_id": 99
}
```

**Response (success):**
```json
{
  "success": true,
  "product_id": "12345",
  "status": "published"
}
```

---

## 🎓 Best Practices

1. **Review Before Approving:** Always preview images before bulk approval

2. **Use Descriptive Titles:** When publishing, use meaningful product titles

3. **Monitor Failed Publishes:** Check the "Failed" filter regularly

4. **Backup Regularly:** Use bulk download to keep local copies

5. **Test Single First:** When trying new settings, test on one image before bulk operations

6. **Check Printify:** Verify published products appear correctly in your Printify store

7. **Clear Rejected:** Periodically clean up rejected images to keep gallery manageable

8. **Use Presets:** Leverage T-Shirt and Hoodie presets for consistent product setup

---

## ❓ FAQs

**Q: Can I undo a bulk operation?** ✨ UPDATED
A: Yes! Click the "↶ Undo" button in the toolbar after any bulk operation. You can undo up to 10 recent bulk actions (approve, reject, publish). Note: Published products remain on Printify, only local status is reversed.

**Q: How many images can I bulk publish at once?**
A: No hard limit, but large batches may take time. Recommended: 20-50 images per batch. Progress bar shows real-time status.

**Q: Do bulk operations run in parallel?**
A: No, they run sequentially to avoid rate limits and ensure reliability. Progress bars show current position.

**Q: Can I customize the auto-generated titles?** ✨ UPDATED
A: Yes! In two ways:
1. **Bulk Mode:** Set your title template in Settings (⚙), applies to all bulk publishes
2. **Individual Mode:** Edit the pre-filled title in publish modal before confirming

**Q: How do the title templates work?** ✨ NEW
A: Templates use tokens like `{style}`, `{prompt}`, `{genre}`, `{date}`, `{id}`, and `{filename}`. These are replaced with actual values when generating titles. Example: `{style} {prompt} Design` becomes "Watercolor Mountain Landscape Design".

**Q: What if my title template results in a bad title?** ✨ NEW
A: The system has fallbacks: (1) Multiple spaces are cleaned up, (2) Empty tokens are removed, (3) If final title is too short (<5 chars), it falls back to `Design {date} {id}`.

**Q: Where are my settings saved?** ✨ NEW
A: Settings are saved in your browser's localStorage. They persist across sessions but are browser-specific. Different browsers or private/incognito mode won't share settings.

**Q: What happens if internet disconnects during bulk publish?**
A: Already-published images remain published. Failed images will show error status. Progress bar shows where it stopped. Retry them individually or use undo and try again.

**Q: Can I filter by multiple statuses?**
A: Not currently. Use search within a status filter for more specific results.

**Q: How do I know if a bulk operation succeeded?** ✨ UPDATED
A: Three indicators: (1) Real-time progress bar during operation, (2) Notification appears showing success/fail count, (3) Gallery updates to show new statuses.

**Q: Does the undo button work for everything?** ✨ NEW
A: Undo works for bulk operations only (bulk approve, reject, publish). Individual image actions cannot be undone. The undo stack holds the last 10 bulk operations.

**Q: How do I get better auto-titles?** ✨ NEW
A: Three tips: (1) Write descriptive prompts with key words first, (2) Always select a style and genre when generating, (3) Customize your title template in Settings to prioritize what matters to you.

---

## 🤝 Contributing

Want to add more features? The gallery is built with vanilla JavaScript for simplicity. Key files:

- UI: `gateway/templates/gallery.html`
- Backend: `gateway/app/main.py`
- State: `gateway/app/state.py`

Pull requests welcome!

---

## 📞 Support

Issues? Questions?
- Check gateway logs: `tail -f /tmp/claude-**/tasks/*.output`
- Review Printify API docs: https://developers.printify.com
- Open an issue: https://github.com/ssiens-oss/ssiens-oss-static_pod/issues

---

## 📋 Changelog

### Version 1.1.0 - January 22, 2026

**Major Features:**
- ✨ Smart auto-titling system with customizable templates
- ✨ Progress indicators for all bulk operations
- ✨ Undo functionality (up to 10 actions)
- ✨ Title preview before bulk publish
- ✨ Settings panel with persistent configuration
- ✨ True timestamp-based sorting

**Improvements:**
- Enhanced bulk publish with smart title generation
- Added template presets for quick setup
- Improved individual publish modal with smart pre-fill
- Refactored constants for easier configuration
- Better error handling and user feedback

**Technical:**
- All timing intervals now configurable via constants
- LocalStorage integration for settings persistence
- Undo stack with 10-action history
- Progress tracking for downloads with delay to prevent blocking

### Version 1.0.0 - January 19, 2026

**Initial Release:**
- Batch selection and multi-select
- Bulk operations (approve, reject, publish, download)
- Search and filter functionality
- Image preview modal
- Auto-refresh toggle
- ComfyUI prompter integration
- Publishing modal with product presets
- Keyboard shortcuts
- Toast notifications
- Responsive design

---

**Version:** 1.1.0
**Last Updated:** January 22, 2026
**Powered by:** Flask, RunPod, Printify
