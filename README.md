## Setup & Run
1. clone the repo
1. create a folder for data `mkdir data`
1. place geojson files into the data directory
1. (download earthquakes) url https://www.dropbox.com/scl/fi/1spnzsolti8kapc6a9r8r/Earthquakes.geojson?rlkey=txd77hurv4ewcsskdyplkjxmz&dl=1
1. (download countries) url https://www.dropbox.com/scl/fi/3p6u0sq8ik6grdoihfcvt/Countries.geojson?rlkey=l9bbrrb14shtche60okgilqt7&dl=1
1. run the following commands from within the docker container `docker compose run data bash`
1. run the command to upload Country data `python3 upload.py --file-path data/Countries.geojson --data-type country`
1. run the command to upload Earthquake data `python3 upload.py --file-path data/Earthquakes.geojson --data-type earthquake`
\* Note: if you try to upload the file more than once currently it will duplicate the data, to avoid duplicate data only run the above commands once
