import gradio as gr
from gradio_image_annotation import image_annotator
import easyocr
import pygetwindow as gw
import json
from PIL import ImageGrab
import numpy as np

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Capture screenshot of a selected window
def capture_screenshot(window_title):
    window = gw.getWindowsWithTitle(window_title)[0]
    window.activate()
    window_size = (window.left, window.top, window.width, window.height)
    screenshot = ImageGrab.grab(window_size)
    return screenshot, window_size

# Run OCR and create bounding boxes
def generate_bounding_boxes(image, use_ocr):
    image_np = np.array(image)
    boxes = []

    if use_ocr:
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
    gr.Markdown("## Windows Screenshot Annotation and Keystroke Execution")

    # Step 1: Select Window and Capture Screenshot
    window_dropdown = gr.Dropdown(
        choices=[w.title for w in gw.getAllWindows() if w.title],
        label="Select Window"
    )
    capture_button = gr.Button("Capture Screenshot")
    image_output = gr.Image(label="Captured Screenshot", type="pil")

    # Step 2: Display and Annotate Image
    use_ocr = gr.Checkbox(label="Use OCR to Detect Text")
    annotator = image_annotator(label="Annotate Screenshot", label_list=["Text Region"], label_colors=[(0, 255, 0)])

    # Hidden state for storing window size
    window_size_state = gr.State()

    # Step 3: Save Configuration
    filename_input = gr.Textbox(label="Filename to Save Configuration")
    save_button = gr.Button("Save Configuration")
    save_output = gr.Textbox(label="Save Output")

    # Capture screenshot and populate window size state
    def capture_and_process(window_title, use_ocr):
        screenshot, window_size = capture_screenshot(window_title)
        image_data = generate_bounding_boxes(screenshot, use_ocr)
        return screenshot, image_data, window_size

    def save_annotations(annotations, filename, window_title, window_size):
        return save_configuration(window_title, window_size, annotations, filename)

    capture_button.click(
        fn=capture_and_process,
        inputs=[window_dropdown, use_ocr],
        outputs=[image_output, annotator, window_size_state]
    )

    save_button.click(
        fn=save_annotations,
        inputs=[annotator, filename_input, window_dropdown, window_size_state],
        outputs=save_output
    )

demo.launch()