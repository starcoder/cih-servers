from .base_visualization import BaseVisualization

class Geography(BaseVisualization):

    @property
    def icon(self):
        return """<path fill-rule="evenodd" d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm7.5-6.923c-.67.204-1.335.82-1.887 1.855A7.97 7.97 0 0 0 5.145 4H7.5V1.077zM4.09 4H2.255a7.025 7.025 0 0 1 3.072-2.472 6.7 6.7 0 0 0-.597.933c-.247.464-.462.98-.64 1.539zm-.582 3.5h-2.49c.062-.89.291-1.733.656-2.5H3.82a13.652 13.652 0 0 0-.312 2.5zM4.847 5H7.5v2.5H4.51A12.5 12.5 0 0 1 4.846 5zM8.5 5v2.5h2.99a12.495 12.495 0 0 0-.337-2.5H8.5zM4.51 8.5H7.5V11H4.847a12.5 12.5 0 0 1-.338-2.5zm3.99 0V11h2.653c.187-.765.306-1.608.338-2.5H8.5zM5.145 12H7.5v2.923c-.67-.204-1.335-.82-1.887-1.855A7.97 7.97 0 0 1 5.145 12zm.182 2.472a6.696 6.696 0 0 1-.597-.933A9.268 9.268 0 0 1 4.09 12H2.255a7.024 7.024 0 0 0 3.072 2.472zM3.82 11H1.674a6.958 6.958 0 0 1-.656-2.5h2.49c.03.877.138 1.718.312 2.5zm6.853 3.472A7.024 7.024 0 0 0 13.745 12H11.91a9.27 9.27 0 0 1-.64 1.539 6.688 6.688 0 0 1-.597.933zM8.5 12h2.355a7.967 7.967 0 0 1-.468 1.068c-.552 1.035-1.218 1.65-1.887 1.855V12zm3.68-1h2.146c.365-.767.594-1.61.656-2.5h-2.49a13.65 13.65 0 0 1-.312 2.5zm2.802-3.5h-2.49A13.65 13.65 0 0 0 12.18 5h2.146c.365.767.594 1.61.656 2.5zM11.27 2.461c.247.464.462.98.64 1.539h1.835a7.024 7.024 0 0 0-3.072-2.472c.218.284.418.598.597.933zM10.855 4H8.5V1.077c.67.204 1.335.82 1.887 1.855.173.324.33.682.468 1.068z"/>"""
        
    @property
    def data(self):
        fd = super(Geography, self).data
        fd[0]["transform"] = [
            {
               "type": "filter",
               "expr": "datum.{} != null && datum.{} != null".format(self.fields[0], self.fields[1])
            },
            {
                "type": "geopoint",
                "projection": "overall",
                "fields": ["{}.longitude".format(self.fields[0]), "{}.latitude".format(self.fields[0])],
                "as" : ["longitude", "latitude"],
            },
            {
               "type": "filter",
               "expr": "datum.longitude != null && datum.latitude != null".format(self.fields[0])
            }
        ]
        return [
            {
                "name" : "world",
                "url" : "/static/countries-110m.json",
                "format": {"type": "topojson", "feature" : "countries"},
            },
            {
                "name" : "cities",
                "url" : "/static/ne_10m_populated_places.geojson",
                "format": {"type": "json", "property" : "features"},
                "transform": [
                    {
                        "type" : "filter",
                        "expr" : "datum.properties.POP_MIN > 1000000 && datum.geometry.type == 'Point'"
                    },
                    {
                        "type": "geopoint",
                        "projection": "overall",
                        "fields" : ["properties.LONGITUDE", "properties.LATITUDE"],
                        "as" : ["longitude", "latitude"],
                    }
                ],
                
            },
            #{
            #    "name" : "roads",
            #    "url" : "/static/ne_10m_roads.geojson",
            #    "format": {"type": "json", "property" : "features"},
                #"transform": [
                #   {
                #       "type": "geojson",
                #       "projection": "overall",
                #        "fields" : ["properties.LONGITUDE", "properties.LATITUDE"],
                #        "as" : ["longitude", "latitude"],
                #   }, type == Major Highway
                #]
                
            #},
            {
                "name": "graticule",
                "transform": [
                    { "type": "graticule", "stepMinor" : [2, 2] }
                ]
            }
        ] + fd

    @property
    def scales(self):
        return []

    @property
    def axes(self):
        return []
    
    @property
    def marks(self):
        return [
            {
                "type": "shape",
                "from": {"data": "graticule"},
                "zindex" : 1,
                "encode": {
                    "update": {
                        "strokeWidth": {"value": .1},
                        "stroke": {"value" : "white"},
                        "fill": {"value": None}
                    }
                },
                "transform": [
                    { "type": "geoshape", "projection": "focus" }
                ]
            },
            {
                "type": "shape",
                "from": {"data": "world"},
                "encode": {
                    "update": {
                        "strokeWidth": {"value" : 1},
                        "stroke": {"value": "#777"},
                        "fill": {"value": "#000"},
                        "zindex": {"value": 0}
                    },
                },
                "transform": [
                   { "type": "geoshape", "projection": "focus" }
                ]
            },
            {
                "type": "symbol",
                "from": {"data": "table"},
                "shape" : "circle",
                "encode": {
                    "enter": {
                        "fill": {"value": "red"},
                    },
                    "update": {
                        "x": {"field": "longitude"},
                        "y": {"field": "latitude"}
                    }
                },
                #"transform" : [
                #    {"type" : "geopoint", "projection": "focus"}
                #]
            },
            {
                "type": "shape",
                "from": {"data": "cities"},
                "encode": {
                    "enter": {
                        "fill" : {"value" : "blue"},
                    }
                },
                "transform" : [
                    {"type" : "geoshape", "projection": "focus"}
                ]
                
            },
            # {
            #     "type": "shape",
            #     "from": {"data": "roads"},
            #     "encode": {
            #         "enter": {
            #             "size": {"value" : 1},
            #             "fill": "false",
            #             "fillOpacity": {"value": 0.8},
            #             "stroke": {"value": "white"},
            #             "strokeWidth": {"value": 1}
            #         },
            #         #"update": {
            #         #    "x": {"field": "longitude"},
            #         #    "y": {"field": "latitude"}
            #         #}
            #     },
                
            #     "transform" : [
            #         {"type" : "geoshape", "projection": "overall"}
            #     ]
                
            # }
            
        ]

    @property
    def signals(self):
        return []

    @property
    def projections(self):
        return [
            {
                "name": "overall",
                "type" : "mercator",
            },
            {
                "name": "focus",
                "type" : "mercator",
                #"fit" : {"signal" : "data('table')"},
                #"scale" : 500,                
                #"size" : {"signal" : "[width,height]"},
            }
            
        ]

    @property
    def config(self):
        return {}
