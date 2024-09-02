from argparse import ArgumentParser
import logging

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

if __name__ == '__main__':
    configure_logging()
    args = parse_args()
    cli(args)
