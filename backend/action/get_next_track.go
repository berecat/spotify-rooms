package action

import (
	"github.com/go-redis/redis/v8"
	"github.com/timfuhrmann/spotify-rooms/backend/entity"
	"time"
)

func GetNextTrack(rdb *redis.Client, rid string) (*entity.Track, error)  {
	playlist, err := GetPlaylistByRoom(rdb, rid)
	if err != nil {
		return nil, err
	}

	if len(playlist) == 0 {
		return nil, nil
	}

	var track *entity.Track
	for _, newTrack := range playlist {
		if track == nil {
			track = newTrack
		} else {
			date := track.Date.UnixNano() / int64(time.Millisecond)
			newDate := newTrack.Date.UnixNano() / int64(time.Millisecond)
			if newDate < date {
				track = newTrack
			}
		}
	}

	return track, err
}