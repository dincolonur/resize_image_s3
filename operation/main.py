from multiprocessing import Process
import boto3
import botocore.exceptions
import os
import json
from PIL import Image
import base64
import requests
import argparse


class Operation:

    def create(self,
               source_bucket_name='source_bucket_name',
               target_bucket_name='target_bucket_name'):
        """
        @param source_bucket_name: Source Bucket Name
        @param target_bucket_name: Target Bucket Name
        @return: (source_bucket, target_bucket)
        """
        def read_secrets() -> dict:
            filename = os.path.join('./secrets.json')
            try:
                with open(filename, mode='r') as f:
                    return json.loads(f.read())
            except FileNotFoundError:
                return {}
        secrets = read_secrets()
        s3 = boto3.resource('s3',
                    region_name=secrets['region_name'],
                    aws_access_key_id=secrets['aws_access_key_id'],
                    aws_secret_access_key=secrets['aws_secret_access_key'])
        return  s3.Bucket(source_bucket_name), s3.Bucket(target_bucket_name)

    def main_operation(self,
                       partition='',
                       source_bucket_name='onurtest2',
                       target_bucket_name='onurtest3',
                       size=(500,500),
                       api_url='http://127.0.0.1:5000/im_size'):
        """
        @param partition: source/target partition to specify process location
        @param source_bucket_name: Source Bucket Name
        @param target_bucket_name: Target Bucket Name
        @param size:      Image Resize parameter, default (500,500)
        @param api_url:   we service api URL, default: http://127.0.0.1:5000/im_size
        @return:
        """
        source_bucket, target_bucket = self.create(source_bucket_name, target_bucket_name)
        for obj in source_bucket.objects.all():
            if 'jpg' in obj.key and partition in obj.key:
                print(obj.key)
                fn = obj.key.split('/')[-1]
                folder = '/'.join(obj.key.split('/')[:-1])
                try:
                    source_bucket.download_file(obj.key, fn)
                    # Image Ops, resize & thumbnail
                    resized_img, thumb_image = self.image_ops(fn, size)

                    # POST Image to URL
                    print(self.send_image(resized_img, api_url).json())

                    # Upload and clean resized image
                    self.upload_clean(resized_img, target_bucket, os.path.join(folder, resized_img))

                    # Upload and clean thumbnail image
                    self.upload_clean(thumb_image, target_bucket, os.path.join(folder, thumb_image))

                except botocore.exceptions.DataNotFoundError as e:
                    print(e)

    def upload_clean(self, img, target_bucket, target_path):
        """
        @param img:           Image to upload
        @param target_bucket: Target S3 Bucket
        @param target_path:   Target S3 path to upload
        @return:
        """
        target_bucket.upload_file(img, target_path)
        Operation.clean(img)

    def image_ops(self, fn, size):
        """
        @param fn:
        @param size:
        @return:
        """
        img = Image.open(fn)
        resized_image = img.resize(size)
        resized_image.save(fn, 'PNG')

        img.thumbnail((100,100))
        thumb_name = 'thumbnail_' + fn
        img.save(thumb_name, 'PNG')
        return fn, thumb_name

    def send_image(self, fn, api_url):
        """
        @param fn:        Image File Name
        @param api_url:   API URL of the Web Service
        @return:          response of the post request
        """
        with open(fn, 'rb') as f:
            im_base64 = base64.b64encode(f.read())

            payload = {type: 'jpg', 'img_name': fn, 'image': im_base64}
            r = requests.post(api_url, data=payload)
        return r

    @staticmethod
    def clean(item_to_del, folder='.'):
        """
        @param item_to_del: To be deleted item
        @param folder:      Folder of the item to delete, default: '.'
        @return:
        """
        item_path = os.path.join(folder, item_to_del)
        os.remove(item_path)


if __name__ == '__main__':
    """
    Main function: 
    - Runs a process for input folder(partition)
    - Every Process 
        1 - Reads from source bucket in the input partition
        2 - resize the images & create thumbnails
        3 - POST the resized image to API URL
        4 - Upload the resized images to the target bucket
        5 - Upload the thumbnail images to the target bucket
    """
    parser = argparse.ArgumentParser(
        description="Resize Image Application ",
        epilog="Example Usage:  python3 operation/main.py -p folder_1 "
               "-s source_bucket_name -t target_bucket_name -r 500,500 -u http://127.0.0.1:5000/im_size",
    )
    parser.add_argument("-p", help="Partition to be processed", default='folder_1')
    parser.add_argument("-s", help="Source Bucket Name", default='source_bucket_name')
    parser.add_argument("-t", help="Target Bucket Name", default='target_bucket_name')
    parser.add_argument("-r", help="Resize dimensions int,int", default='500,500')
    parser.add_argument("-u", help="API url to POST resized Image", default='http://127.0.0.1:5000/im_size')
    args = parser.parse_args()
    op = Operation()
    new_size = tuple(int(i.strip()) for i in args.r.split(','))
    p1 = Process(target=op.main_operation, args=(args.p, args.s, args.t, new_size, args.u))
    p1.start()
    p1.join()


