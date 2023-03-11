cd ${UP4ROOT}
mkdir build
cd build
cmake ..   # (optional add the debug flag) -DCMAKE_BUILD_TYPE=DEBUG  
make -j2   # This should create p4c-msa executable in the build directory 
cd ..
