# setlist_data_fetching
Code and script that can be used to fetch setlist data for an artist from setlist.fm as well as track features for songs in setlists from Spotify

# LIBRARIES USED


# SETUP
To run this code, Spotify and setlist.fm developer account credentials are required. These can be obtained for free by any user with an account on these services by following the instructions in these links:

https://developer.spotify.com/dashboard/

https://api.setlist.fm/docs/1.0/index.html

Once you have developer credentials, the get_setlist_fm_api_key.py file must be modified by replacing YOUR-SETLISTFM-API-KEY in the get_api_key() function with your setlist.fm API key and in get_spotify_credentials.py the dictionary values in the function get_credential_dict() must be replaced with your Spotify developer credentials.

# RUNNING THE CODE
Once setup is complete, 
