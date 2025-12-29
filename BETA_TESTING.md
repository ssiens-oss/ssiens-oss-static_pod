# StaticWaves POD Studio - Beta Testing Guide

Welcome to the StaticWaves POD Studio Beta! This guide will help you get started with testing.

## What is StaticWaves POD Studio?

A web-based simulation of the StaticWaves Print-on-Demand automation suite, featuring:
- **Batch Processing:** Process multiple drops simultaneously
- **Real-time Logging:** Live terminal output for all operations
- **Interactive Design Editor:** Transform and adjust designs before upload
- **Printify Queue Management:** Track product upload status

## Beta Version Information

- **Version:** 6.0-beta.1
- **Release Date:** 2025-12-29
- **Environment:** Staging
- **Access:** Open Beta (no invite required)

## Getting Started

### Access the Beta

**RunPod Deployment:**
- URL: `https://<your-pod-id>-80.proxy.runpod.net`
- Health Check: Add `/health.json` to the URL

**Local Testing:**
```bash
# Clone the repository
git clone https://github.com/ssiens-oss/ssiens-oss-static_pod.git
cd ssiens-oss-static_pod

# Install dependencies
npm install

# Run locally
npm run dev
```

## Features to Test

### 1. Single Drop Processing

**Steps:**
1. Enter a drop name (e.g., "TestDrop1")
2. Set design count (e.g., 10)
3. Configure Blueprint ID and Provider ID
4. Click "Run Single Drop"
5. Watch the logs and progress bar

**What to verify:**
- [ ] Logs appear in real-time
- [ ] Progress bar updates smoothly
- [ ] Design preview loads
- [ ] Mockup preview appears
- [ ] Queue items update correctly

### 2. Batch Mode

**Steps:**
1. Enter multiple drop names in "Batch List" (comma-separated)
   - Example: `Drop1, Drop2, Drop3`
2. Click "Run Batch Mode"
3. Observe processing of multiple drops

**What to verify:**
- [ ] All drops are processed sequentially
- [ ] Progress bar shows cumulative progress
- [ ] Logs distinguish between drops
- [ ] Queue accumulates items from all drops

### 3. Design Editor

**Steps:**
1. Run a simulation to generate a design
2. Use editor controls:
   - Zoom In (+) / Zoom Out (-)
   - Move Up/Down/Left/Right
3. Click "Save Edit"

**What to verify:**
- [ ] Zoom controls work smoothly
- [ ] Pan controls move the design
- [ ] Transform persists until new run
- [ ] Save action logs confirmation

### 4. Queue Management

**Steps:**
1. Run a simulation with multiple designs
2. Watch the Printify Queue panel

**What to verify:**
- [ ] Items appear as "pending"
- [ ] Status changes to "uploading" (animated)
- [ ] Items complete with green checkmark
- [ ] Failed items show red error icon
- [ ] Queue count updates correctly

## Known Issues

### BETA-001: Editor Zoom Resets
- **Severity:** Low
- **Description:** Zoom level resets when starting a new simulation
- **Workaround:** Re-adjust zoom after each run

## What to Report

Please report any issues you encounter:

### Bug Reports Should Include:

1. **Description:** What happened?
2. **Expected Behavior:** What should have happened?
3. **Steps to Reproduce:** How can we recreate it?
4. **Screenshots:** If applicable
5. **Browser/Environment:**
   - Browser name and version
   - Operating system
   - Screen resolution
   - RunPod pod ID (if deployed)

### Example Bug Report:

```
**Issue:** Progress bar stuck at 50%

**Expected:** Progress should reach 100%

**Steps:**
1. Enter "Drop1" as drop name
2. Set design count to 5
3. Click "Run Single Drop"
4. Progress stops at 50%

**Environment:**
- Browser: Chrome 120
- OS: macOS Sonoma
- Screen: 1920x1080
```

## Performance Testing

Please note and report:

- [ ] Page load time (first visit)
- [ ] Page load time (subsequent visits)
- [ ] Simulation completion time for 10 designs
- [ ] Simulation completion time for 50 designs
- [ ] UI responsiveness during processing
- [ ] Memory usage (check browser task manager)

## Feature Requests

We welcome suggestions! When requesting features:

1. Describe the feature clearly
2. Explain the use case
3. Suggest how it might work
4. Note if it's critical or nice-to-have

## Feedback Channels

### GitHub Issues (Preferred)
https://github.com/ssiens-oss/ssiens-oss-static_pod/issues

**Label your issue:**
- `bug` - Something isn't working
- `enhancement` - New feature request
- `beta-feedback` - General feedback
- `documentation` - Documentation improvements

### AI Studio
https://ai.studio/apps/drive/1tFlXgUzuZqrOcLHGveQzS2XoSnQEtQc4

## Beta Testing Checklist

Use this checklist for comprehensive testing:

### Core Functionality
- [ ] Single drop processing works
- [ ] Batch mode processes multiple drops
- [ ] Logs display in real-time
- [ ] Progress bar updates accurately
- [ ] Design previews load correctly
- [ ] Mockup previews appear
- [ ] Queue updates properly

### Editor Controls
- [ ] Zoom in/out functions
- [ ] Pan in all directions works
- [ ] Save edit confirms action
- [ ] Reset on new run works

### UI/UX
- [ ] All buttons are clickable
- [ ] Forms accept input correctly
- [ ] Color scheme is readable
- [ ] Layout is responsive
- [ ] No console errors
- [ ] Tooltips/labels are clear

### Performance
- [ ] No lag during simulation
- [ ] Smooth animations
- [ ] Quick page loads
- [ ] Efficient memory usage
- [ ] No crashes or freezes

### Edge Cases
- [ ] Empty batch list handling
- [ ] Very large design counts (100+)
- [ ] Special characters in drop names
- [ ] Rapid successive runs
- [ ] Browser refresh during processing

## Beta Timeline

- **Week 1-2:** Initial testing and bug reports
- **Week 3:** Feature refinement based on feedback
- **Week 4:** Performance optimization
- **Week 5+:** Production preparation

## Thank You!

Your feedback is invaluable in making StaticWaves POD Studio better. We appreciate your time and effort in testing this beta version.

## Support

Questions? Need help?
- Check the [Deployment Guide](DEPLOYMENT.md)
- Read the main [README](README.md)
- Open a GitHub issue
- Contact via AI Studio

Happy Testing! 🚀
