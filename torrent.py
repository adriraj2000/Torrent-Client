
import sys
import logging
import os
import bencodepy
import decoding

# general torrent settings
torrent_settings = {
    "max_d_speed": 0,
    "max_u_speed": 0,
    "pieces_downloaded": 0,
    "download_location": os.getcwd()+"/",
    "upload_location": ""
}

if(len(sys.argv) < 2):
    print("Invalid arguments")
    sys.exit(1)
else:
    if(not os.path.isfile(sys.argv[1])):
        raise Exception()
    try:
        for i in range(2, len(sys.argv), 2):
            if(sys.argv[i] == '-d'):
                print(int(sys.argv[i+1]))
                torrent_settings['max_d_speed'] = int(sys.argv[i+1])
            if(sys.argv[i] == '-l'):
                if(os.path.isdir(sys.argv[i+1])):
                    torrent_settings["download_location"] = sys.argv[i+1] + "/"
                else:
                    raise Exception()
    except Exception as e:
        logging.exception(e)
        print("Invalid args")
        sys.exit(1)

# Decoding the bencoded torrent file and extracting the metadata
f = open(sys.argv[1], "rb")  # Read in buffer mode
data = bencodepy.decode(f.read())

metadata = {}
for key, val in data.items():
    metadata[key.decode()] = val

final_metadata = decoding.decode_torrent(sys.argv[1])
