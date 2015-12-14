#myServer.py

import socket
import sys
import select
import Queue
from thread import *

HOST = '10.0.0.4'
PORT = 8008
BUFFER_SIZE = 1024

#initialize user_list
user_list = []
unread = []
conns = []
subs = []

user = {'username': 'britt', 'password': 'seto',
    'status': 'offline', 'unread_messages': unread,
    'subsriptions': subs,
    'connections': conns, 'num_unread': 0}
user['subscriptions'] = ['admin', 'username']
user_list.append(user)
user = {'username': 'admin', 'password': 'admin',
    	'status': 'offline', 'unread_messages': unread,
    	'subsriptions': subs,
    'connections': conns, 'num_unread': 0}
user['subscriptions'] = ['britt', 'username']
user_list.append(user)
user = {'username': 'username', 'password': 'password',
    	'status': 'offline', 'unread_messages': unread,
    	'subsriptions': subs,
    'connections': conns, 'num_unread': 0}
user['subscriptions'] = ['britt','admin']
user_list.append(user)



user['subscriptions'] = []

message_list = []
hashtags = []
############################################################################
def get_user( USER, user_list ):
    for usr in user_list:
   	 if usr['username'] == USER:
   		 return usr

def verify_user( user_pw, client ):
    user_found = False

    data = user_pw.split()
    
#    print data    
    
    username = data[0]
    password = data[1]
    
    for user in user_list:
   	 if((username == user['username']) and
   		(password == user['password'])):
   		 user['status'] = 'online'
   		 user['connections'] = client
   		 user_found = True
   		 break
    
    return user_found

def edit_subs( USER, option, client):    
    curr_usr = get_user(USER, user_list)
    if option == '1':
   	 usr = client.recv(BUFFER_SIZE)
   	 msg_to_send = ''
   	 for n in user_list:
   		 if n['username'] == usr:
   			 curr_usr['subscriptions'].append(usr)
   			 msg_to_send = 'User added!'
   	 if msg_to_send == '':
   		 msg_to_send = 'Invalid username.'

   	 client.send(msg_to_send)
    if option == '2':
   	 curr_subs = ''
   	 
   	 if len(curr_usr['subscriptions']) > 0:
   		 for n in curr_usr['subscriptions']:
   			 curr_subs += n + '~'
   		 client.send(curr_subs)
   	 
   		 usr_dlt = client.recv(BUFFER_SIZE)

   		 for n in curr_usr['subscriptions']:
   			 if n == usr_dlt:
   				 curr_usr['subscriptions'].remove(usr_dlt)
   	 
   		 msg_to_send = usr_dlt + ' has been removed.'
   		 client.send(msg_to_send)
   	 
   	 else:
   		 msg_to_send = 'No subscriptions'
   		 client.send(msg_to_send)

def see_followers( USER, client ):
    msg_to_send = ''

    for n in user_list:
   	 for m in n['subscriptions']:
   		 if m == USER:
   			 msg_to_send += n['username'] + '~'
    
    if msg_to_send == '':
   	 msg_to_send = 'No followers.'
   	 client.send(msg_to_send)
    else:    
   	 client.send(msg_to_send)

def see_offline_msgs( USER, client, option ):
    messages = ''
    subs = ''
    s_msg = ''
    tmp_msg = ''
    usr = get_user(USER, user_list)
    
    if option == '1':
   	 if len(usr['unread_messages']) == 0:
   		 client.send('0')
   	 else:
    
   		 for msg in usr['unread_messages']:
   			 if tmp_msg != msg:
   				 print 'Sending...' + msg
        			 messages += msg + '~'
   			 tmp_msg = msg

   		 client.send(messages)
   		 usr['unread_messages'] = []
   		 usr['num_unread'] = 0

    elif option == '2':
   	 for s in usr['subscriptions']:    
   		 subs += s + '~'
   	 client.send(subs)
    
   	 option_usr = client.recv(BUFFER_SIZE)
   			 
   	 for s in usr['unread_messages']:
   		 if s.find(option_usr) > -1:
   			 if tmp_msg != s:
   				 s_msg += s + '~'
   			 tmp_msg = s
   			 usr['unread_messages'].remove(s)

   	 if s_msg == '':
   		 s_msg = 'No unread messages from this user.'
   		 client.send(s_msg)
   	 else:
   		 s_msg = 'Messages from ' + option_usr + ':~' + s_msg
   		 client.send(s_msg)


def post_message( USER, t, msg, ht, client):

    message = {'username': USER, 'time': t, 'bdy': msg, 'hashtag': []}
    
    if ht != '0':
   	 h = ht.split()

   	 for n in h:
   		 message['hashtag'].append(n)

    message_list.append(message)

    client.send('Message posted!')

    msg_to_send = USER + ' (' + t + '): ' + msg + ht

    curr_user = get_user(USER, user_list)

    if len(curr_user['subscriptions']) > 0:

   	 for s in curr_user['subscriptions']:
   		 curr_sub = get_user(s, user_list)
    
   		 if curr_sub['status'] == 'online':
   			 #print curr_sub['username'] + ' is online.'
   			 curr_sub['connections'].send(msg_to_send)
   		 elif curr_sub['status'] == 'offline':
   			 #print curr_sub['username'] + ' is offline.'
   			 curr_sub['unread_messages'].append(msg_to_send)   		 
   			 curr_sub['num_unread'] += 1
    else:
   	 msg_to_send = 'No subscriptons.'
   	 client.send(msg_to_send)

def hashtag_search( USER, ht, client):
    #print 'in hashtag_search'
    msg_to_send = ''
    total_msg = ''
    #print message_list
    
    for m in message_list:
   	 for n in m['hashtag']:
   		 if n == ht:
   			 msg_to_send = str(m['username']) + ' (' + str(m['time']) + '): ' + str(m['bdy'])
   			 for i in m['hashtag']:
   				 msg_to_send += ' ' + i + ' '
   			 msg_to_send += '~'
   		 total_msg += msg_to_send    
   	 msg_to_send = ''
    #print total_msg
    
    if total_msg != '':
   	 client.send(total_msg)
    else:
   	 msg_to_send = 'No hashtags found'
   	 client.send(msg_to_send)
############################################################################


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except socket.error, msg:
    print 'Failed to create socket. Error code: ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
print 'Socket created'

try:
    s.bind(('', PORT))
except socket.error, msg:
    print 'Bind failed. Error Code: ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
print 'Socket bind complete'

s.listen(10)
print 'Socket is now listening'

inputs = [s]
outputs = []
message_queues = {}

def client_thread( client ):
    
    while 1:
   	 user_recv = ''
   	 user_recv = client.recv(BUFFER_SIZE)

   	 user_found = verify_user(user_recv, client)
   	 
   	 if user_found is True:
   		 data = user_recv.split()
   		 
   		 usr = get_user(data[0], user_list)
   		 
   		 num = usr['num_unread']
   	 
   		 str_to_send = '1~' + str(num)   		 
   		 client.send(str_to_send)

   		 break
   	 else:
   		 msg_to_send = '0~0'
   		 client.send(msg_to_send)

    while 1:

   	 socket_list = [sys.stdin, client]
   	 read_s, write_s, error_s = select.select(socket_list, [], [])
   	 userinput = ''
   	 option_recv = ''

   	 for sock in read_s:
   		 if sock == client:
   			 option_recv = sock.recv(BUFFER_SIZE)   	 
   			 
   		 else:
   			 userinput = sys.stdin.readline().strip()

   	 if userinput == 'messagecount':
   		 print len(message_list)
   	 if userinput == 'usercount':
   		 i = 0
   		 for n in user_list:
   			 if n['status'] == 'online':
   				 i += 1
   		 print i
   	 if userinput == 'storedcount':
   		 i = 0
   		 for n in user_list:
   			 i += n['num_unread']
   		 print i
   	 if userinput == 'newuser':
   		 newusr = raw_input('Enter new username: ')
   		 newpw = raw_input('Enter new password: ')

   		 newuser = {'username': newusr, 'password': newpw,
   					'status': 'offline', 'unread_messages': unread,
   					'subsriptions': subs,
   					'connections': conns, 'num_unread': 0}    
   		 newuser['subscriptions'] = []   		 
   		 user_list.append(newuser)
   		 
   		 print 'Users in database: '
   		 for n in user_list:
   			 print n['username'] + ' '
 	 
   	 if option_recv != '':
   		 data_recv = option_recv.split('~')
   		 username = data_recv[0]
   		 option = data_recv[1]
   		 
   		 if option == 'logout':
   			 for user in user_list:
   				 if user['username'] == username:
   					 user['status'] = 'offline'		 
   					 client.send('You have logged out.')
   					 break

   		 if option == 'offline_msgs':
   			 see_offline_msgs(username, client, data_recv[2])
   		 
   		 if option == 'post_msg':
   			 time = data_recv[2]
   			 msg = data_recv[3]
   			 ht = data_recv[4]   			 
   			 post_message(username, time, msg, ht, client)
    
   		 if option == 'hashtag':
   			 hashtag_search(username, data_recv[2], client)
   	 
   		 if option == 'edit_subscriptions':
   			 edit_subs(username, data_recv[2], client)    
   		 
   		 if option == 'see_followers':
   			 see_followers(username, client)

    client.close()

while 1:
    timeout = 120
    readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
    
    if not (readable or writable or exceptional):
   		 print >>sys.stderr, 'TIMEOUT'
   		 continue

    for sock in readable:
   	 if sock == s:
   		 client, address = s.accept()
    
    start_new_thread(client_thread, (client,))



