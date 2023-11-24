# ultrasonic-computer-controller

This project uses ~20kHZ sound wave to do real-time gesture recongnization.  
It uses doppler effect to detect the relative movement bewteen the computer(microphone) and the hand.  
  
There are currently 4 gestures:
- up: swipe you palm up away from the computer keyboard
- down: swipe you palm down toward the computer keyboard
- single-tap: a quick down then up
- double-tap: 2 consecutive single-tap in a short time

## System Requirements
You would need `pyaudio` library to run this, do:  
`pip install pyaudio`  
to install it.

If you are on MacOS, you would need extra work to do it:
Please download `brew` from here: https://brew.sh
Then run  
`brew install portaudio` in your terminal
install the CLI tool if prompted
and finally run  
`pip install pyaudio`

other requirements:
- numpy
- matplotlib

## File Structures
In ./integratedDemo is the completed program, run main.py to start the project


