# processing/track_matcher.py
import numpy as np
import pandas as pd

class TrackMatcher:
    def __init__(self, ref_coords, ref_s, ref_s_norm):
        self.ref_coords = ref_coords
        self.ref_s = ref_s
        self.ref_s_norm = ref_s_norm

    @classmethod
    def build_from_best_lap(cls, df_combined, ref_driver_number):
        """Фабричный метод: создает матчер на основе лучшего круга водителя."""
        clean_laps = df_combined[(df_combined['driver_number'] == ref_driver_number) & (~df_combined['is_pit_out_lap'])]
        best_lap = clean_laps.sort_values('lap_duration').iloc[0]

        df_ref = df_combined[
            (df_combined['driver_number'] == ref_driver_number) &
            (df_combined['lap_number'] == best_lap['lap_number'])
        ].dropna(subset=['x', 'y']).sort_values('date_timestamp')

        x_ref = df_ref['x'].to_numpy()
        y_ref = df_ref['y'].to_numpy()
        dx, dy = np.diff(x_ref), np.diff(y_ref)
        
        ref_s = np.concatenate(([0], np.cumsum(np.hypot(dx, dy)))) / 10.0  # в метры
        ref_s_norm = ref_s / ref_s[-1]
        ref_coords = np.column_stack([x_ref, y_ref])

        return cls(ref_coords, ref_s, ref_s_norm)

    def map_group_to_reference(self, group):
        group = group.sort_values('date_timestamp').copy()
        pts = group[['x', 'y']].to_numpy()
        n = len(pts)
        valid = ~np.isnan(pts).any(axis=1)

        idx_ref = np.full(n, -1, dtype=int)
        cur, window = 0, 50
        max_idx = len(self.ref_coords) - 1

        for i in range(n):
            if not valid[i]: continue
            start = max(cur - 10, 0)
            end = min(cur + window, max_idx)
            seg = self.ref_coords[start:end + 1]
            
            dists = np.sum((seg - pts[i])**2, axis=1)
            j = np.argmin(dists)
            cur = start + j
            idx_ref[i] = cur

        s_vals = np.full(n, np.nan)
        s_norm_vals = np.full(n, np.nan)

        good = idx_ref >= 0
        s_vals[good] = self.ref_s[idx_ref[good]]
        s_norm_vals[good] = self.ref_s_norm[idx_ref[good]]

        group['s_ref'] = s_vals
        group['percent_progress_ref'] = s_norm_vals
        group['distance_ref'] = s_vals
        return group