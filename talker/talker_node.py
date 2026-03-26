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
            piper_dir = os.path.dirname(self._piper)

            env = os.environ.copy()
            env["LD_LIBRARY_PATH"] = piper_dir + ":" + env.get("LD_LIBRARY_PATH", "")

            piper_cmd = [
                self._piper,
                "--model", self._model,
                "--length_scale", str(length_scale),
                "--noise_scale", str(self._noise),
                "--output-raw"
            ]

            p1 = subprocess.Popen(
                piper_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )

            audio_data, piper_err = p1.communicate(input=(text + "\n").encode("utf-8"))

            if p1.returncode != 0:
                self.get_logger().error(
                    f"Piper falló con código {p1.returncode}: "
                    f"{piper_err.decode('utf-8', errors='ignore')}"
                )
                return False

            if not audio_data:
                self.get_logger().error(
                    "Piper no generó audio. stderr: " +
                    piper_err.decode("utf-8", errors="ignore")
                )
                return False

            sox_cmd = [
                "sox",
                "-t", "raw",
                "-r", "22050",
                "-e", "signed-integer",
                "-b", "16",
                "-c", "1",
                "-",
                "-t", "alsa",
                "default",
                "vol", str(self._volume),
                "lowpass", "4000"
            ]

            p2 = subprocess.Popen(
                sox_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            _, sox_err = p2.communicate(input=audio_data)

            if p2.returncode != 0:
                self.get_logger().error(
                    f"Sox falló con código {p2.returncode}: "
                    f"{sox_err.decode('utf-8', errors='ignore')}"
                )
                return False

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
