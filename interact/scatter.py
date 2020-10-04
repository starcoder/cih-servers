from .base_visualization import BaseVisualization

class Scatter(BaseVisualization):
    # color-according-to
    @property
    def marks(self):
        return [
            {
                "name" : "points",
                "type": "symbol",
                "from": {"data":self.dfields[0]},
                "encode": {
                    "enter": {
                        "size" : {"value" : 16},
                        "x": {"scale": "xscale", "field": self.ifield},
                        "width": {"scale": "xscale", "band": 1},
                        "y": {"scale": "yscale", "field": self.dfields[0]},
                        "y2": {"scale": "yscale", "value": 0}
                    },
                }
            },
        ]


    @property
    def scales(self):
        return [
            {
                "name" : "xscale",
                "type" : "linear",
                "domain" : {"data" : self.dfields[0], "field" : self.ifield},
                "range" : "width"
            },
            {
                "name" : "yscale",
                "type" : "linear",
                "domain" : {"data" : self.dfields[0], "field" : self.dfields[0]},
                "range" : "height"
            }
        ]

    @property
    def axes(self):
        return [
            {"orient" : "left", "scale" : "yscale", "title" : self.dfields[0]},
            {"orient" : "bottom", "scale" : "xscale", "title" : self.ifield}
        ]
