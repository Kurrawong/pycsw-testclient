import yaml
from pathlib import Path
from box import Box

REPO_ROOT = Path(__file__).parent.parent.resolve()

config = Box.from_yaml(filename=REPO_ROOT / "config.yml", Loader=yaml.FullLoader)

print(config.csw.endpoint)




def test_GetCapabilities():
    print()
    for version in config.csw.versions:
        print(version)