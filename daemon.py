import websocket

__author__ = 'xsank'
import logging
import paramiko
from paramiko.ssh_exception import AuthenticationException, SSHException
from tornado.websocket import WebSocketClosedError
import message_pb2
import socket

from ioloop import IOLoop


class Bridge(object):
    def __init__(self, websocket):
        self._websocket = websocket
        self._shell = None
        self.ssh = None
        self._id = 0
        self._type = "os"

    @property
    def id(self):
        return self._id

    @property
    def websocket(self):
        return self._websocket

    @property
    def shell(self):
        return self._shell

    def open(self, data={}):
        if data["type"] == "os":
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                self.ssh.connect(
                    hostname=data["hostname"],
                    port=int(data["port"]),
                    username=data["username"],
                    password=data["password"],
                )
            except AuthenticationException:
                raise Exception("auth failed user:%s ,passwd:%s" %
                                (data["username"], data["password"]))
            except SSHException:
                raise Exception("could not connect to host:%s:%s" %
                                (data["hostname"], data["port"]))
        else:
            appname = "test"
            access_token = "test"
            proc_name = "test"
            instance_no = "test"
            # ip = "10.11.20.103"
            ip = data["ip"]
            endpoint = "ws://%s:8888/enter" % ip
            # containerID = "882bb35343f2"
            containerid = data["containerid"]
            header = ["access-token: %s" % access_token,
                      "app-name: %s" % appname,
                      "proc-name: %s" % proc_name,
                      "instance-no: %s" % instance_no,
                      "term-type: xterm",
                      "containerID: %s" % containerid]
            sslopt = {"cert_reqs": 0}
            self._type = "docker"
            self._shell = websocket.create_connection(
                url=endpoint, header=header, sslopt=sslopt)

        self.establish()

    def establish(self, term="xterm"):

        #   data = self.bridges[fd].shell.recv(MAX_DATA_BUFFER)
        #   data = self._ws.recv()
        if self._type == "os":
            self._shell = self.ssh.invoke_shell(term)
            self._shell.setblocking(0)
            self._id = self._shell.fileno()
            IOLoop.instance().register(self)
            IOLoop.instance().add_future(self.trans_back())
        else:
            self._id = self._shell.fileno()
            self._send_window_resize()
            IOLoop.instance().register(self)
            IOLoop.instance().add_future(self.trans_back())

    def trans_forward(self, data=""):
        if self._shell:
            if self._type == "os":
                self._shell.send(data)
            else:
                utf8char = self._gen_plain_request(data)
                self._shell.send(utf8char)

    def recv(self):
        data = ""
        if self._type == "os":
            data = self._shell.recv(1024 * 1024)
        else:
            try:
                tmp = self._shell.recv()
            except websocket.WebSocketConnectionClosedException:
                self._websocket.close()
            if tmp == 'ping':
                raise socket.timeout
            resp_msg = self._gen_response(tmp)
            if resp_msg.msgType == message_pb2.ResponseMessage.STDOUT:
                data = resp_msg.content.decode('utf-8', 'replace')

        return data

    def trans_back(self):
        #logging.info('trans_back  self.id: %s' % self.id)
        if self._type == "os":
            yield self.id
            connected = True
            while connected:
                result = yield
                logging.info('trans_back os self._websocket: %s' % self._websocket)
                if self._websocket:
                    try:
                        #logging.info('trans_back os result: %s' % result)
                        self._websocket.write_message(result)
                    except WebSocketClosedError:
                        connected = False
                    if result.strip() == 'logout':
                        connected = False
            self.destroy()
        else:
            yield self.id
            connected = True
            while connected:
                result = yield
                #logging.info('trans_back docker self._websocket: %s' % self._websocket)
                if self._websocket:
                    try:
                        #logging.info('trans_back docker result: %s' % result)
                        self._websocket.write_message(result)
                    except WebSocketClosedError:
                        connected = False
                    if result.strip() == 'exit':
                        connected = False
            self.destroy()

    def destroy(self):
        if self._type == "os":
            self._websocket.close()
            self.ssh.close()
        else:
            self._websocket.close()
            self._shell.close()

    def _gen_plain_request(self, content):
        req_message = message_pb2.RequestMessage()
        req_message.msgType = message_pb2.RequestMessage.PLAIN
        data = content.decode("utf-8")
        req_message.content = data.encode("utf-8")
        print content
        print content.decode("utf-8")
        return req_message.SerializeToString()

    def _gen_response(self, payload):
        resp_message = message_pb2.ResponseMessage()
        resp_message.ParseFromString(payload)
        return resp_message

    def _gen_resize_request(self, width, height):
        req_message = message_pb2.RequestMessage()
        req_message.msgType = message_pb2.RequestMessage.WINCH
        req_message.content = "%d %d" % (width, height)
        return req_message.SerializeToString()

    def _send_window_resize(self):
        width, height = 80, 24
        self._shell.send(self._gen_resize_request(width, height))
