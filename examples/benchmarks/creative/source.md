# Frozen source for the 0.5.0 benchmarks

27 November 2026. All organizations, terms, metrics, schedules and examples are synthetic. Preserve these facts in the native reading sequence of each brief. The full text in each JSON brief is also an acceptance input to the generator.

## B and E — A cooler route

The fictional Northbank Mobility Lab observed three walking routes between May and August 2026. It logged 240 observations and identified 18 sites suitable for shade. Priority links cover 2.4 km. This was a planning study, with no measured temperature reductions. The first phase recommends temporary shade and free seating at Junction, East Arcade and River Steps.

| Route | Observations | Candidate sites | Priority km |
| --- | ---: | ---: | ---: |
| Junction | 96 | 8 | 0.9 |
| East Arcade | 78 | 6 | 0.8 |
| River Steps | 66 | 4 | 0.7 |
| Total | 240 | 18 | 2.4 |

Walk each link at midday, record shaded seating and step-free access, and repeat after installing the temporary elements. The report includes an illustration of a walkway under a canopy and an illustration of a shaded seating area. Neither represents a real observation site. The creative and structured editions use the same verbatim source, images, captions, alternative descriptions and block order.

## C — Fieldwork agreement

Order FW-024. Ember Survey Studio will deliver one access audit and one editable route inventory to Orchard Commons Cooperative. Review is on 18 December 2026. Scope includes site notes, one joint review and one consolidated revision. Fixtures and construction are outside the order. Draft due 11 December, comments due 18 December, final delivery 22 December 2026. Audit EUR 1,200.00, inventory EUR 600.00, total EUR 1,800.00. No tax line is included in the synthetic order. Payment is due 14 calendar days after final delivery. Both parties keep field notes private and circulate aggregated findings only.

## D — Как данные связаны

`authors(id, name)` contains `(1, «Анна»)` and `(2, «Марк»)`; `books(id, title, author_id)` contains `(10, «Маяк», 1)`, `(11, «Порт», 1)`, `(12, «Тропа», 2)`. `authors.id` is a primary key; `books.author_id` references it. A single author can have several books. An inner join returns one row for each match. Ordering by `b.id` yields «Анна — Маяк», «Анна — Порт», «Марк — Тропа». The lesson asks readers to add an author without a book and predict the result, then compare with a left join.

```sql
SELECT a.name, b.title
FROM authors AS a
JOIN books AS b ON b.author_id = a.id
ORDER BY b.id;
```

## F — Night relay

A synthetic radio performance score. Two performers, receiver and reader. From the start, hold silence for eight seconds. At 00:08 receiver says “Channel open.”, at 00:16 reader says “The jetty light is turning.”, at 00:28 both pause for four seconds, and at 00:32 reader says “Channel closed.”. The 00:28 cue is silent. All times are measured from the start of the piece. Perform at conversational volume with an unobstructed line of sight between performers.
