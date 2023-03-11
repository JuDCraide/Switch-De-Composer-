sudo apt-get install cmake g++ git automake libtool libgc-dev bison flex libfl-dev libgmp-dev \
   libboost-dev libboost-iostreams-dev libboost-graph-dev llvm pkg-config python python-scapy \
   python-ipaddr python-ply tcpdump

sudo apt-get install autoconf automake libtool curl make g++ unzip
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.2.0/protobuf-cpp-3.2.0.zip
unzip protobuf-cpp-3.2.0.zip
cd protobuf-3.2.0
./configure
make
make check
sudo make install
sudo ldconfig