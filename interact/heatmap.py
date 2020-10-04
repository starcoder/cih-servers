from .base_visualization import BaseVisualization

class Heatmap(BaseVisualization):

    @property
    def icon(self):
        return """<path fill-rule="evenodd" d="M0 1.5A1.5 1.5 0 0 1 1.5 0h13A1.5 1.5 0 0 1 16 1.5v13a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 0 14.5v-13zM1.5 1a.5.5 0 0 0-.5.5V5h4V1H1.5zM5 6H1v4h4V6zm1 4V6h4v4H6zm-1 1H1v3.5a.5.5 0 0 0 .5.5H5v-4zm1 0h4v4H6v-4zm5 0v4h3.5a.5.5 0 0 0 .5-.5V11h-4zm0-1h4V6h-4v4zm0-5h4V1.5a.5.5 0 0 0-.5-.5H11v4zm-1 0H6V1h4v4z"/>"""
        
    @property
    def transforms(self):
        return [
            {
                "type" : "aggregate",
                "ops" : ["count"],
                "fields" : [self.fields[0]],
                "as" : ["count"],
                "groupby" : [self.fields[0], self.fields[1]]
            },
            {
                "type" : "filter",
                "expr" : "datum.{} != '' && datum.{} != ''".format(self.fields[0], self.fields[1]),
            },
            
        ]
    
    @property
    def marks(self):
        return [
            {

                "type": "rect",
                "align": "center",
                "baseline" : "middle",
                "from": {"data":"table"},
                "encode": {
                    "enter": {
                        "align": "center",
                        "baseline" : "middle",                        
                        "x": {"scale": "xscale", "field": self.fields[1]},
                        "width": {"scale" : "xscale", "band" : 1},
                        "height": {"scale" : "yscale", "band" : 1},
                        "y": {"scale": "yscale", "field": self.fields[0]},
                        "fill" : {"value" : "red"},
                        #"path" : {"scale" : "icon", "field" : "plot_type"},
                        #"href" : {"field" : "url"},
                    },
                    "update" : {
                        "fill" : {"value" : "steelblue"},                        
                    },
                    "hover" : {
                        "fill" : {"value" : "red"},
                    },
                }
            }
                

#                "type": "rect",
#                "from": {"data":"table"},
#                "encode": {
#                    "enter": {
#                        "x": {"scale": "xscale", "field": self.fields[0]},
#                        "width": {"scale": "xscale", "band": 1},
#                        "y": {"scale": "yscale", "field": self.fields[1]},
#                        "y2": {"scale": "yscale", "value": 0}
#                    },
#                }
#            },
        ]

    @property
    def axes(self):
        return [
            { "orient": "bottom", "scale": "xscale", "title": "Against", "labelAngle" : 45, "ticks" : False, "domain" : False},
            { "orient": "left", "scale": "yscale", "title" : "Plot", "ticks" : False, "grid" : False, "domain" : False}
        ]
    
    @property
    def scales(self):
        return [
            {
                "name": "xscale",
                "type": "band",
                "domain": {"data": "table", "field": self.fields[0]},
                "range": "width",
                "padding": 0.05,
                "round": True
            },
            {
                "name": "yscale",
                "type" : "band",
                "domain": {"data": "table", "field": self.fields[1]},
                "round": True,
                "padding" : 0.05,
                "range": "height"
            }
        ]
