from interact import models
import datetime

class BaseVisualization(object):
    
    def __init__(self, spec, *argv, **argd):
        self.spec = spec
        self.argv = argv
        self.argd = argd
        if isinstance(spec, dict):
            self.ifield = spec["independent_field"]["field_name"]
            self.dfields = [x["field_name"] for x in spec["dependent_fields"]["items"]]
        
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
        project = models.Project.objects.get(starcoder_id=self.spec["project"])
        retval = []
        for dep_field in self.spec["dependent_fields"]["items"]:
            
            entity_a = getattr(models, models.make_name(project.starcoder_id, self.spec["independent_field"]["entity_type"]))
            entity_b = getattr(models, models.make_name(project.starcoder_id, dep_field["entity_type"]))
            field_a = self.spec["independent_field"]["field_name"]
            field_b = dep_field["field_name"]
            data = []
            if "relationship" in dep_field:
                pass
            else:
                for obj in entity_a.objects.all():
                    data.append(
                        {
                            field_a : getattr(obj, field_a),
                            field_b : getattr(obj, field_b),                            
                        }
                    )
            retval.append({"name" : field_b, "values" : data})
            #     for e in entity_b.objects.all() if self.spec["direction"] == "reverse" else entity_a.objects.all():
            #         if self.spec["direction"] == "forward":
            #             for oe in getattr(e, rel, []).all():
            #                 data.append({field_a : getattr(e, field_a, None), field_b : getattr(oe, field_b, None)})
            #         elif self.spec["direction"] == "reverse":
            #             for oe in getattr(e, rel, []).all():
            #                 data.append({field_b : getattr(e, field_b, None), field_a : getattr(oe, field_a, None)})
            #         else:
            #             data.append({field_a : getattr(e, field_a, None), field_b : getattr(e, field_b, None)})
            # #final_data = []
            # #for datum in data:
            # #    final_datum = {}
            # #    for k, v in datum.items():
            # #        final_datum[k] = v.timestamp() if isinstance(v, datetime.datetime) else datetime.datetime.fromordinal(v.toordinal()).timestamp() if isinstance(v, datetime.date) else v
            # #    final_data.append(final_datum)
        return retval #[{"name" : "table", "values" : final_data}]

    @property
    def scales(self):
        return []

    @property
    def encode(self):
        return []

    @property
    def usermeta(self):
        return []
    
