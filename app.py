import os
from flask import Response, Flask, request, send_file, flash, redirect, url_for, render_template, abort
from werkzeug.utils import secure_filename
import uuid
import datetime
import cv2
from pathlib import Path
from process import process_image

WEBSERVICE_PORT = int(os.environ["WEBSERVICE_PORT"])
UPLOAD_FOLDER = os.environ["UPLOAD_FOLDER"]
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mpeg', 'avi', 'mov', 'wmv', 'flv', 'avchd', 'webm', 'mkv'}
ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


application = Flask(__name__, static_folder=UPLOAD_FOLDER, static_url_path='')


@application.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@application.route('/listall/', defaults={'req_path': UPLOAD_FOLDER})
@application.route('/listall/<path:req_path>')
def dir_listing(req_path):
    # Joining the base and the requested path
    abs_path = os.path.join(UPLOAD_FOLDER, req_path)
    print(UPLOAD_FOLDER, ' ', abs_path, ' ', req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = os.listdir(abs_path)
    return render_template('files.html', files=files)


@application.route('/feedback/<file_id>/<feedback_type>', methods=['GET', 'POST'])
def feedback(file_id, feedback_type):
    if feedback_type == 'Correct' or feedback_type == 'Incorrect':
        with open(os.path.join(application.config['UPLOAD_FOLDER'], file_id, 'feedback.txt'), "w") as file1:
            file1.write(f"{feedback_type}")
        message = f'Feedback received for file id#{file_id}. Feedback is {feedback_type}'
    else:
        message = 'Wrong feedback type'
    return message


@application.route('/process_photo/', methods=['GET', 'POST'])
def process_photo():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('Not selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, ALLOWED_PHOTO_EXTENSIONS):
            filename = secure_filename(file.filename)
            extension=filename.split('.')[-1]
            file_id=f'{str(uuid.uuid4())}'
            uploded_filename = f'{file_id}.{extension}'
            folder_path=os.path.join(application.config['UPLOAD_FOLDER'], file_id)
            save_dir = Path(folder_path, exist_ok=True)  # increment run
            save_dir.mkdir(parents=True, exist_ok=True)  # make dir
            path = str(save_dir / uploded_filename)
            file.save(path)
            print(f'Upload is done, path={path}')

            processed_image_path, crops = process_image(path)
             
            print(f'Processing is done, path={processed_image_path}')
            return render_template('process_photo.html', output_filename=(processed_image_path, file_id), crops=crops)
        else:
            print('Unknown file extension')
            return {"status": "error", "message": 'Unknown file extension'}, 404

    return '''
        <h1>Balcony recognition service. Please upload photo</h1>
        <form method="post" enctype="multipart/form-data">
          <input type="file" name="file">
          <input type="submit">
        </form>
        ''', 200


if __name__ == '__main__':
    application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    application.run(debug=False, port=WEBSERVICE_PORT, host='0.0.0.0')
