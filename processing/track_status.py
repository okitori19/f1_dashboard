import pandas as pd


class TrackStatusProcessor:
    def __init__(self, api_client):
        self.api = api_client


    def fetch_track_status(self, session_key):
        race_control = self.api.get_race_control(session_key=session_key)
        df_race_control = pd.DataFrame(race_control)

        return df_race_control


    def process_safety_car_laps(self, df):
        """Заполняет пропуски между кругами для периодов SC и VSC."""
        SC_START = 'SAFETY CAR DEPLOYED'
        SC_END = 'SAFETY CAR IN THIS LAP'
        VSC_START = 'VSC DEPLOYED'
        VSC_END = 'VSC ENDING'
        cols = ['meeting_key', 'session_key', 'lap_number', 'category', 'message']

        df = df.loc[(df['category']=='SafetyCar') & (~df['lap_number'].isna()), cols].sort_values('lap_number').reset_index(drop=True)
        periods = []
        sc_start = vsc_start = None

        for _, row in df.iterrows():
            lap = int(row['lap_number'])
            msg = row['message']

            if msg == SC_START:
                sc_start = lap
            elif msg == SC_END and sc_start is not None:
                periods.append((sc_start, lap, 'SC'))
                sc_start = None
            elif msg == VSC_START:
                vsc_start = lap
            elif msg == VSC_END and vsc_start is not None:
                periods.append((vsc_start, lap, 'VSC'))
                vsc_start = None

        if not periods:
            df['type'] = None
            return df.copy()

        template = df.iloc[0]
        rows = []
        for start_lap, end_lap, sc_type in periods:
            for lap in range(start_lap, end_lap + 1):
                lap_events = df[df['lap_number'] == lap]
                if not lap_events.empty:
                    message = ' | '.join(lap_events['message'].dropna().unique())
                else:
                    message = f'{sc_type} ACTIVE'

                rows.append({
                    'meeting_key': template['meeting_key'],
                    'session_key': template['session_key'],
                    'lap_number': lap,
                    'category': template['category'],
                    'message': message,
                    'type': sc_type,
                })

        return pd.DataFrame(rows).sort_values('lap_number').reset_index(drop=True)


    def process_flag_laps(self, df):
        cols = ['meeting_key', 'session_key', 'lap_number', 'category', 'message', 'flag']

        df_flags = df.loc[  (df['category']=='Flag')
                          & (df['flag'].isin(['YELLOW', 'DOUBLE YELLOW', 'RED']))
                          & (~df['lap_number'].isna()),
                          cols]
        df_flags['message'] = None
        df_flags = df_flags.rename(columns={"flag": "type"})
        df_flags['type'] = df_flags['type'].replace('DOUBLE YELLOW', 'Yellow Flags')
        df_flags['type'] = df_flags['type'].replace('YELLOW',        'Yellow Flags')
        df_flags['type'] = df_flags['type'].replace('RED',           'Red Flags')
        df_flags.drop_duplicates()


    def merge_track_status(self, df_safety_car, df_flags):
        """Объединяет SC/VSC и флаги без дублей по кругу c приоритетом RED > SC > VSC > Yellow."""
        TYPE_PRIORITY = {
            'Red Flags': 0,
            'SC': 1,
            'VSC': 2,
            'Yellow Flags': 3,
        }
        KEY_COLS = ['meeting_key', 'session_key', 'lap_number']

        df = pd.concat([df_safety_car, df_flags], ignore_index=True)
        df['priority'] = df['type'].map(TYPE_PRIORITY)

        unknown = df.loc[df['priority'].isna(), 'type'].unique()
        if len(unknown):
            raise ValueError(f'Unknown type values: {unknown}')

        df = (
            df.sort_values(KEY_COLS + ['priority'])
            .drop_duplicates(KEY_COLS, keep='first')
            .drop(columns='priority')
            .sort_values('lap_number')
            .reset_index(drop=True)
        )
        return df