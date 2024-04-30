from minio import Minio
from minio.error import S3Error
from dashboard.lib.sugar import *
from dashboard.lib.log_color import log
from dashboard.variables.variable import Var

minio_url = Var.MINIO_url


#  用于获取minio存储桶的体积
@timer
def get_bucket_size(client, bucket_name_2):
    try:
        objects = client.list_objects(bucket_name_2, recursive=True)
        total_size = sum(obj.size for obj in objects if obj.size is not None)
        return total_size
    except S3Error as e:
        log.error("S3 error: ", e)


def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.3f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.3f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.3f} GB"


def read_bucket_size():
    # 创建 MinIO 客户端实例
    client = Minio(
        endpoint=minio_url,  # 替换为您的 MinIO 服务器地址
        access_key="QyjlstaWZz0j1YUl0ydr",  # 替换为您的 access key
        secret_key="133TqGsrixXoIrvhnIQUsGRnWTaqSTYWShSAaXhZ",  # 替换为您的 secret key
        secure=False  # 设置为 True 如果是 HTTPS，否则设置为 False
    )

    # 获取 bucket 的容量
    bucket_name_1 = "usedfor-s-three-test"  # 替换为您要查询的 bucket 名称
    bucket_size_1 = get_bucket_size(client, bucket_name_1)
    bucket_size_1 = format_size(bucket_size_1)
    return bucket_size_1, bucket_name_1


if __name__ == '__main__':
    bucket_size, bucket_name = read_bucket_size()
    if bucket_size is not None:
        log.info(f"存储桶 '{bucket_name}' 已使用: {bucket_size} ")
