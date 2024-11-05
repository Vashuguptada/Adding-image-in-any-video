import os

# Define the project structure
directories = ['templates', 'uploads', 'outputs']

# Create directories
for directory in directories:
    os.makedirs(directory, exist_ok=True)

# Create index.html in templates directory
index_html = """<!DOCTYPE html>
<html>
<head>
    <title>Video Image Processor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .upload-form {
            border: 2px dashed #ccc;
            padding: 20px;
            border-radius: 8px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
        }
        .submit-btn {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .submit-btn:hover {
            background-color: #45a049;
        }
        #loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Video Image Processor</h1>
    <div class="upload-form">
        <form id="uploadForm" action="/upload" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="video">Select Video:</label>
                <input type="file" id="video" name="video" accept="video/mp4" required>
            </div>
            <div class="form-group">
                <label for="image">Select Image:</label>
                <input type="file" id="image" name="image" accept="image/*" required>
            </div>
            <button type="submit" class="submit-btn">Process Video</button>
        </form>
    </div>
    <div id="loading">
        <p>Processing your video... Please wait...</p>
    </div>

    <script>
        document.getElementById('uploadForm').onsubmit = function() {
            document.getElementById('loading').style.display = 'block';
        };
    </script>
</body>
</html>
"""

# Write index.html
with open(os.path.join('templates', 'index.html'), 'w') as f:
    f.write(index_html)

print("Project structure created successfully!")