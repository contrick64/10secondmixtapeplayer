import logging

from utils import load_json

instruments = load_json('instruments.json')

def map_notes(instrument_type):
    note_map = [61, 63, 65, 66, 68, 70, 72, 73, 75, 77, 78, 80, 82, 84, 85]
    if instrument_type == "drums":
        raise Exception("Drums not mapped by Instrument()!")
    if instrument_type == "bass":
        note_map = [int(note)-24 for note in note_map]
        logging.debug(f"Processing bass part with note map {note_map}")
    return note_map

class Instrument():
    def __init__(self,name):
        inst = instruments.get(name, None)
        if not inst:
            raise Exception(f"Invalid instrument {name}")
        self.notes = inst.get("notes", None)
        if not self.notes:
            self.notes = map_notes(inst["type"])
        self.name = name
        self.type = inst["type"]
        self.program = inst["program"]