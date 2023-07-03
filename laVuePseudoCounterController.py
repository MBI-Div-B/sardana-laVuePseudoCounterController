from sardana.pool.controller import (
    PseudoCounterController,
    Type,
    Description,
    MaxDimSize,
)
import numpy as np
import json
from tango import AttributeProxy, EventType
from os.path import join


class LaVuePseudoCounterController(PseudoCounterController):
    counter_roles = ("input_image",)
    pseudo_counter_roles = ("output_roi",)

    ctrl_attributes = {
        "lavue_tangoDS": {
            Type: str,
            Description: ("lavue tangoDS address"),
            #DefaultValue: "rsxs/lavuecontroller/henry",
        },
        "ROI_name": {
            Type: str,
            Description: ("name of the ROI"),
            #DefaultValue: "dummy_name",
        },
        "ROI_coords": {
            Type: (int,),
            Description: ("ROI corners"),
        }
    }

    def __init__(self, inst, props, *args, **kwargs):
        super(PseudoCounterController, self).__init__(inst, props, *args, **kwargs)
        self._lavue_tangoDS = ""
        self._ROI_name = ""
        self._mean = 0
        self._ROI_coords = [0, 0, 0, 0]
    
    def GetCtrlPar(self, par):
        if par == "ROI_name":
            return self._ROI_name
        elif par == "lavue_tangoDS":
            return self._lavue_tangoDS
        elif par == "ROI_coords":
            return self._ROI_coords
        # if par in self.ctrl_attributes.keys():
        #     getattr(self, f"_{par}")

    def SetCtrlPar(self, par, value):
        # if par in self.ctrl_attributes.keys():
        #     setattr(self, f"_{par}", value)
        if par == "ROI_name":
            self._ROI_name = value
        elif par == "lavue_tangoDS":
            self._lavue_tangoDS = value
            self.create_attribute_proxy()
        self.fetch_ROI()

    def Calc(self, axis, image):
        if axis == 1:
            image = image[0]
            #print(f'axis={axis}, image={image}')
            # in lavuecontroller x1, y1, x2, y2
            x1, y1, x2, y2 = self._ROI_coords
            self._mean = np.mean(image[y1:y2, x1:x2])
            return self._mean

    def create_attribute_proxy(self):
        try:
            lavue_tango_full_path = join(self._lavue_tangoDS, "DetectorROIs")
            self.lavue_attr = AttributeProxy(lavue_tango_full_path)
            if self.lavue_attr.get_poll_period() == 0:
                self.lavue_attr.poll(1000)
            self._event_id = self.lavue_attr.subscribe_event(
                EventType.CHANGE_EVENT, self.fetch_ROI
            )
        except:
            self.lavue_attr = None

    def fetch_ROI(self, e=None):
        if self.lavue_attr is not None:
            try:
                ROIs = json.loads(self.lavue_attr.read().value)
            except:
                print("Unable to read attribute from lavue TangoDS")
                ROIs = None
            self.ROI_dict = ROIs
            self.update_coords()

    def update_coords(self):
        if self._ROI_name != "":
            ROI = self.ROI_dict.get(self._ROI_name)[0]
            if ROI is not None:
                self._ROI_coords = list(map(lambda x: max(x, 0), ROI))
