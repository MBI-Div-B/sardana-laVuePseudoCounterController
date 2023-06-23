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
    counter_roles = "input_image"
    pseudo_counter_roles = "ouput_roi"

    ctrl_attributes = {
        "lavue_tangoDS": {
            Type: str,
            Description: ("lavue tangoDS address"),
            DefaultValue: "rsxs/lavuecontroller/henry",
        },
        "ROI_name": {
            Type: str,
            Description: ("name of the ROI"),
            DefaultValue: "dummy_name",
        },
    }

    def __init__(self, inst, props, *args, **kwargs):
        super(PseudoCounterController, self).__init__(inst, props, *args, **kwargs)
        self._lavue_tangoDS = ""
        self.create_attribute_proxy()
        self._ROI_name = None
        self._ROI_coords = [0, 0, 0, 0]

    def GetCtrlPar(self, par):
        if par in self.ctrl_attributes.keys():
            getattr(f"_{par}")

    def SetCtrlPar(self, par, value):
        if par in self.ctrl_attributes.keys():
            setattr(f"_{par}", value)

    def Calc(self, axis, image):
        if axis == 0:
            # in lavuecontroller x1, y1, x2, y2
            x1, y1, x2, y2 = self._ROI_coords
            mean = np.mean(image[y1:y2, x1:x2])
            return mean

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

    def fetch_ROI(self, e):
        if self.lavue_attr is not None:
            try:
                ROIs = json.loads(self.lavue_attr.read().value)
            except:
                print("Unable to read attribute from lavue TangoDS")
                ROIs = None
            self.ROI_dict = ROIs
            self.update_coords()

    def update_coords(self):
        if self.ROI_keys is not None:
            ROI = self.ROI_dict.get(self._ROI_name)
            if ROI is not None:
                # order is x1, y1, x2, y2
                self._ROI_coords = list(map(lambda x: max(x, 0), ROI))
