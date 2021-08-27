from configparser import ConfigParser

config = ConfigParser()

with open("settings.ini", "w") as f:
    pass

config.read("settings.ini")
config['Main'] = {
    "screen_width": "1920",
    "screen_height": "1080",

    "color_lower_bound": "60 32 28",
    "color_upper_bound": "130 255 255",

    "dilate_iterations": "1",

    "contouring": "True",

    "interp": "0.9",
    "noshake": "4"
}
config['Calibration'] = {
    "source": "0 0 1 0 0 1 1 1",
    "warp": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"
}

with open("settings.ini", "w") as f:
    config.write(f)
