# CMS-CR1000x
CRBasic unit tests, integration test, and final deployment files for the OSU Climate Monitoring Station


### Polled Mode Sampling 
These CRBasic programs assume sensor(s) are polled, i.e., a RS-232 or SDI-12 command summons data from each sensor.

* ECO-SUNA-Polled.CR1X
* **ECO-SUNA-SeapHOx-EXO-Polled.CR1X   (for Deployment)**
* ECO-SUNA-SeapHOx-Polled.CR1X
* EXO-Polled_SDI12.CR1X
* EcoTriplet-Polled.CR1X
* EcoTriplet2.CR1X  (Two EcoTriplets)
* SUNA-Polled.CR1X
* SeapHOx-Polled.CR1X
* YSI-Polled_RS232.CR1X

### Continuous Mode Sampling 
These CRBasic programs assume the sensor is sampling continuously and does not need to be commanded to start sampling.

* EcoTriplet-Continous.CR1X
* SUNA-Continuous.CR1X
* YSI-Continuous_RS232.CR1X

_Note that YSI and EXO prefixes refer to the same YSI EXO<sup>2</sup> instrument.  The EXO prefix is reserved for CRBasic programs that access the instrument using the SDI-12 interface on the YSI DCP Signal Output Adapter._
