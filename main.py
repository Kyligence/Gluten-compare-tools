from flask import Flask, request

from core.common import config
from core.compare_tools import CompareTools

app = Flask(__name__)
compare_tools = CompareTools()


@app.route(config.FORWARD_PATH, methods=['POST'])
def forward():
    source_message = request.get_json()

    urls = compare_tools.connection_manager.urls

    results = compare_tools.messageProcessor.forward(urls, source_message)
    standards_results = compare_tools.messageProcessor.parse_results(results)

    compare_tools.resultProcessor.compare(standards_results)

    return "compare done"


if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True)  # 单进程单线程

    app.run(host='0.0.0.0', debug=True, threaded=True)  # 单进程多线程，进程默认为1
    #
    # app.run(host='0.0.0.0', debug=True, threaded=True, processes=4)  # 多进程多线程，进程processes默认为1
