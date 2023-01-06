# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 16:34:32 2023

@author: Steve
"""

import numpy as np
import pandas as pd

import argparse

from setlist_fm_scraping import *
from spotify_scraping_for_setlists import *

def main(artist_name):
    sp = get_sp_obj()
    sfm_api = get_setlist_fm_api()
    setlist_df = get_setlist_df_with_features(artist_name,
                                              sp, sfm_api)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get artist name for data collection')
    parser.add_argument('--artist_name', metavar='path',
                        required=True, help='Name of artist to obtain data for')
    args = parser.parse_args()

    main(args.artist_name)
