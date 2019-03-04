from flask import Flask, jsonify, request
from pynodes import pynodes
import logging, requests, _thread
import time, sys

# user input
username = input("Username: ")

# async i/o
messages = []
msg = "(%s): " % username
def myth():
	time.sleep(0.1)
	while (lambda: not globals()['stopnode'])():
		for i in messages:
			sys.stdout.flush()
			sys.stdout.write("\r%s\n%s" % (i, msg))
			messages.remove(i)

# bye bye stupid flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# these must be the same on all lanchat users
srv_port = 8080
nod_port = 8088

# for killing the node's threads
stopnode = False

# simple chat msg reciever
app = Flask(__name__)
@app.route("/send", methods=['POST'])
def app_send():
	usr = request.form['user']
	msg = request.form['msg']
	messages.append("[%s]: %s" % (usr, msg))
	return "ok"
_thread.start_new_thread(lambda: app.run(host="0.0.0.0", port=srv_port), ())

# lets make it public
node = pynodes.Node(("0.0.0.0",nod_port))
_thread.start_new_thread(node.start, (lambda: not globals()['stopnode'],))

# sending messages
def send_msg(node, msg, user):
	for addr in node.peers:
		url = "http://%s:%i/send" % (addr.split(":")[0], srv_port)
		try:
			r = requests.post(url, data={'user':user, 'msg':msg}).content
		except Exception as e:
			messages.append("[!] Error connecting to peer[%s]:" % addr,e)
			continue

# main
_thread.start_new_thread(myth, ())
while True:
	try:
		send = input(msg)
		_thread.start_new_thread(send_msg, (node, send, username))
	except KeyboardInterrupt:
		globals()['stopnode'] = True
		print("[*] Waiting for threads to finish...")
		time.sleep(4) # thats a good number, right?
		exit(0)