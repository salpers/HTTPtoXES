# HTTPtoXES
Recognizing Activity-Level Events from Network Data Streams

## About
An approach to identify activity-level events from a network traffic stream while adhering to the constraints of a streaming setting.
Our approach consists of multiple hierarchical components responsible for event extraction, abstraction, contextualization,
and correlation tasks.
It operates on the network traffic data recordings from Hadad et al. [From Network Traffic to Event Logs](https://github.com/HaifaUniversityBPM/traffic-data-to-event-log).

WIth raw network traffic data as input, our approach continuously forms sequences of low-level
representing activity instances, determines their activity type, and assigns them a
case ID. For each identified activity, activity-level events that conform to process
mining requirements are emitted to an output stream.

Our evaluation showed that our approach is effective, as it produces high fitness and precision results when compared to ground truth data as well as results with high conformance to a reference
process model.

## Setup 
1. Create virtual env
2. install requirements in requirements via pip.  
`pip install -r requirements.txt`
4. Download [data.zip](https://drive.google.com/file/d/1LpoE9J23hurN4ppgrPEcLLenalWfowNT/view?usp=sharing).
5. Unpack the files to the [data folder](data). 

## Usage
Run the [notebook](notebook/pipeline_final.ipynb) to obtain the results presented.


