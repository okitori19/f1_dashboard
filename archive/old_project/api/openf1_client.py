# api/openf1_client.py
import time
import requests
from collections import deque
import logging

logger = logging.getLogger(__name__)

class OpenF1API:
    def __init__(self, max_requests_per_minute=30, max_requests_per_second=3, max_retries=5, timeout=30):
        self.base_url = "https://api.openf1.org/v1"
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_second = max_requests_per_second
        self.max_retries = max_retries
        self.timeout = timeout
        self._request_timestamps = deque()
        self._request_timestamps_sec = deque()

    def _throttle(self):
        while True:
            now = time.time()

            # удаляем запросы старше 60 секунд
            while self._request_timestamps and now - self._request_timestamps[0] >= 60:
                self._request_timestamps.popleft()

            # удаляем запросы старше 1 секунды
            while self._request_timestamps_sec and now - self._request_timestamps_sec[0] >= 1:
                self._request_timestamps_sec.popleft()

            wait_minute = 0
            wait_second = 0

            if len(self._request_timestamps) >= self.max_requests_per_minute:
                wait_minute = 60 - (now - self._request_timestamps[0]) + 0.05
            if len(self._request_timestamps_sec) >= self.max_requests_per_second:
                wait_second = 1 - (now - self._request_timestamps_sec[0]) + 0.02

            wait_seconds = max(wait_minute, wait_second)
            if wait_seconds > 0:
                logger.info(f"Rate limit guard: sleep {wait_seconds:.2f}s")
                time.sleep(wait_seconds)
                continue
            break

    def _request(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(self.max_retries + 1):
            self._throttle()

            response = requests.get(url, params=params, timeout=self.timeout)
            req_time = time.time()
            self._request_timestamps.append(req_time)
            self._request_timestamps_sec.append(req_time)

            if response.status_code in (429, 422):
                retry_after = response.headers.get("Retry-After")
                sleep_seconds = float(retry_after) if retry_after else min(2 ** attempt, 30)
                logger.warning(f"{response.status_code} Rate limit. Sleep {sleep_seconds:.2f}s")
                time.sleep(sleep_seconds)
                continue

            if response.status_code == 404:
                return []

            response.raise_for_status()
            return response.json()

        raise RuntimeError(f"Failed to fetch {endpoint}: too many retries")

    def get_meetings(self, year=None):
        params = {'year': year} if year else {}
        return self._request("meetings", params=params)

    def get_sessions(self, meeting_key=None, year=None):
        params = {}
        if meeting_key: params['meeting_key'] = meeting_key
        if year: params['year'] = year
        return self._request("sessions", params=params)

    def get_drivers(self, meeting_key=None, session_key=None, driver_number=None):
        params = {}
        if session_key: params['meeting_key'] = meeting_key
        if session_key: params['session_key'] = session_key
        if driver_number: params['driver_number'] = driver_number
        return self._request("drivers", params=params)

    def get_car_data(self, session_key, driver_number=None, speed=None):
        params = {'session_key': session_key}
        if driver_number: params['driver_number'] = driver_number
        if speed: params['speed>'] = speed
        return self._request("car_data", params=params)

    def get_laps(self, session_key, driver_number=None):
        params = {'session_key': session_key}
        if driver_number: params['driver_number'] = driver_number
        return self._request("laps", params=params)

    def get_location(self, session_key, driver_number=None):
        params = {'session_key': session_key}
        if driver_number: params['driver_number'] = driver_number
        return self._request("location", params=params)

    def get_race_control(self, session_key=None, meeting_key=None, driver_number=None, lap_number=None):
        params = {'session_key': session_key}
        if meeting_key: params['meeting_key'] = meeting_key
        if meeting_key: params['driver_number'] = driver_number
        if meeting_key: params['lap_number'] = lap_number
        return self._request("race_control", params=params)
