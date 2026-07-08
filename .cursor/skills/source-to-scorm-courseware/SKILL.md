---
name: source-to-scorm-courseware
description: Convert PPT, PDF, lesson notes, images, and other teaching materials into SCORM 1.2 or SCORM 2004 courseware packages. Use when the user asks to turn source teaching files into LMS-uploadable courseware, preserve teaching flow, add interactions, package imsmanifest metadata, or adapt a web course into SCORM format.
disable-model-invocation: true
---

# Source To SCORM Courseware

## Goal

Turn source teaching material into a SCORM-ready package that can be uploaded to an LMS and still feel like a modern interactive web lesson rather than a static slide deck.

## Default Output

Unless the user says otherwise, structure the result like this:

```text
course-name/
├── index.html
├── scorm-api.js
├── imsmanifest.xml
├── data/
│   ├── lesson.json
│   └── questions.json
├── assets/
│   ├── pages/
│   ├── audio/
│   └── videos/
└── analysis/
```

Use `lesson.json` for course flow and global metadata. Use `questions.json` for interaction definitions.

## Workflow

### 1. Analyze the source

Identify:

- course title, audience, lesson objective
- page/slide order
- media assets: images, videos, audio
- points that should become interactions instead of passive reading
- whether the final output must be SCORM `1.2` or `2004`

If the source is mostly static, do not blindly preserve every slide as-is. Convert slides into learning steps.

### 2. Choose the conversion mode

Pick one of these and state it before implementation:

- `light conversion`: mostly page display, minimal interactions
- `interactive conversion`: multiple question types, progress, scoring, feedback
- `game-like conversion`: stronger animation, sound, rewards, replay loops

Default to `interactive conversion`.

### 3. Separate content from rendering

Do not hardcode all lesson content directly into `index.html`.

Prefer:

- `lesson.json`: title, sections, flow, cover, scoring rules, report config
- `questions.json`: per-step interaction config, correct answers, feedback copy

This keeps the course maintainable and lets later lessons reuse the same shell.

### 4. Build the web lesson first

SCORM is a wrapper around a web course. First ensure the web lesson works well on its own:

- responsive layout
- readable content density
- click/drag/input interactions
- success/failure feedback
- progress display
- final report or completion state

Do not treat SCORM packaging as a substitute for product quality.

### 5. Add SCORM runtime integration

Implement a thin runtime layer that:

- detects `API_1484_11` for SCORM 2004
- detects `API` for SCORM 1.2
- falls back to `localStorage` for local preview
- saves location, score, completion, success status, progress measure, suspend data

Local preview should work without an LMS.

### 6. Create `imsmanifest.xml`

Ensure:

- correct schema and edition
- one launchable SCO unless the user explicitly needs multiple SCOs
- `href` points to `index.html`
- file entries match the packaged local assets

If a video uses an external URL for direct playback, do not list it as a local packaged file.

### 7. Handle media intentionally

Default rules:

- images: package locally
- small audio effects: package locally if used often
- large videos: prefer external CDN links when the LMS and network environment allow it

For external media, explicitly check:

- hotlink restrictions
- CORS behavior
- LMS environment network access

### 8. Validate preview correctly

Never validate with `file://index.html` if the lesson uses `fetch()` for JSON.

Always preview over HTTP, for example:

```bash
python3 -m http.server 8899
```

Then open:

```text
http://localhost:8899/index.html
```

### 9. Package for delivery

Before packaging:

- preview flow end to end
- verify every referenced local file exists
- verify progress and score persistence
- verify the last step reaches completed status

When the user needs LMS delivery, zip the package with `imsmanifest.xml` at the root.

## Quality Gates

Before considering the work done, verify:

- [ ] the lesson can run locally over HTTP
- [ ] the lesson still works when SCORM API is absent
- [ ] content is data-driven, not only hardcoded in HTML
- [ ] interactions match the teaching objective, not just decoration
- [ ] external media links are playable without forced download
- [ ] `imsmanifest.xml` matches actual packaged assets
- [ ] mobile and narrow-width layout remain usable
- [ ] completion, score, and suspend data are saved

## Interaction Guidance

Prefer interaction types that map naturally from source material:

- visual spotting -> click targets / overlay hotspots
- pattern completion -> drag to slots / grid fill
- arithmetic reasoning -> input / multiple choice
- ordered process -> step path / sequence challenge
- recap -> multi-round mixed challenge

Use richer feedback when the lesson is exploratory or game-like:

- correct: visible celebration + positive sound
- wrong: clear retry feedback + automatic reset if appropriate

## Common Failure Modes

- trying to preview with `file://` and assuming data is broken
- packing remote video paths into manifest as if they were local files
- converting every slide literally instead of redesigning for interaction
- hardcoding lesson data into the page shell
- forgetting LMS completion fields even though UI progress looks correct

## Response Pattern

When asked to do this work, answer in this order:

1. state the chosen conversion mode
2. summarize the source breakdown
3. outline the interaction plan
4. implement the web lesson
5. add SCORM packaging and validation
