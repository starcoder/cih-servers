from .base_visualization import StarcoderVisualization
# categorical and numeric
class TimeSeries(StarcoderVisualization):

    @property
    def icon(self):
        return """<path fill-rule="evenodd" d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm8-7A8 8 0 1 1 0 8a8 8 0 0 1 16 0z"/>
        <path fill-rule="evenodd" d="M7.5 3a.5.5 0 0 1 .5.5v5.21l3.248 1.856a.5.5 0 0 1-.496.868l-3.5-2A.5.5 0 0 1 7 9V3.5a.5.5 0 0 1 .5-.5z"/>"""

    #@property
    #def scales(self):
    #    return [
    #        {
    #            "name" : "x",
    #            "type" : "time",
    #            
    #        }
    #    ]

