# In-Memory Music Playlist

## 1. Problem Statement

Design an in-memory music playlist system that combines song portions from two different sources:

- **DJ Service:** Provides song portions selected by DJs.
- **Recommendation Service:** Provides song portions recommended to users.

The system should generate a playlist by combining portions from both sources based on a configurable mixing ratio.

It should also support filtering songs based on user preferences and limit the number of portions returned.

## 2. Functional Requirements

1. Add song portions from the DJ service.
2. Add song portions from the recommendation service.
3. Support two mixing modes:
   - **EQUAL:** Equal contribution from DJ and recommendation services (1:1).
   - **CUSTOM:** Contribution based on user-defined weights, such as 2:1 or 3:2.
4. Filter song portions using preferred tags.
5. Preserve the insertion order of portions within each source.
6. Generate a playlist containing at most the requested number of song portions.
7. Handle cases where one or both sources run out of portions.
8. Validate timestamps, weights, and mixing configuration.

## 3. Class Design

The implementation uses three main components.

### MixType (Enum)

Defines the supported mixing modes:

- `EQUAL`
- `CUSTOM`

### SongPortion

Represents a playable segment of a song.

| Attribute | Type | Description |
|---|---|---|
| `song_id` | str | Song identifier |
| `start_second` | int | Starting timestamp |
| `end_second` | int | Ending timestamp |
| `tags` | set[str] | Categories associated with the song |

For example:

`SongPortion("song-4", 90, 220, ["rock", "dance"])`

This represents a portion of `song-4` playing from 1 minute 30 seconds to 3 minutes 40 seconds.

### MusicPlaylist

Manages the song collections and generates the final playlist.

**Attributes**

- `mix_type`: Equal or custom mixing mode.
- `dj_weight`: DJ contribution weight.
- `rec_weight`: Recommendation contribution weight.
- `preferred_tags`: Tags used for filtering.
- `dj_songs`: List of DJ song portions.
- `rec_songs`: List of recommended song portions.

**Methods**

| Method | Responsibility |
|---|---|
| `add_dj_song()` | Adds a DJ song portion |
| `add_recommended_song()` | Adds a recommended song portion |
| `filter_songs()` | Filters portions using preferred tags |
| `get_playlist()` | Generates the final playlist |

## 4. Design Approach

### Step 1: Store Song Portions

Maintain two separate lists:

- `dj_songs`
- `rec_songs`

Each list preserves the order in which song portions are added.

### Step 2: Filter Based on User Preferences

Before mixing, filter both lists using the preferred tags.

A song portion is eligible when at least one of its tags matches the user's preferred tags.

For example:

- Preferred tags: `{"rock"}`
- Song tags: `{"rock", "dance"}`
- Result: Included

If the preferred-tags set is empty, no filtering is applied.

### Step 3: Determine Mixing Weights

For `EQUAL` mixing, the system uses:

- DJ weight = 1
- Recommendation weight = 1

For `CUSTOM` mixing, the configured weights are used.

For example, a 2:1 ratio targets approximately two DJ portions for every recommendation portion, when both sources have enough eligible portions.

### Step 4: Generate the Playlist

The system uses two indexes and two counters:

- `dj_index`: Next DJ portion to select.
- `rec_index`: Next recommendation portion to select.
- `dj_count`: Number of DJ portions already selected.
- `rec_count`: Number of recommendation portions already selected.

At each iteration, the algorithm calculates which source is further behind its ideal weighted contribution.

The deficit calculations are:

```python
dj_deficit = (
    next_position * dj_weight
    - dj_count * total_weight
)

rec_deficit = (
    next_position * rec_weight
    - rec_count * total_weight
)
```

The source with the larger deficit is selected.

If both deficits are equal, the DJ source is selected first.

If one source is exhausted, the system continues using the other available source.

The process stops when the maximum requested number of portions is reached or both sources are exhausted.

## 5. Example 1 — Equal Mixing

**Configuration**

```python
playlist = MusicPlaylist(
    MixType.EQUAL, 1, 1, ["rock"]
)
```

**Input**

```python
playlist.add_dj_song("song-4", 90, 220, ["rock", "dance"])
playlist.add_dj_song("song-9", 15, 75, ["rock"])

playlist.add_recommended_song("song-12", 30, 150, ["rock", "chill"])
playlist.add_recommended_song("song-15", 45, 105, ["rock"])

print(playlist.get_playlist(4))
```

**Expected Output**

```text
DJ,song-4,90,220
RECOMMENDATION,song-12,30,150
DJ,song-9,15,75
RECOMMENDATION,song-15,45,105
```

The final playlist contains two DJ portions and two recommendation portions.

All portions match the preferred tag `rock`.

## 6. Example 2 — Custom Mixing

**Configuration**

```python
playlist = MusicPlaylist(
    MixType.CUSTOM, 2, 1, []
)
```

**Input**

```python
playlist.add_dj_song("track-A", 0, 50, ["dance"])
playlist.add_dj_song("track-B", 80, 160, ["pop"])
playlist.add_dj_song("track-C", 20, 100, ["rock"])
playlist.add_dj_song("track-D", 120, 210, ["electronic"])

playlist.add_recommended_song("track-X", 10, 70, ["acoustic"])
playlist.add_recommended_song("track-Y", 40, 130, ["jazz"])

print(playlist.get_playlist(6))
```

**Expected Output**

```text
DJ,track-A,0,50
RECOMMENDATION,track-X,10,70
DJ,track-B,80,160
DJ,track-C,20,100
RECOMMENDATION,track-Y,40,130
DJ,track-D,120,210
```

The final playlist contains four DJ portions and two recommendation portions, satisfying the 2:1 ratio.

Since the preferred-tags collection is empty, no song portions are filtered out.

## 7. Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Both sources are empty | Return an empty playlist |
| No portions match preferred tags | Return an empty playlist |
| Preferred tags are empty | Include all portions |
| Only DJ portions are available | Select from DJ |
| Only recommendation portions are available | Select from recommendation |
| Maximum portions is zero | Return an empty playlist |
| Maximum exceeds available portions | Return all eligible portions |
| Invalid timestamps | Raise `ValueError` |
| Negative or zero weights | Raise `ValueError` |
| Invalid mixing type | Raise `ValueError` |

Duplicate song IDs are allowed because multiple portions of the same song can be valid entries.

## 8. Time and Space Complexity

Let:

- `D` = number of DJ portions.
- `R` = number of recommendation portions.
- `K` = maximum number of requested portions.

**Time Complexity: O(D + R + K)**

Filtering examines the DJ and recommendation lists, and playlist generation selects at most `K` portions.

This assumes tag-intersection operations are bounded in cost.

**Space Complexity: O(D + R + K)**

Additional space is used to store filtered lists and the resulting playlist.

## 9. Object-Oriented Design Concepts

**Encapsulation:** `SongPortion` stores information about a song segment, while `MusicPlaylist` manages playlist operations.

**Composition:** `MusicPlaylist` contains collections of `SongPortion` objects.

**Enums:** `MixType` defines the supported mixing modes and avoids relying on arbitrary string values throughout the implementation.

**Separation of Concerns:** Song representation, filtering, and weighted mixing have distinct responsibilities.

## 10. Possible Improvements

- Introduce the Strategy pattern to support additional mixing algorithms.
- Add a dedicated filtering interface for more complex user preferences.
- Support filtering by artist, genre, or duration.
- Add unit tests for mixing behavior and edge cases.
- Support concurrent additions from multiple services.
- Generate playlists based on total playback duration instead of portion count.

## 11. How to Run

**Requirements:** Python 3.9 or later.

Run:

```bash
python music_playlist.py
```

To see example output, add the sample usage from Sections 5 and 6 to the Python file or a separate test script.

## 12. Key Learnings

This problem demonstrates:

- Designing classes based on responsibilities.
- Using composition to manage related objects.
- Implementing weighted scheduling.
- Filtering data using Python sets.
- Maintaining insertion order across multiple data sources.
- Handling edge cases and input validation.
- Analyzing time and space complexity.

**Topics:** Python, Low-Level Design, Object-Oriented Programming, Enums, Weighted Scheduling, Filtering, In-Memory Data Structures.
