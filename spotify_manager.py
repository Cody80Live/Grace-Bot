import spotipy
from spotipy.oauth2 import SpotifyOAuth
from modules.replit_connector import ReplitConnector

class SpotifyManager:
    def __init__(self):
        self.sp = None
        self._init_spotify()
    
    def _init_spotify(self):
        try:
            creds = ReplitConnector.get_spotify_credentials()
            
            self.sp = spotipy.Spotify(auth=creds['access_token'])
            print("✅ Spotify initialized")
        except Exception as e:
            print(f"⚠️ Spotify initialization warning: {e}")
    
    def get_user_playlists(self):
        if not self.sp:
            return {'error': 'Spotify not connected'}
        
        try:
            playlists = self.sp.current_user_playlists(limit=10)
            return {
                'playlists': [
                    {'name': p['name'], 'id': p['id'], 'tracks': p['tracks']['total']}
                    for p in playlists['items']
                ]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def create_playlist(self, name, description=''):
        if not self.sp:
            return {'error': 'Spotify not connected'}
        
        try:
            user_id = self.sp.current_user()['id']
            playlist = self.sp.user_playlist_create(
                user_id,
                name,
                public=False,
                description=description
            )
            return {
                'success': True,
                'playlist_id': playlist['id'],
                'name': playlist['name']
            }
        except Exception as e:
            return {'error': str(e)}
    
    def search_and_add_tracks(self, playlist_id, search_queries):
        if not self.sp:
            return {'error': 'Spotify not connected'}
        
        try:
            track_uris = []
            
            for query in search_queries:
                results = self.sp.search(q=query, type='track', limit=1)
                if results['tracks']['items']:
                    track_uris.append(results['tracks']['items'][0]['uri'])
            
            if track_uris:
                self.sp.playlist_add_items(playlist_id, track_uris)
            
            return {
                'success': True,
                'tracks_added': len(track_uris)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_recommendations(self, genre='indie', limit=5):
        if not self.sp:
            return {'error': 'Spotify not connected'}
        
        try:
            results = self.sp.search(q=f'genre:{genre}', type='track', limit=limit)
            tracks = [
                {'name': t['name'], 'artist': t['artists'][0]['name'], 'uri': t['uri']}
                for t in results['tracks']['items']
            ]
            return {'tracks': tracks}
        except Exception as e:
            return {'error': str(e)}
