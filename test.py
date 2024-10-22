import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import assemblyai as aai

# Definir uma taxa de amostragem (sample rate)
SAMPLE_RATE = 44100  # 44.1kHz (qualidade de CD)
FILENAME = "meu_audio.wav"  # Nome do arquivo gravado

# Configuração da API AssemblyAI
aai.settings.api_key = "a0409b075c654b65a1dafea74e87d54f"

class AudioApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        # Botão para gravar áudio
        self.record_button = Button(text="Iniciar Gravação")
        self.record_button.bind(on_press=self.start_recording)

        # Label para exibir a transcrição
        self.transcription_label = Label(text="Transcrição aparecerá aqui", size_hint_y=None, height=100)

        # Adicionar o botão e o label ao layout
        layout.add_widget(self.record_button)
        layout.add_widget(self.transcription_label)

        return layout

    def start_recording(self, instance):
        # Atualiza o texto do botão
        self.record_button.text = "Gravando... Pressione para Parar"
        self.record_button.unbind(on_press=self.start_recording)
        self.record_button.bind(on_press=self.stop_recording)

        # Inicia a gravação de áudio
        self.audio_data = []  # Para armazenar o áudio gravado
        self.stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=self.audio_callback)
        self.stream.start()

    def stop_recording(self, instance):
        # Para a gravação e salva o arquivo
        self.stream.stop()
        self.stream.close()

        # Converte a lista de áudio para um array NumPy
        audio_array = np.concatenate(self.audio_data, axis=0)

        # Salva o arquivo WAV
        write(FILENAME, SAMPLE_RATE, audio_array)

        # Atualiza o texto do botão
        self.record_button.text = "Gravação Completa. Transcrevendo..."
        self.record_button.unbind(on_press=self.stop_recording)

        # Envia o áudio para a API da AssemblyAI
        self.transcribe_audio(FILENAME)

    def audio_callback(self, indata, frames, time, status):
        # Função de callback chamada durante a gravação
        self.audio_data.append(indata.copy())

    def transcribe_audio(self, filepath):
        # Transcreve o arquivo de áudio usando AssemblyAI
        try:
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(filepath)  # Envia o arquivo local para transcrição

            if transcript.status == aai.TranscriptStatus.error:
                print(f"Erro ao transcrever: {transcript.error}")
                self.transcription_label.text = "Erro ao transcrever o áudio."
            else:
                print(f"Transcrição: {transcript.text}")
                self.transcription_label.text = f"Transcrição: {transcript.text}"
                self.record_button.text = "Transcrição Completa. Iniciar Nova Gravação"
                # Reconfigura o botão para iniciar uma nova gravação
                self.record_button.unbind(on_press=self.stop_recording)
                self.record_button.bind(on_press=self.start_recording)
        except Exception as e:
            print(f"Erro durante a transcrição: {e}")
            self.transcription_label.text = "Erro na Transcrição. Tente Novamente."
            self.record_button.text = "Erro na Transcrição. Tente Novamente."
            # Reconfigura o botão para iniciar uma nova gravação
            self.record_button.unbind(on_press=self.stop_recording)
            self.record_button.bind(on_press=self.start_recording)

# Rodar o aplicativo Kivy
if __name__ == '__main__':
    AudioApp().run()
