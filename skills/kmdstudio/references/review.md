# Review and correction records

1. Freeze the source facts, reading order, code, data and acceptance criteria. Generate to a new path and run the content, structural, editability and security gates. A mandatory failure blocks delivery.
2. Use an authorized renderer to inspect every page and zoom into the parts that carry the most information. Identify the first thing a reader needs, what should stay together, and which space serves a break in the reading sequence. Record actual application, preview, or markup evidence for each issue.
3. Record a stable ID and page or block for each issue. Use `fidelity`, `structure`, `security`, `editability`, `accessibility`, `layout` for deterministic or application evidence. Use `visual` for visible defects and `art-direction` for preferences. The latter can be accepted as an observation with an explicit reason.
4. Save the brief and DOCX for each pass. Describe the change and how it addresses the finding. Link its resolution to a subsequent stage with an observed result. If the render is unavailable, record that state and keep the visual finding open. Inspect all changed pages and check adjacent pages for reflow. End at three correction stages plus the initial stage.
5. Deliver after the mandatory gates pass. Keep validated source changes explicit and compare the deliverable against the frozen source. Distinguish Word's structure and accessibility checker results from actual keyboard or screen-reader use. A serial sequence of label, value and related paragraph is available when a layout row interferes with access.

The [record schema](../schemas/quality.schema.json) uses relative paths and SHA-256 for the brief and DOCX at each stage. Number stages from 0. For layout-only revisions, use `scope: layout-only` to verify exact native text order, figure descriptions and image bytes across stages. `source-correction` permits text changes and requires a separate comparison against the source. Mark `outcome` as `pass`, `partial` or `blocked`. `pass` requires a recorded final inspection. The checker verifies evidence references, native text and record consistency. It cannot attest to human authorship, independent review, visual quality or performance of the other mandatory gates.

```text
python -E -s -B scripts/review_quality.py --root ABSOLUTE_WORKSPACE --record RELATIVE_RECORD.json
```

## Human review rubric

Report defects separately from preferences. For each applicable row, use 1 when the problem obstructs the reading task, 2 when the task can be completed with noticeable friction, and 3 when the intended task is clear and easy. Point to a page or block and describe the evidence. `N/A` is valid. Keep brief identity and revision labels hidden when comparing candidates.

| Review areas | What a 3 looks like |
| --- | --- |
| Shared fidelity, accessibility and editing | Required facts, units, code and assets remain available in reading order. Native semantics support navigation. Run safety and fidelity as mandatory gates independent of the rubric. |
| Structured readability and navigation | A reader locates a decision, follows a procedure, or checks a data row with predictable labels and structure. |
| Creative hierarchy and rhythm | A reader sees the intended entry point, follows the main sequence and understands why scale, images and gaps change. Detail type and primary imagery remain usable. |
| Hybrid coherence and technical precision | Editorial cues help readers transition into the exact source material. Code, tables and diagrams remain legible, consistent and reusable. |

Record preferences and their rationale separately. XML, page counts and pixel measurements can supply evidence about specific properties. Professional design acceptance requires human judgment.
