---
name: collision-scene-diagram
summary: Create a clean, editable, evidence-aware top-down sketch of a vehicle collision for review or reporting.
description: Use this skill when someone provides a vehicle-collision narrative, photos or video and wants a simple, labelled diagram. Separate observations from uncertainties; never invent vehicle positions, door motion, contact points or fault percentages. Export an SVG, plus an accessible text description.
---

# Collision Scene Diagram

## Purpose
Turn an often confusing collision account into a **clear, minimalist, top-down diagram**: vehicle boxes, FRONT/REAR labels, parking boundaries, door state, movement arrows, and a prominent **Not to scale** disclaimer. The output is a visual aid, **not** a forensic reconstruction, official police form, or fault decision.

## Workflow
1. **Inventory sources**: identify what came from firsthand recollection, photographs, dashcam footage, the other driver's account, and later observations. Mark disagreement or missing information rather than reconciling by guesswork.
2. **Extract the minimum scene data**: car A/car B labels; relative positions; front/rear orientation; parking lines or lanes; movement directions; any door/object that matters; approximate contact area *only if observable*.
3. **Separate observations from inferences**. “Door appears open in footage before approach” does **not** prove “door never moved” or “door caused the collision.” “Speed readout became 0” does **not** prove when the driver braked.
4. **Ask one clarification only when an essential orientation is missing**. Otherwise use visibly approximate geometry and label it “illustrative.” Never silently choose lane count, door swing angle, timestamps, or point of impact.
5. **Make a simple scene JSON** following `examples/fictional_parking_lot.json`. Replace all real people, plate numbers, policy IDs, phone numbers and street addresses with A/B labels when preparing anything for publication.
6. **Render** with `python scripts/render_diagram.py scene.json -o collision_sketch.svg`. Open the SVG to verify label legibility, arrows, orientation and consistency with the source. SVG is editable and scalable.
7. **Offer a low-bandwidth fallback**: brief plain-text directions for drawing two rectangles, door line and arrow on an official form if a phone fails to display the image. Never provide a broken link as the only option.
8. **Describe precisely** what is established, what is approximate, and what remains unknown. Provide a neutral one-paragraph description if requested; do not write a statement that overclaims video evidence.
9. **Protect privacy**: raw footage, personal contacts, driver licence numbers, insurance IDs and actual case sketches stay private. For demos, use fabricated examples only.

## Required visual conventions
- A and B are neutral identifiers; neither means at fault.
- Vehicle orientation is explicit (FRONT / REAR).
- Lines/arrows denote *reported* movement, not necessarily collision speed or exact trajectory.
- An open door is drawn as one line at an **illustrative** angle; only show if supported by evidence.
- Include **Not to scale — approximate positions** and an uncertainty note if appropriate.
- Use black-and-white, thick lines, short English labels, enough whitespace for printing on paper.
- **Do not** add fault percentages, admissions of liability, legal conclusions or speculative mechanical failures.

## Scene format
JSON keys accepted by the renderer:
- `canvas_width`, `canvas_height`: integer canvas size, minimum 500 each.
- `title`, `area_label`: plain text.
- `parking_spaces`: array of objects with `rect: [x,y,width,height]`.
- `vehicles`: 1–8 objects with `id`, `label`, `state`, `front` (`top|bottom|left|right`), `rect`; optionally `door` with `side`, `at` (relative position 0–1), `tip` ([x,y]), `label`.
- `arrows`: objects with `from: [x,y]`, `to: [x,y]`, `label`.
- `notes`: up to two uncertainty labels.

All measurements are diagram coordinates, **not measured road distances**. Avoid using coordinates presented as exact when unverified.

## Quick use
```bash
python scripts/render_diagram.py examples/fictional_parking_lot.json \
  -o examples/fictional_parking_lot.svg
python -m unittest discover -s tests -v
```

## What this skill does NOT do
It cannot establish liability, replace an insurance adjuster or police report, extract exact distance from a single camera view, prove door movement from camera parallax, or certify footage authenticity. If evidence is contradictory, keep the contradiction visible and ask for the missing perspective.