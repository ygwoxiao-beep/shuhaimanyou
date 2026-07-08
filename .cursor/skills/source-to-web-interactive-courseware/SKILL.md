---
name: source-to-web-interactive-courseware
description: Convert PPT, PDF, lesson notes, images, and other source teaching files into standalone web-based interactive courseware. Use when the user wants HTML courseware, browser-playable lessons, interactive teaching pages, cloud-deployable lesson sites, or a reusable web lesson instead of a SCORM package.
disable-model-invocation: true
---

# Source To Web Interactive Courseware

## Goal

Turn source teaching material into a browser-first interactive lesson with better pacing, feedback, and reuse than a direct slide export.

## Default Output

Unless the user specifies a framework, default to a static web app:

```text
course-name/
├── index.html
├── data/
│   ├── lesson.json
│   └── questions.json
├── assets/
│   ├── pages/
│   ├── audio/
│   └── videos/
└── analysis/
```

Keep the shell reusable. Put lesson-specific content in data files.

## Workflow

### 1. Understand the source

Extract:

- lesson structure
- teacher intent
- key visuals
- candidate interaction moments
- media dependencies

If the source is a PPT or PDF, do not assume one source page equals one web page.

### 2. Redesign for the browser

Map the source into browser-native steps:

- cover / intro
- concept explanation
- guided interaction
- practice rounds
- recap / result page

Reduce passive reading. Favor shorter steps with immediate response.

### 3. Choose interaction density

State one of:

- `presentation-first`
- `balanced interactive`
- `high-energy interactive`

Default to `balanced interactive`.

### 4. Use a data-driven course model

Prefer:

- `lesson.json` for metadata, flow, sections, scoring, badges, report config
- `questions.json` for prompt-level interaction config

This makes later lesson cloning fast and keeps page logic reusable.

### 5. Reuse a small set of interaction primitives

Default building blocks:

- click choice
- click hotspot
- drag to slot
- grid fill
- sequence path
- number input
- multi-round challenge

Only invent a new interaction when existing primitives cannot express the learning goal.

### 6. Make feedback feel alive

The browser lesson should feel better than source slides. Add:

- success animation
- failure animation
- success/failure sound
- automatic next-step or retry rules when appropriate

Do not add effects randomly. Tie feedback to learning actions.

### 7. Treat media as delivery strategy

Default:

- images local
- lightweight audio local or generated
- large video via stable external URL when appropriate

If using remote video, ensure it is directly playable and not forced to download.

### 8. Validate in the actual delivery mode

If the lesson loads JSON with `fetch()`, do not test via `file://`.

Preview via local HTTP:

```bash
python3 -m http.server 8899
```

Then open:

```text
http://localhost:8899/index.html
```

If the user deploys to cloud static hosting, verify:

- asset paths
- remote media playback
- mobile layout
- no console errors

## Quality Gates

- [ ] page works over HTTP without build tooling
- [ ] lesson structure is clearer than the source deck
- [ ] large visuals use most of the viewport
- [ ] navigation is compact and user-controllable
- [ ] interactions give visible and audible feedback
- [ ] retry loops are fast and understandable
- [ ] content is separated from rendering
- [ ] deployment does not rely on local file access

## UI Heuristics

Prefer these patterns unless the user asks otherwise:

- narrow side navigation, wide main teaching area
- one dominant teaching task per screen
- large buttons and touch-friendly targets
- concise prompts above the interaction zone
- automatic next step after successful completion when it improves pacing

## Deployment Notes

For cloud deployment, this output should work on any static host such as:

- Tencent Cloud static hosting / CVM nginx
- Vercel
- Netlify
- GitHub Pages

Check remote resource access after deployment, especially for CDN-hosted video.

## Common Failure Modes

- shipping a browser lesson that still behaves like a slideshow
- tightly coupling course content to the page markup
- using oversized sidebars that steal space from the learning task
- adding interaction without strong success/failure feedback
- assuming local preview behavior matches cloud hosting

## Response Pattern

When using this skill:

1. summarize the source and lesson goal
2. propose the browser interaction model
3. define the data structure
4. implement the reusable lesson shell
5. validate local preview and deployment readiness
