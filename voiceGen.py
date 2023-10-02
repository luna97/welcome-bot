from gtts import gTTS
import sys

text = ""
if len(sys.argv) == 0:
    print("Error, you must pass text")
    exit()
elif len(sys.argv) == 1:
    text = sys.argv[0]
else:
    for arg in sys.argv[1:]:
        text += arg + " "
    text = text[:-1]
    
tts = gTTS(text=text, lang='en')
tts.save("output.mp3")
