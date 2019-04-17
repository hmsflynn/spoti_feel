import spotipy
import spotipy.util as util
import pandas
import random

# AUTHENTIFICATION INFO
client_id = 
client_secret = 
username = 
scope = 'user-library-read user-top-read playlist-modify-public user-follow-read'
redirect_uri = 'http://localhost:888/callback'


def authenticate_spotify(token):
    print("...connecting to Spotify...")
    sp = spotipy.Spotify(auth=token)
    print('Done!')
    return sp

def top_artists(sp):
    print('...determining your top artists..')
    top_artist_names=[]
    top_artist_uris=[]

    ranges = ['short_term','medium_term','long_term']
    for r  in ranges:
        top_artists_all_data = sp.current_user_top_artists(limit=100, time_range=r)
        top_artists_data = top_artists_all_data['items']
        for artist_data in top_artists_data:
            top_artist_names.append(artist_data['name'])
            top_artist_uris.append(artist_data['uri'])
    print('Done!')
    return top_artist_uris

def aggregate_top_tracks(sp, top_artist_uris):
    print("...getting top tracks...")
    top_tracks_uri=[]
    for artist in top_artist_uris:
        top_tracks_all_data=sp.artist_top_tracks(artist)
        top_tracks_data = top_tracks_all_data['tracks']
        for track_data in top_tracks_data:
            top_tracks_uri.append(track_data['uri'])
    print('Done!')
    return top_tracks_uri

def select_tracks(sp, top_tracks_uri,mood):
    print("...selecting tracks!")
    random.shuffle(top_tracks_uri)
    selected_tracks_uri=[]
    def group(seq, size):
        for pos in range(0, len(seq), size):
            return (seq[pos:pos + size])
    for tracks in list(group(top_tracks_uri, 100)):
        tracks_all_data = sp.audio_features(tracks)
        for track_data in tracks_all_data:
            try:
                if mood < 0.10:
                    if (0 <= track_data["valence"] <= (mood + 0.15)
                    #and track_data["danceability"] <= (mood*8)
                    and track_data["energy"] <= (mood*10)):
                        selected_tracks_uri.append(track_data["uri"])					
                elif 0.10 <= mood < 0.25:						
                    if ((mood - 0.075) <= track_data["valence"] <= (mood + 0.075)
                    #and track_data["danceability"] <= (mood*4)
                    and track_data["energy"] <= (mood*5)):
                        selected_tracks_uri.append(track_data["uri"])
                elif 0.25 <= mood < 0.50:											
                    if ((mood - 0.085) <= track_data["valence"] <= (mood + 0.085)
                    and track_data["danceability"] <= (mood*3)
                    and track_data["energy"] <= (mood*3.5)):
                        selected_tracks_uri.append(track_data["uri"])
                elif 0.50 <= mood < 0.75:						
                    if ((mood - 0.075) <= track_data["valence"] <= (mood + 0.075)
                    #and track_data["danceability"] >= (mood/2.5)
                    and track_data["energy"] >= (mood/2)):
                        selected_tracks_uri.append(track_data["uri"])
                elif 0.75 <= mood < 0.90:						
                    if ((mood - 0.075) <= track_data["valence"] <= (mood + 0.075)
                    #and track_data["danceability"] >= (mood/2)
                    and track_data["energy"] >= (mood/1.75)):
                        selected_tracks_uri.append(track_data["uri"])
                elif mood >= 0.90:
                    if ((mood - 0.15) <= track_data["valence"] <= 1
                    #and track_data["danceability"] >= (mood/1.75)
                    and track_data["energy"] >= (mood/1.5)):
                        selected_tracks_uri.append(track_data["uri"])
            except TypeError as te:
                continue
    print('Done!')
    return selected_tracks_uri

def create_playlist(sp, selected_tracks_uri,mood):
    print("...creating playlist..")
    user_all_data = sp.current_user()
    user_id = user_all_data['id']

    playlist_all_data = sp.user_playlist_create(user_id, "Spotifind v1.0: Mood " + str(mood))
    playlist_id=playlist_all_data['id']

    random.shuffle(selected_tracks_uri)
    sp.user_playlist_add_tracks(user_id, playlist_id, selected_tracks_uri[0:40])
    print('Done!')

def spotifind(mood):
    mood=float(mood)
    token = util.prompt_for_user_token(username, scope, client_id, client_secret,redirect_uri)
    sp = authenticate_spotify(token)
    top_artist_uris = top_artists(sp)
    top_tracks_uri = aggregate_top_tracks(sp, top_artist_uris)
    selected_tracks_uri = select_tracks(sp, top_tracks_uri,mood)
    create_playlist(sp, selected_tracks_uri,mood)

spotifind(.2)

# cache_token = token.get_access_token()
#spotify = spotipy.Spotify(token)

#results1 = spotify.user_playlist_tracks(username,
#    playlist, limit=100, offset=0)
#tracks = results1['items']
#df = pandas.DataFrame(tracks[])
#df.to_csv('tracks.csv')
# redirect='http://localhost:8888'
