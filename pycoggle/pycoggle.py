# -*- coding: utf-8 -*-

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import request, parse
from urllib.error import *
import base64
import json
import re


class CoggleApi:
    url_template = "{api}/{verb}?{params}"
    default_headers = {"Content-Type": "application/json"}

    def get_access_token(oauth_code, username, password, redirect_uri='http://localhost:8080'):
        coggle_api_code = None
        url_get_token_data = {"grant_type": "authorization_code", "code": oauth_code, "redirect_uri": redirect_uri}
        url_get_token_data = json.dumps(url_get_token_data)
        url_get_token_data = url_get_token_data.encode()
        query = request.Request('https://coggle.it/token', data=url_get_token_data, headers=CoggleApi.default_headers, method='POST')
        auth_handler = request.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='Users', uri='coggle.it', user=username, passwd=password)
        opener = request.build_opener(auth_handler)
        request.install_opener(opener)
        with request.urlopen(query) as result:
            if 200 <= result.status <= 204:
                result_data = result.read()
                result_json = json.loads(result_data)
                coggle_api_code = result_json['access_token']
            else:
                print(result.status)
                print(result.reason)
        return coggle_api_code

    def __init__(self, token):
        self.token = token
        self.default_params = {"access_token": token}
        self._diagrams = {}
        self._url = "https://coggle.it/api/1"

    def _get(self, verb, params, headers):
        return self._http('GET', verb, params, headers, None)

    def _put(self, verb, params, headers, data):
        return self._http('PUT', verb, params, headers, data)

    def _post(self, verb, params, headers, data):
        return self._http('POST', verb, params, headers, data)

    def _delete(self, verb, params, headers):
        return self._http('DELETE', verb, params, headers, None)

    def _http(self, method, verb, params, headers, data):
        results_json = []
        url_params = self.default_params.copy()
        if params:
            url_params.update( params )
        url_headers = CoggleApi.default_headers.copy()
        if headers:
            url_headers.update( headers )
        url_data = None
        if data:
            url_data = data.encode()
        url = CoggleApi.url_template.format(api=self._url, verb=verb, params=parse.urlencode(url_params))
        query = request.Request(url, data=url_data, headers=url_headers, method=method)
        with request.urlopen(query) as result:
            if 200 <= result.status <= 204:
                result_data = result.read()
                results_json = json.loads(result_data)
            else:
                print(result.status)
                print(result.reason)
        return results_json

    @property
    def diagrams(self):
        self._diagrams = {}
        diagrams_json = self._get(verb="diagrams", params=None, headers=None)
        for diagram_json in diagrams_json:
            diagram_coggle = CoggleDiagram(self, diagram_json)
            self._diagrams.update( {diagram_coggle.title: diagram_coggle} )
        return self._diagrams


class CoggleDiagram:
    def __init__(self, api, diagram_json):
        self._api = api
        self._verb = 'diagrams/' + diagram_json['_id']
        self._id = diagram_json['_id']
        self._title = diagram_json['title']
        self._nodes = []
        self._root_node = None

    @property
    def id(self):
        return _id

    @property
    def title(self):
        return self._title

    @property
    def root_node(self):
        if not self._root_node:
            self.nodes
        return self._root_node

    @property
    def nodes(self):
        self._nodes = []
        nodes_verb = self._verb + '/nodes'
        nodes_json = self._api._get(verb=nodes_verb, params=None, headers=None)
        node_coggle = CoggleNode(self, nodes_json[0], None)
        self._nodes.append(node_coggle)
        self._root_node = node_coggle
        self._find_child_nodes(nodes_json[0], node_coggle)
        return self._nodes

    def create_node(self, text, parent):
        nodes_verb = self._verb + '/nodes'
        if parent:
            parent_id = parent._id
        else:
            parent_id = self.root_node._id
        node_data = {'text': text, 'parent': parent_id}
        node_data = json.dumps( node_data )
        node_json = self._api._post(verb=nodes_verb, params=None, headers=None, data=node_data)
        node_coggle = CoggleNode(self, node_json, parent)
        self._nodes.append(node_coggle)
        return node_coggle

    def clear(self):
        [ node.delete() for node in self.nodes if node.parent is None ]
        self._nodes = []

    def arrange(self):
        nodes_verb = self._verb + '/nodes'
        arrange_params = {'action': 'arrange'}
        self._api._put(verb=nodes_verb, params=arrange_params, headers=None, data=None)

    def _find_child_nodes(self, node_json, node):
        for child_json in node_json['children']:
            child_coggle = CoggleNode(self, child_json, node)
            self._nodes.append( child_coggle )
            self._find_child_nodes(child_json, child_coggle)


class CoggleNode:
    def __init__(self, diagram, node_json, parent):
        self._diagram = diagram
        self._verb = self._diagram._verb + '/nodes/' + node_json['_id']
        self._id = node_json['_id']
        self._parent = parent
        self._text = node_json['text']

    @property
    def id(self):
        return self._id

    @property
    def parent(self):
        return self._parent

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        node_text = {"text": value}
        node_text = json.dumps( node_text )
        self._diagram._api._put(verb=self._verb, params=None, headers=None, data=node_text)

    def delete(self):
        nodes_count = self._diagram._api._delete(verb=self._verb, params=None, headers=None)
        return nodes_count['count']

    def __str__(self):
        return 'Node {0}: text="{1}" parent={2}'.format(self._id, self._text, self._diagram._id)

