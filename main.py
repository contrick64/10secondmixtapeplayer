from playsong import play_song
from utils import load_json
from config import configure_logging

def main():
    song = load_json('../examples/song.json')
    midi_file = play_song(song)
    midi_file.save('../output.mid')

if __name__ == '__main__':
    configure_logging()
    main()