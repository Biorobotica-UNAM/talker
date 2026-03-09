#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import subprocess
import os
from pathlib import Path
from talker_interfaces.srv import Talk

class Speaker(Node):

    def __init__(self):
        super().__init__("speaker_piper_node")

        home = str(Path.home())
        piper_base_path = os.path.join(home, "model_piper")

        default_model = os.path.join(piper_base_path, "piper", "en_US-lessac-medium.onnx")
        default_piper = os.path.join(piper_base_path, "piper", "piper")

        # Declaración de parámetros
        self.declare_parameter("enable_tts", True)
        self.declare_parameter("model_path", default_model)
        self.declare_parameter("piper_path", default_piper)
        self.declare_parameter("speed", 1.0)
        self.declare_parameter("noise_scale", 0.667)
        self.declare_parameter("volume", 1.0)

        self._enable = self.get_parameter("enable_tts").value
        self._model = self.get_parameter("model_path").value
        self._piper = self.get_parameter("piper_path").value
        self._speed = float(self.get_parameter("speed").value)
        self._noise = float(self.get_parameter("noise_scale").value)
        self._volume = float(self.get_parameter("volume").value)

        self.create_service(Talk, "talk", self.HandleSpeakText) #Hri_talker
        self.get_logger().info("Piper TTS Service Ready: /talk")
        self.get_logger().info(f"Model: {os.path.basename(self._model)} | Speed: {self._speed} | Noise: {self._noise}, Volume: {self._volume}")

    def HandleSpeakText(self, request, response):
        text = request.text.strip()
        if not text:
            self.get_logger().warning("Received empty text for TTS")
            response.success = False
            response.message = "Error: Text is empty"
            return response

        self.get_logger().info(f"TALKING: '{text}'")
        
        if self._enable:
            success = self._speak(text)
            response.success = success
            response.message = f"ROBOT SAID: {text}" if success else "ERROR IN TTS EXECUTION"
        else:
            response.success = False
            response.message = "TTS is disabled in configuration"
            
        return response
 
    # Filtro pasa bajas ganancia de 0.9
    def _speak(self, text: str):
        try:
            length_scale = 1.0 / self._speed
            piper_cmd = [
                self._piper,
                "--model", self._model,
                "--length_scale", str(length_scale),
                "--noise_scale", str(self._noise),
                "--output-raw"
            ]
            
            sox_cmd = [
                "sox", "-t", "raw", "-r", "22050", "-e", "signed-integer", 
                "-b", "16", "-c", "1", "-", "-t", "alsa", "default", 
                "vol", "0.9", "lowpass", "4000"
            ]

            p1 = subprocess.Popen(piper_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p2 = subprocess.Popen(sox_cmd, stdin=p1.stdout)
            
            # Enviamos el texto al proceso Piper
            p1.stdin.write(text.encode('utf-8'))
            p1.stdin.close()
            p2.communicate()
            self.get_logger().info("ROBOT SAID: " + text)
            return True

        except Exception as e:
            self.get_logger().error(f"Error en Piper TTS: {e}")
            return False

def main(args=None):
    rclpy.init(args=args)
    node = Speaker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()