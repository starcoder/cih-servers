from .base_visualization import BaseVisualization

class Bar(BaseVisualization):

    # @property
    # def layout(self):
    #     return {
    #         "columns" : 2,
    #         "padding" : 20,
    #     }

    @property
    def data(self):
        values = []
        for dep in super(Bar, self).data:
            for item in dep["values"]:
                item["vega_group"] = dep["name"]
                item["value"] = item[dep["name"]]
                del item[dep["name"]]
                values.append(item)
        return [
            {
                "name" : "starcoder_data",
                "values" : values
            }
        ]

    @property
    def scales(self):
        return [
            {
                "name" : "xscale",
                "type" : "band",
                "domain" : {
                    "data" : "starcoder_data",
                    "field" : self.spec["independent_field"]["field_name"]
                },
                "range" : "width",
            },
            {
                "name": "yscale",
                "type": "linear",
                "domain": {"data": "starcoder_data", "field": "value"},
                "range": "height",
                "round": True,
                "zero": True,
                "nice": True
            },
            {
                "name": "cscale",
                "type": "ordinal",
                "range": {"scheme" : "category20"},
                "domain": {"data": "starcoder_data", "field": "vega_group"}
            },
            
        ]
        # return [
        #     {
        #         "name": dep["field_name"],
        #         "domain": {"data": dep["field_name"], "field": dep["field_name"]},
        #         "nice": True,
        #         "range": "height"
        #     } for dep in self.spec["dependent_fields"]["items"]] + [
        #         {
        #             "name" : "xscale",
        #                 "type": "band",
        #                 "domain": {"data": "slave_height", "field": self.spec["independent_field"]["field_name"]},
        #                 "range": "width",
        #                 "padding": 0.05,
        #                 "round": True
        #         }
        #     ]

    
    @property
    def marks(self):
        return [
            {
                "type" : "group",
                "from" : {
                    "facet" : {
                        "data" : "starcoder_data",
                        "name" : "facet",
                        "groupby" : "vega_group"
                    }
                },
                "encode": {
                    "enter": {
                        "x": {"scale": "xscale", "field": self.spec["independent_field"]["field_name"]}
                    }
                },

                #"signals": [
                #    {"name": "height", "update": "bandwidth('yscale')"}
                #],

                "scales": [
                    {
                        "name": "pscale",
                        "type": "band",
                        "range": "width",
                        "domain": {"data": "facet", "field": "vega_group"}
                    },
                ],

                "marks": [
                    {
                        "name": "bars",
                        "from": {"data": "facet"},
                        "type": "rect",
                        "encode": {
                            "enter": {
                                "x": {"scale": "pscale", "field": "vega_group"},
                                "width": {"scale": "pscale", "band": 1},
                                "y": {"scale": "yscale", "field": "value"},
                                "y2": {"scale": "yscale", "value": 0},
                                "fill": {"scale": "cscale", "field": "vega_group"}
                            }
                        }
                    },
                ]
            }

        ]
            #{
                #"type": "rect",
                #"from" : {"data" : dep["field_name"]}, #[x for x in data if x["name"] == dep_field["field_name"]],
                
                #"marks" : [
                #    {
                #        "from": {"data":dep_field["field_name"]},
                # "encode": {
                #     "enter": {
                #         "x": {"scale": "xscale", "field": self.spec["independent_field"]["field_name"]},
                #         "width": {"scale": "xscale", "band": 1},
                #         "y": {"scale": dep["field_name"], "field": dep["field_name"]},
                #         "y2": {"scale": dep["field_name"], "value": 0}
                #     },
                #     "hover" : {
                #         "tooltip": {"field": "slave_race"}
                #     }
                # },
                #    }
                #],
                #"scales" : [
                #    {
                #        "name": "xscale",
                #        "type": "band",
                #        "domain": {"data": dep_field["field_name"], "field": self.spec["independent_field"]["field_name"]},
                #        "range": "width",
                #        "padding": 0.05,
                #        "round": True
                #    },
                #    {
                #        "name": "yscale",
                #        "domain": {"data": dep_field["field_name"], "field": dep_field["field_name"]},
                #        "nice": True,
                #        "range": "height"
                #    }
                #]                                                    
            #} for dep in self.spec["dependent_fields"]["items"]]

    
    @property
    def axes(self):
        return [
            { "labelAngle" : 45, "orient": "bottom", "scale": "xscale", "title": ""}, #self.fields[0]},
            {"orient": "left", "scale": "yscale", "tickSize": 0, "labelPadding": 4, "zindex": 1},
        ]
    #        { "orient": "left", "scale": "yscale", "title" : ""}, #self.fields[1]}
    #    ]

            #{
           #     "name": "xscale",
            #    "type": "band",
            #    "domain": {"data": "amount", "field": "status"},
            #    "range": "width",
            #    "padding": 0.05,
            #    "round": True
            #},
            #{
            #    "name": "yscale",
            #    "domain": {"data": "amount", "field": "amount"},
            #    "nice": True,
            #    "range": "height"
            #}
            #]

