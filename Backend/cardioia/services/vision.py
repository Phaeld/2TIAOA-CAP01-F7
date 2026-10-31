"""Phase-four ResNet50 inference and Grad-CAM, loaded only when requested."""
import base64
import io
import os
from threading import Lock

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from ..config import ASSETS, DISCLAIMER


class VisionService:
    def __init__(self, enabled):
        self.enabled = enabled
        self.model = None
        self.lock = Lock()

    def predict(self, content):
        if not self.enabled:
            raise RuntimeError("Visão desativada. Instale requirements-vision.txt e ative CARDIOIA_VISION_ENABLED.")
        if len(content) > 5 * 1024 * 1024:
            raise ValueError("Imagem excede 5 MB.")
        try:
            with Image.open(io.BytesIO(content)) as image:
                if image.format not in ("JPEG", "PNG") or image.width * image.height > 16_000_000:
                    raise ValueError("Use PNG/JPEG de até 16 megapixels.")
                array = np.asarray(ImageOps.exif_transpose(image).convert("RGB").resize((224, 224)), dtype=np.float32)
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
            raise ValueError("Arquivo de imagem inválido.") from error
        with self.lock:
            os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
            os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
            try:
                import tensorflow as tf
                from tensorflow.keras.applications.resnet50 import preprocess_input
                import cv2
            except ImportError as error:
                raise RuntimeError("Dependências de visão não instaladas.") from error
            if self.model is None:
                self.model = tf.keras.models.load_model(ASSETS / "resnet50_finetuned.keras", compile=False)
            pre = preprocess_input(np.expand_dims(array.copy(), axis=0))
            probability = float(self.model(pre, training=False).numpy().ravel()[0])
            grad_model = tf.keras.models.Model(self.model.inputs, [self.model.get_layer("conv5_block3_out").output, self.model.output])
            with tf.GradientTape() as tape:
                conv, pred = grad_model(pre)
                score = pred[:, 0]
            grads = tape.gradient(score, conv)
            weights = tf.reduce_mean(grads, axis=(0, 1, 2))
            heat = tf.maximum(tf.reduce_sum(conv[0] * weights, axis=-1), 0)
            heat = (heat / (tf.reduce_max(heat) + 1e-8)).numpy()
            heat = np.uint8(255 * cv2.resize(heat, (224, 224)))
            color = cv2.cvtColor(cv2.applyColorMap(heat, cv2.COLORMAP_JET), cv2.COLOR_BGR2RGB)
            overlay = cv2.addWeighted(array.astype("uint8"), 0.6, color, 0.4, 0)
            buffer = io.BytesIO()
            Image.fromarray(overlay).save(buffer, format="PNG")
        return {
            "classe": "cardiomegalia" if probability >= 0.5 else "normal",
            "prob_cardiomegalia": round(probability, 4),
            "confianca": round(probability if probability >= 0.5 else 1-probability, 4),
            "gradcam_png_b64": "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode(),
            "source": "phase4_resnet50", "disclaimer": DISCLAIMER,
        }
