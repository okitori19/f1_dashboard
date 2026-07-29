# processing/telemetry.py
import pandas as pd


class TelemetryProcessor:
    def __init__(self, session):
        self.session = session


    def fetch_full_telemetry(self):
        telemetry_list = []

        # Извлекаем ключи из session_info
        session_key = self.session.session_info['Key']
        meeting_key = self.session.session_info['Meeting']['Key']

        # Проходим по каждому кругу в сессии
        for _, lap in self.session.laps.iterlaps():
            try:
                # Получаем телеметрию текущего круга
                lap_telemetry = lap.get_telemetry()
                
                # Если телеметрия для круга есть, добавляем информацию о круге и гонщике
                if not lap_telemetry.empty:
                    lap_telemetry['MeetingKey'] = meeting_key
                    lap_telemetry['SessionKey'] = session_key
                    
                    lap_telemetry['LapNumber'] = lap['LapNumber']
                    lap_telemetry['Driver'] = lap['Driver']
                    lap_telemetry['DriverNumber'] = lap['DriverNumber']
                    lap_telemetry['IsAccurate'] = lap['IsAccurate']
                    lap_telemetry['Compound'] = lap['Compound']  # Можно добавить тип шин
                    lap_telemetry['LapTimeSeconds'] = lap['LapTime'].total_seconds()
                    lap_telemetry['IsPitOutLap'] = pd.notna(lap['PitOutTime'])
                    lap_telemetry['IsPitInLap'] = pd.notna(lap['PitInTime'])
                    
                    telemetry_list.append(lap_telemetry)
            except Exception as e:
                # Пропускаем круги без данных (например, если нет телеметрии)
                continue

        # Объединяем все круги в один общий DataFrame
        full_telemetry = pd.concat(telemetry_list, ignore_index=True)
        return full_telemetry
