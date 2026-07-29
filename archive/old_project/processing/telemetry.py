# processing/telemetry.py
import pandas as pd
import numpy as np
import time
from processing.locations import filter_points_by_dist_to_7


class TelemetryProcessor:
    def __init__(self, api_client):
        self.api = api_client

    def fetch_drivers(self, session_key):
        cols = ['driver_number', 'broadcast_name', 'full_name', 'name_acronym',
                'team_name', 'team_colour', 'first_name', 'last_name']

        drivers = self.api.get_drivers(session_key=session_key)
        df_drivers = pd.DataFrame(drivers)[cols]

        return df_drivers

    def fetch_full_telemetry(self, session_key, drivers_list):
        """Скачивает и соединяет car_data + location для всех пилотов."""
        df_car_list = []
        df_loc_list = []
        df_lap_list = []
        
        car_cols = ['date', 'rpm', 'driver_number', 'n_gear', 'throttle', 'drs', 'speed', 'brake']
        loc_cols = ['date', 'driver_number', 'x', 'y', 'z']
        lap_cols = ['driver_number', 'lap_number', 'date_start', 'is_pit_out_lap', 'lap_duration']

        for driver in drivers_list:
            # 1. Car Data
            car_data = self.api.get_car_data(session_key=session_key, driver_number=driver, speed=10)
            if car_data:
                df_c = pd.DataFrame(car_data)[car_cols]
                df_c['date_timestamp'] = pd.to_datetime(df_c['date'], format='ISO8601').astype(np.int64) // 10**6
                df_car_list.append(df_c)

            # 2. Location Data
            loc_data = self.api.get_location(session_key=session_key, driver_number=driver)
            if loc_data:
                df_l = pd.DataFrame(loc_data)[loc_cols]
                df_l['date_timestamp'] = pd.to_datetime(df_l['date'], format='ISO8601').astype(np.int64) // 10**6
                df_loc_list.append(df_l)

            # 3. Lap Data
            lap_data = self.api.get_laps(session_key=session_key, driver_number=driver)

            if lap_data is None:
                exit
            if isinstance(lap_data, dict):
                # если пришла одна запись или объект-ошибка
                lap_data = [lap_data]
            if not isinstance(lap_data, list) or len(lap_data) == 0:
                continue
            df_lap = pd.DataFrame(lap_data)[lap_cols]

            df_lap['date_formatted'] = pd.to_datetime(df_lap['date_start'], format='ISO8601') # чтобы не было ошибок формата
            df_lap['date_start_timestamp'] = df_lap['date_formatted'].astype('int64') // 10**6
            df_lap = df_lap.drop(columns='date_formatted')
            df_lap['date_end_timestamp'] = df_lap['date_start_timestamp'].shift(-1)
            df_lap.loc[df_lap['date_end_timestamp'].isnull(), 'date_end_timestamp'] = df_lap['date_start_timestamp'] + (df_lap['lap_duration'] * 1000)

            df_lap_list.append(df_lap)

            time.sleep(1)

        df_car = pd.concat(df_car_list, ignore_index=True) if df_car_list else pd.DataFrame()
        df_loc = pd.concat(df_loc_list, ignore_index=True) if df_loc_list else pd.DataFrame()
        df_laps = pd.concat(df_lap_list, ignore_index=True) if df_lap_list else pd.DataFrame()

        # Корректировка координат
        for col in ['x', 'y', 'z']:
            if col in df_loc and df_loc[col].min() < 0:
                df_loc[col] -= df_loc[col].min()

        # Merge telemetry
        df_combined = pd.merge(
            df_car, df_loc, 
            on=['date_timestamp', 'date', 'driver_number'], 
            how='outer'
        ).sort_values(by=['driver_number', 'date_timestamp']).reset_index(drop=True)


        # Оптимизация типов для экономии памяти
        for df in [df_laps, df_combined]:
            for col in df.select_dtypes('float64').columns:
                df[col] = df[col].astype('float32')
            for col in ['driver_number']:
                if col in df.columns:
                    df[col] = df[col].astype('category')

        df_merged = pd.merge(
            df_laps, df_combined,
            on=['driver_number'],
            how='left'
        )

        # Фильтруем по временным рамкам круга
        mask = (df_merged['date_timestamp'] >= df_merged['date_start_timestamp']) & \
               (df_merged['date_timestamp'] < df_merged['date_end_timestamp']) 
        result = df_merged[mask].sort_values(by=['driver_number', 'date_timestamp']).reset_index(drop=True)
        
        result = result.groupby(['driver_number', 'lap_number'], group_keys=False, observed=False).apply(filter_points_by_dist_to_7)

        for coord in ['x', 'y', 'z']:
            result[coord] = result[coord].interpolate(method='linear', limit_direction='forward', axis=0)

        return result
