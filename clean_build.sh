rm -rf dist
pip uninstall -q --exists-action=w whispr
hatch build
pip install -q dist/whispr-$1-py3-none-any.whl
