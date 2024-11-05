from flask import Flask, request, render_template, send_file
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure folders
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Create required directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename, filetypes):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in filetypes

def process_video_with_image(video_path, photo_path, x, y, start_time, end_time):
    try:
        # Load the existing video
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            raise ValueError("Could not open video file")
        
        photo = cv2.imread(photo_path)
        if photo is None:
            raise ValueError("Could not open image file")
        
        # Video properties
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(video.get(cv2.CAP_PROP_FPS))
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        # Calculate start and end frame based on start_time and end_time
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        
        # Resize the photo to fit within the video frame if necessary
        max_photo_width = width - x
        max_photo_height = height - y
        scale_factor = min(max_photo_width / photo.shape[1], max_photo_height / photo.shape[0])
        new_width = int(photo.shape[1] * scale_factor)
        new_height = int(photo.shape[0] * scale_factor)
        photo = cv2.resize(photo, (new_width, new_height))

        # Create a mask if required
        mask = np.zeros((new_height, new_width), dtype=np.uint8)
        center = (new_width // 2, new_height // 2)
        radius = min(new_width, new_height) // 3
        cv2.circle(mask, center, radius, 255, -1)
        
        # Apply circular mask
        photo_circular = cv2.bitwise_and(photo, photo, mask=mask)

        # Output video path
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output_video.mp4')
        output = cv2.VideoWriter(output_path, 
                                  cv2.VideoWriter_fourcc(*'mp4v'), 
                                  fps, 
                                  (width, height))

        # Process each frame
        for frame_index in range(total_frames):
            ret, frame = video.read()
            if not ret:
                break
            
            # Check if current frame is within the overlay duration
            if start_frame <= frame_index <= end_frame:
                # Ensure x and y are within the frame boundaries
                x_pos = max(0, min(x, width - new_width))
                y_pos = max(0, min(y, height - new_height))
                
                frame_roi = frame[y_pos:y_pos+new_height, x_pos:x_pos+new_width]
                frame_bg = cv2.bitwise_and(frame_roi, frame_roi, mask=cv2.bitwise_not(mask))
                photo_fg = cv2.bitwise_and(photo_circular, photo_circular, mask=mask)
                combined = cv2.add(frame_bg, photo_fg)
                frame[y_pos:y_pos+new_height, x_pos:x_pos+new_width] = combined
            
            output.write(frame)
        
        video.release()
        output.release()
        return output_path
    except Exception as e:
        raise Exception(f"Error processing video: {str(e)}")


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        video_file = request.files.get('video')
        image_file = request.files.get('image')
        
        if not video_file or not allowed_file(video_file.filename, {'mp4', 'avi', 'mov'}):
            return 'No valid video uploaded', 400
        if not image_file or not allowed_file(image_file.filename, {'png', 'jpg', 'jpeg'}):
            return 'No valid image uploaded', 400
        
        video_filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        video_file.save(video_path)
        
        image_filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image_file.save(image_path)
        
        x_position = int(request.form.get('x_position', 0))
        y_position = int(request.form.get('y_position', 0))
        start_time = int(request.form.get('start_time', 0))
        end_time = int(request.form.get('end_time', 0))
        
        output_path = process_video_with_image(video_path, image_path, x_position, y_position, start_time, end_time)
        
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Error processing files: {str(e)}", 500
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(image_path):
            os.remove(image_path)

if __name__ == '__main__':
    app.run(debug=True)
