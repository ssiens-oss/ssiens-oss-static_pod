# 🎨 POD Gateway - Feature Documentation

## Overview

The POD Gateway is a powerful, modern web interface for managing your Print-on-Demand (POD) workflow. It provides a comprehensive approval system for generated images with advanced features like batch operations, search, and one-click publishing to Printify.

## 🚀 Key Features

### 1. **Batch Selection & Multi-Select**

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

### 2. **Bulk Operations**

Perform actions on multiple images simultaneously.

#### Available Bulk Actions:

**✓ Bulk Approve**
- Approves all selected images
- Shows confirmation dialog before execution
- Displays success/fail count after completion

**✗ Bulk Reject**
- Rejects all selected images
- Useful for quickly clearing unwanted designs
- Confirmation required

**→ Bulk Publish (One-Click Publish)**
- **Smart filtering:** Only publishes approved images
- Automatically generates titles: "Design {image-id}"
- Publishes to Printify sequentially
- Shows individual error messages if any fail
- Perfect for publishing multiple approved designs at once

**⬇ Bulk Download**
- Downloads all selected images to your computer
- Downloads happen sequentially with progress notifications
- Files keep their original names

**🗑 Bulk Delete**
- Delete multiple images at once
- **Note:** Currently shows "not yet implemented" - backend support needed
- Requires confirmation to prevent accidental deletion

---

### 3. **Search & Filter**

Find images quickly with powerful search and filtering.

**Search Box:**
- Real-time search as you type
- Searches both filename and image ID
- Case-insensitive
- Works with active filters

**Sort Options:**
- **Newest first** (default)
- **Oldest first**
- **Name (A-Z)**
- **Name (Z-A)**

**Status Filters:**
- All (shows everything)
- Pending (newly generated, awaiting approval)
- Approved (ready to publish)
- Published (live on Printify)
- Rejected (not approved)
- Failed (publish attempt failed)

---

### 4. **Image Preview & Download**

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

### 5. **Auto-Refresh & Notifications**

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

### 6. **ComfyUI Prompter**

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

### 7. **Smart Publishing Modal**

Fine-tune product details before publishing.

**Features:**
- Product title (required)
- Optional description
- Price override (leave blank for default)
- Product presets:
  - T-Shirt (Blueprint 3, Provider 99)
  - Hoodie (Blueprint 165, Provider 99)
  - Custom (manual blueprint/provider entry)
  - Use gateway defaults

**Workflow:**
1. Click "→ Publish" on any approved image
2. Review/edit product details
3. Click "Publish Now"
4. Modal closes and image updates to "published"

---

### 8. **Keyboard Shortcuts**

Boost productivity with keyboard shortcuts:

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + A` | Select all visible images |
| `Escape` | Close modal OR deselect all |

---

### 9. **Statistics Dashboard**

Real-time counters at the top of the page:

- **Total:** All images in gallery
- **Pending:** Awaiting approval
- **Approved:** Ready to publish
- **Published:** Live on Printify

---

### 10. **Responsive Design**

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

### Workflow 2: Bulk Approve and Publish Multiple Designs

1. Filter by "Pending" to see only unapproved images
2. Review images visually
3. Click checkboxes on images you want to approve
4. Click "✓ Approve" in bulk actions bar
5. Confirm bulk approval
6. All selected images are now approved
7. Keep them selected (or reselect)
8. Click "→ Publish All" in bulk actions bar
9. Confirm bulk publish
10. ✅ All approved images published to Printify!

---

### Workflow 3: Batch Download for Backup

1. Search or filter images you want to download
2. Click "✓ Select All"
3. Click "⬇ Download" in bulk actions bar
4. All selected images download to your computer
5. ✅ Backup complete!

---

### Workflow 4: Clean Up Rejected Designs

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

### Auto-Refresh Interval

Default: 10 seconds

To change, edit `gateway/templates/gallery.html`:

```javascript
// Line ~1450 and ~1484
autoRefreshInterval = setInterval(loadImages, 10000); // Change 10000 to desired milliseconds
```

### Notification Duration

Default: 3 seconds

To change, edit `gateway/templates/gallery.html`:

```javascript
// Line ~878
setTimeout(() => notif.remove(), 3000); // Change 3000 to desired milliseconds
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

**Q: Can I undo a bulk operation?**
A: Use the "Reset" button to change status back to pending. For deleted images (when implemented), there's no undo.

**Q: How many images can I bulk publish at once?**
A: No hard limit, but large batches may take time. Recommended: 20-50 images per batch.

**Q: Do bulk operations run in parallel?**
A: No, they run sequentially to avoid rate limits and ensure reliability.

**Q: Can I customize the auto-generated titles?**
A: Not in bulk mode. Use individual publish for custom titles.

**Q: What happens if internet disconnects during bulk publish?**
A: Already-published images remain published. Failed images will show error status. Retry them individually.

**Q: Can I filter by multiple statuses?**
A: Not currently. Use search within a status filter for more specific results.

**Q: How do I know if a bulk operation succeeded?**
A: A notification appears showing success/fail count. Check gallery to verify status changes.

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

**Version:** 1.0.0
**Last Updated:** January 2026
**Powered by:** Flask, RunPod, Printify
