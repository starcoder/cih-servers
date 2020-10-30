from .base_visualization import BaseVisualization

class Bottlenecks(BaseVisualization):
    def __init__(self, spec):
        self.values = spec

    @property
    def autosize(self):
        return "pad"
    
    @property
    def signals(self):
        return [
            {"name" : "width", "value" : 400},
            {"name": "cellHeight", "value": 300},
            {"name": "cellWidth", "value": 400},
            {"name" : "height", "value" : 1800},            
            {
                "name": "active",
                "value": {},
                "on": [
                    {"events": "symbol:mousedown, symbol:touchstart", "update": "datum"},
                    #{"events": "window:touchend", "update": "{}"}
                    #{"events": "window:mouseup, window:touchend", "update": "{}"}
                ]
            },
            #{ "name": "isActive", "update": "active.entity" },
            #{
            #    "name": "timeline",
            #    "value": {},
            #    "on": [
            #        {"events": "@point:mouseover", "update": "isActive ? active : datum"},
            #        {"events": "@point:mouseout", "update": "active"},
            #        {"events": {"signal": "active"}, "update": "active"}
            #    ]
            #},
        ]

    @property
    def background(self):
        return None
    
    @property
    def data(self):
        return [
            {
                "name" : "starcoder_data",
                "values" : self.values,
                "transform" : [
                    {
                        "type" : "joinaggregate",
                        "groupby" : ["entity_type"],
                        "fields" : ["tsne[0]", "tsne[0]", "tsne[1]", "tsne[1]"],
                        "ops" : ["min", "max", "min", "max"],
                        "as" : ["x_min", "x_max", "y_min", "y_max"],
                    },
                    {
                        "type" : "filter",
                        "expr" : "datum.tsne != null"
                    },
                    {
                        "type" : "formula",
                        "expr" : "(datum.tsne[0] - datum.x_min) / (datum.x_max - datum.x_min)",
                        "as" : "x",
                    },
                    {
                        "type" : "formula",
                        "expr" : "(datum.tsne[1] - datum.y_min) / (datum.y_max - datum.y_min)", 
                        "as" : "y",
                    }
                ]
            },
            #{
            #    "name": "trackEntity",
            #    "on": [
            #        {"trigger": "active", "toggle": "{entity: active.entity}"}
            #    ]
            #}
        ]

    @property
    def scales(self):
        return [
            {
                "name": "groupy",
                "type": "band",
                "range": "height",
                "domain": {"data": "starcoder_data", "field": "entity_type"}
            },
        ]
    
    @property
    def axes(self):
        return [
        ]
    
    @property
    def marks(self):
        return [
            {
                "type" : "group",
                "from" : {
                    "facet" : {
                        "name" : "facet",
                        "data" : "starcoder_data",
                        "groupby" : "entity_type",
                    }
                },
                "encode": {
                    "update": {
                        "y": {"scale": "groupy", "field": "entity_type"},
                        "width" : {"signal" : "width"},
                        "height" : {"signal" : "cellHeight"},
                        "fill" : {"value" : "lightblue"},
                        "stroke" : {"value" : "black"},
                    }
                },
                "scales" : [
                    {
                        "name": "xscale",
                        "type": "linear",
                        "round": True,
                        "nice": True,
                        "zero": True,
                        "domain": {"data" : "starcoder_data", "field": "x"},
                        "range": {"signal" : "cellWidth"},
                    },
                    {
                        "name": "yscale",
                        "type": "linear",
                        "round": True,
                        "nice": True,
                        "zero": True,
                        "domain": {"data" : "starcoder_data", "field": "y"},
                        "range": {"signal" : "cellHeight"},
                    },
                ],
                "title" : {"text" : {"signal" : "parent.entity_type"}},
                "marks" : [
                    {
                        "type" : "symbol",
                        "from" : {"data" : "facet"},
                        "encode": {
                            "enter": {
                                "fill": {"value": "red"},
                                "opacity": {"value": 1},
                                "x": {"signal" : "datum.x * cellWidth"},
                                "y": {"signal" : "datum.y * cellHeight"},
                                "tooltip" : {"field" : "label"},
                            }
                        }
                    },
                ],
            },
        ]


