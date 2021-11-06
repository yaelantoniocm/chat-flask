from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=None)
personas_en_linea = 0

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat.html', username=username, room=room, personas_en_linea=personas_en_linea)
    else:
        return redirect(url_for('home'))


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} mando un mensaje a la sala {}: {}".format(
        data['username'],
        data['room'],
        data['message']))
    if data['image'] != '':
        app.logger.info("{} mandó una imágen a la sala {}: {}, {}, {}, {} bytes".format(
            data['username'],
            data['room'],
            data['message'],
            data['filename'],
            data['type'],
            data['size']))
    socketio.emit('receive_message', data, room=data['room'])

#Se manda alerta de que se unio a la sala en la consola
@socketio.on('join_room')
def handle_join_room_event(data):
    global personas_en_linea
    personas_en_linea += 1
    app.logger.info("{} se unio a la sala {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'], personas_en_linea=personas_en_linea)

#Se manda alerta de que se salio la sala en la consola
@socketio.on('leave_room')
def handle_leave_room_event(data):
    global personas_en_linea
    personas_en_linea -= 1
    app.logger.info("{} a dejado la sala {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])


if __name__ == '__main__':
    socketio.run(app, debug=True)