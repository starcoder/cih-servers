from interact import models
import datetime

dependent_types = [
    "scalar",
    "numeric",
    "categorical"
]

class BaseVisualization(object):
    
    def __init__(self, *argv, **argd):
        pass
        #self.project_id = project_id
        #self.ifield = independent_field
        #self.schema = schema
        #self.relationships = {"" : []}
        #for field in self.schema["entity_types"][self.ifield[0]]["data_fields"]:
        #    ft = self.schema["data_fields"][field]["type"]
        #    if field != self.ifield[1] and ft in dependent_types:
        #        self.relationships[""].append((self.ifield[0], field, ft))
        
    @property
    def json(self):
        retval = {
            "$schema": "https://vega.github.io/schema/vega/v5.json",
            "description": self.description,
            "background": self.background,
            "width": self.width,
            "height": self.height,
            "padding": self.padding,
            "autosize": self.autosize,
            "config" : self.config,
            "signals": self.signals,
            "data": self.data,
            "scales": self.scales,
            "projections": self.projections,
            "axes": self.axes,
            "legends": self.legends,
            "title" : self.title,
            "marks": self.marks,
            "encode": self.encode,
            "usermeta": self.usermeta,            
        }
        return retval

    @property
    def description(self):
        return "A specification outline example."
    
    @property
    def width(self):
        return 640

    @property
    def height(self):
        return 480

    @property
    def padding(self):
        return None

    @property
    def autosize(self):
        return None

    @property
    def background(self):
        return None
    
    @property
    def legends(self):
        return []

    @property
    def projections(self):
        return []
    
    @property
    def other_data(self):
        return []
    
    @property
    def signals(self):
        return []
    
    @property
    def config(self):
        return []
    
    @property
    def title(self):
        return None
    
    @property
    def transforms(self):
       return []

    @property
    def marks(self):
        return []

    @property
    def axes(self):
        return []

    @property
    def scales(self):
        return []

    @property
    def data(self):
        return []
    
    @property
    def scales(self):
        return []

    @property
    def encode(self):
        return []

    @property
    def usermeta(self):
        return []


class StarcoderVisualization(BaseVisualization):
    
    def __init__(self, project_id, schema, independent_field, *argv, **argd):        
        super(StarcoderVisualization, self).__init__(*argv, **argd)
        self.project_id = project_id
        self.ifield = independent_field
        self.ifield_name = "{}({})".format(self.ifield[0].title(), self.ifield[1])
        self.schema = schema
        self.relationships = {"" : []}
        self.dfield_names = []
        for field in self.schema["entity_types"][self.ifield[0]]["data_fields"]:
            ft = self.schema["data_fields"][field]["type"]
            if field != self.ifield[1] and ft in dependent_types:
                self.relationships[""].append((self.ifield[0], field, ft))
                self.dfield_names.append((ft, "{}({})".format(self.ifield[0].title(), field)))
                
    @property
    def title(self):
        return None #"Plotting against {}({})".format(self.ifield[0].title(), self.ifield[1])

    @property
    def signals(self):
        return [
            {
                "name" : "independent",
                "value" : self.ifield_name,
            },
            {
                "name": "dependent",
                "value" : self.dfield_names[0][1],
                "bind": {
                    "name" : " ",
                    "input": "select",
                    "element" : "#dependent",
                    "options": sum(
                        [
                            [("{1}({2})" if rel == "" else "{0} {1}({2})").format(rel, e.title(), f) for e, f, ft in fields] for rel, fields in self.relationships.items()
                        ],
                        []
                    ),
                    "labels": sum(
                        [
                            [("{1}({2})" if rel == "" else "{0} {1}({2})").format(rel, e.title(), f) for e, f, ft in fields] for rel, fields in self.relationships.items()
                        ],
                        []
                    )
                    
                },
            }
        ] #if len(sum([f for _, f in self.relationships.items()], [])) > 1 else []
                
    @property
    def data(self):
        dep_fields = set()
        project = models.Project.objects.get(id=self.project_id)
        i_ents = getattr(
            models,
            models.make_name(
                project.id,
                self.ifield[0]
            )
        ).objects.all()
        i_name = "{}({})".format(self.ifield[0].title(), self.ifield[1])
        values = []
        for i_ent in i_ents:
            ent_data = {self.ifield_name : getattr(i_ent, self.ifield[1])}
            #ent_data = {i_name : getattr(i_ent, self.ifield[1])}
            for rel, fields in self.relationships.items():
                for d_ent, d_field, d_type in fields:
                    d_name = "{}({})".format(
                        d_ent.title(),
                        d_field,
                    ) if rel == "" else "{} {}({})".format(
                        rel,
                        d_ent.title(),
                        d_field
                    )
                    dep_fields.add((d_name, d_type))
                    if rel == "":
                        ent_data[d_name] = getattr(i_ent, d_field)
                    else:
                        pass
            values.append(ent_data)
        return [
            {"name" : "starcoder", "values" : values},
            {"name" : "fields", "values" : {k : v for k, v in dep_fields}},
        ]
