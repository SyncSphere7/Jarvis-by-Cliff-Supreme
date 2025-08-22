"""
UI for the Jarvis mobile app.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
import socketio

class JarvisApp(App):
    def build(self):
        self.sio = socketio.Client()
        self.sio.connect('http://localhost:5001')

        layout = BoxLayout(orientation='vertical')
        self.text_input = TextInput(font_size=50)
        self.button = Button(text='Send', font_size=50)
        self.button.bind(on_press=self.send_message)
        self.label = Label(font_size=50)
        layout.add_widget(self.text_input)
        layout.add_widget(self.button)
        layout.add_widget(self.label)

        @self.sio.on('chat_response')
        def on_chat_response(data):
            self.label.text = data['response']

        return layout

    def send_message(self, instance):
        self.sio.emit('chat_message', {'message': self.text_input.text})

if __name__ == '__main__':
    JarvisApp().run()
