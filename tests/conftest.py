from os.path import abspath, dirname, join

SUPPORTED_CONFIG_VERSIONS = ["v02", "v01", "v1"]


class TestType:
    pass


def _get_json_path(file_name):
    return join(
        abspath(join(dirname(__file__), "serialised_compiler_config_templates", file_name))
    )


def _get_contents(file_path):
    """Get Json from a file."""
    with open(_get_json_path(file_path)) as ifile:
        return ifile.read()
