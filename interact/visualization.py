from interact import models

from .geography import Geography
from .bar import Bar
from .project_grid import ProjectGrid
from .heatmap import Heatmap
from .time_series import TimeSeries
from .scatter import Scatter
from .topics import Topics
from .bottlenecks import Bottlenecks
from .liwc import LIWC

figure_types = {
    ("place", "categorical") : Geography,
    ("place", "numeric") : Geography,
    ("date", "categorical") : TimeSeries,
    ("date", "numeric") : TimeSeries,
    ("datetime", "categorical") : TimeSeries,
    ("datetime", "numeric") : TimeSeries,
    ("categorical", "numeric") : Bar,
    ("numeric", "numeric") : Scatter,
    ("categorical", "categorical") : Heatmap,
}

# figure_types = {
#     "categorical.categorical" : Heatmap,
#     "categorical.numeric" : Bar,
#     "place.categorical" : Geography,
#     "place.numeric" : Geography,
#     "date.numeric" : TimeSeries,
#     "date.categorical" : TimeSeries,
#     "datetime.numeric" : TimeSeries,
#     "datetime.categorical" : TimeSeries,    
#     "project_grid" : ProjectGrid,
# }

# each date field x (categorical + numeric)
# each place field x (categorical + numeric)
# each categorical x numeric
# each numeric x others
#

def potential_figures(schema):
    mapping = {}
    for entity_type, entity_spec in schema["entity_types"].items():
        fields = entity_spec["data_fields"]
        for independent_field, dependent_field in [(x, y) for x in fields for y in fields if x != y]:
            independent_field_type = schema["data_fields"][independent_field]["type"]
            dependent_field_type = schema["data_fields"][dependent_field]["type"]
            independent_entity_type = entity_type
            dependent_entity_type = entity_type
            if (independent_field_type, dependent_field_type) in figure_types:
                independent = (independent_field, independent_field_type, independent_entity_type)
                dependent = {"field_name" : dependent_field, "entity_type" : dependent_entity_type}
                mapping[independent] = mapping.get(independent, {})
                mapping[independent][dependent_field_type] = mapping[independent].get(dependent_field_type, [])
                mapping[independent][dependent_field_type].append(dependent)
        for independent_field in fields:
            continue
            for rel_name, rel_spec in schema["relationship_fields"].items():
                source = rel_spec["source_entity_type"]
                target = rel_spec["target_entity_type"]
                if entity_type not in [source, target]:
                    continue
                other_entity = target if source == entity_type else source
                direction = "forward" if source == entity_type else "backward"
                for dependent_field in schema["entity_types"][other_entity]["data_fields"]:
                    independent_field_type = schema["data_fields"][independent_field]["type"]
                    dependent_field_type = schema["data_fields"][dependent_field]["type"]
                    independent_entity_type = entity_type
                    dependent_entity_type = other_entity
                    if (independent_field_type, dependent_field_type) in figure_types:
                        independent = (independent_field, independent_field_type, independent_entity_type)
                        dependent = {"field_name" : dependent_field, "entity_type" : dependent_entity_type, "direction" : direction, "relationship" : rel_name}
                        mapping[independent] = mapping.get(independent, {})
                        mapping[independent][dependent_field_type] = mapping[independent].get(dependent_field_type, [])
                        mapping[independent][dependent_field_type].append(dependent)
    figures = []
    for (independent_field, independent_field_type, independent_entity_type), dependent_field_types in mapping.items():
        for dependent_field_type, deps in dependent_field_types.items():
            figure_type = figure_types.get((independent_field_type, dependent_field_type))
            dependent_fields = []
            for dep in deps:
                dependent_fields.append(dep)
            if figure_type != None:
                figures.append(
                    {
                        "independent_field" : {
                            "field_name" : independent_field,
                            "field_type" : independent_field_type,
                            "entity_type" : independent_entity_type,
                        },
                        "dependent_fields" : {
                            "items" : dependent_fields,                            
                            "field_type" : dependent_field_type,
                        }
                    }
                )
        
    return figures
