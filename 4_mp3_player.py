# -*- coding: utf-8 -*-
import pygame

def play_mp3(file_path):
    # Initialize pygame mixer
    pygame.mixer.init()
    
    # Load the MP3 file
    pygame.mixer.music.load(file_path)
    
    # Play the MP3 file
    pygame.mixer.music.play()
    
    # Keep the script running until the music stops
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

if __name__ == "__main__":

#    file_path = "sap_news.mp3"
    file_path = "sap_news_jack.wav"
    play_mp3(file_path)
