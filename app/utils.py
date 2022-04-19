from config import ALLOWED_EXTENSIONS


def config_parser(config_path):
    with open(config_path, 'r') as config_file:
        config = dict()
        lines = config_file.readline()
        for line in lines:
            k, v = line.split(" = ")
            config[k] = v.split('\n')[0]
        return config


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
