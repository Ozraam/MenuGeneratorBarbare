docker build -t combar:v0.1 .
docker run -v ./build:/app/build combar:v0.1