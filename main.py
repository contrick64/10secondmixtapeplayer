from argparse import ArgumentParser
import json
import logging

from convertmidi import convert_midifile_to_song
from utils import load_json
from config import configure_logging
from playsong import convert_song_to_midi, play_midi_file
from api import load_song_by_id, load_page_of_songs

def parse_args():
    parser = ArgumentParser()
    subs = parser.add_subparsers(title='commands', dest='command')

    playfile = subs.add_parser('playfile', help='Play or song from a JSON file')
    playfile.add_argument('song_file', help='Path to the JSON file containing the song')

    download = subs.add_parser('download', help='Convert a JSON song file to a MIDI file')
    download.add_argument('song_id', help='Path to the JSON file containing the song')
    download.add_argument('output_file', help='Path to save the MIDI file')

    play = subs.add_parser('play', help='Play songs from the 10 Second Mixtape API')
    play.add_argument('--songid', help='ID of the song to play', default=None, required=False)

    convert = subs.add_parser('convert', help='Convert a MIDI file to a JSON song file')
    convert.add_argument('midi_file', help='Path to the MIDI file to convert')
    convert.add_argument('output_file', help='Path to save the JSON file')
    convert.add_argument('--song_name', help='Name of the song', default='Untitled')
    convert.add_argument('--musician_name', help='Name of the musician', default='contrick.net')

    return parser.parse_args()

def cli(args):
    if args.command == 'playfile':
        song = load_json(args.song_file)
        midi_file = convert_song_to_midi(song)
        play_midi_file(midi_file)
    elif args.command == 'play':
        if args.songid:
            song = load_song_by_id(args.songid)
            logging.debug(song)
            midi_file = convert_song_to_midi(song)
            play_midi_file(midi_file)
        else:
            for song in load_page_of_songs():
                midi_file = convert_song_to_midi(song)
                play_midi_file(midi_file)

    elif args.command == 'download':
        song = load_song_by_id(args.song_id)
        midi_file = convert_song_to_midi(song)
        midi_file.save(args.output_file)

    elif args.command == 'convert':
        song = convert_midifile_to_song(args.midi_file, args.song_name, args.musician_name)
        with open(args.output_file, 'w') as f:
            f.write(json.dumps(song, indent=4))

if __name__ == '__main__':
    configure_logging()
    args = parse_args()
    cli(args)
