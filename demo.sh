thisdir=$(dirname "$0")

export PYTHONPATH="C:\Users\lcoll\AppData\Local\pypoetry\Cache\virtualenvs\rez-recipes-9BpdTpIw-py3.10\Lib\site-packages;$thisdir"
export KENV_PROFILE_PATHS="$thisdir/tests/data"

cd "$thisdir" || exit

python -m kenvmanager run rezenv knots:echoes --debug

read -n 1 -p "press any key to close"
