rm -rf dist
pip uninstall -q --exists-action=w whispr
hatch build
pip install -q dist/whispr-0.3.0-py3-none-any.whl
