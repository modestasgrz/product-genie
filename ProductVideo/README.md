# LipSync

[![Blender 3.3](https://img.shields.io/badge/blender-3.3-%23f4792b.svg)]() [![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)]()

# Dependancies

- blender-rhubarb-lipsynclinux
- combinator
- Animation-Library

## Installation

- Use zip based blender in linux and extract it
- Install blender-rhubarb-lipsynclinux-3.0.2.zip addon first in blender :

  - From Blender: Edit > Preferences
  - Select the 'Add-ons tab' and click 'Install' in the upper right.
  - Navigate to the zip file and click 'Install Add-on from File'

- Install productvideo-1.0.6.zip addon as above in blender

## Usage

- in the object propperties section there will be a new panel of Lipsync
- select .wav file path
- select Azure as Speech Service Kernel
- select desired voice from dropdown
- run the Convert text to speech operator
- set the desired speech frame start before
- and select the target armature for running add speec hto sequencer operator
- pose assets can be added directly to rhubarb addon matching
- the pose bindings from rhubarb phonetics are tied to selected active armature
- make sure armature is selected while selecting phonetics poses matching
- if animation length is getting clipped then change the fps to 30 again it may be due to blend file transfering from multiple blender version

## Blend File setup

- make sure armature is selected while saving the blend file
-

## Dev

- new text to speech service can be added to processing.py file
  - create a class inherited from BaseTTSKernel
  - and set up necessary **init**(), getVoices(), and convert() function to do the actual tts processing
  - and add referancce of this class to kernel_dict in selection.py and also in properties/\_\_init\_\_.py
- for creating tts speech service in azure
  follow this video : https://www.youtube.com/watch?v=dl0amatX5zs until 1:12 time

- voices supported by azure are based on the region of server mentioned here : https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=stt-tts#voice-styles-and-roles
