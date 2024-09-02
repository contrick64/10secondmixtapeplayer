import logging
import math
import mido
from instruments import Instrument

def convert_midifile_to_song(filepath: str, song_name: str, musician_name: str):
    song:dict = {
        "name": song_name,
        "id": None,
        "parts": [],
        "length": 10,
        "scaleType": "Major"
    }

    file = mido.MidiFile(filepath)
    logging.debug(f"file length: {file.length}")

    logging.debug(f"file tracks: {[track.name for track in file.tracks]}")

    for track in file.tracks:
        if not track.name:
            logging.debug(f"Skipping track with no name: {track}")
            continue
        logging.debug(f"Processing track {track.name}")
        instrument = Instrument(track.name)
        part:dict = {
            "name": musician_name,
            "id": None,
            "instrument": instrument.name,
            "notes": [],
            "scaleType": "Major"
        }
        part["notes"].extend([] for _ in range(18))
        # logging.debug(f"part: {part}")

        stack:list[tuple] = []
        abstime:int = 0

        for msg in track:
            abstime += msg.time
            if msg.type not in ['note_on', 'note_off']:
                continue

            note_i = instrument.notes.index(msg.note)
            if note_i == -1:
                raise Exception(f"Invalid note {msg.note} for instrument {instrument.name}")

            # Add the note to the part
            if msg.type == 'note_on':
                stack.append((msg,abstime))
            elif msg.type == 'note_off':
                if len(stack) > 0:
                    note_on_msg = stack.pop()
                    start_time = math.floor((note_on_msg[1]/1000)*8)/8
                    end_time = math.floor((abstime/1000)*8)/8
                    if start_time > 16 or end_time > 16:
                        raise Exception(f"MIDI file is too long! Must be 10 seconds or less: {start_time} - {end_time}")
                    note = {"start": start_time, "end": end_time}
                    part["notes"][note_i].append(note)
                    # logging.debug(f"note: {note}")
                else:
                    # Handle the case where a note_off message is encountered without a corresponding note_on message
                    # This could indicate a malformed MIDI file
                    raise Exception("Invalid MIDI file: note_off message without corresponding note_on message")
        song["parts"].append(part)

    return song
