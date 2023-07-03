# laVuePseudoCounterController
A pseudocounter that returns an averaged value in the lavue specified ROI. This version replaces an old implementation of [ROICounterController](https://github.com/MBI-Div-B/sardana-ROICounterController).

In contrast with the previous implementation of the ROICounter this version retrieves data not from the Sardana but directly from the running Lavue TangoDS. This approach has multiple advantages among the fetching data from Sardana. One of those is the performance, identification of the rois with its name instead of numbers.

# Requirements
Since this PseudoController communicates with the laVue's TangoDS you need to declare the `LavueController` instance in your TangoDB. The laVue's TangoDS is distrbitued in the same package as the laVue program. I would recommend to add the TangoDS in Starter and allow it to start it on PC startup.

After the `LavueController instance_name` is defined in the Tango you need to start the laVue with an extra `-a` option:

`lavue -a lavuecontroller/device/name`

# Creating the PseudoCounter
A PseudoCounter of `laVuePseudoCounterController` type needs to be created for each ROI separately. Here is an example spock command to create the PseudoCounter with the name `roiCtrl_ccd_direct_roi`:

`defctrl LaVuePseudoCounterController roiCtrl_ccd_direct_roi input_image=ccd_image output_roi=ccd_image_direct_beam`

where `ccd_image` corresponds to output of the 2D controller and `ccd_image_direct_beam` is the averaged output of this controller.

Now you need to define the name of the `LavueController` TangoDS and the name of the ROI with the spock commands:
```python
roiCtrl_ccd_direct_roi.lavue_tangoDS = "rsxs/.../..."
roiCtrl_ccd_direct_roi.ROI_name = "direct_beam"
```

# Usage
Start you laVue with the extra `-a lavuecontroller/device/name` option. Then go to the ROI tab, create a new ROI and specify a "ROI alias(es)" in the text field. The coordinates of the ROI will be updated automaticly on each change of the its coordinates.

You can check that the ROI coordinates are correctly updated in the Sardana controller with the spock command:

`roiCtrl_ccd_direct_roi.ROI_coords`

If the coordinates are all zeros than check that the `lavue_tangoDS` and `ROI_name` are not empty and set correct. If the problem persists restart the `LavueController` TangoDS , laVue and Sardana (order is important).