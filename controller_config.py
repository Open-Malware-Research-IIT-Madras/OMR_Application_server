from email_config import *
from database_config import *
from imports import *
from multipurpose_email import *
from flask import session, send_file, redirect, url_for, render_template, request
from app_config import *
from file_checks import process_zip

username_list = []
picture =""

# ---------------------- ROOT CONTROLLER ----------------------
@app.route("/")
@cache.cached(timeout = 60, key_prefix='login')
def welcome():
    logger.info('Inside the welcome function at root')
    return render_template("sign-in.html")


# ---------------------- GOOGLE LOGIN ----------------------
@app.route("/login/google")
def login_google():
    try:
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=15)
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
    # print("this is the oauth token",json.dumps(token)
    

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
@cache.cached(timeout = 30, key_prefix='your-dashboard')
def send_upload():
    # picture=session['oauth_token']['user_info']['picture'] 
    if 'email' not in session or 'actual_name' not in session or 'oauth_token' not in session:
        return redirect('/')
    logger.info('Inside the send upload function')
    machine_list=[
        "[WM01] : Windows 10, Lenovo think center",
        "[LM01] : Ubuntu 22.04, Dell Optiplex", 
        "[LM02] : Ubuntu 24.04, Asus", 
        "[AP01] : Android 10, Dell Optiplex"
    ]
    # return render_template("dashboard.html", profile_picture=picture)
    return render_template("dashboard.html", machines = machine_list)

# ---------------------- FILE SUBMISSION TABLE PAGE ----------------------
@app.route('/submission-table', methods=['GET'])
@cache.cached(timeout = 30, key_prefix='submission-table')
def submission_table():
    if 'email' not in session or 'actual_name' not in session or 'oauth_token' not in session:
        return redirect('/')
    
    logger.info('Inside the submission table function')
    return render_template("tables.html")

@app.route('/signout')
def signout():
    session.clear
    return redirect('/')


# ---------------------- FILE RECEIVE HANDLER ----------------------
@app.route('/filesend', methods=['POST'])
def receive():
    print("The value of the path is", app.instance_path)
    error_list=[]
    print("In the function 1")
    if request.method == 'POST':
        email = session.get('email')
        actual_name = session.get('actual_name')
        token_temp_store=session.get('oauth_token')
        oauth_token = json.loads(token_temp_store)
        
        print("This is the oauth token", oauth_token)
        
        user_information = oauth_token['userinfo']
        picture=user_information['picture'] 
        file = request.files['file']
        
        print("Values from session:", email, actual_name, user_information)
       
        user_id = User_Check(email=email, username=actual_name, oauth_information=user_information)
        comments = request.form['Comments']
        filename = file.filename 
        machine_destination=request.form['Machine']  #taking the OS on which the file will run 
        
        print("Calline the process_zip method of file_checks")

        file_md5_hash, error_list = process_zip(file, 25, app.config['UPLOAD_EXTENSIONS'])
        print("These are the errors that are recorded",error_list)
        if len(error_list)>0:
            return render_template(
                  "filefailure.html",
                   errors=error_list
            )
        
        filename=file_md5_hash

        
        status, trail, job_id = checkMalware(filename)

        if status != -1 and trail != -1 and job_id != -1:
            setReq(user_id, job_id, comments)

            if status == 2:
                
                email_to_send= [email]
                multi_mail('send_success_email',filename.split('.')[0], job_id, email_to_send, actual_name)
                
                flash("This job has been successfully processed earlier. You will receive your report soon via email.")
                return render_template('submission_table.html')
            
            elif status == 0 or status == 1:
                flash("Kindly wait, somebody has uploaded the same file that you have that is currently in process. You will be notified shortly")
        else:
            job_id = enterMalware(filename, user_id)
            setReq(user_id, job_id, comments)

            file.seek(0)
         
            save_location_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_location_path)
            
            p=subprocess.Popen([f'mkdir {save_location_path}{file_md5_hash} ; zip  '],shell=True, stdout=subprocess.PIPE)
            p.wait()
            print("file split into 5 parts and stored in NFS")


            email_to_send = [email]
            multi_mail('job_sent_ack', filename_to_send, job_id, email_to_send, actual_name)
            pushqueue(file_md5_hash, job_id, machine_destination)
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
# @app.route('/download/<Trail_Name>', methods=['GET'])
# def send_email(Trail_Name):
#     path = "/home/omrapp/Desktop/reporthash/" + "radar_processed_" + Trail_Name + ".zip"
#     print("User is downloading trail file:", Trail_Name)
#     return send_file(path, as_attachment=True)
