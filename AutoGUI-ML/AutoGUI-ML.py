import gradio as gr
from gradio_image_annotation import image_annotator
import easyocr
import pygetwindow as gw, pyautogui
import json
import numpy as np
import time, sys

if __name__ == '__main__' and len(sys.argv) == 1:

    # Initialize EasyOCR reader

    # Capture screenshot of a selected window
    def capture_screenshot(window_title):
        window = gw.getWindowsWithTitle(window_title)[0]
        if window.isMinimized:
            window.restore()
        time.sleep(1)
        window.activate()

        time.sleep(1)

        window_size = (window.width, window.height)
        screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
        return screenshot, window_size

    # Run OCR and create bounding boxes
    def generate_bounding_boxes(image, use_ocr):
        image_np = np.array(image)
        boxes = []

        if use_ocr:
            import easyocr
            reader = easyocr.Reader(['en'], model_storage_directory='./models/', download_enabled=False, gpu=False)

            results = reader.readtext(image_np)
            for result in results:
                top_left, bottom_right = result[0][0], result[0][2]
                box = {
                    'xmin': int(top_left[0]),
                    'ymin': int(top_left[1]),
                    'xmax': int(bottom_right[0]),
                    'ymax': int(bottom_right[1]),
                    'label': result[1]
                }
                boxes.append(box)

        return {'image': image_np, 'boxes': boxes}

    # Save configuration to a file
    def save_configuration(window_title, window_size, annotations, filename):
        configurations = {
            window_title: {
                'window_size': window_size,
                'annotations': annotations['boxes']
            }
        }
        with open(filename, 'w') as f:
            json.dump(configurations, f)
        return f"Configuration saved to {filename}"

    # Gradio UI
    with gr.Blocks() as demo:
        gr.Markdown("## AutoGUI-ML: Powering automatic GUI operations")

        # Step 1: Select Window and Capture Screenshot
        window_dropdown = gr.Dropdown(
            choices=[w.title for w in gw.getAllWindows() if w.title],
            label="Select Window"
        )
        capture_button = gr.Button("Capture Screenshot")

        # Step 2: Display and Annotate Image
        use_ocr = gr.Checkbox(label="Use EasyOCR to Detect Text and draw bounding boxes")
        annotator = image_annotator(label="Annotated Screenshot", label_list=["Text Region"], label_colors=[(0, 255, 0)])

        # Hidden state for storing window size
        window_size_state = gr.State()

        # Step 3: Save Configuration
        filename_input = gr.Textbox(label="Filename to Save Configuration (.json)")
        save_button = gr.Button("Save Configuration")
        save_output = gr.Textbox(label="Save Output Status")

        # Capture screenshot and populate window size state
        def capture_and_process(window_title, use_ocr):
            screenshot, window_size = capture_screenshot(window_title)
            image_data = generate_bounding_boxes(screenshot, use_ocr)
            return image_data, window_size

        def save_annotations(annotations, filename, window_title, window_size):
            return save_configuration(window_title, window_size, annotations, filename)

        capture_button.click(
            fn=capture_and_process,
            inputs=[window_dropdown, use_ocr],
            outputs=[annotator, window_size_state]
        )

        save_button.click(
            fn=save_annotations,
            inputs=[annotator, filename_input, window_dropdown, window_size_state],
            outputs=save_output
        )

    demo.launch()

else:
    def open_and_resize_window(window_title, window_size):
        # Open and resize the window

        window = pyautogui.getWindowsWithTitle(window_title)[0]

        if window.isMinimized:
            window.restore()
        time.sleep(1)
        window.activate()

        time.sleep(1)
        window.resizeTo(window_size[0], window_size[1])
        print(f"Window '{window_title}' opened and resized to {window_size[0]}x{window_size[1]}")

        time.sleep(1)

    def read_bounding_box(bbox, window_title):
        # Read text from the bounding box

        window = pyautogui.getWindowsWithTitle(window_title)[0]

        screenshot = pyautogui.screenshot(region=(bbox['xmin'], bbox['ymin'], bbox['xmax'] - bbox['xmin'], bbox['ymax'] - bbox['ymin']))

        import easyocr
        reader = easyocr.Reader(['en'], model_storage_directory='./models/', download_enabled=False, gpu=False)

        ss_np = np.array(screenshot)
        results = reader.readtext(ss_np)

        for detection in results:
            print(detection[1])

    def write_bounding_box(bbox, operations, window_title):
        # Perform the specified operations on the bounding box

        window = pyautogui.getWindowsWithTitle(window_title)[0]

        center_x = window.left + (bbox['xmin'] + bbox['xmax']) // 2
        center_y = window.top +(bbox['ymin'] + bbox['ymax']) // 2


        for operation in operations:
            if operation == 'click':
                pyautogui.click(center_x, center_y)
            elif operation.startswith('keypress:'):
                keys = operation.split(':')[1]
                for key in str(keys):
                    pyautogui.press(key, interval=0.1)
            elif operation == 'enter':
                pyautogui.press('enter', interval=0.1)
            elif operation == 'copy':
                pyautogui.hotkey('ctrl', 'c')
            elif operation == 'paste':
                pyautogui.hotkey('ctrl', 'v')
            elif operation == 'delete':
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.hotkey('del')
            elif operation == 'undo':
                pyautogui.hotkey('ctrl', 'z')
            elif operation == 'redo':
                pyautogui.hotkey('ctrl', 'y')

    def exec_cmd(json_file, *args):
        print("Reading JSON file...", json_file)
        with open(json_file) as f:
            config = json.load(f)

        window_name = list(config.keys())[0]
        window_size = config[window_name]['window_size']

        open_and_resize_window(window_name, window_size)

        for i in range(0, len(args), 2):
            bb = args[i]
            fn = args[i+1]

            bbox = next((b for b in config[window_name]['annotations'] if b['label'] == bb), None)

            if bbox is None:
                print(f"Bounding box {bb} not found in config file.")
                continue

            if fn == 'read':
                read_bounding_box(bbox, window_name)
            elif fn == 'write':
                oprations = fn.split('::')[1].split(',')
                write_bounding_box(bbox, oprations, window_name)

    exec_cmd(sys.argv[1], *sys.argv[2:])


