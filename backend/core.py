from werkzeug.wrappers import Request, Response
from jsonrpc import JSONRPCResponseManager, dispatcher


class BackendServer:
    def __init__(self):
        pass

    @staticmethod
    @dispatcher.add_method
    def query(string):
        return string

    @dispatcher.add_method
    def query_test(self):
        raise NotImplementedError

    @Request.application
    def application(self, request):
        response = JSONRPCResponseManager.handle(request.data, dispatcher)
        return Response(response.json, mimetype='application/json')
