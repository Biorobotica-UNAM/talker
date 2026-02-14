#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import subprocess
from talker_interfaces.srv import Talk

class Speaker(Node):
    def __init__(self):
        super().__init__("speaker_node")
        #Configurar parametros
        self.declare_parameter("enable_tts", True)
        self.declare_parameter("tts_voice", "en_US/ljspeech_low")
        self.declare_parameter("tts_output", "play")
        self.declare_parameter("tts_speed", 0.88)
        self.declare_parameter("tts_noise_w", 0.9)
        self.declare_parameter("tts_noise_scale", 0.7)
        #Cargar parametros
        self._enable = bool(self.get_parameter("enable_tts").value)
        self._voice = self.get_parameter("tts_voice").value
        self._output = self.get_parameter("tts_output").value
        self._speed = float(self.get_parameter("tts_speed").value)
        self._noise_w = float(self.get_parameter("tts_noise_w").value)
        self._noise_scale = float(self.get_parameter("tts_noise_scale").value)
        #Servicio de voz
        self._srv = self.create_service(Talk, "talk", self.HandleSpeakText)
        self.get_logger().info("Servicio de voz listo: /talk")
        self.get_logger().info(
            f"Voz: {self._voice} | Speed(length_scale): {self._speed} | "
            f"noise_w: {self._noise_w} | noise_scale: {self._noise_scale}"
        )

    #Callback del servicio
    def HandleSpeakText(self, request, response):
        text = request.text.strip()
        if not text:
            self.get_logger().warning("Texto vacío recibido")
            response.success = False
            response.message = "Texto vacío"
            return response
        self.get_logger().info(f"Diciendo: '{text}'")
        if self._enable:
            ok = self._speak(text)
            if not ok:
                response.success = False
                response.message = "Error en TTS"
                return response
        response.success = True
        response.message = "Texto reproducido"
        return response

    #Motor de voz
    def _speak(self, text: str) -> bool:
        try:
            length_scale = max(0.5, min(2.0, float(self._speed)))
            noise_w = max(0.0, min(1.0, float(self._noise_w)))
            noise_scale = max(0.0, min(1.0, float(self._noise_scale)))
            mimic3_cmd = [
                "mimic3",
                "--voice", self._voice,
                "--length-scale", str(length_scale),
                "--noise-w", str(noise_w),
                "--noise-scale", str(noise_scale),
                "--stdout",
                text
            ]
            if self._output == "play":
                p = subprocess.Popen(mimic3_cmd, stdout=subprocess.PIPE)
                subprocess.run(["aplay", "-q"], stdin=p.stdout, check=True)
                p.wait()
            else:
                out_wav = "tts_output.wav"
                with open(out_wav, "wb") as f:
                    p = subprocess.Popen(mimic3_cmd, stdout=f)
                    p.wait()
                subprocess.run(["aplay", "-q", out_wav], check=True)
            return True
        except Exception as e:
            self.get_logger().error(f"Error TTS (Mimic3): {e}")
            return False

def main(args=None):
        rclpy.init(args=args)
        node = Speaker()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            node.get_logger().info("Nodo de voz detenido manualmente.")
        finally:
            node.destroy_node()
            rclpy.shutdown()

if __name__ == "__main__":
    main()