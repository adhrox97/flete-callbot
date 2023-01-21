#XDG_RUNTIME_DIR=/run/user/1000
import gtts
import pygame
from playsound import playsound

def t2s():
    tts = gtts.gTTS("Buenos dias, hay un nuevo servicio de flete a disposicion, si esta interasado puede contactarnos en nuestro chat de whatsapp", lang="es")
    tts.save("p1.mp3")
    #playsound("p1.mp3")
    pygame.mixer.pre_init(22050, -16, 2, 2048) # setup mixer to avoid sound lag
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load('p1.mp3')
    pygame.mixer.music.play()
    #pygame.event.wait()
    while pygame.mixer.music.get_busy():
    
        pygame.time.Clock().tick(10)
    
#t2s()
