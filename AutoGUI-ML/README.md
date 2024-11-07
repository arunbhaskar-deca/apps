# AutoGUI-ML: Your GUI automation buddy

A simple yet powerful tool for streamlining GUI repetitive tasks and extracting valuable data
This Python-powered application offers a simple solution for seamlessly automating interactions with graphical user interfaces (GUIs).
This tool empowers users to capture screenshots, perform advanced optical character recognition (OCR), annotate detected text regions, and programmatically execute actions within targeted GUI windows.

The typical use case is control of instruments in industrial settings. Many of the GUI interfaces provided by the instruments (temperature control etc.)
are built with legacy software and there are no APIs to control them directly.

The tool operates in 2 modes:

## 1) Configuration mode

Run AutoGUI-ML without any arguments.

```python AutoGUI-ML.py```

This launches a gradio web server which you can open to capture the GUI window on which you want to execute.

1) Select the window you want to capture
2) Edit the bounding boxes and provide suitable names to the bounding boxes (These names will be used as arguments in execution mode)
3) Save the configuration by providing a json file name (The window title, dimensions, bounding box coordinates are saved in the json)

## 2) Execution mode

### 2.1) Read mode

The window will be opened, resized and text will be read from all bounding boxes specified

```python AutoGUI-ML.py bb1 read bb2 read ...```

### 2.2) Operate mode

The window will be opened, resized and operations will be performed on all bounding boxes specified

```python AutoGUI-ML.py bb1 write::click,keypress:abcd,enter ...```

This will click the center of the bounding box, press keys abcd and then hits the enter key.

Currently only basic operations are supported and it can easily be expanded based on user requirements.

Only basic operations have been added in the code
