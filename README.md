# HTTPtoXES
Recognizing Activity-Level Events from Network Data Streams

## About
An approach to identify activity-level events from a network traffic stream while adhering to the constraints of a streaming setting. Our approach consists of multiple hierarchical components responsible for event extraction, abstraction, contextualization, and correlation tasks. It operates on the network traffic data recordings from Hadad et al. [From Network Traffic to Event Logs](https://github.com/HaifaUniversityBPM/traffic-data-to-event-log).

With raw network traffic data as input, our approach continuously forms sequences of low-level representing activity instances, determines their activity type, and assigns them a case ID. For each identified activity, activity-level events that conform to process mining requirements are emitted to an output stream.

Our evaluation showed that our approach is effective, as it produces high fitness and precision results when compared to ground truth data as well as results with high conformance to a reference
process model.

## Overview
Our approach aims to identify activities from a stream of low-level network packets. To achieve this, the resulting activities must meet the following criteria: They need to contain a) a notion of start and end, b) a label that identifies the type of activity, and c) a case identifier. 
As illustrated below, our approach involves several steps to generate activities from a stream of network packets. These steps include event extraction, abstraction, contextualization, and correlation.

1. **Preprocessing** - We convert network packet data into low-level network events while filtering any technical overhead from the data, resulting in the network event stream SE.
2. **Activity Boundary Detection** - We detect low-level events that indicate the start and end of activities.
3. **Event-Activity Assignment** - However, since our approach operates in a setting where multiple activities from multiple cases are executed in concurrency, detecting event boundaries is insufficient. We must also assign each event that does not indicate the start of a new activity to one running activity. This process allows us to form sequences of low-level events, each representing an activity.
4.  **Activity Type Classification** - We classify the sequences with an activity label.
5.  **Case ID Assignment** - Assignment of a case identifier.
6.  **Output** - We transform each sequence into an activity instance and emit corresponding activity-level events (start & end) into the result stream SA.

![Picture 1](https://github.com/salpers/HTTPtoXES/assets/23464191/0fd0dd12-4fcc-4d50-899c-77d644e3cf27)



## Setup 
1. Create virtual env
2. install requirements in requirements via pip.  
`pip install -r requirements.txt`
4. Download [data.zip](https://drive.google.com/file/d/1LpoE9J23hurN4ppgrPEcLLenalWfowNT/view?usp=sharing).
5. Unpack the files to the [data folder](data). 

## Usage
Run the [notebook](notebook/pipeline_final.ipynb) to obtain the results presented.

## File Structure 
- [**Archive**](archive) contains notebooks and files to illustrate my progress throughout my master thesis. However, I did not check whether the notebooks run with the new file structure.
- [**Data**](data) Data folder for the submission notebook. Due to file size constraints from GitHub this folder needs to be manually populated by downloading the [data.zip](https://drive.google.com/file/d/1LpoE9J23hurN4ppgrPEcLLenalWfowNT/view?usp=sharing) file.
- [**Event Loop**](event_loop) Python package with all classes related to the approach. 
- [**Notebook**](notebook) Contains the final event loop notebook for the submisison. Launch this notebook to obtain the results reported in my thesis. 
- [**Out**](out) Data folder for the output xes files. Used in earlier versions for conformance checking. However, conformance checking is now integrated in the submission notebook.

