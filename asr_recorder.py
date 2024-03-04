import signal
from asr_client import Dhruva_ASR_SpeechStreamingClient_SocketIO

def display_results(transcript_history, current_transcript):
    print()
    if transcript_history:
        print("Transcript:", transcript_history)
    print("Current:", current_transcript)

if __name__ == "__main__":
    from turtle_helper import move_turtle
    streamer= Dhruva_ASR_SpeechStreamingClient_SocketIO(

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
            },
            {  
               "taskType": "tts",
            	"config": {
                "language": {
                    "sourceLanguage": "en"
                   }
            	}
            }
        ],
        response_callback=display_results,
        auto_start=True,
        device_name="rockchip-es8316: dailink-multicodecs es8316.7-0011-0 (hw:2,0)"
    )
    signal.signal(signal.SIGINT, streamer.force_disconnect)

	while True :
    	if streamer.x : #in ["Let ' s go", "Let ' s"]:
        	move_turtle(streamer.x)
        	streamer.x = ''
			
    try:
        input("(Press Enter to Stop) ")
        streamer.stop()
    except:
        pass
