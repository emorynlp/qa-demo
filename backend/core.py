from werkzeug.wrappers import Request, Response
from jsonrpc import JSONRPCResponseManager, dispatcher


class BackendServer:
    def __init__(self):
        pass

    @staticmethod
    @dispatcher.add_method
    def query(string):
        raise NotImplementedError

    @staticmethod
    @dispatcher.add_method
    def query_test():
        raise NotImplementedError

    @Request.application
    def application(self, request):
        response = JSONRPCResponseManager.handle(request.data, dispatcher)
        return Response(response.json, mimetype='application/json')


class ATBackendServer(BackendServer):
    """
    Backend server for Answer Triggering task.
    Source: <provide a url here>
    """

    @staticmethod
    @dispatcher.add_method
    def query(string):
        return string

    @staticmethod
    @dispatcher.add_method
    def query_test():
        return True
