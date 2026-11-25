"""Лабораторная работа №4, вариант 4: инвентарь 3x3, болезни нет, старт 15 очков."""
from collections import namedtuple
from itertools import combinations, permutations

Item = namedtuple("Item", "code name size value")

ITEMS = [
    Item("r", "Винтовка", 3, 25),
    Item("p", "Пистолет", 2, 15),
    Item("a", "Боекомплект", 2, 15),
    Item("m", "Аптечка", 2, 20),
    Item("i", "Ингалятор", 1, 5),
    Item("k", "Нож", 1, 15),
    Item("x", "Топор", 3, 20),
    Item("t", "Оберег", 1, 25),
    Item("f", "Фляжка", 1, 15),
    Item("d", "Антидот", 1, 10),
    Item("s", "Еда", 2, 20),
    Item("c", "Арбалет", 2, 20),
]
TOTAL_VALUE = sum(item.value for item in ITEMS)

ROWS, COLS = 3, 3
START = 15
REQUIRED = []  # обязательные предметы: [] - нет болезни, ["i"] - астма, ["d"] - паранойя


def final_score(taken, start=START):
    """Итог = старт + очки взятого - очки оставленного."""
    taken_value = sum(item.value for item in taken)
    return start + taken_value - (TOTAL_VALUE - taken_value)


def knapsack(items, capacity):
    """Динамическое программирование: возвращает (макс. ценность, список предметов)."""
    n = len(items)
    table = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        item = items[i - 1]
        for j in range(capacity + 1):
            table[i][j] = table[i - 1][j]
            if item.size <= j:
                with_item = item.value + table[i - 1][j - item.size]
                table[i][j] = max(table[i][j], with_item)

    chosen = []
    j = capacity
    for i in range(n, 0, -1):
        if table[i][j] != table[i - 1][j]:
            chosen.append(items[i - 1])
            j -= items[i - 1].size
    return table[n][capacity], chosen[::-1]


def solve(capacity, required=REQUIRED, start=START):
    """Лучший набор с учётом обязательных предметов. Возвращает (набор, счёт) или None."""
    forced = [item for item in ITEMS if item.code in required]
    rest = [item for item in ITEMS if item.code not in required]
    free_space = capacity - sum(item.size for item in forced)
    if free_space < 0:
        return None
    _, chosen = knapsack(rest, free_space)
    best = forced + chosen
    return best, final_score(best, start)


def all_good_sets(capacity, required=REQUIRED, start=START):
    """Полный перебор: все наборы, которые влезают и дают положительный счёт."""
    result = []
    for count in range(len(ITEMS) + 1):
        for combo in combinations(ITEMS, count):
            codes = {item.code for item in combo}
            if sum(item.size for item in combo) > capacity:
                continue
            if not set(required) <= codes:
                continue
            score = final_score(combo, start)
            if score > 0:
                result.append((combo, score))
    return result


def fits_rows(order):
    """True, если ни один предмет не переносится с одной строки сетки на другую."""
    pos = 0
    for item in order:
        if pos // COLS != (pos + item.size - 1) // COLS:
            return False
        pos += item.size
    return True


def layout(chosen):
    """Строит текстовый инвентарь ROWS x COLS, как в примере из README."""
    base = sorted(chosen, key=lambda item: -item.size)
    order = base
    for variant in permutations(base):
        if fits_rows(variant):
            order = list(variant)
            break
    cells = []
    for item in order:
        cells += [item.code] * item.size
    cells += [" "] * (ROWS * COLS - len(cells))
    rows = [cells[r * COLS:(r + 1) * COLS] for r in range(ROWS)]
    return "\n".join(",".join(f"[{c}]" for c in row) for row in rows)


def show(chosen, score):
    print(layout(chosen))
    print("Предметы:", ", ".join(f"{i.name} ({i.code})" for i in chosen))
    print("Занято ячеек:", sum(i.size for i in chosen))
    print("Итоговые очки выживания:", score)


if __name__ == "__main__":
    capacity = ROWS * COLS

    print(f"=== Основное задание: {ROWS}x{COLS}, старт {START}, обязательные: {REQUIRED or 'нет'} ===")
    best, score = solve(capacity)
    show(best, score)
    print("Счёт положительный:", score > 0)

    print("\n=== Допзадание 1: инвентарь на 7 ячеек ===")
    best7, score7 = solve(7)
    show(best7, score7)
    if score7 > 0:
        print("Решение существует.")
    else:
        print("Решения нет: даже лучший набор не даёт положительный счёт.")
        brute = max(final_score(c) for n in range(len(ITEMS) + 1)
                    for c in combinations(ITEMS, n) if sum(i.size for i in c) <= 7)
        print("Проверка полным перебором, максимум счёта:", brute)

    print("\n=== Допзадание 2: все наборы с положительным счётом ===")
    good = all_good_sets(capacity)
    good.sort(key=lambda pair: (-pair[1], len(pair[0])))
    print("Всего наборов:", len(good))
    with open("combinations_variant4.txt", "w", encoding="utf-8") as file:
        for combo, sc in good:
            line = f"{''.join(i.code for i in combo):<10} ячеек: {sum(i.size for i in combo)}  счёт: {sc}"
            file.write(line + "\n")
    for combo, sc in good[:10]:
        print(f"{''.join(i.code for i in combo):<10} счёт: {sc}")
    print("Полный список записан в combinations_variant4.txt")
