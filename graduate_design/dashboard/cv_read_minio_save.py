import cv2
import time
import datetime
import os  # 导入 os 模块
from minio import Minio
from minio.error import S3Error
from dashboard.variables.variable import Var
def upload_to_minio(client, bucket_name, object_name, file_path):
    try:
        client.fput_object(bucket_name, object_name, file_path)
        print(f"文件 {file_path} 已成功上传到 {bucket_name}/{object_name}")
    except S3Error as e:
        print(f"上传到 MinIO 时发生错误: {e}")

def read_camera_and_upload():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    minio_client = Minio(
        endpoint=Var.MINIO_url,
        access_key="QyjlstaWZz0j1YUl0ydr",
        secret_key="133TqGsrixXoIrvhnIQUsGRnWTaqSTYWShSAaXhZ",
        secure=False
    )

    bucket_name = "usedfor-s-three-test"
    folder_name = "camera_snapshots"

    start_time = time.time()
    save_interval = 30  # 定义保存间隔（秒）

    fixed_filename = 'fixed_snapshot.jpg'  # 定义固定文件名

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头帧")
            break

        cv2.imshow('Camera Test', frame)

        if time.time() - start_time > save_interval:
            start_time = time.time()
            current_time = datetime.datetime.now()

            # 如果存在旧的固定截图，则删除
            if os.path.exists(fixed_filename):
                os.remove(fixed_filename)

            filename = current_time.strftime('%Y_%m_%d_%H_%M_%S') + '.jpg'
            cv2.imwrite(fixed_filename, frame)  # 保存新的固定截图
            object_name = f"{folder_name}/{filename}"
            upload_to_minio(minio_client, bucket_name, object_name, fixed_filename)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

#if __name__ == '__main__':
#    read_camera_and_upload()