#!/usr/bin/env python3

# FOR THIS VOICE SYNTHESIZER, “flite” WAS USED, SINCE THE "SOUND_PLAY" PACKAGE THAT JUSTINA ORIGINALLY USED
# IS NOW VERY OLD AND DOESN'T SUPPORT ROS2. YOU CAN INSTALL flite with 

import rclpy
from rclpy.node import Node
import subprocess
from talker_interfaces.srv import Talk


class Speaker(Node): 
    def __init__(self):
        super().__init__("speaker_node")

        # CONFIGURAR PARAMETROS
        self.declare_parameter("enable_tts", True)
        self.declare_parameter("tts_voice", "slt")      # Voz SLT (FEMENINA)
        self.declare_parameter("tts_output", "play")
        self.declare_parameter("tts_speed", 1.05)       # VELOCIDAD
        self.declare_parameter("tts_volume", 1.0)       # VOLUMEN BASE
        self.declare_parameter("tts_f0_mean", 160)      # TONO DE LA VOZ
        self.declare_parameter("tts_f0_std", 35)        # Variación suave

        # CARGAR PARAMETROS
        self._enable = self.get_parameter("enable_tts").value
        self._voice  = self.get_parameter("tts_voice").value
        self._output = self.get_parameter("tts_output").value
        self._speed  = float(self.get_parameter("tts_speed").value)
        self._volume = float(self.get_parameter("tts_volume").value)
        self._f0_mean = float(self.get_parameter("tts_f0_mean").value)
        self._f0_std  = float(self.get_parameter("tts_f0_std").value)

        # SERVICIO DE VOZ
        self._srv = self.create_service(Talk, "talk", self.HandleSpeakText)
        self.get_logger().info("Servicio de voz listo: /talk")

        self.get_logger().info(
            f"Voz: {self._voice} | Velocidad: {self._speed} | Volumen: {self._volume} | "
            f"Pitch: {self._f0_mean} | Suavidad: {self._f0_std}"
        )

    # CALLBACK DEL SERVICIO
    def HandleSpeakText(self, request, response):
        text = request.text.strip()
        if not text:
            self.get_logger().warning("Texto vacío recibido")
            response.success = False
            response.message = "Texto vacío"
            return response
        self.get_logger().info(f"Diciendo: '{text}'")
        if self._enable:
            self._speak(text)
        response.success = True
        response.message = "Texto reproducido"
        return response

    # MOTOR DE VOZ - FLITE
    def _speak(self, text: str):
        try:
            duration = max(0.5, min(2.0, self._speed))
            pitch_mean = int(self._f0_mean)
            pitch_std  = int(self._f0_std)
            flite_cmd = [
                "flite",
                "-voice", self._voice,
                "--setf", f"duration_stretch={duration}",
                "--setf", f"int_f0_target_mean={pitch_mean}",
                "--setf", f"int_f0_target_stddev={pitch_std}",
                "-t", text
            ]

            if self._output == "play":
                subprocess.run(flite_cmd, check=True)
            else:
                flite_cmd.extend(["-o", "tts_output.wav"])
                subprocess.run(flite_cmd, check=True)
                subprocess.run(["aplay", "tts_output.wav"], check=True)

        except Exception as e:
            self.get_logger().error(f"Error en TTS: {e}")


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
