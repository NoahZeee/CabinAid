The goal of CabinAID was to assist people with locating certain objects in their cabinets, or identifying if a certain item was present. 
It works by a sliding camera that, when prompted through user input via a webpage we set up, slides across the cabinet and identifies if the item specified by the user can be found in the cabinet. 
The way we implemented this is by using an AI video detection library included in OpenCV to process the video feed and identify objects in frame during a live video feed.
