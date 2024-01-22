from argparse import ArgumentParser, Namespace
from abc import ABC, abstractmethod
from json import loads
from requests import post
from uuid import uuid4
from re import compile


class ParseGeoJsonFile(ABC):
    filePath: str
    buffer: list
    bufferSize: int
    entryCount: int

    def __init__(self, filePath: str, bufferSize: int = 50):
        self.filePath = filePath
        self.bufferSize = bufferSize
        self.buffer = []
        self.entryCount = 0

    def process(self):
        data = None
        with open(self.filePath, 'r') as f:
            data = loads(f.read())
        
        features = data.get('features', None)
        if (features == None):
            raise Exception('Error: unable to find the features in the geojson file')

        for entry in features:
            self.entryCount += 1
            result = self.parse(entry)
            if (result == False):
                print('Error: unable to parse the entry', entry)
                continue

            self.buffer.append(result)
            if (len(self.buffer) >= self.bufferSize):
                if (not self.handleBatch(self.buffer)):
                    print(f'Error: unable to handle the batch of data entries {self.entryCount - len(self.buffer)} - {self.entryCount}')
                self.buffer.clear()

        if (len(self.buffer) >= self.bufferSize):
            if (not self.handleBatch(self.buffer)):
                print(f'Error: unable to handle the batch of data entries {self.entryCount - len(self.buffer)} - {self.entryCount}')
            self.buffer.clear()

    @abstractmethod
    def parse(self, entry: dict) -> dict | bool:
        pass

    @abstractmethod
    def handleBatch(self, entries: list[dict]) -> bool:
        pass

    @abstractmethod
    def getParserName(self) -> str:
        pass

class ParseCountryFile(ParseGeoJsonFile):
    def parse(self, entry: dict) -> dict | bool:
        countryName = entry.get('properties', {}).get('NAME', None)
        if (countryName == None):
            print("unable to find the country name")
            return False
        
        geometryData = entry.get('geometry', None)
        if (geometryData == None):
            print('unable to find the gemetry data in the entry')
            return False
        
        return {
            'geometry': geometryData,
            'countryName': countryName,
        }
    
    def handleBatch(self, entries: list[dict]) -> bool:
        request_data = []
        for i in range(0, len(entries)):
            entry = entries[i]
            request_data.append({
                'requestId': str(uuid4()),
                'name': entry['countryName'],
                'coordinates': entry.get('geometry', {})['coordinates'],
                'shapeType': entry.get('geometry', {})['type'].upper()
            })

        resp = post('http://backend:8080/countries',json={ 'data': request_data })
        if (resp.status_code >= 300):
            print('unable to batch insert the data', resp.text)
            return False
        
        respJson = resp.json()
        if (len(respJson.get('errors', [])) > 0):
            print('some errors occurred when batch uploading data')
            return False
        
        return True
    
    def getParserName(self) -> str:
        return 'Country Parser'

class ParseEarthquakeFile(ParseGeoJsonFile):
    dateFormat1 = compile(r'^\d{2}/\d{2}/\d{4}$')
    dateFormat2 = compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$')

    def parse(self, entry: dict) -> dict | bool:
        props = entry.get('properties', {})
        latitude = props.get('Latitude', None)
        longitude = props.get('Longitude', None)
        date = props.get('Date', None)
        time = props.get('Time', None)
        providerId = props.get('ID', None)
        magnitude = props.get('Magnitude', None)

        if (latitude == None or longitude == None or date == None or time == None or providerId == None or magnitude == None):
            print('missing one of the following, latitude, longitude, date, time, id, magnitude')
            return False

        type = props.get('Type', None)
        depth = props.get('Depth', None)

        formattedDate = None
        if (self.dateFormat1.match(date)):
            dates = date.split('/')
            if len(dates) < 3:
                print('Error: unable to parse the date into 3 parts', date)
                return False
            month, day, year = dates
            formattedDate = f'{year}-{month}-{day}T{time}Z'
        elif (self.dateFormat2.match(date)):
            formattedDate = date
        else:
            print('Error: unable to recognize the date format', date)

        if (formattedDate == None):
            print("unable to format the date correctly", date)
            return False

        data = {
            'latitude': latitude,
            'longitude': longitude,
            'date': formattedDate,
            'providerId': providerId,
            'magnitude': magnitude,
        }

        if (type != None):
            data['type'] = type
        
        if (depth != None):
            data['depth'] = depth

        return data


    def handleBatch(self, entries: list[dict]) -> bool:
        request_data = []
        for i in range(0, len(entries)):
            entry = entries[i]
            request_data.append(entry)

        resp = post('http://backend:8080/earthquakes',json={ 'data': request_data })
        if (resp.status_code >= 300):
            print('unable to batch insert the data', resp.text)
            return False
        
        respJson = resp.json()
        if (respJson.get('errors', None) != None):
            print('some errors occurred when batch uploading data')
            return False
        
        return True
    
    def getParserName(self) -> str:
        return 'Earthquake Parser'

def main(args: Namespace):
    parser: ParseGeoJsonFile = None

    if (args.data_type == 'country'):
        parser = ParseCountryFile(args.file_path)
    elif (args.data_type == 'earthquake'):
        parser = ParseEarthquakeFile(args.file_path)
    else:
        print(f'Error: unrecognized data upload type {args.data_type}')
        return
    
    print(f'uploading {args.data_type} data using {parser.getParserName()}...')
    parser.process()
    print('completed upload')

if (__name__ == '__main__'):
    parser = ArgumentParser(prog = 'upload')
    parser.add_argument('--file-path', type=str, required=True)
    parser.add_argument('--data-type', type=str, required=True, choices=['country', 'earthquake'])
    args = parser.parse_args()
    main(args)