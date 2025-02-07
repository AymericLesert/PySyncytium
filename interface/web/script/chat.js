var ws = new WebSocket("ws://127.0.0.1:8081/ws");

ws.onmessage = function(event) {
    var messages = document.getElementById('messages')
    var message = document.createElement('li')
    var content = document.createTextNode(event.data)
    message.appendChild(content)
    messages.appendChild(message)
};

function sendMessage(event) {
    var input = document.getElementById("messageText")
    request = {
        "action": "message",
        "parameters": {
            "message": input.value
        }
    };
    ws.send(JSON.stringify(request))
    input.value = ''
    event.preventDefault()
}

function getSchema() {
    request = {
        "action": "schema",
        "parameters": { }
    };
    ws.send(JSON.stringify(request))
}

function getTable(table) {
    request = {
        "action": "table",
        "parameters": {
            "table": table
        }
    };
    ws.send(JSON.stringify(request))
}
