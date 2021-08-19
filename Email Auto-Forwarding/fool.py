from apiclient import discovery
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from bs4 import BeautifulSoup
import re
import time
import dateutil.parser as parser
from datetime import datetime
import datetime
import csv
from email.mime.text import MIMEText

# Creating a storage.JSON file with authentication details
SCOPES = 'https://www.googleapis.com/auth/gmail.modify' # we are using modify and not readonly, as we will be marking the messages Read
store = file.Storage('storage.json') 
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
GMAIL = discovery.build('gmail', 'v1', http=creds.authorize(Http()))
#print time.time()
#print "current time"

'''current_milli_time = lambda: int(round((time.time()-5000)))
print "milli time -5000"
'''
user_id =  'me'
label_id_one = 'INBOX'
label_id_two = 'UNREAD'

# Getting all the unread messages from Inbox
# labelIds can be changed accordingly
#time_current = str(current_milli_time())
#print time_current
#q = "after:"+time_current
unread_msgs = GMAIL.users().messages().list(userId='me',labelIds=[label_id_one,label_id_two]).execute()

print "unread_msgs"
print unread_msgs

print "unread_msgs"
# We get a dictonary. Now reading values for the key 'messages'
mssg_list = unread_msgs['messages']

print ("Total unread messages in inbox: ", str(len(mssg_list)))

final_list = [ ]


for mssg in mssg_list:
    
    temp_dict = { }
    m_id = mssg['id'] # get id of individual message
    t_id=mssg['threadId']
    message = GMAIL.users().messages().get(userId=user_id, id=m_id).execute() # fetch the message using API
    thread = GMAIL.users().messages().get(userId=user_id, id=t_id).execute()
    payld = message['payload'] # get payload of the message 
    headr = payld['headers'] # get header of the payload
    for one in headr:
        
        # getting the Subject
        if one['name'] == 'Subject':
            msg_subject = one['value']
            temp_dict['Subject'] = msg_subject
        else:
            pass
    for two in headr:
        # getting the date
        if two['name'] == 'Date':
            msg_date = two['value']
            date_parse = (parser.parse(msg_date))
            m_date = (date_parse.date())
            temp_dict['Date'] = str(m_date)
        else:
            pass
    for three in headr:
        # getting the Sender
        if three['name'] == 'From':
            msg_from = three['value']
            temp_dict['Sender'] = msg_from
        else:
            pass
    temp_dict['Snippet'] = message['snippet'] # fetching message snippet
    try:
        # Fetching message body
        mssg_parts = payld['parts'] # fetching the message parts
        part_one  = mssg_parts[0] # fetching first element of the part 
        part_body = part_one['body'] # fetching body of the message
        part_data = part_body['data'] # fetching data from the body
        clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
        clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
        clean_two = base64.b64decode(clean_one.encode('UTF-8')) # decoding from Base64 to UTF-8
        #print (clean_two)
        #soup = BeautifulSoup(clean_two , "lxml" )
        #mssg_body = soup.body()
         # mssg_body is a readible form of message body
            # depending on the end user's requirements, it can be further cleaned 
            # using regex, beautiful soup, or any other method
        mssg_body = str(clean_two)
        #temp_dict['Message_body'] = mssg_body
        mssg_body=str(mssg_body)
        '''print "body"
        print mssg_body
        print "body"'''
        counts = dict()
        words = mssg_body.split()
        for word in words:
            if word in counts:
                counts[word] += 1
            else:
                counts[word] = 1
                                          

        count_status=0
        count_enq=0
        count_notify=0
        if "enquiry" in counts:
            count_enq=count_enq+1
        if "Enquiry" in counts:
            count_enq=count_enq+1
        if "ENQUIRY" in counts:
            count_enq=count_enq+1
        if "rfiq" in counts:
            count_enq=count_enq+1
        if "Rfiq" in counts:
            count_enq=count_enq+1
        if "RFIQ" in counts:
            count_enq=count_enq+1

        if "status" in counts:
            count_status=count_status+1
        if "Status" in counts:
            count_status=count_status+1
        if "STATUS" in counts:
            count_status=count_status+1
        if "status1" in counts:
            count_status=count_status+1
        if "Status1" in counts:
            count_status=count_status+1
        if "STATUS1" in counts:
            count_status=count_status+1
        
        if "notification" in counts:
            count_notify=count_notify+1
        if "Notification" in counts:
            count_notify=count_notify+1
        if "NOTIFICATION" in counts:
            count_notify=count_notify+1
        if "notification1" in counts:
            count_notify=count_notify+1
        if "Notification1" in counts:
            count_notify=count_notify+1
        if "NOTIFICATION1" in counts:
            count_notify=count_notify+1
        
        title="Forwarded message\n"

        sendfrom="From : " + (msg_from) + "\n"
        senddate="Date :" +str(m_date)+ "\n"
        sendto="To : scriptscheck@gmail.com"+"\n"
        subject="Fwd:"+msg_subject+"\n"
        sendmssg_body=title+sendfrom+senddate+sendto+subject
        sendbody="Forwared using autoresponder \n"+"  "+sendmssg_body + "\n \n \n  \n \n Current message:\n" +mssg_body
        finalmessage=MIMEText(sendbody)
        
        finalmessage['from']=msg_from
        finalmessage['subject']="notification"
       
 
        if (max(count_notify,count_status,count_enq) == count_notify):
            finalmessage['to']="arjunsk1997@gmail.com"
            body = {'raw': base64.urlsafe_b64encode(finalmessage.as_string())}
            
        if (max(count_notify,count_status,count_enq) == count_status):
            finalmessage['to']="andyforbarca.123@gmail.com"
            body = {'raw': base64.urlsafe_b64encode(finalmessage.as_string())}

        if (max(count_notify,count_status,count_enq) == count_enq):
            finalmessage['to']="andyforbarca.1@gmail.com"
            body = {'raw': base64.urlsafe_b64encode(finalmessage.as_string())}
        try:
            message = (GMAIL.users().messages().send(userId="me", body=body).execute())
            print('Message Id: %s' % message['id'])
            print(message)
        except Exception as error:
            print('An error occurred: %s' % error)   
            
          
       
        GMAIL.users().messages().modify(userId=user_id, id=m_id,body={ 'removeLabelIds': ['UNREAD']}).execute()
        
    except:
        pass
              #print (temp_dict)
              #final_list.append(temp_dict) # This will create a dictonary item in the final list
              
              # This will mark the messagea as read
              #GMAIL.users().messages().modify(userId=user_id, id=m_id,body={ 'removeLabelIds': ['UNREAD']}).execute() 
  
  


#print ("Total messaged retrived: ", str(len(final_list)))

