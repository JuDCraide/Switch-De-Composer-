cd ${UP4ROOT}/extensions/csa/msa-examples/bmv2
bash ./install_deps.sh
./autogen.sh
./configure 'CXXFLAGS=-O0 -g' --enable-debugger    # Mandatory for μP4, because I will need logs in error scenarios. :)
make
sudo make install  # if you need to install bmv2
sudo ldconfig # for linux
