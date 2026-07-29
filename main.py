# main.py
import pandas as pd
import logging
import config
from api.openf1_client import OpenF1API
from processing.openf1_data import OpenF1Fetcher
import fastf1
from processing.telemetry import TelemetryProcessor
from processing.track_status import TrackStatusProcessor
from processing.csv_writer import CsvWriter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline():
    api = OpenF1API()

    YEAR = 2026

    csv_writer = CsvWriter(logging)
    f1_data_fetcher = OpenF1Fetcher(api)

    # # 1. ДОСТАЕМ СОБЫТИЯ
    # logging.info("Скачиваем список событий...")
    # df_meetings = f1_data_fetcher.fetch_meetings(year=YEAR)
    # csv_writer.write(output_filename=f"meetings.csv", df=df_meetings)


    # # 2. ДОСТАЕМ СЕССИИ
    # logging.info("Скачиваем список сессий...")
    # df_sessions_list = []
    # for meet_key in df_meetings['meeting_key']:
    #     df_s = f1_data_fetcher.fetch_sessions(meeting_key=meet_key)
    #     df_sessions_list.append(df_s)
    
    # df_sessions = pd.concat(df_sessions_list, ignore_index=True) if df_sessions_list else pd.DataFrame()
    # csv_writer.write_with_check(output_filename=f"sessions.csv", df=df_sessions, check_cols=['session_key'])


    # 3. ДОСТАЕМ ПИЛОТОВ
    logging.info("Скачиваем список пилотов...")
    df_pilots_list = []
    session_list = [11335, 11336, 11337, 11338, 11342]
    # for s_key in df_sessions['session_key']:
    for s_key in session_list:
        df_d = f1_data_fetcher.fetch_drivers(session_key=s_key)
        df_pilots_list.append(df_d)
    
    df_drivers = pd.concat(df_pilots_list, ignore_index=True) if df_pilots_list else pd.DataFrame()
    df_drivers = df_drivers.drop_duplicates()
    csv_writer.write_with_check(output_filename=f"drivers.csv", df=df_drivers, check_cols=['driver_number'])


    # # # 4. ДОСТАЕМ ТЕЛЕМЕТРИЮ
    # logging.info("Получаем телеметрию и локации...")
    # fastf1.Cache.enable_cache('cache')

    # # COUNTRY = 'Belgium'
    # COUNTRY = 'Monaco'
    # # SESSION = 'Practice 1'
    # # SESSION = 'Practice 2'
    # # SESSION = 'Practice 3'
    # SESSION = 'Qualifying'
    # # SESSION = 'Race'

    # session = fastf1.get_session(YEAR, COUNTRY, SESSION)
    # session.load()
    # processor = TelemetryProcessor(session)
    # df_telemetry = processor.fetch_full_telemetry()

    # filename = f'telemetry_' + str(YEAR) + '_' + COUNTRY + '_' + SESSION + '.csv'
    # csv_writer.write(output_filename=filename, df=df_telemetry)


    # 5. ДОСТАЕМ SC, VSC, FLAGS
    track_status = TrackStatusProcessor(api)

    logging.info("Получаем данные по SC, VSC, Flags...")
    df_ts_list = []
    # session_list = [11335, 11336, 11337, 11338, 11342]
    for s_key in session_list:
        df_ts = track_status.fetch_track_status(session_key=s_key)

        df_safety_car = track_status.process_safety_car_laps(df_ts)
        df_flags = track_status.process_flag_laps(df_ts)
        df_track_status = track_status.merge_track_status(df_safety_car, df_flags)

        df_ts_list.append(df_track_status)
    
    df_track_statuses = pd.concat(df_ts_list, ignore_index=True) if df_ts_list else pd.DataFrame()
    csv_writer.write_with_check(output_filename=f"track_status.csv",
                                df=df_track_statuses,
                                check_cols=['meeting_key', 'session_key', 'lap_number', 'category', 'type']
                               )


    logging.info("Пайплайн завершен успешно!")

if __name__ == "__main__":
    run_pipeline()