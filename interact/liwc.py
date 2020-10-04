from .base_visualization import BaseVisualization

class LIWC(BaseVisualization):

    def __init__(self, spec):
        self.values = []
        for item in spec:
            point = {k : v for k, v in item.items() if k != "liwc_features"}
            for k, v in item["liwc_features"].items():
                point["liwc_feature"] = k
                point["liwc_value"] = v
                self.values.append({k : v for k, v in point.items()})
        super(LIWC, self).__init__(spec)

    @property
    def autosize(self):
        return "fit"
    
    #@property
    #def height(self):
    #    return 8000

    #@property
    #def width(self):
    #    return 400
    
    @property
    def padding(self):
        return 5
    
    @property
    def data(self):
        return [
            {
                "name" : "starcoder_data",
                "values" : self.values,
                "transform" : [
                    {
                        "type" : "aggregate",
                        "groupby" : ["entity_type", "liwc_feature"],
                        "cross" : True,
                        "fields" : ["liwc_value"],
                        "ops" : ["sum"],
                        "as" : ["liwc_value"]
                    }
                ]
            }
        ]

    @property
    def scales(self):
        return [
            {
                "name": "global_position",
                "type": "band",
                "domain": {"data": "starcoder_data", "field": "liwc_feature"},
                "range": "height",
                "padding": 0.2
            },
            {
                "name": "xscale",
                "type": "linear",
                "domain": {"data": "starcoder_data", "field": "liwc_value"},
                "range": "width",
                "round": True,
                "zero": True,
                "nice": True
            },
            {
                "name": "cscale",
                "type": "ordinal",
                "domain": {"data": "starcoder_data", "field": "entity_type"},
                "range": {"scheme" : "category20"},
            },
        ]            

    @property
    def axes(self):
        return [
            {"orient": "left", "scale": "global_position", "tickSize": 0, "labelPadding": 80, "zindex": 1},
            {"orient": "bottom", "scale": "xscale"}
        ]

    
    @property
    def marks(self):
        return [
            {
                "type" : "group",
                "from" : {
                    "facet" : {
                        "data" : "starcoder_data",
                        "name" : "facet",
                        "groupby" : "liwc_feature",
                    },
                },
                "signals": [
                    {"name": "height", "update": "bandwidth('global_position')"}
                ],               
                "encode": {
                    "enter": {
                        "y": {"scale": "global_position", "field": "liwc_feature"}
                    }
                },
                "scales" : [
                    {
                        "name": "local_position",
                        "type": "band",
                        "domain": {"data": "facet", "field": "entity_type"},
                        "range": "height",
                    }
                ],
                "axes" : [
                    {"orient": "left", "scale": "local_position", "tickSize": 0, "labelPadding": 4, "zindex": 1},
                ],
                "marks": [
                    {
                        "name": "bars",
                        "from": {"data": "facet"},
                        "type": "rect",
                        "encode": {
                            "enter": {
                                "y": {"scale": "local_position", "field": "entity_type"},
                                "height": {"scale": "local_position", "band": 1},
                                "x": {"scale": "xscale", "field": "liwc_value"},
                                "x2": {"scale": "xscale", "value": 0},
                                "fill": {"scale": "cscale", "field": "entity_type"},
                            },
                            "hover": {
                                "fill": {"value": "red"}
                            },
                            "update" : {
                                "fill": {"scale": "cscale", "field": "entity_type"},
                            }
                        }
                    },
                ]
            }
        ]
    
