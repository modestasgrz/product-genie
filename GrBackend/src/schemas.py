from pydantic import BaseModel, model_validator

from utils.exceptions import JSONDecodeRetranslateError

ASSETS_MAP: dict[str, dict[str, str]] = {
    "Movement": {
        "A product spins 360 by itself, camera static": "PRODUCT_360",
        "Camera orbits 360 around the product": "CAMERA_360",
        "Camera dutch-angle-zoom in on the product, product static": "CAMERA_DUTCH_ZOOM_IN",  # noqa: E501
        "Camera zoom in on the product, product static": "ZOOM_IN",
        "Camera zoom out from the product, product static": "ZOOM_OUT",
        "Camera top view rotation, product static": "CAMERA_TOP_SPIN",
        "Dolly pan left, product static": "CAMERA_PAN_LEFT",
        "Dolly pan right, product static": "CAMERA_PAN_RIGHT",
        "Close up spin on logo, product static": "CAMERA_CLOSE_SPIN",
        "Pan from the top to the packshot, product static": "CAMERA_TOP_PACKSHOT",
        "Camera static, product rotates diagonally": "PRODUCT_DIAGONAL_ROTATE",
        "Camera static, far away, product static": "CAMERA_STILL_FAR",
        "Camera static, close up, product static": "CAMERA_STILL_CLOSE",
    },
    "VFX": {
        "None": "None",
        "Sparkles overlay effect": "VFX_SPARKLE",
        "Snowing overlay effect": "VFX_SNOW",
        "Vegetables fly behind product": "VFX_VEGETABLE_FLOAT",
        "Vegetables explode behind product": "VFX_VEGETABLE_EXPLODE",
        "Berries fly behind product": "VFX_BERRY_FLOAT",
        "Berries explode behind product": "VFX_BERRY_EXPLODE",
        "Lemon fly behind product": "VFX_LEMON_FLOAT",
        "Lemon explode behind product": "VFX_LEMON_EXPLODE",
        "Fire burst overlay": "VFX_FIRE",
        "Screen frost overlay": "VFX_FREEZE",
        "Lighting": "VFX_LIGHTNING",
        "Flowers overlay effect": "VFX_FLOWERS",
    },
}


class ShotCompositionParams(BaseModel):
    movement: str | None = None
    vfx_shot: str | None = None
    environment_color: str | None = None
    movement_speed: float | None = None
    movement_interpolation: str | None = None
    vfx_shot_speed: float | None = None
    vfx_shot_interpolation: str | None = None

    @model_validator(mode="before")
    @classmethod
    def preprocess_fields(cls, values: object) -> object:
        if not isinstance(values, dict):
            raise TypeError("Values must be a dictionary")

        movement = values.pop("Movement", None)
        if not movement:
            raise JSONDecodeRetranslateError("Missing 'Movement' field")
        values["movement"] = (
            movement  # ASSETS_MAP.get("Movement").get(movement)  # type: ignore[union-attr]  # noqa: E501
        )
        movement_speed = float(values.pop("Movement_Speed", 1.2))
        values["movement_speed"] = movement_speed
        movement_interpolation = values.pop("Movement_Interpolation", "None")
        values["movement_interpolation"] = movement_interpolation

        vfx_shot = values.pop("VFX", "None")
        values["vfx_shot"] = (
            vfx_shot  # ASSETS_MAP.get("VFX").get(vfx_shot, "None")  # type: ignore[union-attr]  # noqa: E501
        )
        vfx_shot_speed = float(values.pop("VFX_Speed", 1.0))
        values["vfx_shot_speed"] = vfx_shot_speed
        vfx_shot_interpolation = values.pop("VFX_Interpolation", "None")
        values["vfx_shot_interpolation"] = vfx_shot_interpolation

        return values
