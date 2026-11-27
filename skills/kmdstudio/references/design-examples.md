# Design choices in practice

Select a relevant row and adjust its controls to the material. These studies use fictional sources and native brief options. Each fragment illustrates one decision in a larger brief.

| Purpose and constraint | Weak choice | Improved choice and reader benefit | Cards and evidence |
| --- | --- | --- | --- |
| A route report must preserve the evidence and next action | Lead with several equally weighted panels and treat totals as another bar. | Make the title or subject image dominant. Then compare same-unit route values on a shared scale, set the total in type and give the action a simple heading. | D01, D06, D08, D15. The `routes` fragment leaves the total outside the graphic. Check arithmetic and anonymized openings. |
| A booking confirmation needs short dates alongside longer terms | Give the two regions equal space and fill the remainder with decoration. | Use a compact left rail, wider terms and a deliberately quiet lower page. Readers find the reference first and follow it to the action. | D02, D07, D11. The `booking` fragment expresses the asymmetry. Check intended reading order and one-page fit. |
| An exhibition guide asks readers to compare a break in a contour | Use generic banners and equal panels on each page. | Use a wide image-led entry, one isolated detail and equally sized comparison prints with matched captions. A shared axis links these differing roles. | D03, D05, D12, D13. Use `cover.illustration` with `image_position: before-title` and consecutive equal-width `figure` blocks. Inspect focal scale and the actual crops. |
| A Cyrillic lesson needs readable explanation and exact Python | Use one generic large font and put the trace in a picture. | Use distinct display, body and code roles. Keep a worked trace, listing and exercise in native blocks. | D04, D09, D10, D14. Use the `update` fragment near the trace and retain exact editable code. Check actual fonts, copy the code and verify the result. |

```json
{"id":"routes","kind":"table","headers":["Route","Sites"],"rows":[["East","6"],["West","4"],["Total","10"]],"column_alignments":["left","right"],"bars":{"column":2,"through":2}}
```

```json
{"id":"booking","kind":"sidebar","sidebar_percent":29,"items":[{"label":"Date","value":"14 October 2027"},{"label":"Booking","value":"AR-104"}],"text":"Use the courtyard entrance and bring the booking reference."}
```

```json
{"id":"update","kind":"diagram","caption":"Первый сдвиг окна","steps":[{"label":"Вычесть 4","detail":"13 − 4 = 9"},{"label":"Прибавить 6","detail":"9 + 6 = 15"},{"label":"Получить 15","detail":"Сумма второго окна"}]}
```
