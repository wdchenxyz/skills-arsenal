---
name: schoger-ui-craft
description: Steve Schoger's actionable UI craft techniques for polishing Tailwind CSS landing pages and marketing sites. Apply when building or refining hero sections, feature cards, navbars, buttons, testimonials, logo clouds, or any marketing/landing page UI with Tailwind. Triggers on "make this look less like a template", "polish this landing page", "refine this marketing site", "Schoger techniques", or when UI has muddy borders, generic layout, or template-like appearance.
---

# Schoger UI Craft

18 specific techniques for elevating Tailwind CSS landing pages from template-quality to designer-quality. Based on Steve Schoger's (Refactoring UI) approach.

## Borders & Shadows

### 1. Outer ring, not solid border

When an element has a shadow, **never** combine it with a solid `border`. The shadow-border junction looks muddy. Replace with an outer ring:

```html
<!-- Bad: muddy shadow-border junction -->
<div class="border border-gray-200 shadow-lg">
  <!-- Good: crisp edge with ring -->
  <div class="shadow-lg ring-1 ring-gray-950/10"></div>
</div>
```

Apply to: screenshot containers, buttons, navbar, feature cards — any element with `shadow`.

### 2. Concentric border-radius

When a rounded container holds a rounded child, the inner radius must equal outer radius minus padding. Otherwise the curves fight.

```html
<!-- outer: rounded-2xl (16px), padding: p-4 (16px) → inner: rounded-xl (12px) -->
<div class="rounded-2xl p-4">
  <img class="rounded-xl" />
</div>
```

Formula: `inner-radius = outer-radius - padding`. Same radius on both layers looks wrong when spacing is tight.

### 3. Inset ring for edge definition

On light-background containers, use an inset ring at low opacity instead of a border. More subtle, doesn't steal focus from content.

```html
<div class="bg-white ring-1 ring-inset ring-gray-950/5"></div>
```

## Typography

### 4. Inter variable (display version)

Use Inter from [rsms.me](https://rsms.me/inter/), not Google Fonts. Variable font enables intermediate weights like `font-[550]` (between medium 500 and semibold 600). Disable stylistic set `ss02` (tailed lowercase L variant — looks odd in some contexts).

### 5. Tighten tracking on large text

At 24px+, default letter-spacing looks too loose. Tighten it:

```html
<h1 class="text-4xl tracking-tight">
  <h2 class="text-2xl tracking-tight"></h2>
</h1>
```

Larger text = more visible letter gaps. `tracking-tight` or tighter gives headlines more impact.

### 6. Eyebrow text formula

Section eyebrow labels (e.g., "Everything you need", "Get started") — fixed recipe:

```html
<span class="font-mono text-xs uppercase tracking-wider text-gray-600">
  Everything you need
</span>
```

Use Geist Mono or any monospace font. The monospace + uppercase + wide tracking combination reads as technical and refined.

### 7. text-pretty vs text-balance

- `text-pretty` — prevents orphan words (single word on last line)
- `text-balance` — distributes text evenly across lines

Different effects. Test both on each text block and pick whichever reads better.

### 8. Double line-height on small text

For `text-sm` (14px) body copy / subtitles, set line-height to 28px (2x font size):

```html
<p class="text-sm leading-7"></p>
```

Sounds extreme but gives breathing room to secondary text. Improves readability significantly.

## Layout

### 9. Left-align, don't center everything

AI-generated pages default to centered everything. Break this immediately. Use a split layout for hero sections:

```html
<div class="flex items-start gap-16">
  <div class="w-3/5"><!-- Headline --></div>
  <div class="w-2/5"><!-- Subtitle + description --></div>
</div>
```

Left-aligned, top-aligned split headline (inspired by Tailwind Plus) — more editorial, easier to read.

### 10. Inline section headings

Don't stack title + subtitle on separate lines. Put them inline with color/weight differentiation:

```html
<p>
  <span class="font-bold text-gray-950">Feature title</span>
  <span class="font-medium text-gray-600">
    followed by a longer subtitle that explains the feature in more detail.
  </span>
</p>
```

Inspired by Apple, Linear, Stripe. Needs a longer subtitle to work well.

### 11. Max-width in ch units

Control text block width with `ch` (width of the `0` character), not fixed pixels:

```html
<p class="max-w-[40ch]"></p>
```

~40 characters wide. Stays comfortable regardless of font size. Test values between 35-50ch.

## Element Design

### 12. Button height and shape

- Height: 36-38px via padding (not fixed `h-*`)
- Shape: fully rounded (pill)
- Font: `text-sm` (14px)
- Remove default icons — keep it clean

```html
<button class="rounded-full px-4 py-2 text-sm font-medium"></button>
```

### 13. Fix 2px height mismatch between ring/no-ring buttons

A button with `ring` renders 2px taller than one without. Fix (by Adam Wathan):

```html
<span class="inline-flex p-px">
  <button
    class="rounded-full ring-1 ring-gray-950/10 px-4 py-[calc(0.5rem-1px)] text-sm"
  >
    Secondary
  </button>
</span>
```

Wrap the ring button in `inline-flex p-px` span. Use `calc` to subtract the pixel from padding.

### 14. Recessed screenshot container

Feature section screenshot containers — subtle recessed look:

```html
<div class="rounded-2xl bg-gray-950/[0.025] ring-1 ring-inset ring-gray-950/5">
  <img class="rounded-t-xl" />
  <!-- no bottom radius, no bottom padding -->
</div>
```

- Background: `gray-950` at 2.5-5% opacity
- No border, use inset ring
- Screenshot sits at container bottom (zero bottom padding, no bottom border-radius)

### 15. Use high-res app screenshots

No custom illustrations? A 3x resolution screenshot of your app is the easiest way to add visual weight. Ensure crisp rendering on high-DPI screens.

## Decorative Details

### 16. Canvas grid (decorative border lines)

Add decorative line borders between sections. Horizontal lines span full viewport width; vertical lines stay within page container. Creates a refined grid framework.

Inspired by Stripe, Tailwind, and Adio. Instantly removes "template feel" without custom graphics.

### 17. Background-image testimonial cards

Skip the standard avatar + quote layout. Use AI-generated portrait photos as card backgrounds with a dark gradient overlay at the bottom:

```html
<div class="relative overflow-hidden rounded-2xl">
  <img src="portrait.jpg" class="absolute inset-0 h-full w-full object-cover" />
  <div
    class="relative bg-gradient-to-t from-gray-950/80 to-transparent p-8 pt-48"
  >
    <p class="text-white">"Quote text here"</p>
  </div>
</div>
```

More visual impact than circular avatars.

### 18. Logo cloud — keep it simple

- No section title needed — logos are self-explanatory
- Use real SVG logos, not text placeholders
- Color: `gray-950` (no opacity tricks)
- Fill the container width evenly
- Don't over-design this section
