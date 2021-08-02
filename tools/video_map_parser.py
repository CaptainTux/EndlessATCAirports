import configparser
import re
from pathlib import Path
from xml.dom import minidom

# this script was written by Captain Tux - https://github.com/CaptainTux
# the latest version will be available at https://github.com/AdamJCavanaugh/EndlessATCAirports

# this is a videomap parser for vSTARS sector files
# output is written to video_map_parser_out directory


def write_videomaps(filename, t, line_startindex=0):
    with open(filename, 'r') as f:
        x = minidom.parse(f)

    video_maps = x.getElementsByTagName('VideoMap')
    for video_map in video_maps:
        map_name = video_map.attributes['ShortName'].firstChild.data
        outname = re.sub('[^\w_.)( -]', '', map_name)
        lines = video_map.getElementsByTagName('Elements')[0].getElementsByTagName('Element')
        with open(f'video_map_parser_out/{outname}_{t}.txt', 'w') as f:
            i = line_startindex
            end_lat = ''
            end_lon = ''
            for line in lines:
                try:
                    start_lat = 'N' + line.attributes['StartLat'].firstChild.data
                    start_lon = 'W' + line.attributes['StartLon'].firstChild.data[1:]
                    cont = bool(start_lat == end_lat and start_lon == end_lon)
                    end_lat = 'N' + line.attributes['EndLat'].firstChild.data
                    end_lon = 'W' + line.attributes['EndLon'].firstChild.data[1:]
                    if cont:
                        f.write(f'\t{end_lat}, {end_lon}\n')
                    else:
                        i += 1
                        if t == 'area':
                            f.write(f'\n[area{i}]\n'
                                    f'shape = polygon\n'
                                    f'altitude = 0\n'
                                    f'draw = 1\n'
                                    f'labelpos = 0, 0\n'
                                    f'points = \n'
                                    f'\t{start_lat}, {start_lon}\n'
                                    f'\t{end_lat}, {end_lon}\n')
                        if t == 'line':
                            f.write(f'\nline{i} =\n'
                                    f'\t{start_lat}, {start_lon}\n'
                                    f'\t{end_lat}, {end_lon}\n')
                except KeyError:
                    pass


if __name__ == '__main__':
    config = configparser.ConfigParser(allow_no_value=True)
    config.read('video_map_parser_config.ini')
    Path(f'video_map_parser_out').mkdir(parents=True, exist_ok=True)
    filenames = [a for a in config._sections['filenames']]
    for filename in filenames:
        write_videomaps(filename, 'line', 0)
        write_videomaps(filename, 'area', 0)
