from .base_visualization import BaseVisualization
import re

def make_values(model, name="", path=[0]):
    parent_path = path[:-1]
    parent_id = None if parent_path == [] else " ".join([str(x) for x in parent_path])
    this_id = " ".join([str(x) for x in path])
    this_type = "starcoder" if parent_id == None else "module"
    return [
        {
            "id" : this_id,
            "name" : name,
            "type" : this_type,
            "parent" : parent_id,
        }
    ] + sum([make_values(c, n, path + [i]) for i, (n, c) in enumerate(model.items()) if n not in ["dropout"] and not n.startswith("_") and len(path) < 3 and not re.match(r"^\d+$", n)], [])
        
    

        

class Model(BaseVisualization):

    def __init__(self, model):
        self.model = model
        super(Model, self).__init__(model)

    @property
    def autosize(self):
        return "fit"

    @property
    def data(self):
        return [
            {
                "name" : "tree",
                "values" : make_values(self.model),
                "transform": [
                    {
                        "type": "stratify",
                        "key" : "id",
                        "parentKey" : "parent"
                    },
                    {
                        "type" : "tree",
                        "method" : "tidy",
                        "separation" : True,
                        "size": [{"signal": "width"}, {"signal": "height"}],
                    },
                ],
            },
            {
      "name": "links",
      "source": "tree",
      "transform": [
        { "type": "treelinks" },
        {
          "type": "linkpath",
          "orient": "horizontal",
            "shape": "diagonal",
        }
      ]
    }
        ]
    
    @property
    def height(self):
      return 300

    @property
    def width(self):
      return 2048 #800

    #@property
    #def title(self):
    #    return "Schema"
    
    @property
    def padding(self):
        return 5
    
    @property
    def scales(self):
        return [
            {
                "name": "color",
                "type": "ordinal",
                "range": {"scheme": "category20"}
            }
        ]
    
    @property
    def axes(self):
        return []
    
    @property
    def marks(self):
        return [
            {
                "type": "path",
                "from": {"data": "links"},
                "encode": {
                    "update": {
                        "path": {"field": "path"},
                        "stroke": {"value": "#ccc"}
                    }
                }
            },
            {
                "type": "symbol",
                "from": {"data": "tree"},
                "encode": {
                    "enter": {
                        "size": {"value": 200},
                        "stroke": {"value": "#fff"}
                    },
                    "update": {
                        "x": {"field": "x"},
                        "y": {"field": "y"},
                        "fill": {"scale": "color", "field": "depth"}
                    }
                }
            },            
            {
                "type": "text",
                "from": {"data": "tree"},
                "encode": {
                    "enter": {
                        "text": {"field": "name"},
                        "fontSize": {"value": 15},
                        "baseline": {"value": "middle"},
                        "angle" : {"value" : 45},
                        "align" : {"value" : "center"},
                    },
                    "update": {
                        "x": {"field": "x"},
                        "y": {"field": "y"},
                        #"dx": {"signal": "datum.children ? -7 : 7"},
                        #"align": {"signal": "datum.children ? 'right' : 'left'"},
                        #"opacity": {"signal": "labels ? 1 : 0"}
                    }
                }
            }
            
        ]
        #     {
        #         "type": "path",
        #         "from": {"data": "relationships"},
        #         "interactive": True,
        #         "encode": {
        #             "update": {
        #                 "stroke": {"value": "black"}, ##ccc"},
        #                 "strokeWidth": {"value": 15},
        #                 "tooltip" : {"signal" : "datum.name"},
        #             }
        #         },
        #         "transform": [
        #             {
        #                 "type": "linkpath",
        #                 #"require": {"signal": "force"},
        #                 "shape": "curve",
        #                 "sourceX": "datum.source.x", "sourceY": "datum.source.y",
        #                 "targetX": "datum.target.x", "targetY": "datum.target.y"
        #             }
        #         ]
        #     },
        #     {
        #         "name" : "nodes",
        #         "type" : "rect",
        #         "from" : {"data" : "entities"},
        #         "encode": {
        #             "enter": {
        #                 "cornerRadius" : {"value" : 4},
        #                 "x" : {"signal" : "datum.x - 100"},
        #                 "y" : {"signal" : "datum.y - 50"},                        
        #                 "fill": {"value" : "lightblue"},
        #                 "stroke": {"value": "white"},
        #                 "width" : {"value" : 200},
        #                 "height" : {"signal" : "35 + 10 * datum.field_count"}, #100},
        #             },
        #         },
        #     },
        #     {
        #         "name" : "entity_labels",
        #         "type" : "text",
        #         "from" : {"data" : "entities"},
        #         "encode": {
        #             "enter": {
        #                 "text" : {"field" : "name"},
        #                 "fontSize" : {"value" : 20},
        #                 "x" : {"field" : "x"},
        #                 "y" : {"signal" : "datum.y - 45"},                        
        #                 "fill": {"value" : "black"},
        #                 "stroke": {"value": "black"},
        #                 "align" : {"value" : "center"},
        #                 "baseline" : {"value" : "top"},
        #             },
        #         },
        #     },
        #     {
        #         "name" : "field_labels",
        #         "type" : "text",
        #         "from" : {"data" : "fields"},
        #         "encode": {
        #             "enter": {
        #                 "text" : {"field" : "field"},
        #                 "fontSize" : {"value" : 10},
        #                 "x" : {"field" : "entity.x"},
        #                 "y" : {"signal" : "datum.entity.y + datum.order * 10 + 20 - 40"},
        #                 "fill": {"value" : "black"},
        #                 "stroke": {"value": "black"},
        #                 "align" : {"value" : "center"},
        #                 "baseline" : {"value" : "top"},
        #             },
        #         },
        #     },
        # ]
