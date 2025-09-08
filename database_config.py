from app_config import *
from imports import *
load_dotenv()

#--------------------------------------------------
def pushqueue(filehash, jobid, machine_destination):
  
#   RABBITMQ_USERNAME=os.getenv('RABBITMQ_USERNAME')
#   RABBITMQ_PASSWORD=os.getenv('RABBITMQ_PASSWORD')
#   RABBITMQ_IP=os.getenv('RABBITMQ_IP')
#   RABBITMQ_PORT=os.getenv('RABBITMQ_PORT')

  credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
  connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_IP, 5672, '/',   credentials))

  channel =connection.channel()

  channel.queue_declare("master_job_queue")
  
  message = { 'File_Hash':filehash,
               'Job_Id':jobid
               
               }
  
  channel.basic_publish(exchange='job_router',
                      routing_key=machine_destination,
                      body=json.dumps(message) )

  print("Message pushed to the queue")
#---------------------------------Newly Designed Function ----------------------------------------------------------------------

def User_Check(email, username, oauth_information):
    query_check = "SELECT User_Id, NOR FROM User_Table WHERE Email = %s;" # Check if the user already exists in the User_Table
    cursor.execute(query_check, (email,))
    result = cursor.fetchone()

    if result:  # User exists, extract User_Id and current NOR
        user_id = result[0]  
        current_nor = result[1]
        new_nor = current_nor + 1   # Increment NOR (Number of Requests)
        query_update_nor = "UPDATE User_Table SET NOR = %s WHERE User_Id = %s;"
        cursor.execute(query_update_nor, (new_nor, user_id))
        return user_id   # Return the existing User_Id
    
    else:       # User does not exist, insert new user with unique User_Id based on reduced timestamp
        
        current_time = int(time.time() * 1000)  # Use milliseconds since epoch, fits within BIGINT
        # Insert new user into the User_Table
        query_insert = """   
        INSERT INTO User_Table (User_Id, Email, Date, NOR, username, oauth_information)
        VALUES (%s, %s, CURRENT_TIMESTAMP, 1, %s, %s);  -- New user, so NOR starts at 1
        """
        cursor.execute(query_insert, (current_time, email, username, oauth_information))
        return current_time  # Return the newly generated User_Id

#--------------------------------------------------
def checkMalware(filehash):
    query = "select * from malware_table where filehash = %s"
    cursor.execute(query,(filehash,))
    result = cursor.fetchone()
    if result:#--------------------------------------------------
        jobId = result[0]
        trail = result[2]
        status= result[4]
        return  status,trail,jobId
    else:
        return -1,-1,-1
        
#--------------------------------------------------
def enterMalware(filehash , user_id):
    query="insert into malware_table (filehash,user_id) values(%s,%s)"
    query2="select * from malware_table where filehash = %s"
    cursor.execute(query,(filehash,user_id,))
    result = cursor.fetchone
    if result:
        cursor.execute(query2,(filehash,))
        result2 = cursor.fetchone()
        Job_id = result2[0]
        return Job_id
        
    else:
        return -1
#--------------------------------------------------
def setReq(user_id , job_id, comment):
    query = "insert into request_table (user_id , job_id, comment)values(%s , %s , %s)"
    cursor.execute(query,(user_id,job_id,comment))
    result = cursor.fetchone
    if result:
        return 1
    else:
        return 0
#--------------------------------------------------
def enterTH(job_id , trailHash):
    query="update malware_table set status = %s,trailhash = %s where job_id = %s"
    query2="select * from malware_table where job_id = %s"
    cursor.execute(query,(2,trailHash,job_id,))
    result = cursor.fetchone
    if result:
        cursor.execute(query2,(job_id,))
        result2 = cursor.fetchone()
        Job_id = result2[0]
        return Job_id
        
    else:
        return -1
#--------------------------------------------------
def getUIDS(job_id):
    query = "SELECT user_id FROM request_table WHERE job_id = %s"
    cursor.execute(query, (job_id,))
    result = cursor.fetchall()  # Fetch all matching rows

    if result:
        # Extract user_ids from the result tuples
        user_ids = [row[0] for row in result] 
       # print(user_ids) # row[0] gets the user_id from each tuple
        return user_ids
    else:
        return [-1]  # Return [-1] if no results are found
#--------------------------------------------------
def getEmail(user_ids):
    # Create placeholders for each user_id in the tuple
    placeholders = ', '.join(['%s'] * len(user_ids))
    query = f"SELECT email FROM user_table WHERE user_id IN ({placeholders})"

    # Execute the query with the tuple of user_ids
    cursor.execute(query, user_ids)  # user_ids is already a tuple
    result = cursor.fetchall()  # Fetch all matching rows

    if result:
        # Extract emails from the result tuples
        emails = [row[0] for row in result]  # row[0] gets the email from each tuple
        return emails
    else:
        return [""]  # Return an empty string if no results are found
#--------------------------------------------------
def getUserName(user_id):
    query = "SELECT username FROM user_table WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()  # Fetch all matching rows

    if result:
        # Extract user_ids from the result tuples
        user_ids = [row[0] for row in result]  # row[0] gets the user_id from each tuple
        return user_ids
    else:
        return [-1]  # Return [-1] if no results are found

#--------------------------------------------------
#--------------------------------------------------     



# print("This is only for testing")
# uid=getUIDS(342)[0]
# value=getUserName(uid)
# print(value)