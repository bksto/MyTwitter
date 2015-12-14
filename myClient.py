#myClient.py

import socket
import sys
import time
import select
import getpass #for invisible pw

print time.ctime()

time = time.strftime('%X %x')

HOST = '10.0.0.4'
PORT = 8008
BUFFER_SIZE = 1024

try:
    	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    	print 'Failed to create socket'
    	sys.exit()

#remote_ip = socket.gethostbyname(HOST)
s.connect((HOST, PORT))

##########################################################################
def see_offline_messages(USER):
    msg = ''    
    print '1. See all offline messages'
    print '2. See message from particular user'
    
    offline_option = raw_input('Select an option: ')
    
    offline_msg_send = USER + '~' + 'offline_msgs~' + offline_option
    s.send(offline_msg_send)

    if offline_option == '1':
   	 msg = s.recv(BUFFER_SIZE)
   	 if msg != '0':
   		 msg_split = msg.split('~')
   		 for m in msg_split:
   			 print m
    elif offline_option == '2':  	 
   	  msg = s.recv(BUFFER_SIZE)
   	 

   	 msg_split = msg.split('~')
   	 for m in msg_split:
   		 print m

   	 usr_option = raw_input('Select a user: ')
   	 s.send(usr_option)    

   	 msg = s.recv(BUFFER_SIZE)
   	 
   	 msg_split= msg.split('~')
   	 for m in msg_split:
   		 print m

   	 
def edit_subscriptions(USER):
    print
    print '1. Add subscriptions'
    print '2. Delete subscriptions'
    
    sub_option = raw_input('Select option: ')

    msg_to_send = USER + '~edit_subscriptions~' + sub_option

    s.send(msg_to_send)

    if sub_option == '1':
   	 usr = raw_input('Enter user to add: ')
   	 s.send(usr)

   	 print s.recv(BUFFER_SIZE)    
 
    elif sub_option == '2':
   	 recv_msg = s.recv(BUFFER_SIZE)    

   	 if recv_msg == 'No subscriptions':
   		 print recv_msg
   	 else:
   		 recv_msg = recv_msg.split('~')

   		 for n in recv_msg:
   			 print n

   		 usr_dlt = raw_input('Which user do you want to delete? ')

   		 s.send(usr_dlt)

   		 recv_msg = s.recv(BUFFER_SIZE)
   		 print recv_msg

def post_message(USER):
    
    msg = raw_input('Enter a message to post (max. 140 characters): ')

    if len(msg) > 140:
   	 print 'Message too long.'
   	 msg = raw_input('Enter a message to post (max. 140 characters): ')

    hashtags = raw_input('Enter hashtags (Enter 0 if none): ')

    post_msg_send = USER + '~' + 'post_msg' + '~' + str(time) + '~' + msg + '~' + hashtags
    s.send(post_msg_send)

    #if s.recv(BUFFER_SIZE) != '':
    print s.recv(BUFFER_SIZE) + '\n'
 
    
def hashtag_search(USER):
    print 'hashtag search'

    ht = raw_input('Enter hashtag to search for: ')

    msg_to_send = USER + '~hashtag~'+ ht

    s.send(msg_to_send)

    msg = s.recv(BUFFER_SIZE)

    msg = msg.split('~')

    for n in msg:
   	 print n

def see_followers(USER):
    print 'Followers: '
    
    msg_to_send = USER + '~see_followers~'

    s.send(msg_to_send)

    msg = s.recv(BUFFER_SIZE)
    msg = msg.split('~')

    for n in msg:
   	 print n

def logout(USER):
    
    out = raw_input('Do you wish to logout? (Y/N) ')
    if out == 'Y':
   	 logout_msg = USER + '~' + 'logout'   	 
   	 s.send(logout_msg)    
   	 print s.recv(BUFFER_SIZE)
   	 return True
    else:
   	 return False

def display_menu(USER):
    
    while 1:
   	 print '========= Menu ========='
   	 print '1. See Offline Messages'
   	 print '2. Edit Subscriptions'
   	 print '3. Post a Message'
   	 print '4. Hashtag Search'
   	 print '5. See Followers'
   	 print '6. Logout'
   	 print '========================='
   	 print

   	 print 'Select option(1-6) from above: '
    
######    
   	 socket_list = [sys.stdin, s]
   	 read_s, write_s, error_s = select.select(socket_list, [], [])
    
   	 option = ''
    
   	 for sock in read_s:
   		 if sock == s:
   			 data = sock.recv(BUFFER_SIZE)
   		 
   			 print '\n======NEW MESSAGES=======\n'
   			 print data + '\n'
   		 else:
   			 option = sys.stdin.readline().strip()

########
   	 if option != '':
   		 if option == '1':
   			 see_offline_messages(USER)
   		 elif option == '2':
   			 edit_subscriptions(USER)
   		 elif option == '3':
   			 post_message(USER)
   		 elif option == '4':
   			 hashtag_search(USER)
   		 elif option == '5':
   			 see_followers(USER)
   		 elif option == '6':
   			 if logout(USER) == True:
   				 break
   		 else:
   			 print 'Invalid input. \n'
   		 

def display_welcome(USER, num):
    
    print '\nWelcome! You have ' + num + ' unread messages.\n'
    
    display_menu(USER)

def verify_user_pass():
    username = raw_input('Username: ')
    #password = raw_input('Password: ')
    password = getpass.getpass()
    user_pw = username + ' ' + password
    s.send(user_pw)
    
    return username

##########################################################################

while 1:
    
    USER = verify_user_pass()
    verify_user = s.recv(BUFFER_SIZE)
    verf_user, data = verify_user.split('~')
    
    if (verf_user == '1'):
   	 #display_welcome(USER, data)
   	 break
    print 'User not found!\n'

display_welcome(USER, data)


s.close()


