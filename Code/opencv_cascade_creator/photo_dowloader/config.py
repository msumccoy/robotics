""" Kuwin Wyke
Midwestern State University
Start: 26 December 2019
End: work in progress

***Description to be made***
"""


class Conf:
    # neg_images_link = (
    #     'http://image-net.org/api/text/imagenet.synset.geturls?wnid=n00523513'
    # )  # replaced and modified by neg_image_urls
    neg_image_urls = "negatives_urls.txt"  # modified version of url
    neg_folder = 'neg/'
    neg_size = 300
    im_type = ".jpg"

    pos_folder = "pos"
    pos_size = neg_size / 2
