#----------------------------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License.txt in the project root for license information.
#----------------------------------------------------------------------------------------------

import argparse
import os
from six import text_type as _text_type
from mmdnn.conversion.common.utils import download_file

BASE_MODEL_URL = 'https://www.cntk.ai/Models/CNTK_Pretrained/'
# pylint: disable=line-too-long
MODEL_URL = {
    'alexnet'              : BASE_MODEL_URL + 'AlexNet_ImageNet_CNTK.model',
    'inception_v3'         : BASE_MODEL_URL + 'InceptionV3_ImageNet_CNTK.model',
    'resnet50'             : BASE_MODEL_URL + 'ResNet50_ImageNet_CNTK.model',
    'resnet101'            : BASE_MODEL_URL + 'ResNet101_ImageNet_CNTK.model',
    'resnet152'            : BASE_MODEL_URL + 'ResNet152_ImageNet_CNTK.model',
    'Fast-RCNN_grocery100' : 'https://www.cntk.ai/Models/FRCN_Grocery/Fast-RCNN_grocery100.model',
    'Fast-RCNN_Pascal'     : 'https://www.cntk.ai/Models/FRCN_Pascal/Fast-RCNN.model'
}
# pylint: enable=line-too-long


def _main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--network', type=_text_type, help='Model Type', required=True,
                        choices=MODEL_URL.keys())

    parser.add_argument('-i', '--image', default=None,
                        type=_text_type, help='Test Image Path')

    parser.add_argument('-o', '--output_dir', default='./',
                        type=_text_type, help='Caffe Checkpoint file name')

    args = parser.parse_args()

    fn = download_file(MODEL_URL[args.network], directory=args.output_dir)
    if not fn:
        return -1

    print("Model {} is saved as {}.".format(args.network, fn))

    if args.image:
        import caffe
        import numpy as np
        from mmdnn.conversion.examples.imagenet_test import TestKit

        net = caffe.Net(arch_fn, weight_fn, caffe.TEST)
        func = TestKit.preprocess_func['caffe'][args.network]
        img = func(args.image)
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, 0)
        net.blobs['data'].data[...] = img
        predict = np.squeeze(net.forward()['prob'][0])
        predict = np.squeeze(predict)
        top_indices = predict.argsort()[-5:][::-1]
        result = [(i, predict[i]) for i in top_indices]
        print(result)
        print(np.sum(result))

    return 0


if __name__ == '__main__':
    _main()
