import sounddevice
import socketio
import pyaudio
import turtle
import tkinter as tk
from turtle_helper import move_turtle
class Dhruva_ASR_SpeechStreamingClient_SocketIO:
    def __init__(
        self,
        socket_url: str,
        api_key: str,
        task_sequence: list,
        response_callback,
        auto_start: bool = False,
        device_name: str ="rockchip-es8316: dailink-multicodecs es8316.7-0011-0 (hw:2,0)"
    ) -> None:

        # Default ASR settings
        self.input_audio__streaming_rate = 3200
        self.input_audio__sampling_rate = task_sequence[0]["config"]["samplingRate"]

        self.input_audio__bytes_per_sample = 2 # Do not change
        self.input_audio__num_channels = 1 # Do not change

        self.response_frequency_in_secs = 2.0
        self.transcript_history = ""

        # Parameters
        # assert len(task_sequence) == 1, "Only ASR task allowed in sequence"
        self.task_sequence = task_sequence
        self.response_callback = response_callback
        self.device_name = device_name

        # states
        self.audio_stream = None
        self.is_speaking = False
        self.is_stream_inactive = True

        self.socket_client = self._get_client(
            on_ready=self.start_transcribing_from_mic if auto_start else None
        )
        self.x =''
        
        
        self.socket_client.connect(
            url=socket_url,
            transports=["websocket", "polling"],
            socketio_path="/socket.io",
            auth={
                "authorization": api_key
            }
        )

    def _get_client(self, on_ready=None) -> socketio.Client:
        sio = socketio.Client(reconnection_attempts=5)

        @sio.event
        def connect():
            print("Socket connected with ID:", sio.get_sid())
            streaming_config = {
                "responseFrequencyInSecs": self.response_frequency_in_secs,
                "responseTaskSequenceDepth":2
            }
            sio.emit("start", data=(self.task_sequence, streaming_config))
        
        @sio.event
        def connect_error(data):
            print("The connection failed!")
        
        @sio.on('ready')
        def ready():
            self.is_stream_inactive = False
            print("Server ready to receive data from client")
            if on_ready:
                on_ready()
        
        @sio.on('response')
        def response(response, streaming_status):
            print(response)
            print()
            if streaming_status["isIntermediateResult"]:
                current_transcript = response["pipelineResponse"][1]["output"][0]["target"]
                x = current_transcript
                print('#'*10+x+'#'*10)
                self.response_callback(self.transcript_history, current_transcript)
                print("transcript printing")
            else:
                current_transcript = '. '.join(chunk["target"] for chunk in response["pipelineResponse"][1]["output"] if chunk["target"].strip())
                self.response_callback(self.transcript_history, current_transcript)
                print("transcript printing 1")
                if current_transcript.strip():
                    self.transcript_history += current_transcript + '. '
                    print("transcript printing 2")
            
            self.x = x       
        @sio.on('abort')
        def abort(message):
            print("Connection aborted with message:")
            print(message)

        @sio.on('terminate')
        def terminate():
            sio.disconnect()
            if self.audio_stream:
                # Probably server-side terminated first
                self.audio_stream.stop_stream()
                self.audio_stream = None

        @sio.event
        def disconnect():
            if not self.is_stream_inactive:
                print("Force-disconnected by server, press Enter to stop client.")
            else:
                print("Stream disconnected!")

        return sio

    def stop(self) -> None:
        print("Stopping...")
        if self.audio_stream:
            self.audio_stream.stop_stream()
        else:
            # Likely that already somehow force-stopped
            return

        self.is_speaking = False
        self._transmit_end_of_stream()

        # Wait till stream is disconnected
        self.socket_client.wait()

    def force_disconnect(self, sig=None, frame=None) -> None:
        self.socket_client.disconnect()
    
    def _create_audio_stream(self, device_name: str) -> pyaudio.Stream:
        p = pyaudio.PyAudio()
        input_device_index = None
        print("Available audio devices:")
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            print(f"{i}: {device_info['name']}")
            if device_info["name"] == device_name:
                input_device_index = i
                break

        if input_device_index is None:
           raise ValueError(f"Input device '{device_name}' not found.")

        stream = p.open(
            format=p.get_format_from_width(self.input_audio__bytes_per_sample),
            channels=self.input_audio__num_channels,
            rate=self.input_audio__sampling_rate,
            input=True,
            input_device_index=input_device_index,
            output=False,
            frames_per_buffer=self.input_audio__streaming_rate,
            stream_callback=self.recorder_callback,
        )
        return stream
    
    def start_transcribing_from_mic(self) -> None:
        self.is_speaking = True
        print("Device Name:", self.device_name)
        self.audio_stream = self._create_audio_stream(self.device_name)
        print("START SPEAKING NOW!!!")
    
    def recorder_callback(self, in_data, frame_count, time_info, status_flags) -> tuple:
        if self.is_speaking:
            # print("is speaking now")
            # print(in_data)
            input_data = {
                "audio": [{
                    "audioContent": in_data
                }]
            }
            clear_server_state = not self.is_speaking
            streaming_config = {}
            self.socket_client.emit("data", data=(input_data, streaming_config, clear_server_state, self.is_stream_inactive))
        return (None, pyaudio.paContinue)
    
    def _transmit_end_of_stream(self) -> None:
        # Convey that speaking has stopped
        clear_server_state = not self.is_speaking
        self.socket_client.emit("data", (None, None, clear_server_state, self.is_stream_inactive))
        # Convey that we can close the stream safely
        self.is_stream_inactive = True
        self.socket_client.emit("data", (None, None, clear_server_state, self.is_stream_inactive))
