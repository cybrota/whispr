rm -rf dist
pip uninstall -q --exists-action=w whispr
hatch build
VER=$(ls ./dist/*.whl | sed 's/.*-\([0-9.]*\)-.*/\1/')
echo $VAR
pip install -q dist/whispr-${VER}-py3-none-any.whl
