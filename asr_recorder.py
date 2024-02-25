import signal
from asr_client import Dhruva_ASR_SpeechStreamingClient_SocketIO

def display_results(transcript_history, current_transcript):
    print()
    if transcript_history:
        print("Transcript:", transcript_history)
    print("Current:", current_transcript)

if __name__ == "__main__":
    streamer = Dhruva_ASR_SpeechStreamingClient_SocketIO(

        socket_url="wss://dhruva-api.bhashini.gov.in",

        api_key="INSERT_API_KEY_HERE",
        task_sequence=[
            {
                "taskType": "asr",
                "config": {
                    "preProcessors":["vad"],
                    "postProcessors":["itn","punctuation"],
                    "serviceId": "ai4bharat/conformer-hi-gpu--t4",
                    "language": {
                        "sourceLanguage": "hi"
                    },
                    "samplingRate": 8000,
                    "audioFormat": "wav",
                    "encoding": None,
                    # "channel": "mono",
                    # "bitsPerSample": "sixteen"
                }
            },
            {
                "taskType": "translation",
                "config": {
                    "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4",
                    "language": {
                        "sourceLanguage": "hi",
                        "targetLanguage": "en"
                    }
                }
            }
        ],
        response_callback=display_results,
        auto_start=True,
    )
    signal.signal(signal.SIGINT, streamer.force_disconnect)

    try:
        input("(Press Enter to Stop) ")
        streamer.stop()
    except:
        pass
