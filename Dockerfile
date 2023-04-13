FROM nvcr.io/nvidia/pytorch:23.02-py3

RUN apt update && apt install -y git
RUN pip3 install Flask opencv-python
WORKDIR /project
RUN git clone https://github.com/WongKinYiu/yolov7
WORKDIR /project/yolov7/templates
ADD process_photo.html files.html index.html .
WORKDIR /project/yolov7
ADD ./app.py ./process.py ./yolov7_balcony.pt /project/yolov7/
RUN mkdir -p /project/yolov7/static/media

ENTRYPOINT ["python3", "app.py"]
#ENTRYPOINT /bin/bash