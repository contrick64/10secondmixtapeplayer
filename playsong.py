import mido
import logging
from utils import load_json
from instruments import Instrument

def make_event_list(part):
    instrument = Instrument(part['instrument'])
    note_map = instrument.notes
    instrument_type = instrument.type

    notes = part['notes']
    note_list = {note_map[i]:sound for i,sound in enumerate([note for note in notes]) if sound}
    # make note list one flat list
    note_list = [
        {
            'note': key,
            "instrument_type":instrument_type,
            "instrument":part['instrument'],
            **note
        }
    for key, ul in note_list.items() for note in ul
    ]
    part_event_list = [{"message":'note_on',"time":int(note['start']*1000),**note} for note in note_list]
    part_event_list.extend({"message":'note_off',"time":int(note['end']*1000),**note} for note in note_list)
    return part_event_list

def make_midi_from_events(file, track_event_list, track_index, prev_time=0):
    logging.debug([track.name for track in file.tracks])
    for event in track_event_list:
        # logging.debug(f"prev_time: {prev_time}")
        time = int(event['time'] - prev_time)
        channel = 9 if event['instrument_type'] == 'drums' else track_index # Set channel to 9 for drums
        # logging.debug(f"Adding message {event['message']} with note {event['note']} and time {time} to track {track_index}")
        file.tracks[track_index].append(
            mido.Message(
                event['message'],
                note=event['note'],
                velocity=64 if event['message'] == 'note_on' else 0,
                time=time,
                channel=channel
            )
        )
        prev_time = int(event['time'])
        # logging.debug(f"Added message {event['message']} with note {event['note']} and time {time} to track {track}")
    file.tracks[track_index].append(mido.MetaMessage('end_of_track', time=16000-prev_time))

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

def process_part(part):
    instrument_name = part['instrument']
    logging.debug(f"Processing part for instrument {instrument_name}")
    part_event_list = make_event_list(part)
    part_event_list.sort(key=lambda x: x['time'])
    return part_event_list

def make_track(file, part, i):
    inst_name = part['instrument']
    logging.debug(f"Making midi track {i}: {inst_name}")
    track = mido.MidiTrack()
    file.tracks.append(track)
    instrument = Instrument(inst_name)
    track_name = inst_name
    if any(track.name == track_name for track in file.tracks):
        track_name += " 2"
        logging.debug(f"Track name {inst_name} already exists, renaming to {track_name}")
    track.append(mido.MetaMessage('track_name', name=track_name, time=0))
    logging.debug(f"Adding track {track_name} at index {i}")
    channel = 9 if instrument.type == 'drums' else i
    track.append(mido.Message('program_change', program=instrument.program, channel=channel))
    track = mido.MidiTrack()
    file.tracks.append(track)

def convert_song_to_midi(song):
    if song.get('id',''):
        logging.info(f"Converting song {song['id']} to MIDI")

    file = mido.MidiFile(type=1)
    file.ticks_per_beat = 800

    tracks = [part["instrument"] for part in song['parts']]
    logging.debug(f"Tracks: {tracks}")

    for i, part in enumerate(song['parts']):
        make_track(file, part, i)
        event_list = process_part(part)
        make_midi_from_events(file, event_list, i)

    logging.debug(f"Tracks: {file.tracks}")

    return file

def play_midi_file(file):
    port = mido.open_output('Microsoft GS Wavetable Synth 0')

    try:
        while True:
            for msg in file.play():
                port.send(msg)
    except KeyboardInterrupt:
        port.reset()
        port.close()
