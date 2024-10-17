from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os, cv2, numpy as np

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['RESIZED_FOLDER'] = 'resized'


#Create a directory with name= 'resized' to store resized images if not exists
if not os.path.exists(os.path.join('static', 'resized')):
    os.makedirs(os.path.join('static', 'resized'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    print(f"the operation is : {operation} And file name is : {filename}")
    img = cv2.imread(f"uploads/{filename}")
    match operation:
        case "cgrey":
            processedImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, processedImg)
            return newFilename
        case "cwebp":
            newFilename = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cjpg":
            newFilename = f"static/{filename.split('.')[0]}.jpg"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cjpeg":
            newFilename = f"static/{filename.split('.')[0]}.jpeg"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cpng":
            newFilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newFilename, img)
            return newFilename

    pass

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/resize")
def resize():
    return render_template("resize.html")


@app.route("/guidance")
def contact():
    return render_template("guidance.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return "No file is selected !"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new=processImage(filename, operation)
            flash(f"Your image has been processed and is available <a href='/{new}' style='text-decoration: none' target='_blank'>here</a>")
            return render_template("index.html")
        
    return render_template("index.html")


@app.route("/upload", methods=["POST", "GET"])
def upload_image():
    if request.method == "POST":
        # Get the user-uploaded image:
        file = request.files['image']
        # Get the width and height provided:
        width = int(request.form['width'])
        height = int(request.form['height'])

        # Read the image using CV2:
        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

        # Resize the image:
        resized_image = cv2.resize(image, (width, height))

        # Save the resized image in the 'resized' folder:
        resized_image_path = os.path.join('static', 'resized', file.filename)
        cv2.imwrite(resized_image_path, resized_image)

        # Update the flash message URL
        flash(f"Your image has been resized and is available <a href='/static/resized/{file.filename}' style='text-decoration: none' target='_blank'>here</a>")

        return render_template("index.html")


app.run(debug=True, port=5001)
