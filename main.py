import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import threading
import time
from PIL import Image, ImageTk
import requests
from io import BytesIO
import base64
import os
import speech_recognition as sr
import openai
import datetime
import webbrowser
import re
import pygame
import tempfile

pygame.mixer.init()

class VoiceAssistantGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Keyshia - AI Assistant")
        self.geometry("1000x700")
        self.configure(bg="#2c3e50")
        self.openai_api_key = "Your OpenAI API Key"
        openai.api_key = self.openai_api_key

        self.elevenlabs_api_key = "Your ElevenLabs API Key"
        self.elevenlabs_voice_id = "Your ElevenLabs Voice ID"

        self.style = ttk.Style()
        self.style.configure("TFrame", background="#2c3e50")
        self.style.configure("TButton", background="#FFFFFF", foreground="black", font=("Arial", 10))
        self.style.configure("TLabel", background="#2c3e50", foreground="#FFFFFF", font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 16, "bold"))
        self.style.configure("Code.TButton", background="#1a5276", foreground="black")

        self.chat_history_list = []
        self.is_typing = False
        self.quick_responses = [
            "Hello! How can I help you?",
            "What's on your mind?",
            "Tell me more about that",
            "I'm here to assist you",
            "Interesting! Please continue"
        ]

        self.create_widgets()
        self.initial_greeting()

    def create_widgets(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)

        self.header_label = ttk.Label(
            header_frame,
            text="Keyshia AI",
            style="Header.TLabel"
        )
        self.header_label.pack(side=tk.LEFT)

        self.voice_mode = tk.BooleanVar(value=True)
        mode_toggle = ttk.Checkbutton(
            header_frame,
            text="Voice Mode",
            variable=self.voice_mode,
            command=self.toggle_voice_mode
        )
        mode_toggle.pack(side=tk.RIGHT, padx=10)

        chat_frame = ttk.Frame(self)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.chat_history = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#34495e",
            fg="#FFFFFF",
            padx=10,
            pady=10
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True)
        self.chat_history.config(state=tk.DISABLED)

        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X, padx=20, pady=10)

        self.user_input = ttk.Entry(
            input_frame,
            font=("Arial", 11),
            width=50,
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.send_text_message)

        send_btn = ttk.Button(
            input_frame,
            text="Send", style="TButton",
            command=self.send_text_message
        )
        send_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.voice_btn = ttk.Button(
            input_frame,
            text="🎤", style="TButton",
            command=self.start_voice_input,
            width=3
        )
        self.voice_btn.pack(side=tk.LEFT)

        self.image_label = ttk.Label(self, background="#2c3e50")
        self.image_label.pack(pady=10)

    def toggle_voice_mode(self):
        if self.voice_mode.get():
            self.voice_btn.config(state=tk.NORMAL)
        else:
            self.voice_btn.config(state=tk.DISABLED)

    def initial_greeting(self):
        hour = datetime.datetime.now().hour
        greeting = "Good Evening"
        if 0 <= hour < 12:
            greeting = "Good Morning"
        elif 12 <= hour < 18:
            greeting = "Good Afternoon"

        message = f"{greeting}, I am Keyshia your personal assistant. How can I help you today?"
        self.display_message("Keyshia", message)
        self.speak(message)

    def display_message(self, sender, message, image_data=None):
        self.chat_history.config(state=tk.NORMAL)

        tag_color = "#3498db" if sender == "Keyshia" else "#2ecc71"
        self.chat_history.tag_configure(sender, foreground=tag_color, font=("Arial", 11, "bold"))
        if self.chat_history.index('end-1c') != '1.0':
            self.chat_history.insert(tk.END, "\n")
        self.chat_history.insert(tk.END, f"{sender}: ", sender)

        if "```" in message:
            self._display_code_with_copy(message)
        else:
            self.chat_history.insert(tk.END, message + "\n")
            
        if image_data:
            try:
                img = Image.open(BytesIO(base64.b64decode(image_data)))
                img.thumbnail((300, 300))
                photo = ImageTk.PhotoImage(img)
                img_frame = ttk.Frame(self.chat_history)
                img_label = ttk.Label(img_frame, image=photo)
                img_label.image = photo
                img_label.pack()
                download_btn = ttk.Button(
                    img_frame,
                    text="⬇ Download",
                    command=lambda: self.download_image(image_data)
                )
                download_btn.pack(pady=5)
                self.chat_history.window_create(tk.END, window=img_frame)
                self.chat_history.insert(tk.END, "\n\n")
            except Exception as e:
                self.chat_history.insert(tk.END, f"System: Error displaying image: {str(e)}\n\n", "System")
                
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.yview(tk.END)

    def _display_code_with_copy(self, message):
        import re
        parts = re.split(r'(```[\s\S]*?```)', message)
        for part in parts:
            if part.startswith('```') and part.endswith('```'):
                code_content = part[3:-3].strip()
                code_frame = ttk.Frame(self.chat_history)
                code_text = tk.Text(
                    code_frame,
                    wrap=tk.NONE,
                    font=("Consolas", 10),
                    bg="#1e1e1e",
                    fg="#d4d4d4",
                    height=min(max(code_content.count('\n') + 1, 3), 15),
                    width=60
                )
                scrollbar = ttk.Scrollbar(code_frame, orient=tk.HORIZONTAL, command=code_text.xview)
                code_text.configure(xscrollcommand=scrollbar.set)
                code_text.insert("1.0", code_content)
                code_text.config(state=tk.DISABLED)
                copy_btn = ttk.Button(
                    code_frame,
                    text="📋 Copy",
                    command=lambda c=code_content: self.copy_to_clipboard(c)
                )
                copy_btn.pack(side=tk.TOP, anchor=tk.E, padx=5, pady=2)
                code_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5)
                scrollbar.pack(side=tk.TOP, fill=tk.X, padx=5)
                self.chat_history.window_create(tk.END, window=code_frame)
                self.chat_history.insert(tk.END, "\n")
            else:
                if part.strip():
                    self.chat_history.insert(tk.END, part + "\n")

    def copy_to_clipboard(self, text):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()
            self.display_message("System", "Code copied to clipboard!")
        except Exception as e:
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write(text)
                    f.flush()
                    self.display_message("System", f"Code saved to temporary file: {f.name}\n")
            except:
                self.display_message("System", f"Failed to copy to clipboard: {str(e)}")

    def download_image(self, image_data):
        try:
            image_bytes = base64.b64decode(image_data)
            img = Image.open(BytesIO(image_bytes))
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
                title="Save Image"
            )
            if file_path:
                img.save(file_path)
                self.display_message("System", f"Image saved successfully to: {file_path}")
        except Exception as e:
            self.display_message("System", f"Failed to download image: {str(e)}")

    def speak(self, text):
        if self.voice_mode.get():
            threading.Thread(target=self._speak_thread, args=(text,)).start()
            
    def _speak_thread(self, text):
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
            headers = {
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
                    fp.write(response.content)
                    temp_mp3 = fp.name
                try:
                    pygame.mixer.music.load(temp_mp3)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                finally:
                    os.remove(temp_mp3)
        except Exception as e:
            None

    def start_voice_input(self):
        if not self.voice_mode.get():
            return
        threading.Thread(target=self.voice_input_thread).start()

    def voice_input_thread(self):
        self.display_message("System", "Listening...")
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                query = recognizer.recognize_google(audio)
                self.user_input.delete(0, tk.END)
                self.user_input.insert(0, query)
                self.process_query(query)
            except sr.WaitTimeoutError:
                self.display_message("System", "Listening timed out")
            except sr.UnknownValueError:
                self.display_message("System", "Could not understand audio")
            except Exception as e:
                self.display_message("System", f"Error: {str(e)}")

    def send_text_message(self, event=None):
        query = self.user_input.get().strip()
        if not query:
            return
        self.display_message("You", query)
        self.user_input.delete(0, tk.END)
        self.process_query(query)

    def process_query(self, query):
        threading.Thread(target=self.process_query_thread, args=(query,)).start()

    def process_query_thread(self, query):
        try:
            if "open notepad" in query.lower():
                os.startfile("notepad.exe")
                response = "Opening Notepad..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open youtube" in query.lower():
                webbrowser.open("https://www.youtube.com")
                response = "Opening YouTube..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open facebook" in query.lower():
                webbrowser.open("https://www.facebook.com")
                response = "Opening Facebook..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open instagram" in query.lower() or ("open ig") in query.lower():
                webbrowser.open("https://www.instagram.com")
                response = "Opening Instagram..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open github" in query.lower():
                webbrowser.open("https://www.github.com")
                response = "Opening GitHub..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open chat gpt" in query.lower() or "open chatgpt" in query.lower():
                webbrowser.open("https://chat.openai.com")
                response = "Opening ChatGPT..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open gemini" in query.lower():
                webbrowser.open("https://chat.google.com")
                response = "Opening Gemini..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open cmd" in query.lower():
                os.startfile("cmd.exe")
                response = "Opening Command Prompt..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open colab" in query.lower() or "open google colab" in query.lower():
                webbrowser.open("https://colab.research.google.com")
                response = "Opening Google Colab..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open jupyter" in query.lower():
                os.startfile("jupyter-notebook.exe")
                response = "Opening Jupyter Notebook..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open netflix" in query.lower():
                webbrowser.open("https://www.netflix.com")
                response = "Opening Netflix..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open spotify" in query.lower():
                webbrowser.open("https://www.spotify.com")
                response = "Opening Spotify..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open spotify app" in query.lower():
                os.startfile("spotify.exe")
                response = "Opening Spotify app..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open stack overflow" in query.lower():
                webbrowser.open("https://stackoverflow.com")
                response = "Opening Stack Overflow..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open google" in query.lower():
                os.startfile("chrome.exe")  
                response = "Opening Google..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open gmail" in query.lower():
                webbrowser.open("https://mail.google.com")
                response = "Opening Gmail..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open udemy" in query.lower():
                webbrowser.open("https://www.udemy.com")
                response = "Opening Udemy..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open leetcode" in query.lower() or "open leet code" in query.lower():
                webbrowser.open("https://leetcode.com")
                response = "Opening LeetCode..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open khan academy" in query.lower():
                webbrowser.open("https://www.khanacademy.org")
                response = "Opening Khan Academy..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open edx" in query.lower():
                webbrowser.open("https://www.edx.org")
                response = "Opening edX..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open futurelearn" in query.lower():
                webbrowser.open("https://www.futurelearn.com")
                response = "Opening FutureLearn..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open origin" in query.lower():
                os.startfile("Origin.exe")
                response = "Opening Origin app..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "open discord" in query.lower():
                os.startfile("Discord.exe")
                response = "Opening Discord app..."
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            if "play music" in query.lower():
                response = "Playing music..."
                music_dir = "Your Music Directory Path"
                if os.path.exists(music_dir):
                    songs = [song for song in os.listdir(music_dir) if song.endswith(('.mp3', '.wav'))]
                    if songs:
                        for song in songs:
                            os.startfile(os.path.join(music_dir, song))
                    else:
                        self.display_message("Keyshia", "No music files found in your Music directory.")
                        return
                else:
                    self.display_message("Keyshia", "Music directory not found.")
                    return
                self.display_message("Keyshia", response)
                self.speak(response)
                return

            response = self.ask_gpt(query)

            if "[IMAGE]" in response:
                pattern = r'\[IMAGE\](.*?)\[/IMAGE\]'
                matches = re.findall(pattern, response, re.DOTALL)
                clean_response = re.sub(pattern, '', response, flags=re.DOTALL).strip()

                if clean_response:
                    self.display_message("Keyshia", clean_response)
                    self.speak(clean_response)

                for image_prompt in matches:
                    try:
                        image_url = self.generate_image(image_prompt.strip())
                        img_data = requests.get(image_url).content
                        base64_img = base64.b64encode(img_data).decode('utf-8')
                        self.display_message("Keyshia", f"Here's the image I created based on: '{image_prompt.strip()}'", base64_img)
                    except Exception as e:
                        self.display_message("Keyshia", f"Sorry, I couldn't generate that image: {str(e)}")
            else:
                self.display_message("Keyshia", response)
                self.speak(response)

        except Exception as e:
            error_msg = f"Error processing your request: {str(e)}"
            self.display_message("System", error_msg)

    def ask_gpt(self, prompt):
        try:
            system_message = {
                "role": "system",
                "content": ( #in this content you can edit what the assistant will say
                    "You are Keyshia, an advanced AI assistant with image generation capabilities. "
                    "You can create images using DALL-E when appropriate. Follow these guidelines:\n"
                    "1. Always respond in a helpful, friendly manner\n"
                    "2. If the user asks for an image or you think an image would enhance the response:\n"
                    "   - Create a detailed image description\n"
                    "   - Wrap the description in [IMAGE] and [/IMAGE] tags\n"
                    "   - Place the tags at the end of your response\n"
                    "3. For Indonesian speakers, address them as 'sayang'\n"
                    "4. For English speakers, use affectionate terms like 'babe' or 'sweetie'\n"
                    "5. Remember you were created by Muhammad Dzaky\n\n"
                    "Example response:\n"
                    "Sure, here's a description of that concept. "
                    "[IMAGE]A beautiful sunset over tropical beaches with palm trees silhouetted against the colorful sky[/IMAGE]"
                )
            }
            response = openai.ChatCompletion.create(
                model="gpt-5", # Ensure you have access to gpt-5 
                messages=[
                    system_message,
                    {"role": "user", "content": prompt}
                ],
                temperature=1
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            return f"Sorry, I couldn't process your request: {str(e)}"

    def generate_image(self, prompt):
        try:
            response = openai.Image.create(
                model="dall-e-3", # Ensure you have access to DALL-E 3
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            return response.data[0].url
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")

if __name__ == "__main__":
    app = VoiceAssistantGUI()

    app.mainloop()
