from time import sleep
import mido
import json
import logging

def configure_logging():
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('__main__').setLevel(logging.DEBUG)

def load_json(file):
    with open(file) as f:
        data = json.load(f)
    return data

def make_tracks(file:mido.MidiFile, event_list):
    tracks = {}
    for event in event_list:
        if not tracks.get(event['instrument'],''):
            tracks[event['instrument']] = {'program':event['program'],'index':len(file.tracks)}
            file.add_track(event['instrument'])
            file.tracks[-1].append(mido.Message('program_change', program=event['program'], time=0))
    return tracks

def make_event_list(instrument, part):
    instrument_type = instrument["type"]
    note_map = [61, 63, 65, 66, 68, 70, 72, 73, 75, 77]
    if instrument_type == "drums":
        note_map = instrument["notes"]
        logging.debug(f"Processing drums part with note map {note_map}")
    if instrument_type == "bass":
        note_map = [int(note)-12 for note in note_map]
    program = instrument["program"]
    notes = part['notes']
    note_list = {note_map[i]:sound for i,sound in enumerate([note for note in notes]) if sound}
    # make note list one flat list
    note_list = [
        {
            'note': key,
            'program':program,
            "instrument_type":instrument_type,
            "instrument":part['instrument'],
            **note
        }
    for key, ul in note_list.items() for note in ul
    ]
    part_event_list = [{"message":'note_on',"time":int(note['start']*1000),**note} for note in note_list]
    part_event_list.extend({"message":'note_off',"time":int(note['end']*1000),**note} for note in note_list)
    return part_event_list

# def make_midi_from_events(file, event_list, prev_time=0):
#     tracks = make_tracks(file, event_list)
#     logging.debug(f"Tracks: {tracks}")

#     for event in event_list:
#         # logging.debug(f"prev_time: {prev_time}")
#         time = int(event['time'] - prev_time)
#         channel = 9 if event['instrument_type'] == 'drums' else 0  # Set channel to 9 for drums        
#         track = tracks.get(event['instrument'],'')
#         if track:
#             file.tracks[track['index']].append(mido.Message(event['message'], note=event['note'], velocity=64, time=time, channel=channel))
#             prev_time = int(event['time'])
#         # logging.debug(f"Added message {event['message']} with note {event['note']} and time {time} to track {track} {event['instrument']}")

def make_midi_from_events(file, event_list):
    track = mido.MidiTrack()
    file.tracks.append(track)
    prev_time = 0
    for event in event_list:
        time = int(event['time'] - prev_time)
        channel = 9 if event['instrument_type'] == 'drums' else 0  # Set channel to 9 for drums
        track.append(mido.Message('program_change', program=event['program'], time=0, channel=channel))
        track.append(mido.Message(event['message'], note=event['note'], velocity=64, time=time, channel=channel))
        prev_time = int(event['time'])


def main():
    instruments = load_json('instruments.json')
    song = load_json('../examples/song.json')
    file = mido.MidiFile()
    file.ticks_per_beat = 1800

    event_list = []
    for part in song['parts']:
        instrument_name = part['instrument']
        logging.debug(f"Processing part for instrument {instrument_name}")
        if instrument_name in instruments.keys():
            instrument=instruments[instrument_name]
            part_event_list = make_event_list(instrument, part)
            # logging.trace(f"Notes: {note_list}")
            # logging.debug(f"Events: {part_event_list}")
            event_list.extend(part_event_list)
    event_list.sort(key=lambda x: x['time'])
    # event_list_copy = event_list.copy()
    # event_list.extend({'time':int(event['time']+16000), **event} for event in event_list_copy)
    make_midi_from_events(file, event_list)

    file.save('../output.mid')
    
if __name__ == '__main__':
    configure_logging()
    main()