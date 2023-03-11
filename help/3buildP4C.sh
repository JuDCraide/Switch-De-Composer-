SDCPATH=$(dirname "$(readlink -f "$0")")
export UP4ROOT="${SDCPATH%/*}/obs-microp4"

cd ${UP4ROOT}/extensions/csa/msa-examples/p4c
mkdir build
cd build
cmake ..   # (optional add the debug flag) -DCMAKE_BUILD_TYPE=DEBUG  
make -j2
