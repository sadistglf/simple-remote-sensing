#!/usr/bin/python
# vim: set fileencoding=utf-8 :
#
# server.py
# 
# Usage:
#
# python server.py 55557 
#
# Example call from command line:
# 
# wget 'http://localhost:55557?{"action":"test"}'
# wget 'http://localhost:55557?{"action":"chart"}'
#

# REQUIRED MODULES
import os
import signal
import sys
import glob
import socket
import threading
import time
import json
import numpy as np
from http_parser.parser import HttpParser
import urllib


# Define SIGHUP signal handler
def handler(signum, frame):
    print 'Signal handler called with signal', signum
    exit()
#enddef
signal.signal(signal.SIGHUP, handler)

# Command line arguments 
socket_port = int(sys.argv[1])

# Load In-Memory data (h5 links, templates)
data = {}
 
# Kill  existing process
mypid = int(os.getpid())
for line in os.popen("ps xa"):
   fields  = line.split()
   pid     = fields[0]
   process = fields[4]

   if len(fields)<6: continue
   ipid    = int(fields[0])
   if (fields[5].find('db_server.py') > 0) & (ipid!=mypid):
        print "KILLING PROCESS",pid
        os.kill(int(pid), signal.SIGHUP)
        print "Sleeping 5 seconds"
        time.sleep(1)
   #endif
#endfor

#-------------------------------------------------------------------------------
# DATA LOADER
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# THREAD PROGRAM 
#-------------------------------------------------------------------------------
class ClientThread ( threading.Thread ):

   # Override Thread's __init__ method to accept the parameters needed:
    def __init__ ( self, channel, details ):

      self.channel = channel
      self.details = details
      threading.Thread.__init__ ( self )

    def run ( self ):

      # Get the request info
      start = time.time()
      print 'Received connection:', self.details [ 0 ]
      js = self.channel.recv(8192);

      if js[0]=="G":
        # Its a GET 
        p = HttpParser()
        print 'Hola!'
        print js
        n = len(js)
        p.execute(js, n)
        js = p.get_query_string()
        js = urllib.unquote(js)

      print js  

      response = {
        '__status': 200,
        '__text': "oh my server"
      }
      response = json.dumps(response)

      # response = cs.sist_solares_termicos(sstopt)


      # Send data back to client
      self.channel.send(response) 

      # Close the connection
      self.channel.close()
      print 'Elapsed time ', (time.time() - start)
      print 'Closed connection: ' + self.details [ 0 ] + '  [Elapsed time ' + str((time.time() - start)) + ']'

#-------------------------------------------------------------------------------
# LISTEN FOR NEW REQUESTS
#-------------------------------------------------------------------------------

# Open socket
HOST = ''                 # Symbolic name meaning all available interfaces
PORT = socket_port        # Arbitrary non-privileged port
while True:
   socket_err = 0
   try:
      server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      server.bind((HOST, PORT))
   except socket.error, msg:
      socket_err = 1
      continue;
   #endtry

   if socket_err==1:
      print "ERROR OPENING SOCKET - WAITING 3 SECONDS"
      time.sleep(3)
   else:
      print "SOCKET OPENED"
      break
   #endif
#endwhile
      
# Wait for Requests
print '[OK]'
print '[Waiting for Requests...]'
server.listen(5)

while True:
    channel, details = server.accept()
    ClientThread ( channel, details ).start()
# endwhile

