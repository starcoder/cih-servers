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
from .schema_graph import SchemaGraph
from .model import Model

# thumbnails = {
#     "" : """<path fill-rule="evenodd" d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm7.5-6.923c-.67.204-1.335.82-1.887 1.855A7.97 7.97 0 0 0 5.145 4H7.5V1.077zM4.09 4H2.255a7.025 7.025 0 0 1 3.072-2.472 6.7 6.7 0 0 0-.597.933c-.247.464-.462.98-.64 1.539zm-.582 3.5h-2.49c.062-.89.291-1.733.656-2.5H3.82a13.652 13.652 0 0 0-.312 2.5zM4.847 5H7.5v2.5H4.51A12.5 12.5 0 0 1 4.846 5zM8.5 5v2.5h2.99a12.495 12.495 0 0 0-.337-2.5H8.5zM4.51 8.5H7.5V11H4.847a12.5 12.5 0 0 1-.338-2.5zm3.99 0V11h2.653c.187-.765.306-1.608.338-2.5H8.5zM5.145 12H7.5v2.923c-.67-.204-1.335-.82-1.887-1.855A7.97 7.97 0 0 1 5.145 12zm.182 2.472a6.696 6.696 0 0 1-.597-.933A9.268 9.268 0 0 1 4.09 12H2.255a7.024 7.024 0 0 0 3.072 2.472zM3.82 11H1.674a6.958 6.958 0 0 1-.656-2.5h2.49c.03.877.138 1.718.312 2.5zm6.853 3.472A7.024 7.024 0 0 0 13.745 12H11.91a9.27 9.27 0 0 1-.64 1.539 6.688 6.688 0 0 1-.597.933zM8.5 12h2.355a7.967 7.967 0 0 1-.468 1.068c-.552 1.035-1.218 1.65-1.887 1.855V12zm3.68-1h2.146c.365-.767.594-1.61.656-2.5h-2.49a13.65 13.65 0 0 1-.312 2.5zm2.802-3.5h-2.49A13.65 13.65 0 0 0 12.18 5h2.146c.365.767.594 1.61.656 2.5zM11.27 2.461c.247.464.462.98.64 1.539h1.835a7.024 7.024 0 0 0-3.072-2.472c.218.284.418.598.597.933zM10.855 4H8.5V1.077c.67.204 1.335.82 1.887 1.855.173.324.33.682.468 1.068z"/>"""

# bar = """M11 2a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v12h.5a.5.5 0 0 1 0 1H.5a.5.5 0 0 1 0-1H1v-3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3h1V7a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v7h1V2z"""

# clock = """<path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm8-7A8 8 0 1 1 0 8a8 8 0 0 1 16 0z"/>
#   <path fill-rule="evenodd" d="M7.5 3a.5.5 0 0 1 .5.5v5.21l3.248 1.856a.5.5 0 0 1-.496.868l-3.5-2A.5.5 0 0 1 7 9V3.5a.5.5 0 0 1 .5-.5z"/>"""

# grid = """<path fill-rule="evenodd" d="M0 1.5A1.5 1.5 0 0 1 1.5 0h13A1.5 1.5 0 0 1 16 1.5v13a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 0 14.5v-13zM1.5 1a.5.5 0 0 0-.5.5V5h4V1H1.5zM5 6H1v4h4V6zm1 4V6h4v4H6zm-1 1H1v3.5a.5.5 0 0 0 .5.5H5v-4zm1 0h4v4H6v-4zm5 0v4h3.5a.5.5 0 0 0 .5-.5V11h-4zm0-1h4V6h-4v4zm0-5h4V1.5a.5.5 0 0 0-.5-.5H11v4zm-1 0H6V1h4v4z"/>"""


# figure_types = {
#     ("place", "categorical") : Geography,
#     ("place", "numeric") : Geography,
#     ("date", "categorical") : TimeSeries,
#     ("date", "numeric") : TimeSeries,
#     ("datetime", "categorical") : TimeSeries,
#     ("datetime", "numeric") : TimeSeries,
#     ("categorical", "numeric") : Bar,
#     ("numeric", "numeric") : Scatter,
#     ("categorical", "categorical") : Heatmap,
# }

figure_types = {
    "place" : Geography,
    "categorical" : Bar,
    "date" : TimeSeries,
    "datetime" : TimeSeries,
    "scalar" : Scatter,
    "numeric" : Scatter,
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
