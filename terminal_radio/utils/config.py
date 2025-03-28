def load_config(file_path):
    """Load configuration settings from a JSON file."""
    import json

    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_config(file_path, config):
    """Save configuration settings to a JSON file."""
    import json

    with open(file_path, "w") as f:
        json.dump(config, f, indent=4)


def get_default_config():
    """Return the default configuration settings."""
    return {"volume": 50, "stations": []}
