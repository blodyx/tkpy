from utils import vid, fishout, COLOR
from primordial.gameworld import Gameworld


class Cell:
    def __init__(self, client, cell_id, data=None):
        self.client = client
        self.id = cell_id
        self.coord = fishout(self.id)
        self._data = data or dict()

    def __getitem__(self, key):
        return self._data[key]

    def __repr__(self):
        return f'{type(self).__name__}({self._data})'

    def details(self):
        r = self.client.cache.get(
            {
                'names': [
                    f'MapDetails:{self.id}'
                ]
            }
        )
        return r

    def coloring_cell(self, color=None):
        color = color.upper() or 'BLUE'
        errmsg = f'there is no {color} color, <object>.color_list is '+\
                  'complete list of color'
        assert color in COLOR, errmsg
        r = self.client.cache.get({'names':['Collection:MapMarker:']})
        for caches in r['cache'][0]['data']['cache']:
            if caches['data']['targetId'] == str(self.id):
                if caches['data']['color'] == str(COLOR[color]):
                    return
                self._edit_cell_color(int(caches['data']['id']), color)
                return
        markers = [
            {
                'color': COLOR[color],
                'editType': 3,
                'owner': 1,
                'ownerId': self.client.player_id,
                'targetId': self.id,
                'type': 3
            }
        ]
        self.client.post(
            action='editMapMarkers',
            controller='map',
            params={
                'markers': markers
            }
        )

    def delete_cell_color(self):
        r = self.client.cache.get({'names':['Collection:MapMarker:']})
        for caches in r['cache'][0]['data']['cache']:
            if caches['data']['targetId'] == str(self.id):
                markers = [
                    {
                        'editType': 2,
                        'id': int(caches['data']['id'])
                    }
                ]
                self.client.post(
                    action='editMapMarkers',
                    controller='map',
                    params={
                        'markers': markers
                    }
                )
                return

    def _edit_cell_color(self, id, color):
        markers = [
            {
                'color': COLOR[color],
                'editType': 1,
                'owner': 1,
                'ownerId': self.client.player_id,
                'targetId': self.id,
                'type': 3,
                'id': id
            }
        ]
        self.client.post(
            action='editMapMarkers',
            controller='map',
            params={
                'markers': markers
            }
        )


class Map:
    def __init__(self, client, data=None):
        assert isinstance(client, Gameworld), 'Need Gameworld object'
        self.client = client
        self._data = data or dict()

    def __setitem__(self, key, value):
        assert isinstance(value, Cell), 'value must be Cell object'
        if isinstance(key, tuple) and len(key) == 2:
            for k in key:
                errmsg = f'value must be integer but {k} is given'
                assert isinstance(k, int), errmsg
            self._data[key] = value
        else:
            errmsg = 'key must x, y pairing tuple'
            raise AssertionError(errmsg)

    def __getitem__(self, key):
        """the only way to get the item is use coordinate method"""
        errmsg = f'\'{type(self).__name__}\' object does not support indexing'
        raise TypeError(errmsg)

    def __iter__(self):
        return iter(list(self._data.keys()))

    def __repr__(self):
        return f'{type(self).__name__}({dict(self._data.items())})'

    def pull(self):
        """git pull like function for pulling map data from server"""
        req_list = list()
        for x in range(-13, 14):
            for y in range(-13, 14):
                req_list.append(vid(x, y))
        r = self.client.map.getByRegionIds(
            {
                'regionIdCollection': {
                    '1': req_list
                }
            }
        )
        for vids in r['response']['1']['region']:
            for result in r['response']['1']['region'][vids]:
                id = int(result['id'])
                self.__setitem__(fishout(id), Cell(self.client, id, result))

    def coordinate(self, x, y):
        """the one and only method for getting the item"""
        return self._data[(x, y)]

    @property
    def color_list(self):
        for color in COLOR:
            print(f'{color}')

    def _filter(self, group):
        results = dict()
        for coord in self._data.keys():
            try:
                oasis = self._data[coord][group]
                results[coord] = self._data[coord]
            except KeyError:
                continue
        return results

    def oasis(self):
        return Map(self.client, self._filter('oasis'))

    def tiles(self):
        return Map(self.client, self._filter('resType'))
