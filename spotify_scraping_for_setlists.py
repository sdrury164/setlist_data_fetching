# -*- coding: utf-8 -*-
"""
Created on Sat Dec 31 11:36:02 2022

@author: Steve
"""

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime
import time

import spotipy
# import SpotipyTools as spt
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import spotipy.cache_handler as ch
import get_spotify_credentials as sp_cred

import requests
from requests.exceptions import ReadTimeout

import os
import pickle

from repertorio import Repertorio
import get_setlist_fm_api_key as sfm_key
import setlist_fm_scraping as sfm

def print_dd_tab_formatted(dd, indent=0):
    if type(dd) == dict:
        for key in dd.keys():
            print(' * '*indent + key + ' ' + str(type(dd[key])) + '\n')
            if type(dd[key]==dict):
                print_dd_tab_formatted(dd[key], indent=indent+1)

def get_current_dt_str():
    return datetime.now().strftime('%m-%d-%Y_%H-%M-%S')

'''
Get object used to query Spotify servers
'''
def get_sp_obj():
    scope = 'user-library-read'

    os.environ['SPOTIPY_CLIENT_ID'] = sp_cred.get_credential_dict()['id']
    os.environ['SPOTIPY_CLIENT_SECRET'] = sp_cred.get_credential_dict()['secret']
    os.environ['SPOTIPY_REDIRECT_URI'] = sp_cred.get_credential_dict()['url']

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    sp.trace = False

    return sp

def get_setlist_fm_api():
    api_key = sfm_key.get_api_key()
    api = Repertorio(api_key)
    return api

def get_sp_id_for_setlist_row(row, sp):
    track_name = row['track_name']
    artist_name = row['artist']
    query = str(track_name) + ' ' + artist_name
    query_results = sp.search(query)
    if len(query_results['tracks']['items']) > 0:
        track_id = query_results['tracks']['items'][0]['id']
    else:
        track_id = '%NO_TRACK_ID_FOUND%'
    return track_id

def get_track_feature_df(sp, track_id_list):
    track_feature_dl = []
    for track_id in track_id_list:
        track_feature_dict = sp.audio_features(track_id)[0]
        if type(track_feature_dict) == dict:
            track_feature_dict = sp.audio_features(track_id)[0]
            track_feature_dict['track_id'] = track_id
            track_feature_dl.append(track_feature_dict)
    track_feature_df = pd.DataFrame(track_feature_dl).drop(['type', 'uri', 'track_href', 'analysis_url', 'id'], axis=1)
    return track_feature_df

def get_setlist_df_with_features(artist_name, sp, sfm_api,
                                 setlist_df=pd.DataFrame(),
                                 save_to_excel=True):
    if len(setlist_df) == 0:
        new_setlist_df = sfm.get_setlist_df_from_artist_name(artist_name, sfm_api)
    else:
        new_setlist_df = setlist_df.copy()
    if 'artist' not in new_setlist_df.keys():
        new_setlist_df['artist'] = [artist_name for i in range(len(new_setlist_df))]
    track_df = new_setlist_df[['track_name', 'artist']].drop_duplicates().copy()
    track_df['track_id'] = [get_sp_id_for_setlist_row(track_df.iloc[i], sp) for i in range(len(track_df))]
    track_id_list = list(track_df['track_id'])
    track_feature_df = get_track_feature_df(sp, track_id_list)
    new_setlist_df = new_setlist_df.merge(track_df, on=['track_name', 'artist'])
    new_setlist_df = new_setlist_df.merge(track_feature_df, on='track_id').drop_duplicates()

    if save_to_excel:
        new_setlist_df.to_excel(artist_name + ' __ setlist_df_w_features __ ' + get_current_dt_str() + '.xlsx')

    return new_setlist_df.drop_duplicates()
