import pandas as pd
import numpy as np

# функция, чтобы убрать точки, которые начинаются до стартовой линии
def filter_points_by_dist_to_7(group):
    group = group.sort_values('date_timestamp').copy()
    n = len(group)
    if n < 7:
        return group

    coords = group[['x', 'y']].to_numpy()
    valid = ~np.isnan(coords).any(axis=1)  # точки с координатами

    # ищем первую валидную "7-ю" точку: индекс >= 6
    idx = np.arange(n)
    candidates = idx[valid & (idx >= 6)]
    # если нет валидной "7-й" или первая точка без координат — не фильтруем
    if len(candidates) == 0 or not valid[0]:
        return group

    ref_idx = candidates[0]
    x_ref, y_ref = coords[ref_idx]

    # расстояния до выбранной "7-й" точки
    dists = np.full(n, np.nan)
    dists[valid] = np.hypot(coords[valid, 0] - x_ref, coords[valid, 1] - y_ref)

    threshold = dists[0]  # расстояние 1-й точки до "7-й"

    # по умолчанию оставляем все точки
    mask = np.ones(n, dtype=bool)

    # для точек 2–6, у которых есть координаты, применяем порог
    mask_2_6 = (idx >= 1) & (idx <= 5) & valid
    mask[mask_2_6] = dists[mask_2_6] <= threshold

    # точки с NaN в x или y всегда остаются (valid=False → мы их не трогаем)

    return group[mask]