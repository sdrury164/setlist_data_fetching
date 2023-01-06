# -*- coding: utf-8 -*-
"""
Created on Sat Dec 31 08:03:08 2022

@author: Steve
"""

import numpy as np
import pandas as pd
import get_setlist_fm_api_key as sfm_key
from datetime import datetime
import time
import requests
import pickle

from repertorio import Repertorio

def print_dd_tab_formatted(dd, indent=0):
    if type(dd) == dict:
        for key in dd.keys():
            print(' * '*indent + key + ' ' + str(type(dd[key])) + '\n')
            if type(dd[key]==dict):
                print_dd_tab_formatted(dd[key], indent=indent+1)

def get_current_dt_str():
    return datetime.now().strftime('%m-%d-%Y_%H-%M-%S')

def get_setlist_fm_api():
    api_key = sfm_key.get_api_key()
    api = Repertorio(api_key)
    return api

def get_artist_mbid(artist_name, api=get_setlist_fm_api()):
    artist_search = api.artists(artistName=artist_name)
    artist_mbid = '%NO_mbid_FOUND%'
    for artist in artist_search['artist']:
        if artist['name'] == artist_name:
            print(artist)
            artist_mbid = artist['mbid']
    return artist_mbid

def get_artist_setlist_lists(artist_name,
                             api=get_setlist_fm_api(),
                             iteration_limit=None):
    mbid = get_artist_mbid(artist_name, api)
    if mbid == '%NO_mbid_FOUND%':
        print('Could not find artist mbid. Returning empty list.')
        return []
    else:
        artist_setlists = []
        iteration = 1
        keep_going = True
        error_thrown = ''

        while keep_going:
            try:
                artist_setlists.append(api.artist_setlists(mbid, p=iteration))
                iteration += 1
                if iteration_limit:
                    if iteration > iteration_limit:
                        keep_going = False
            except requests.exceptions.HTTPError as e:
                if str(e).split(':')[0] == '429 Client Error':
                    print('Hit an HTTPError on setlist iteration ' + str(iteration) + ' at ' + get_current_dt_str() + ':\n')
                    print(e)
                    print('\nWaiting for 30 seconds.\n')
                    time.sleep(30)
                else:
                    print('Hit an error on iteration ' + str(iteration) + '.\nError message:\n')
                    print(e)
                    keep_going = False
                    error_thrown = e
            # except Exception as e:

        return artist_setlists

def get_setlist_df_from_setlist_list(setlist_list, return_error_df=True):
    setlist_dl = []
    error_setlist_dl = []
    setlist_list = setlist_list['setlist']
    # for setlist in setlist_list:
    for setlist in setlist_list:
        # setlist_dict = setlist['setlist']
        try:
            # if 'sets' in setlist['setlist'].keys():
            #     for s in setlist['setlist']['sets']['set']:
            # for s in setlist:
            # for s in setlist['setlist']:
            if 'sets' in setlist.keys():
                track_number = 0
                if len(setlist['sets']['set']) > 0:
                    for song in setlist['sets']['set'][0]['song']:
                        track_number += 1
        #                 print(type(song))
        #                 print(type(s))
                        track_dict = {
                            'track_name': song['name'],#['name'],
        #                     'song_info': song['info'],
                            'setlist_id': setlist['id'],
                            'track_number': track_number,
                            'artist': setlist['artist']['name'],
                            'artist_id': setlist['artist']['mbid'],
                            'event_date': setlist['eventDate'],
                            'venue_name': setlist['venue']['name'],
                            'venue_id': setlist['venue']['id'],
                            'venue_city': setlist['venue']['city']['name'],
                            'venue_city_id': setlist['venue']['city']['id'],
                            'venue_city_lat': setlist['venue']['city']['coords']['lat'],
                            'venue_city_long': setlist['venue']['city']['coords']['long'],
                            'venue_country': setlist['venue']['city']['country']['name'],
                            'venue_country_code': setlist['venue']['city']['country']['code'],
                            'venue_url': setlist['venue']['url']
                        }

                        if 'tour' in setlist.keys():
                            track_dict['tour'] = setlist['tour']['name']
                        else:
                            track_dict['tour'] = '%NO_TOUR%'

                        if 'state' in setlist['venue']['city'].keys():
                            track_dict['venue_state'] = setlist['venue']['city']['state']
                        else:
                            track_dict['venue_state'] = '%NO_STATE%'

                        setlist_dl.append(track_dict)

        except Exception as e:
            error_dict = {
                'error': e,
                'setlist': setlist
            }

            print('Error on setlist:')
            print(setlist)
            print('Exception:')
            print(e)

            error_setlist_dl.append(error_dict)

    setlist_df = pd.DataFrame(setlist_dl)
    error_setlist_df = pd.DataFrame(error_setlist_dl)

    if return_error_df:
        return setlist_df, error_setlist_df
    else:
        return setlist_df

def get_setlist_df_from_artist_name(artist_name,
                                    api=get_setlist_fm_api(),
                                    save_to_excel=False,
                                    iteration_limit=None):
    setlist_list_list = get_artist_setlist_lists(artist_name, api, iteration_limit=iteration_limit)
    setlist_df_list = []
    for setlist_list in setlist_list_list:
        temp_setlist_df = get_setlist_df_from_setlist_list(setlist_list,
                                                           return_error_df=False)
        setlist_df_list.append(temp_setlist_df)
    setlist_df = pd.concat(setlist_df_list).drop_duplicates()
    if save_to_excel:
        setlist_df.to_excel(artist_name + ' setlist df __ ' + get_current_dt_str() + '.xlsx')
    return setlist_df
