# NeuroPSI - SensoMotion - VisuoVestibular Setup

Integrated control system (PC, Raspberry Pi 5, Arduino Uno) for mouse visuo-vestibular integration experiments with open-loop motor rig and lick port reward, with hardware and software documentation for users.


## Attributions

This repository serves as a complete personal backup of the mouse visuo-vestibular experimental rig developed at NeuroPSI (Sensomotion Lab). 
It contains a combination of original scripts, third-party libraries, and existing laboratory code that was heavily restructured and adapted for this project.

While some base scripts originate from prior lab setups or external sources, my main work focused on bringing system stability, hardware synchronization, and hardware-software reliability to the setup:

-  Maintained and debugged the primary control scripts (`experiment_manager.py`, `open_loop.py`, `visual_stimulation.py`).

- Designed and implemented a photo-diode alignment system (via a custom light spot generated in `visual_stimulation.py`) to achieve precise temporal synchronization across all experiment modules.

- Simplified overall wiring and corrected power supply.

- Debugged existing modules and implemented error handling to make the entire experimental pipeline resilient to crashes during long acquisition sessions.
