from email_config import *
from database_config import *
from imports import *
from multipurpose_email import *
from flask import session, send_file, redirect, url_for, render_template, request
from app_config import *

username_list = []

# ---------------------- ROOT CONTROLLER ----------------------
@app.route("/")
def welcome():
    logger.info('Inside the welcome function at root')
    return render_template("sign-in.html")


# ---------------------- GOOGLE LOGIN ----------------------
@app.route("/login/google")
def login_google():
    try:
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=30)
        logger.info('Calling Oauth')
        session['email'] = ''
        session['actual_name'] = ''
        session['oauth_token'] = ''

        redirect_uri = url_for('authorize_google', _external=True)
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        print("There was an error in the google authentication")
        logger.error('Google authentication error', e)
        return f"Error occurred during login {str(e)}", 500

# ---------------------- GOOGLE AUTH CALLBACK ----------------------
@app.route("/authorize/google")
def authorize_google():
    global username_list

    token = google.authorize_access_token()
    userinfo_endpoint = google.server_metadata['userinfo_endpoint']
    resp = google.get(userinfo_endpoint)
    user_info = resp.json()

    session['email'] = user_info['email']
    session['actual_name'] = user_info['name']
    session['oauth_token'] = json.dumps(token)

    email_verification_status = user_info['email_verified']
    if email_verification_status != True:
        return "Your email is not verified, Please verify it first and then proceed with the file upload"

    username_list.append(session['email'])

    print("From the authorize function call username is ", session.get('actual_name'))
    print("From the authorize function call email id is ", session.get('email'))
    print("From the authorization function call token is", session.get('oauth_token'))

    return redirect(url_for('send_upload'))

# ---------------------- FILE UPLOAD PAGE ----------------------
@app.route('/your-dashboard', methods=['GET'])
def send_upload():
    return render_template("dashboard.html")

# ---------------------- FILE SUBMISSION TABLE PAGE ----------------------
@app.route('/submission-table', methods=['GET'])
def submission_table():
    
    
    
    return render_template("tables.html")

@app.route('/signout')
def signout():
    session.clear
    return redirect('/')


@app.route('/contact')
def email_contact():
    # This function is yet to be implemented 
    pass 

# ---------------------- FILE RECEIVE HANDLER ----------------------
@app.route('/filesend', methods=['POST'])
def receive():
    print("The value of the path is", app.instance_path)

    if request.method == 'POST':
        email = session.get('email')
        actual_name = session.get('actual_name')
        oauth_token = session.get('oauth_token')

        file = request.files['files']
        print("Values from session:", email, actual_name, oauth_token)

        user_id = User_Check(email=email, username=actual_name, oauth_information=oauth_token)
        comments = request.form['comments']
        filename = file.filename

        if filename != '':
            file_ext = os.path.splitext(filename)[1]
        else:
            return "You have not uploaded any file! Please try again!"

        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return "File type not supported. Please try again with executables only!"

        filename_to_send = filename
        filename = secure_filename(filename)
        file_md5_hash = hashlib.md5(file.read()).hexdigest()
        filename = file_md5_hash + ".dat"

        # Check if file has already been processed
        status, trail, job_id = checkMalware(filename)

        if status != -1 and trail != -1 and job_id != -1:
            setReq(user_id, job_id, comments)

            if status == 2:
                email_to_send= [email]
                multi_mail('send_success_email',filename.split('.')[0], job_id, email_to_send, actual_name)
                return "This job has been successfully processed earlier. You will receive your report soon via email."
            elif status == 0 or status == 1:
                return "File is under processing"
        else:
            job_id = enterMalware(filename, user_id)
            setReq(user_id, job_id, comments)

            file.seek(0)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            os.chmod(os.path.join(app.config['UPLOAD_FOLDER'], filename), 0o777)

            email_to_send = [email]
            multi_mail('job_sent_ack', filename_to_send, job_id, email_to_send, actual_name)
            pushqueue(file_md5_hash, job_id)
            file.seek(0)

            return render_template(
                "filesuccess.html",
                job_id=job_id,
                email=email,
                filename_to_send=filename_to_send,
                actual_name=actual_name
            )

    return "Bad response, POST request criteria not satisfied"

# ---------------------- FILE DOWNLOAD ----------------------
@app.route('/download/<Trail_Name>', methods=['GET'])
def send_email(Trail_Name):
    path = "/home/omrapp/Desktop/reporthash/" + "radar_processed_" + Trail_Name + ".zip"
    print("User is downloading trail file:", Trail_Name)
    return send_file(path, as_attachment=True)
