from .base_visualization import BaseVisualization

import random
class LIWC(BaseVisualization):
    @property
    def height(self):
        return 2048
    
    def __init__(self, project_id, spec, schema, ifield):
        self.values = []
        self.schema = schema
        random.shuffle(spec)
        for item in spec:
            point = {k : v for k, v in item.items() if k != "liwc_features"}
            for k, v in item["liwc_features"].items():
                point["liwc_feature"] = k
                point["liwc_value"] = v
                self.values.append({k : v for k, v in point.items()})
        self.categoricals = []
        for field_name, field_spec in self.schema["data_fields"].items():
            if field_spec["type"] == "categorical":
                self.categoricals.append(field_name)
        super(LIWC, self).__init__()

    @property
    def signals(self):
        return [
            {
                "name": "dependent",
                "value" : self.categoricals[0],
                "bind": {
                    "name" : " ",
                    "input": "select",
                    "element" : "#dependent",
                    "options": self.categoricals,
                    "labels": self.categoricals,
                },
            }
        ]

    @property
    def legends(self):
        return [
            {
                "fill" : "cscale",
                "type" : "symbol",
                "orient" : "top-right",
            }
        ]
        
    #@property
    #def autosize(self):
     #   return "fit"
    
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
                        "type" : "filter",
                        "expr" : "datum[dependent] != null",
                    },
                    {
                        "type" : "formula",
                        "as" : "dependent",
                        "expr" : "datum[dependent]",
                    },
                    {
                        "type" : "aggregate",
                        "groupby" : ["liwc_feature", "dependent"],
                        #"cross" : True,
                        "fields" : ["liwc_value"],
                        "ops" : ["average"],
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
                "domain": {"data": "starcoder_data", "field": "dependent"},
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
                        "domain": {"data": "facet", "field": "dependent"},
                        "range": "height",
                    }
                ],
                #"axes" : [
                #    {"orient": "left", "scale": "local_position", "tickSize": 0, "labelPadding": 4, "zindex": 1},
                #],
                "marks": [
                    {
                        "name": "bars",
                        "from": {"data": "facet"},
                        "type": "rect",
                        "encode": {
                            "update": {
                                "y": {"scale": "local_position", "field": "dependent"},
                                "height": {"scale": "local_position", "band": 1},
                                "x": {"scale": "xscale", "field": "liwc_value"},
                                "x2": {"scale": "xscale", "value": 0},
                                "fill": {"scale": "cscale", "field": "dependent"},
                            },
                            #"hover": {
                                #"fill": {"value": "red"}
                                #},
                            #"update" : {
                            #    "fill": {"scale": "cscale", "field": "dependent"},
                            #}
                        }
                    },
                ]
            }
        ]
    
