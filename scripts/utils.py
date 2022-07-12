#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime

from stravalib.client import Client
import pytz
from generator import Generator


def adjust_time(time, tz_name):
    tc_offset = datetime.now(pytz.timezone(tz_name)).utcoffset()
    return time + tc_offset


def adjust_time_to_utc(time, tz_name):
    tc_offset = datetime.now(pytz.timezone(tz_name)).utcoffset()
    return time - tc_offset


def make_activities_file(sql_file, gpx_dir, json_file):
    generator = Generator(sql_file)
    generator.sync_from_gpx(gpx_dir)
    activities_list = generator.load()
    with open(json_file, "w") as f:
        json.dump(activities_list, f)


def make_strava_client(client_id, client_secret, refresh_token):
    client = Client()

    refresh_response = client.refresh_access_token(
        client_id=client_id, client_secret=client_secret, refresh_token=refresh_token
    )
    client.access_token = refresh_response["access_token"]
    return client

def get_strava_last_time(client, is_milliseconds=True):
    """
    if there is no activities cause exception return 0
    """
    try:
        activity = None
        activities = client.get_activities(limit=10)
        # for else in python if you don't know please google it.
        for a in activities:
            if a.type == "Run":
                activity = a
                break
        else:
            return 0
        end_date = activity.start_date + activity.elapsed_time
        last_time = int(datetime.timestamp(end_date))
        if is_milliseconds:
            last_time = last_time * 1000
        return last_time
    except Exception as e:
        print(f"Something wrong to get last time err: {str(e)}")
        return 0


def upload_file_to_strava(client, file_name, data_type):
    with open(file_name, "rb") as f:
        r = client.upload_activity(activity_file=f, data_type=data_type)
        try:
            r.wait()
            print(file_name)
            print("===== waiting for upload ====")
            print(r.status, f"strava id: {r.activity_id}")
        except Exception as e:
            print(str(e))
