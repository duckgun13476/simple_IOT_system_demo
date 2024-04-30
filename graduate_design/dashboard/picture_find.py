from minio import Minio
from minio.error import S3Error
from dashboard.variables.variable import Var


def find_latest_image_in_bucket(minio_client, bucket_name, folder_name):
    try:
        objects = minio_client.list_objects(bucket_name, prefix=folder_name, recursive=True)
        # 根据文件名（假设包含时间戳）排序找到最新的文件
        latest_object = max(objects, key=lambda obj: obj.object_name)
        return latest_object.object_name
    except S3Error as e:
        print(f"在MinIO中查找文件时出错: {e}")
        return None


def find_newest_file():
    minio_client = Minio(
        Var.MINIO_url,  # MinIO服务器地址
        access_key=Var.MINIO_access_key,  # 替换为你的access key
        secret_key=Var.MINIO_secret_key,  # 替换为你的secret key
        secure=False  # 如果使用HTTPS则设置为True
    )
    bucket_name = Var.bucket_name  # 存储桶名
    folder_name = Var.folder_name  # 文件夹名，以斜杠结尾

    # 找到并打印最新的图像文件名
    latest_image_name = find_latest_image_in_bucket(minio_client, bucket_name, folder_name)
    if latest_image_name:
        print(f"最新的图像文件是: {latest_image_name}")
    return latest_image_name


if __name__ == '__main__':
    # 设置MinIO客户端
    late = find_newest_file()
