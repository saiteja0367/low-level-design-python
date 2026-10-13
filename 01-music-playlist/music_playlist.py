from enum import Enum


class MixType(Enum):
    EQUAL = "EQUAL"
    CUSTOM = "CUSTOM"


class SongPortion:
    def __init__(
        self,
        song_id: str,
        start_second: int,
        end_second: int,
        tags: list[str]
    ):
        if start_second < 0 or end_second <= start_second:
            raise ValueError("Invalid song timestamps")

        self.song_id = song_id
        self.start_second = start_second
        self.end_second = end_second
        self.tags = set(tags)


class MusicPlaylist:
    def __init__(
        self,
        mix_type: MixType,
        dj_weight: int,
        recommendation_weight: int,
        preferred_tags: list[str]
    ):
        if isinstance(mix_type, str):
            mix_type = MixType(mix_type)

        if not isinstance(mix_type, MixType):
            raise ValueError("Invalid mix type")

        if dj_weight <= 0 or recommendation_weight <= 0:
            raise ValueError("Weights must be positive")

        self.mix_type = mix_type

        if mix_type == MixType.EQUAL:
            self.dj_weight = 1
            self.rec_weight = 1
        else:
            self.dj_weight = dj_weight
            self.rec_weight = recommendation_weight

        self.preferred_tags = set(preferred_tags)

        self.dj_songs = []
        self.rec_songs = []

    def add_dj_song(self, song_id, start_second, end_second, tags):
        song = SongPortion(song_id, start_second, end_second, tags)
        self.dj_songs.append(song)

    def add_recommended_song(self, song_id, start_second, end_second, tags):
        song = SongPortion(song_id, start_second, end_second, tags)
        self.rec_songs.append(song)

    def filter_songs(self, songs):
        if not self.preferred_tags:
            return songs.copy()

        return [
            song for song in songs
            if song.tags & self.preferred_tags
        ]

    def get_playlist(self, maximum_song_portions: int):
        if maximum_song_portions < 0:
            raise ValueError("Maximum must be nonnegative")

        dj = self.filter_songs(self.dj_songs)
        rec = self.filter_songs(self.rec_songs)

        playlist = []

        dj_index = 0
        rec_index = 0

        dj_count = 0
        rec_count = 0

        total_weight = self.dj_weight + self.rec_weight

        while len(playlist) < maximum_song_portions:
            dj_available = dj_index < len(dj)
            rec_available = rec_index < len(rec)

            if not dj_available and not rec_available:
                break

            if not dj_available:
                choose_dj = False

            elif not rec_available:
                choose_dj = True

            else:
                next_position = dj_count + rec_count + 1

                dj_deficit = (
                    next_position * self.dj_weight
                    - dj_count * total_weight
                )

                rec_deficit = (
                    next_position * self.rec_weight
                    - rec_count * total_weight
                )

                choose_dj = dj_deficit >= rec_deficit

            if choose_dj:
                song = dj[dj_index]

                playlist.append(
                    f"DJ,{song.song_id},"
                    f"{song.start_second},{song.end_second}"
                )

                dj_index += 1
                dj_count += 1

            else:
                song = rec[rec_index]

                playlist.append(
                    f"RECOMMENDATION,{song.song_id},"
                    f"{song.start_second},{song.end_second}"
                )

                rec_index += 1
                rec_count += 1

        return playlist
