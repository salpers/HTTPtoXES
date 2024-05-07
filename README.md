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

## File Structure 
- [**Archive**](archive) contains notebooks and files to illustrate my progress throughout my master thesis. However, I did not check whether the notebooks run with the new file structure.
- [**Data**](data) Data folder for the submission notebook. Due to file size constraints from GitHub this folder needs to be manually populated by downloading the [data.zip](https://drive.google.com/file/d/1LpoE9J23hurN4ppgrPEcLLenalWfowNT/view?usp=sharing) file.
- [**Event Loop**](event_loop) Python package with all classes related to the approach. 
- [**Notebook**](notebook) Contains the final event loop notebook for the submisison. Launch this notebook to obtain the results reported in my thesis. 
- [**Out**](out) Data folder for the output xes files. Used in earlier versions for conformance checking. However, conformance checking is now integrated in the submission notebook.

