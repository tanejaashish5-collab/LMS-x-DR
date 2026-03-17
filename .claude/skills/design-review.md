---
name: design-review
description: Visual design review using Playwright for UI/UX and accessibility
---

# Design Review Workflow
# Inspired by OneRedOak/claude-code-workflows

## When to Use
- After building or modifying UI components
- Before merging frontend PRs
- When reviewing responsive layouts
- For accessibility compliance checks

## Review Process

### Step 1: Capture Screenshots
Use Playwright to capture the UI at multiple viewport sizes:
- Mobile (375px)
- Tablet (768px)
- Desktop (1280px)
- Wide (1920px)

### Step 2: Visual Checklist

#### Layout & Spacing
- [ ] Consistent spacing between elements
- [ ] Proper alignment (grid-based)
- [ ] No overlapping elements
- [ ] Responsive breakpoints work correctly
- [ ] No horizontal scrolling on mobile

#### Typography
- [ ] Hierarchy is clear (H1 > H2 > H3)
- [ ] Font sizes are readable (min 14px body)
- [ ] Line height is comfortable (1.4-1.6)
- [ ] Contrast ratio meets WCAG AA (4.5:1 for text)

#### Color & Contrast
- [ ] Color palette is consistent
- [ ] Interactive elements are visually distinct
- [ ] Error states use red/warning colors
- [ ] Success states use green/confirmation colors
- [ ] Dark mode support (if applicable)

#### Interaction
- [ ] Buttons have hover/active states
- [ ] Focus indicators are visible (keyboard nav)
- [ ] Loading states exist for async operations
- [ ] Empty states are handled gracefully
- [ ] Error states show helpful messages

#### Accessibility (WCAG 2.1 AA)
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] ARIA roles on dynamic content
- [ ] Tab order is logical
- [ ] Screen reader compatible

### Step 3: Performance Check
- [ ] Images are optimized (WebP, lazy loading)
- [ ] No layout shifts (CLS < 0.1)
- [ ] First paint < 1.5s
- [ ] Interactive < 3.5s

### Step 4: Report
Output findings with screenshots and specific recommendations.
