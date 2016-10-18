from werkzeug.wrappers import Request, Response
from jsonrpc import JSONRPCResponseManager, dispatcher


class BackendServer:
    def __init__(self):
        pass

    @staticmethod
    @dispatcher.add_method
    def query(q_string, results, page):
        raise NotImplementedError

    @staticmethod
    @dispatcher.add_method
    def query_test():
        raise NotImplementedError

    @Request.application
    def application(self, request):
        response = JSONRPCResponseManager.handle(request.data, dispatcher)
        return Response(response.json, mimetype='application/json')
