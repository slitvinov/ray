OS=$(uname -s); [ "$OS" = Darwin ] && OS=MacOSX
ARCH=$(uname -m)
curl -fsSL "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$OS-$ARCH.sh" -o /tmp/mf.sh
bash /tmp/mf.sh -b
rm /tmp/mf.sh
~/miniforge3/bin/conda install -y python=3.14
~/miniforge3/bin/pip install cloudpickle
