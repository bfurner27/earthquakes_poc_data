## Setup & Run
1. clone the repo
1. create a folder for data `mkdir data`
1. place geojson files into the data directory
1. run this command from within the docker container
1. run the command to upload Country data `python3 upload.py --file-path data/Countries.geojson --file-type country`
1. run the command to upload Earthquake data `python3 upload.py --file-path data/Earthquakes.geojson --file-type earthquake`
\* Note: if you try to upload the file more than once currently it will duplicate the data, to avoid duplicate data only run the above commands once