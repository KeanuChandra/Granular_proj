import tkinter as tk
from tkinter import messagebox
import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import sounddevice as sd
from scipy.io import wavfile
from scipy.signal import find_peaks
import os
import sys

def modal_synth(duration, damping_factor, threshold_ratio):
    #Check that the inputs are correct
    try:
        duration = float(duration.get())
        damping_factor = float(damping_factor.get())
        threshold_ratio = float(threshold_ratio.get())
    except ValueError as e:
        print(f"Error: {e}. Invalid input")
        return None 

    sample_rate, audio_data = wavfile.read(first_file)

    if len(audio_data.shape) == 2:  
        audio_data = np.mean(audio_data, axis=1)  

    #Fourier Transform
    N = len(audio_data)  
    frequencies = np.fft.fftfreq(N, d=1/sample_rate)  
    fft_values = np.fft.fft(audio_data) 
    amplitudes = np.abs(fft_values)  

    #Filter out frequencies not in range
    range_mask = (frequencies >= 0) & (frequencies <= 5000)
    positive_frequencies = frequencies[range_mask]
    positive_amplitudes = amplitudes[range_mask]

    #Find significant frequencies
    threshold = threshold_ratio * np.max(positive_amplitudes)  # Define a threshold
    peaks, _ = find_peaks(positive_amplitudes, height=threshold)  # Find peaks

    #Extract significant frequencies and calculate amplitudes
    significant_freqs = positive_frequencies[peaks]
    significant_amplitudes = positive_amplitudes[peaks]

    frequencies = []  
    damping_factors = []  
    amplitudes = [] 
    sample_rate = 44100  

    #Get db values of amplitude and print frequencies and amplitudes and add them to lists
    reference_amplitude = max(significant_amplitudes)
    for f, a in zip(significant_freqs, significant_amplitudes):
        a_db = 20 * np.log10(a / reference_amplitude)
        frequencies.append(f)
        amplitudes.append(a_db)
        damping_factors.append(damping_factor)
        print(f"Frequency: {f:.2f} Hz, Amplitude: {a_db:.2f}")

    #Function to generate a modal synthesis waveform
    def modal_synthesis(frequencies, damping_factors, amplitudes, duration, sample_rate=44100):
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)  # Time vector
        waveform = np.zeros_like(t)  # Initialize waveform

        for f, d, a in zip(frequencies, damping_factors, amplitudes):
            mode_wave = a * np.exp(-d * t) * np.cos(2 * np.pi * f * t)
            waveform += mode_wave

        return waveform

    #Generate waveform
    waveform = modal_synthesis(frequencies, damping_factors, amplitudes, duration, sample_rate)
    waveform = np.int16(waveform / np.max(np.abs(waveform)) * 32767)

    #Save to a WAV file
    wav.write("modal_synthesis.wav", sample_rate, waveform)

    #Play the sound
    sd.play(waveform, sample_rate)
    sd.wait()

    #Visualize the waveform
    plt.plot(waveform[:1000])  
    plt.title("Modal Synthesis Waveform")
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    plt.show()
    return

#For playing the original sound
def play_sound():
    sample_rate, audio_data = wav.read(first_file)
    sd.play(audio_data, sample_rate)
    sd.wait()
    return
   

#Find the soundfile   
file_directory = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(file_directory, "Sound")
if os.path.exists(folder_path) and os.path.isdir(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]   
    if files:
        first_file = os.path.join(folder_path, files[0])
    else:
        print("No files found in the folder.")
        sys.exit()
else:
    print("folder does not exist in the current working directory.")
    print(folder_path)
    sys.exit()


#Setup root frame
root = tk.Tk()
root.title("The Synthesis Tool")
root.geometry("400x400")
main_frame = tk.Frame(root)
modal_frame = tk.Frame(root)
main_frame.grid(row=0, column=0, sticky="nsew")
modal_frame.grid(row=0, column=0, sticky="nsew")

#Main Frame
header_label = tk.Label(main_frame, text="Choose Feature")
header_label.place(relx=0.5, rely=0.2, anchor="center")

modal_button = tk.Button(main_frame, text="Modal Synthesis", command=lambda: modal_frame.tkraise())
modal_button.place(relx=0.5, rely=0.5, anchor="center")

gran_button = tk.Button(main_frame, text="Granular Synthesis (WIP)", command=lambda: modal_frame.tkraise())
gran_button.place(relx=0.5, rely=0.8, anchor="center")

#Modal Frame
labels = ["Duration:", "Damping Factor:", "Threshold"]
entries = []

header = tk.Label(modal_frame, text="Modal Synthesis Values")
header.grid(row=0, column=0, columnspan=2, pady=(10, 20))

for i, label_text in enumerate(labels):
    # Create labels and text boxes
    label = tk.Label(modal_frame, text=label_text, anchor="w")
    label.grid(row=i+1, column=0, padx=10, pady=5, sticky="w")  

    entry = tk.Entry(modal_frame, width=30)
    entry.grid(row=i+1, column=1, padx=10, pady=5)
    entries.append(entry)

#Create buttons
submit_button = tk.Button(modal_frame, text="Hear Modal", command=lambda:modal_synth(entries[0],entries[1],entries[2]))
submit_button.grid(row=len(labels)+1, column=0, columnspan=2, pady=10)

hear_original = tk.Button(modal_frame, text="Hear Original", command=play_sound)
hear_original.grid(row=len(labels)+1, column=2, columnspan=2, pady=10)

# Start the Tkinter main loop
main_frame.tkraise()
root.mainloop()