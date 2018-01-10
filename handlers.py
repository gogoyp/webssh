__author__ = 'xsank'

import logging

import tornado.web
import tornado.websocket

from daemon import Bridge
from data import ClientData
from utils import check_ip, check_port


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")


class WSHandler(tornado.websocket.WebSocketHandler):

    clients = dict()

    def get_client(self):
        #logging.info('get_client ....self._id()= %s' % self._id())
        return self.clients.get(self._id(), None)

    def put_client(self):
        bridge = Bridge(self)
        #logging.info('put_client ....self._id()= %s' % self._id())
        self.clients[self._id()] = bridge

    def remove_client(self):
        bridge = self.get_client()
        #logging.info('remove_client ....self._id()= %s' % self._id())
        if bridge:
            bridge.destroy()
            del self.clients[self._id()]

    @staticmethod
    def _check_init_param(data):
        #return check_ip(data["hostname"]) and check_port(data["port"])
        return True;
    @staticmethod
    def _is_init_data(data):
        return data.get_type() == 'init'

    def _id(self):
        return id(self)

    def open(self):
        logging.info('open ....self._id()= %s' % self._id())
        self.put_client()

    def on_message(self, message):
        #logging.info('on_message: %s' % self._id())
        bridge = self.get_client()
        client_data = ClientData(message)
        if self._is_init_data(client_data):
            if self._check_init_param(client_data.data):
                bridge.open(client_data.data)
                #logging.info('connection established from: %s' % self._id())
            else:
                self.remove_client()
                #logging.warning('init param invalid: %s' % client_data.data)
        else:
            if bridge:
                #logging.warning('bridge param from: %s' % client_data.data)
                bridge.trans_forward(client_data.data)

    def on_close(self):
        self.remove_client()
        logging.info('client close the connection: %s' % self._id())
