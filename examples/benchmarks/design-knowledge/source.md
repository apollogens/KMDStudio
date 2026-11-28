# Frozen synthetic sources

The walking report reuses the exact source and image descriptions in [the v0.6.0rc1 brief](../quality/cooler-route-refined.json). The exhibition, lesson and booking use the following original material.

## The edge of the water

Title: **The edge of the water**. Subtitle: **Three studies from a fictional tidal observatory**. Cover label: **SHORELINE ROOM / STUDY NOTES**.

At the shoreline, the same mark can read as a boundary, a trace or an opening. Three study prints invite a second look at what the water leaves behind.

**Begin with the edge**

Enter from the dry side. The prints are arranged from a single cut to a sequence of overlapping marks. Stand back first, then move close enough to see where a contour loses its sharpness.

The room follows a low bank imagined for this exhibition. No print records a measured tide or an actual location. The route moves from an overall view into details, then returns to the whole group.

The entrance print gives the eye a long horizontal line to follow. Its break is the first question to carry into the room: which edge are you following when the line disappears?

**Follow a line**

Low Bank sets a pale band against dark water. The band has a clean edge at left and breaks into small steps at right. The change can be read before the print is seen up close.

Keep your gaze on the point where the long band ends. The next mark turns downward. It belongs to the same surface, even though it points in a different direction.

**Index of the studies**

| Print | Room position | Year | Study size (cm) |
| --- | --- | --- | --- |
| Low Bank | Entrance | 2024 | 60 × 36 |
| Slack Water | Long wall | 2025 | 42 × 42 |
| Return Mark | Exit wall | 2026 | 60 × 36 |

Dimensions describe the fictional studies, not the size of their reproductions on these pages. The three prints are shown in reading order around the room.

**Read the return**

Slack Water puts two edges near each other without joining them. The narrow gap becomes visible at the center, then widens toward the right.

Return Mark holds the same opening near its lower edge. The gap now points back toward the route you have walked. Compare where the pale strip ends before comparing color.

**Take the question outside**

On the next walk, choose one edge and follow it until it disappears. Notice whether its return changes the direction of your gaze.

1. Find a sharp edge and a fading edge.
2. Describe what separates them without naming a color.
3. Return to the entrance print and apply the same description.

An edge is easier to remember when you can say where it changes.

Art to be authored for this source, with fixed semantic roles and captions:

- `low-bank`, cover and study. **Low Bank. A continuous upper band breaks into steps.** Alt: **A pale horizontal band above dark teal water ends in three descending steps.**
- `slack-water`, orientation and first comparison. **Slack Water. Two edges open around a central gap.** Alt: **Two offset bands face each other across an opening that widens to the right.**
- `return-mark`, second comparison. **Return Mark. A pale strip turns back below the opening.** Alt: **A pale strip doubles back along the lower edge of a dark opening.**

## Rolling window / Сумма окна

Title: **Сумма окна**. Subtitle: **Как обновить сумму, не складывая всё заново**.

**Цель**

После урока вы сможете обновить сумму окна из трёх соседних значений и проверить результат вручную.

**Первый сдвиг**

Возьмём ряд 4, 7, 2, 6, 3. Первое окно содержит 4, 7 и 2. При сдвиге вправо 4 уходит, а 6 входит. Поэтому новая сумма равна 13 − 4 + 6 = 15.

Diagram caption: **Первый сдвиг окна**. Editable stages: `Вычесть 4` (13 − 4 = 9) → `Прибавить 6` (9 + 6 = 15) → `Получить 15` (Сумма второго окна).

| Окно | Значения | Сумма |
| --- | --- | --- |
| 1 | 4, 7, 2 | 13 |
| 2 | 7, 2, 6 | 15 |
| 3 | 2, 6, 3 | 11 |

**Код и проверка**

Функция принимает список минимум из трёх чисел и возвращает суммы в порядке движения окна.

```python
def window_sums(values):
    total = sum(values[:3])
    result = [total]
    for i in range(3, len(values)):
        total += values[i] - values[i - 3]
        result.append(total)
    return result
```

**Практика**

Сначала найдите третий результат из второго. Затем самостоятельно запишите суммы окон для ряда 1, 3, 5, 7, 9.

1. Запишите значения первого окна, затем вычислите его сумму.
2. Сделайте два сдвига и отметьте, какое число ушло и какое вошло.

**Самопроверка.** Для первого ряда: 15 − 7 + 3 = 11. Для второго ряда: 9, 15, 21.

## Reading room booking

Title: **Reading room booking**. Subtitle: **Confirmation for Alder Archive**.

- Date: 14 October 2027
- Access: 09:00–11:30
- Booking: AR-104

The East Reading Room is reserved for Alder Archive. Please use the courtyard entrance and bring the booking reference. The duty host will meet the group at the entrance at 09:00.

**Charges**

| Item | Fee (GBP) |
| --- | --- |
| Room reservation | 120.00 |
| Equipment | 35.00 |
| Total | 155.00 |

**Confirm by 7 October 2027**

Reply with AR-104 and the name of the group lead. Notify the duty host before the session if the equipment requirement changes.
