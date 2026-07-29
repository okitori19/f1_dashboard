# main.py
import pandas as pd
import logging
import config
from api.openf1_client import OpenF1API
from processing.meetings import MeetingsFetcher
from processing.telemetry import TelemetryProcessor
from processing.track_matcher import TrackMatcher
from processing.track_status import TrackStatusProcessor
from processing.csv_writer import CsvWriter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline():
    api = OpenF1API()

    YEAR = 2026  # можно поменять год
    MEETING_KEY = 1290   # Belgian Grand Prix
    SESSION_KEY = 11329  # Например, FP3 Belgian GP 2026

    csv_writer = CsvWriter(logging)


    meetings_fetcher = MeetingsFetcher(api)

    # # 1. ДОСТАЕМ СОБЫТИЯ
    # logging.info("Скачиваем список событий...")
    # df_meetings = meetings_fetcher.fetch_meetings(year=YEAR)
    # csv_writer.write(output_filename=f"meetings.csv", df=df_meetings)


    # # 2. ДОСТАЕМ СЕССИИ
    # logging.info("Скачиваем список сессий...")
    # df_sessions_list = []
    # for meet_key in df_meetings['meeting_key']:
    #     df_s = meetings_fetcher.fetch_sessions(meeting_key=meet_key)
    #     df_sessions_list.append(df_s)
    
    # df_sessions = pd.concat(df_sessions_list, ignore_index=True) if df_sessions_list else pd.DataFrame()
    # csv_writer.write_with_check(output_filename=f"sessions.csv", df=df_sessions, check_col='session_key')


    # processor = TelemetryProcessor(api)

    # 3. ДОСТАЕМ ПИЛОТОВ
    # logging.info("Скачиваем список пилотов...")
    # df_pilots_list = []
    # for s_key in df_sessions['session_key']:
    #     df_d = processor.fetch_drivers(session_key=s_key)
    #     df_pilots_list.append(df_d)
    
    # df_drivers = pd.concat(df_pilots_list, ignore_index=True) if df_pilots_list else pd.DataFrame()
    # df_drivers = df_drivers.drop_duplicates()
    # csv_writer.write_with_check(output_filename=f"drivers.csv", df=df_drivers, check_col='driver_number')


    # # 4. ДОСТАЕМ ТЕЛЕМЕТРИЮ
    # driver_numbers = [d for d in df_drivers['driver_number'].loc[:3]]  # Возьмем первых 4 пилотов для теста

    # logging.info("Получаем телеметрию и локации...")
    # df_telemetry = processor.fetch_full_telemetry(SESSION_KEY, driver_numbers)


    # # 5. ВЫРАВНИВАЕМ КРУГИ ПО РЕФЕРЕНСУ
    # logging.info("Выравниваем круги по референсу...")
    # matcher = TrackMatcher.build_from_best_lap(df_telemetry, ref_driver_number=1)
    # df_final = df_telemetry.groupby(['driver_number', 'lap_number'], group_keys=False, observed=False).apply(matcher.map_group_to_reference)
    # df_final['meeting_key'] = MEETING_KEY
    # df_final['session_key'] = SESSION_KEY

    # output_filename = f"telemetry.csv"
    # output_path = config.DATA_DIR / output_filename
    # file_exists = os.path.isfile(output_path)  # Write header only if the file doesn't exist yet
    # df_final.to_csv(output_path, mode="a", index=False, header=not file_exists)
    # logging.info(f"Данные успешно сохранены в: {output_path}")


    # 5. ДОСТАЕМ SC, VSC, FLAGS
    track_status = TrackStatusProcessor(api)

    logging.info("Получаем данные по SC, VSC, Flags...")
    df_ts_list = []
    session_list = [11292, 11293, 11294, 11295, 11299, 11327, 11328, 11329, 11330, 11334]
    for s_key in session_list:
        df_ts = track_status.fetch_track_status(session_key=s_key)

        df_safety_car = track_status.process_safety_car_laps(df_ts)
        df_flags = track_status.process_flag_laps(df_ts)
        df_track_status = track_status.merge_track_status(df_safety_car, df_flags)

        df_ts_list.append(df_track_status)
    
    df_track_statuses = pd.concat(df_ts_list, ignore_index=True) if df_ts_list else pd.DataFrame()
    csv_writer.write(output_filename=f"track_status.csv", df=df_track_statuses)


    logging.info("Пайплайн завершен успешно!")

if __name__ == "__main__":
    run_pipeline()