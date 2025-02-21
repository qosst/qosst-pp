echo "Cloning IR_for_CVQKD"

mkdir deps
cd deps
git clone https://github.com/erdemeray/IR_for_CVQKD
cd IR_for_CVQKD
git checkout QOSST

cd IR_lib

echo "Commenting conda lines"
sed -i '29 s/./#&/' CMakeLists.txt
sed -i '30 s/./#&/' CMakeLists.txt
sed -i '31 s/./#&/' CMakeLists.txt
sed -i '32 s/./#&/' CMakeLists.txt
sed -i '33 s/./#&/' CMakeLists.txt
sed -i '34 s/./#&/' CMakeLists.txt


echo "Changing python requirement"
sed -i '44 s/.*/find_package(Python REQUIRED COMPONENTS Interpreter Development)/' CMakeLists.txt


echo "Generating makefile"
mkdir build
cd build
cmake ..

echo "Building package"
make

echo "Copying shared library into python lib"
cp *.so $(python -c 'import site; print(site.getsitepackages()[0])')

if python -c 'import information_reconciliation'; then
    echo "Installation complete"
else
    echo "Installation error"
fi

cd ../../../
rm -rf deps