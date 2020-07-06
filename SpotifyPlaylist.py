import os
import sys
import json
import spotipy
import webbrowser
import math
import csv
import spotipy.util as util
from json.decoder import JSONDecodeError

#Get username
username = sys.argv[1]
scope = 'user-read-private user-read-playback-state user-modify-playback-state playlist-modify-public playlist-modify-private user-top-read'

# Erase cache and prompt for permission
try:
    token = util.prompt_for_user_token(username, scope)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope)

# Create spotifyObject
spotifyObject = spotipy.Spotify(auth=token)

# Get current device
devices = spotifyObject.devices()
deviceID = devices['devices'][0]['id']

#User info
user = spotifyObject.current_user()
displayName = user['display_name']
followers = user['followers']['total']
userID = user['id']

print()
playlist_id = input("What is the playlist ID ? ")
print()

recommendedSongName = []
recommendedSongURI = []
commonSongs = []

#Funtions used in the program
#A function that appends adds recommended songs to the respective lists
def printSongNames (recommendList,recommendedSongName, recommendedSongURI, commonSongs):

    recomindex =0
    for x in recommendList:
        if (recommendList[recomindex]['name'] not in recommendedSongName): # To weed out dublicate
            recommendedSongName.append(recommendList[recomindex]['name'])
            recommendedSongURI.append(recommendList[recomindex]['uri']) # Add URI
        else:
            if(recommendList[recomindex]['name'] not in commonSongs):
                commonSongs.append(recommendList[recomindex]['name'])
        recomindex+=1

#def make playlist
#A function that makes a playlist with specified songs
def makeplaylist(userID,trackURI,playlistId):
    #Add songs
    while True:
        songSelection = input("Enter a song number to add to the playlist (a for all songs and x to exit): ")
        if songSelection == "x":
            break
        elif songSelection =="a":
            tracklen = len(trackURI)
            if (tracklen < 100):
                spotifyObject.user_playlist_add_tracks(userID,playlistId,trackURI)
                print()
                print("A playlist with all the songs has been created")
                break
            else:
                tindex = math.ceil(tracklen/100)
                start = 0
                end = 100
                for x in range(tindex):
                    spotifyObject.user_playlist_add_tracks(userID,playlistId,trackURI[start:end])
                    start+= 100
                    end+=100
                print()
                print("A playlist with all the songs has been created")
                break
        else:
            trackSelectionList = []
            trackSelectionList.append(trackURI[int(songSelection)])
            spotifyObject.user_playlist_add_tracks(userID,playlistId,trackSelectionList)

#Getting a list of songs in the current playlist
currentPlaylistSongsURI = []
currentPlaylistSearch = spotifyObject.playlist_tracks(playlist_id)
currentPlaylistSearch = currentPlaylistSearch['items']

Playlistindex = 0
for item in currentPlaylistSearch:
    currentPlaylistSongsURI.append(currentPlaylistSearch[Playlistindex]['track']['uri'])
    print(currentPlaylistSearch[Playlistindex]['track']['name'])
    Playlistindex+=1
print()

#Getting user top artists and top songs
#Variables for top artists
topArtistsNames =[]
topArtistsURIs =[]

#Getting top artist for all three time period
for x in range (3):
    if (x == 0):
        topArtists = spotifyObject.current_user_top_artists(10,0,'short_term')
    elif(x == 1):
        topArtists = spotifyObject.current_user_top_artists(10,0,'medium_term')
    else:
        topArtists = spotifyObject.current_user_top_artists(10,0,'long_term')
    topArtists = topArtists['items']
    topArtistIndex = 0
    for items in topArtists:
        if (topArtists[topArtistIndex]['name'] not in topArtistsNames):
            topArtistsNames.append(topArtists[topArtistIndex]['name'])
            print(topArtists[topArtistIndex]['name'])
            topArtistsURIs.append(topArtists[topArtistIndex]['uri'])
        topArtistIndex += 1
    print()

#variables for top songs
topSongsNames =[]
topSongsURIs =[]

#Getting top artist for all three time period
for x in range (3):
    if (x == 0):
        topSongs = spotifyObject.current_user_top_tracks(20,0,'short_term')
    elif(x == 1):
        topSongs = spotifyObject.current_user_top_tracks(20,0,'medium_term')
    else:
        topSongs = spotifyObject.current_user_top_tracks(20,0,'long_term')
    topSongs = topSongs['items']
    topSongsIndex = 0
    for items in topSongs:
        topSongsNames.append(topSongs[topSongsIndex]['name'])
        print(topSongs[topSongsIndex]['name'])
        topSongsURIs.append(topSongs[topSongsIndex]['uri'])
        topSongsIndex += 1
    print()

#Generate Recommendations
recommendedSongName = []
recommendedSongURI = []
lstart = 0
lend = 5
printIndex = 0

#Generate Recommendations using current tracks in playlist
tracklength= len(currentPlaylistSongsURI)
tindex =math.ceil(tracklength/5)
for x in range(tindex):
    recommendSongs = spotifyObject.recommendations(seed_tracks = currentPlaylistSongsURI[lstart:lend])
    recommendSongs = recommendSongs['tracks']
    printSongNames(recommendSongs, recommendedSongName, recommendedSongURI, commonSongs)
    lstart+=5
    lend+=5

#Generate Recommendations using top tracks
lstart1 = 0
lend1 = 5
lim = 10
for x in range(12):
    if (x > 8):
        lim = 4
    recommendSongs = spotifyObject.recommendations(seed_tracks = topSongsURIs[lstart1:lend1], limit = lim)
    recommendSongs = recommendSongs['tracks']
    printSongNames(recommendSongs, recommendedSongName, recommendedSongURI, commonSongs)
    lstart1+=5
    lend1+=5

#Generate Recommendations using top artist
lstart2 = 0
lend2 = 5
lim1 = 5
tracklength= len(topArtistsURIs)
tindex1 =math.ceil(tracklength/5)
for x in range(tindex1):
    if (x > 8):
        lim1 = 2
    recommendSongs = spotifyObject.recommendations(seed_artists = topArtistsURIs[lstart2:lend2], limit = lim)
    recommendSongs = recommendSongs['tracks']
    printSongNames(recommendSongs, recommendedSongName, recommendedSongURI, commonSongs)
    lstart2+=5
    lend2+=5

#Adjusting the recommened list
checkindex = 0
for x in recommendedSongName:
    songname = recommendedSongName[checkindex]
    if ((songname.find('mix') != -1) or (songname.find('MIX')!=-1) or (songname.find('Mix')!= -1)):
        print (recommendedSongName[checkindex])
        recommendedSongName.pop(checkindex)
        recommendedSongURI.pop(checkindex)
    checkindex+=1

print()
print("Here are the recommended songs")
printIndex = 0
for x in recommendedSongName:
    print (str(printIndex)+ ' ' + x) # Print name
    printIndex+=1

print()
print("Here are the songs that occured more than once")
for x in commonSongs:
    print (x)

#add songs to cvs of Songs in the playlist
with open('SongList.csv','a') as f:
    thewrite = csv.writer(f)

    csvIndex = 0
    for x in range (len(recommendedSongName)):
        thewrite.writerow([recommendedSongName[csvIndex]])
        csvIndex+= 1

makeplaylist(userID,recommendedSongURI,playlist_id)
