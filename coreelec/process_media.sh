#!/bin/bash
# Receives rating_key and media_type as arguments

RATING_KEY=$1
MEDIA_TYPE=$2

sqlite3 /storage/.kodi/userdata/Database/plex.db --readonly "SELECT kodi_id from $MEDIA_TYPE WHERE plex_id = '$RATING_KEY';"

# Return 0 for success
exit 0