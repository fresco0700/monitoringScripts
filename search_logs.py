import argparse
from datetime import datetime, timedelta

def search_logs(file_name, seconds, phrase):
    time_limit = datetime.now() - timedelta(seconds=seconds)
    with open(file_name, 'r') as file:
        for line in file:
            if phrase in line:
                time_str = line.split()[0] + ' ' + line.split()[1] # assume date and time are the first two elements in each line
                time_of_error = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                if time_of_error > time_limit:
                    print(line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file_name', help='Log file name')
    parser.add_argument('seconds', type=int, help='Number of seconds')
    parser.add_argument('phrase', help='Phrase to search for')
    args = parser.parse_args()

    search_logs(args.file_name, args.seconds, args.phrase)
