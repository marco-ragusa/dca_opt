# Tailwind v4 Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate Tailwind CSS from v3 to v4 using the native Vite plugin, with zero visual changes and no new lock-in.

**Architecture:** Replace the PostCSS-based Tailwind v3 pipeline with `@tailwindcss/vite` (the recommended integration for Vite projects). The CSS custom-property design system in `app.css` is untouched — only the three `@tailwind` directives and tooling config files change. `tailwind.config.js` and `postcss.config.js` are deleted because the v3 config was empty and PostCSS is no longer needed.

**Tech Stack:** Svelte 5, Vite 8, Tailwind CSS v4, `@tailwindcss/vite`

---

### Task 1: Update npm dependencies

**Files:**
- Modify: `ui/package.json`

- [ ] **Step 1: Uninstall old packages**

```bash
cd ui
npm uninstall tailwindcss autoprefixer
```

Expected: `tailwindcss` and `autoprefixer` removed from `package.json` devDependencies.

- [ ] **Step 2: Install new package**

```bash
npm install -D @tailwindcss/vite
```

Expected: `@tailwindcss/vite` appears in `package.json` devDependencies. No `tailwindcss` entry remains.

- [ ] **Step 3: Verify package.json devDependencies**

`package.json` devDependencies should look like:

```json
{
  "@sveltejs/vite-plugin-svelte": "^7.0.0",
  "@tailwindcss/vite": "^4.x.x",
  "@tsconfig/svelte": "^5.0.8",
  "@types/node": "^24.12.2",
  "postcss": "^8.5.x",
  "svelte": "^5.55.4",
  "svelte-check": "^4.4.7",
  "typescript": "~6.0.2",
  "vite": "^8.0.10"
}
```

Note: `postcss` can remain (it's a peer dep of other tools) — just `tailwindcss` and `autoprefixer` must be gone.

---

### Task 2: Wire Tailwind into vite.config.ts

**Files:**
- Modify: `ui/vite.config.ts`

- [ ] **Step 1: Update vite.config.ts**

Replace the entire file content with:

```typescript
import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [svelte(), tailwindcss()],
  server: {
    proxy: {
      '/v1': 'http://localhost:8000',
    },
  },
})
```

---

### Task 3: Delete obsolete config files

**Files:**
- Delete: `ui/postcss.config.js`
- Delete: `ui/tailwind.config.js`

- [ ] **Step 1: Delete postcss.config.js**

```bash
rm ui/postcss.config.js
```

- [ ] **Step 2: Delete tailwind.config.js**

```bash
rm ui/tailwind.config.js
```

Both files are obsolete: PostCSS is no longer needed for Tailwind processing, and the JS config was empty (no custom theme, no plugins to migrate).

---

### Task 4: Update app.css — replace directives and fix Preflight regression

**Files:**
- Modify: `ui/src/app.css` (lines 1–3)

- [ ] **Step 1: Replace @tailwind directives**

In `ui/src/app.css`, replace the first 3 lines:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

With:

```css
@import "tailwindcss";
```

- [ ] **Step 2: Add cursor base override**

Tailwind v4 Preflight changes `<button>` default cursor from `pointer` to `default` (to match browser defaults). Add this immediately after the `@import` line to preserve v3 behavior:

```css
@layer base {
  button:not(:disabled),
  [role="button"]:not(:disabled) {
    cursor: pointer;
  }
}
```

The top of `app.css` should now read:

```css
@import "tailwindcss";

@layer base {
  button:not(:disabled),
  [role="button"]:not(:disabled) {
    cursor: pointer;
  }
}

:root {
  --bg: #f5f4f1;
  /* ... rest of file unchanged ... */
```

---

### Task 5: Verify build and visual correctness

**Files:** none modified

- [ ] **Step 1: Run production build**

```bash
cd ui
npm run build
```

Expected: build completes with `✓ built in ...ms`, **zero warnings**.

- [ ] **Step 2: Run type check**

```bash
npm run check
```

Expected: no errors.

- [ ] **Step 3: Run dev server and inspect visually**

```bash
npm run dev
```

Open `http://localhost:5173` and verify:

1. Light mode renders correctly (background `#f5f4f1`, teal accents)
2. Toggle dark mode — dark mode renders correctly (`html.dark` class applied)
3. Buttons have `cursor: pointer` on hover
4. No layout regressions across breakpoints (resize to < 480px)
5. No console errors

- [ ] **Step 4: Commit**

```bash
cd ..
git add ui/src/app.css ui/vite.config.ts ui/package.json ui/package-lock.json
git commit -m "Migrate Tailwind CSS from v3 to v4 via Vite plugin"
```
