import mido
import logging
from utils import load_json

def make_event_list(instrument, part):
    instrument_type = instrument["type"]
    note_map = [61, 63, 65, 66, 68, 70, 72, 73, 75, 77]
    if instrument_type == "drums":
        note_map = instrument["notes"]
        logging.debug(f"Processing drums part with note map {note_map}")
    if instrument_type == "bass":
        note_map = [int(note)-24 for note in note_map]
        logging.debug(f"Processing bass part with note map {note_map}")
    notes = part['notes']
    note_list = {note_map[i]:sound for i,sound in enumerate([note for note in notes]) if sound}
    # make note list one flat list
    note_list = [
        {
            'note': key,
            "instrument_type":instrument_type,
            "instrument":part['instrument'],
            "program":instrument['program'],
            **note
        }
    for key, ul in note_list.items() for note in ul
    ]
    part_event_list = [{"message":'note_on',"time":int(1+note['start']*1000),**note} for note in note_list]
    part_event_list.extend({"message":'note_off',"time":int(1+note['end']*1000),**note} for note in note_list)
    return part_event_list

def make_midi_from_events(file, track_event_list, track_index, prev_time=0):
    for event in track_event_list:
        # logging.debug(f"prev_time: {prev_time}")
        time = int(event['time'] - prev_time)
        channel = 9 if event['instrument_type'] == 'drums' else track_index # Set channel to 9 for drums        
        file.tracks[track_index].append(
            mido.Message(
                event['message'],
                note=event['note'],
                velocity=64 if event['message'] is 'note_on' else 0,
                time=time,
                channel=channel
            )
        )
        prev_time = int(event['time'])
        # logging.debug(f"Added message {event['message']} with note {event['note']} and time {time} to track {track}")

# def make_midi_from_events(file, event_list):
#     track = mido.MidiTrack()
#     file.tracks.append(track)
#     prev_time = 0
#     for event in event_list:
#         time = int(event['time'] - prev_time)
#         channel = 9 if event['instrument_type'] == 'drums' else 0  # Set channel to 9 for drums
#         track.append(mido.Message('program_change', program=event['program'], time=0, channel=channel))
#         track.append(mido.Message(event['message'], note=event['note'], velocity=64, time=time, channel=channel))
#         prev_time = int(event['time'])

def process_part(part, instruments):
    instrument_name = part['instrument']
    logging.debug(f"Processing part for instrument {instrument_name}")
    if instrument_name in instruments.keys():
        instrument=instruments[instrument_name]
        part_event_list = make_event_list(instrument, part)
        part_event_list.sort(key=lambda x: x['time'])
        return part_event_list

def play_song(song):
    instruments = load_json('instruments.json')
    file = mido.MidiFile(type=1)
    file.ticks_per_beat = 800
    tracks = {part['instrument']:{'index':i} for i, part in enumerate(song['parts'])}
    for key in tracks.keys():
        track = mido.MidiTrack()
        file.tracks.append(track)
        track.append(mido.MetaMessage('track_name', name=key, time=0))
        track_index = file.tracks.index(track)
        logging.debug(f"Adding track {key} at index {track_index}")
        channel = 9 if instruments[key]['type'] == 'drums' else track_index
        track.append(mido.Message('program_change', program=instruments[key]['program'], channel=channel))
        logging.debug(file.tracks[track_index])
    logging.debug(f"Tracks: {file.tracks}")

    for part in song['parts']:
        event_list = process_part(part, instruments)
        make_midi_from_events(file, event_list, tracks[part['instrument']]['index'])
    
    port = mido.open_output('loopMIDI Port 1')
    
    logging.debug(f"Tracks: {file.tracks}")
    
    try:
        while True:
            for msg in file.play():
                port.send(msg)
    except KeyboardInterrupt:
        port.reset()
        port.close()

    return file