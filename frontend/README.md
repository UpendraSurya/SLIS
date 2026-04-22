# Handoff: SLIS Frontend — Teacher & Student Portals

## Overview
Full frontend for the **Student Learning Intelligence System (SLIS)** — an AI-powered academic analytics platform. Two portals: a Teacher Portal for cohort-level analytics and a Student Portal for personal performance tracking. Connects to a FastAPI backend at `http://127.0.0.1:8000`.

## About the Design Files
The files in this bundle (`ui_kits/teacher/`, `ui_kits/student/`) are **high-fidelity HTML prototypes** — they show the intended look, layout, and interactive behavior. Your task is to **recreate these designs** in your production environment. The HTML/JSX files use React + Babel via CDN (no build step) — perfect as a reference, but you should port them to your preferred production stack (e.g. React + Vite, Next.js, etc.) using your codebase's existing patterns.

## Fidelity
**High-fidelity.** These are pixel-close mockups with final colors, typography, spacing, border radii, and interactions. Recreate them faithfully using the design tokens in `colors_and_type.css`.

---

## Design Language
- **Aesthetic:** Linear.app / Vercel dashboard — dark mode, monochromatic, single accent color
- **Colors:** See `colors_and_type.css` for all CSS variables
- **Type:** Space Grotesk (headings) + IBM Plex Sans (body) + IBM Plex Mono (data/IDs)
- **Radii:** Cards `12px`, inputs `8px`, buttons `8px`, badges `20px` (pill), sidebar nav items `8px`
- **Background:** `#080808` with two radial blue glows + fixed SVG geometric layer (concentric rings, rotated rects, crosshairs, triangles)
- **Sidebar:** `rgba(17,17,17,0.85)` with `backdrop-filter: blur(12px)`

---

## Screens / Views

### 1. Login Page (shared entry point)
**Layout:** Full-viewport flex row. Left panel (flex:1) + Right panel (420px fixed).

**Left Panel:**
- Background: `rgba(17,17,17,0.5)`, right border `1px solid #2a2a2a`
- Fixed SVG background with concentric rings, rotated rectangles, crosshairs at very low opacity (~0.05–0.09)
- Top: SLIS wordmark (`Space Grotesk 36px/700`, `letter-spacing: -0.04em`) + tagline (`14px`, `color: #888`)
- Bottom: 3 stat numbers (`Space Grotesk 28px/700`) with mono labels below

**Right Panel:**
- Heading: `Space Grotesk 22px/700`
- Role toggle: 2-button flex row, `border-radius: 8px` overflow hidden. Active = `#4F7FFF` bg, inactive = `#1a1a1a`
- Inputs: `background: #1a1a1a`, `border: 1px solid #3a3a3a`, `border-radius: 8px`, `padding: 9px 14px`, focus ring `box-shadow: 0 0 0 3px rgba(79,127,255,0.12)`
- Submit button: full width, `background: #4F7FFF`, `border-radius: 8px`, `padding: 10px 16px`
- Hint box: `background: #1a1a1a`, `border-radius: 8px`, mono 11px

**Credentials (mock):**
- Teacher: username `teacher`, password `slis2024`
- Student: any ID `STU0001`–`STU0500`

---

### 2. App Shell (Teacher Portal)
**Layout:** Flex row. Sidebar (228px) + Main content area (flex:1, overflow-y: auto).

**Sidebar (`rgba(17,17,17,0.85)`, `backdrop-filter: blur(12px)`):**
- Logo area: `padding: 20px 18px`, bottom border
- Section label: mono 10px, uppercase, `#555`, `padding: 16px 18px 6px`
- Nav items: `height: 38px`, `padding: 0 12px`, `margin: 2px 8px`, `border-radius: 8px`
  - Default: `color: #888`
  - Hover: `background: #1a1a1a`, `color: #f0f0f0`
  - Active: `background: linear-gradient(135deg, rgba(79,127,255,0.18), rgba(79,127,255,0.08))`, `border: 1px solid rgba(79,127,255,0.2)`
- Footer: avatar circle (30px, `border-radius: 50%`), name + role, logout icon button

**Topbar:** `height: 52px`, `background: rgba(8,8,8,0.7)`, `backdrop-filter: blur(8px)`, bottom border. Title + separator + breadcrumb (mono).

**Page body:** `padding: 28px 32px`

---

### 3. Dashboard Page
**Stat grid:** 4 columns, `gap: 14px`, `margin-bottom: 28px`
- Stat card: `background: #111`, `border: 1px solid #2a2a2a`, `border-radius: 12px`, `padding: 20px 22px`
- Label: mono 10px uppercase `#555`; Value: `Space Grotesk 32px/700`; Sub: 11px `#555`
- High risk card gets `border-color: #FF4444`

**Two-column section:** `gap: 18px`
- Risk Distribution: horizontal bars per level (Low/Med/High) with color-coded fills, `border-radius: 20px` bars, 5px height
- Model Metrics: nested metric cards (`background: #1a1a1a`, `border-radius: 8px`) showing CV F1, accuracy, RMSE, R²
- Subject Averages: horizontal bar chart, `border-radius: 8px` bars, 14px height
- Top Performers: table with click-through to profile

---

### 4. Student Directory Page
**Search row:** search input (flex:1, max 320px) + risk filter select (160px), `gap: 8px`
- Search has inline SVG magnifier icon (position: absolute, left: 10px)

**Table:** `border: 1px solid #2a2a2a`, `border-radius: 12px`, overflow hidden
- Columns: Student ID (mono) | Name | Major | Avg Score (mono) | Attendance (mono) | GPA (mono) | Risk (badge)
- Zebra rows: even rows `rgba(255,255,255,0.015)`
- Row hover: `background: #1a1a1a`, cursor pointer → navigate to profile

**Pagination bar:** `border-top: 1px solid #2a2a2a`, prev/next buttons (secondary style), page counter (mono), total count right-aligned

**API:** `GET /api/students?page=N&limit=15&risk_filter=X&search=Y`

---

### 5. Student Profile Page
**Back button** row with student ID (mono) and risk badge.

**Two-column grid:** 300px left + flex right, `gap: 18px`

**Left column cards** (`background: #111`, `border-radius: 12px`, `padding: 22px`):
1. Identity card: name (`Space Grotesk 22px/700`), ID + major + age (mono), divider, then key-value rows (`border-bottom: 1px solid #2a2a2a` each)
2. Risk confidence card: 3 horizontal bars (Low/Med/High probabilities), color-coded
3. LMS Activity card: key-value rows for logins/week, forum posts, resources, session minutes

**Right column:**
1. Subject scores table: Subject | IT1 | IT2 | Final | Weighted — weighted column in accent text color
2. AI Recommendations section: lazy-loaded via "Load" button, then renders rec cards

**API:** `GET /api/students/{id}` + `GET /api/recommendations/{id}`

---

### 6. Custom Prediction Page
**2-column form grid** (max-width 600px), `gap: 16px`:
- Fields: avg_attendance (0–100), engagement_score, gpa_start (1.0–4.0), lms_logins_per_week, forum_posts
- Each field: mono label (uppercase 11px) + input + hint text (11px `#555`)
- Submit button: primary style, `margin-top: 20px`

**Result panel** (appears after submit): `background: #111`, `border-radius: 12px`, `padding: 22px`
- Risk level badge + predicted score (`Space Grotesk 28px`, accent text color)
- Probability bars for each risk level

**API:** `POST /api/predict` with JSON body

---

### 7. Student Portal — My Dashboard
**Risk hero banner:** `background: #111`, `border-radius: 14px`, `padding: 26px 28px`, flex row
- Risk badge + confidence mini-bars | separator | predicted score (52px display) | separator | attendance | separator | avg score
- Separators: `width: 1px; height: 60px; background: #2a2a2a`

**Two-column below:** Attendance by Month (bar per month, color by ≥85%/≥70%/<70%) + LMS Activity (key-value rows, green/amber color coding by threshold)

---

### 8. Student Portal — My Recommendations
Cards sorted High → Medium → Low priority.
- Card: `background: #111`, `border-radius: 12px`, `border-left: 3px solid <risk color>`, `padding: 16px 18px`
- Header row: title (`Space Grotesk 14px/600`) + priority badge (right-aligned)
- Body: description text (`#888`, 13px, `line-height: 1.55`)

---

### 9. Student Portal — My Performance
**Score table:** Subject | IT1 | IT2 | Final | Weighted | Trend
- Trend: ↑ Improving (green) / ↓ Declining (red) / → Stable (grey)

**Score comparison bars:** per subject, 3 stacked bars (IT1 grey, IT2 accent blue, Final green), 6px height pill tracks, label + value beside each

---

## Design Tokens

```css
/* Backgrounds */
--bg-base:       #080808;
--bg-surface:    #111111;
--bg-elevated:   #1a1a1a;
--bg-overlay:    #222222;

/* Borders */
--border:        #2a2a2a;
--border-strong: #3a3a3a;
--border-focus:  #4F7FFF;

/* Text */
--fg-1: #f0f0f0;   /* primary */
--fg-2: #888888;   /* secondary */
--fg-3: #555555;   /* muted */

/* Accent */
--accent:      #4F7FFF;
--accent-hover:#6B95FF;
--accent-dim:  #1a2d5a;
--accent-text: #8FB3FF;

/* Risk */
--risk-high:    #FF4444;  --risk-high-dim: #3a1010;
--risk-med:     #FF9900;  --risk-med-dim:  #3a2500;
--risk-low:     #22C55E;  --risk-low-dim:  #0d2e1a;

/* Typography */
--font-display: 'Space Grotesk', sans-serif;
--font-body:    'IBM Plex Sans', sans-serif;
--font-mono:    'IBM Plex Mono', monospace;
```

---

## API Endpoints

| Method | Endpoint | Used in |
|---|---|---|
| GET | `/api/students?page&limit&risk_filter&search` | Student Directory |
| GET | `/api/students/{id}` | Student Profile, Student Dashboard |
| POST | `/api/predict` | Custom Prediction |
| GET | `/api/dashboard/stats` | Teacher Dashboard |
| GET | `/api/model-metrics` | Teacher Dashboard |
| GET | `/api/recommendations/{id}` | Profile Recs, Student Recs page |
| GET | `/health` | Optional health check |

All endpoints are on `http://127.0.0.1:8000`. CORS is already enabled in the FastAPI backend.

---

## Interactions & Behavior

- **Table rows** → click navigates to student profile view
- **Sidebar nav** → instant page switch (single-page app, no full reload)
- **Risk bars** → animate width on mount (`transition: width 400ms ease`)
- **Inputs** → focus ring via `box-shadow: 0 0 0 3px rgba(79,127,255,0.12)`
- **Buttons** → `transform: scale(0.98)` on `:active`
- **Hover states** → `background` transition `120ms ease` only, no color changes
- **API errors** → fall back to mock data silently, no crash
- **Loading states** → mono text "Loading…" with `padding: 48px`
- **Recommendations** → lazy-loaded on demand (click Load button in profile)
- **Pagination** → prev/next buttons disabled at boundaries

---

## Files in This Package

```
design_handoff_slis/
├── README.md                        ← this file
├── colors_and_type.css              ← all design tokens + base component CSS
├── ui_kits/
│   ├── teacher/
│   │   ├── index.html               ← Teacher Portal shell + all CSS
│   │   └── TeacherApp.jsx           ← all React components (Login, Dashboard, Students, Profile, Predict)
│   └── student/
│       ├── index.html               ← Student Portal shell + all CSS
│       └── StudentApp.jsx           ← all React components (Login, Dashboard, Recs, Performance)
```

Open `ui_kits/teacher/index.html` directly in a browser to interact with the live prototype against your running FastAPI server.

---

## Notes for Claude Code

- The `.jsx` files use React 18 + Babel standalone (CDN). Port to your build system.
- Mock data is defined at the top of each `.jsx` file — remove once your API is confirmed working.
- `apiFetch(path, fallback)` is a helper that calls the API and falls back to mock on failure — keep this pattern for resilience.
- No auth backend exists — the mock credential check (`teacher`/`slis2024`) is frontend-only. Add real auth when ready.
- Student ID format: `STU` + 4 zero-padded digits (e.g. `STU0001`).
