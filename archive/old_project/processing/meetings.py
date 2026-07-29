import pandas as pd

class MeetingsFetcher:
    def __init__(self, api_client):
        self.api = api_client

    def fetch_meetings(self, year):
        cols = ['meeting_key', 'meeting_name', 'meeting_official_name', 'location', 'country_name',
                'country_flag', 'circuit_short_name', 'circuit_image', 'year']

        meetings = self.api.get_meetings(year=year)
        df_meetings = pd.DataFrame(meetings)[cols]

        return df_meetings

    def fetch_sessions(self, meeting_key):
        cols = ['session_key', 'meeting_key', 'session_name']

        sessions = self.api.get_sessions(meeting_key=meeting_key)
        df_sessions = pd.DataFrame(sessions)[cols]

        return df_sessions
