#! usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Copyright 2018 The Google AI Language Team Authors.
BASED ON Google_BERT.
reference from :zhoukaiyin/

@Author:Macan
"""


# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function
import time
import sys,os
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'../..')))
import collections
import os
import numpy as np
import tensorflow as tf
import codecs
import pickle

from bert_base.train import tf_metrics
from bert_base.bert import modeling
from bert_base.bert import optimization
from bert_base.bert import tokenization

# import

from bert_base.train.models import create_model, InputFeatures, InputExample

__version__ = '0.1.0'

__all__ = ['__version__', 'DataProcessor', 'NerProcessor', 'write_tokens', 'convert_single_example',
           'filed_based_convert_examples_to_features', 'file_based_input_fn_builder',
           'model_fn_builder', 'train']



class DataProcessor(object):
    """Base class for data converters for sequence classification data sets."""

    def get_train_examples(self, data_dir):
        """Gets a collection of `InputExample`s for the train set."""
        raise NotImplementedError()

    def get_dev_examples(self, data_dir):
        """Gets a collection of `InputExample`s for the dev set."""
        raise NotImplementedError()

    def get_labels(self):
        """Gets the list of labels for this data set."""
        raise NotImplementedError()

    @classmethod
    def _read_data(cls, input_file):
        """
        ####################BIO################标注格式的data
        Reads a BIO data.##或者是　BIOES数据集都没有影响

        """
        with codecs.open(input_file, 'r', encoding='utf-8') as f:
            lines = []
            words = []
            labels = []
            for line in f:
                contends = line.strip()
                tokens = contends.split(' ')
                if len(tokens) == 2:
                    words.append(tokens[0])
                    labels.append(tokens[1])
                else:
                    if len(contends) == 0:
                        l = ' '.join([label for label in labels if len(label) > 0])
                        w = ' '.join([word for word in words if len(word) > 0])
                        lines.append([l, w])
                        words = []
                        labels = []
                        continue
                if contends.startswith("-DOCSTART-"):
                    words.append('')
                    continue
            return lines
'''
[
    ['O O O O O O O O O O O O O O O B-LOC B-LOC O B-LOC B-LOC O O O O O O O O O O O O O O O O O O O O', '我 们 变 而 以 书 会 友 ， 以 书 结 缘 ， 把 欧 美 、 港 台 流 行 的 食 品 类 图 谱 、 画 册 、 工 具 书 汇 集 一 堂 。']
    ['O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O', '为 了 跟 踪 国 际 最 新 食 品 工 艺 、 流 行 趋 势 ， 大 量 搜 集 海 外 专 业 书 刊 资 料 是 提 高 技 艺 的 捷 径 。']
]
'''


class NerProcessor(DataProcessor):
    def __init__(self, output_dir):
        self.labels = set()
        self.output_dir = output_dir

    def get_train_examples(self, data_dir):
        #得到的数据都是类初始化的数据，需要通过属性值进行调用
        return self._create_example(
            self._read_data(os.path.join(data_dir, "train.txt")), "train"
        )

    def get_dev_examples(self, data_dir):
        return self._create_example(
            self._read_data(os.path.join(data_dir, "dev.txt")), "dev"
        )

    #用于预测
    def get_test_examples(self, data_dir):
        return self._create_example(
            self._read_data_predict(os.path.join(data_dir, "test.txt")), "test")


    # #待会在看怎么调用的
    # def get_labels(self, labels=None):
    #     if labels is not None:
    #         try:
    #             # 支持从文件中读取标签类型
    #             if os.path.exists(labels) and os.path.isfile(labels):
    #                 with codecs.open(labels, 'r', encoding='utf-8') as fd:
    #                     for line in fd:
    #                         self.labels.append(line.strip())
    #             else:
    #                 # 否则通过传入的参数，按照逗号分割
    #                 self.labels = labels.split(',')
    #             self.labels = set(self.labels) # to set
    #         except Exception as e:
    #             print(e)
    #     # 通过读取train文件获取标签的方法会出现一定的风险。
    #     if os.path.exists(os.path.join(self.output_dir, 'label_list.pkl')):
    #         with codecs.open(os.path.join(self.output_dir, 'label_list.pkl'), 'rb') as rf:
    #             self.labels = pickle.load(rf)
    #     else:
    #         if len(self.labels) > 0:
    #             self.labels = self.labels.union(set(["X", "[CLS]", "[SEP]"]))
    #             with codecs.open(os.path.join(self.output_dir, 'label_list.pkl'), 'wb') as rf:
    #                 pickle.dump(self.labels, rf)
    #         else:
    #             self.labels = ["O", 'B-TIM', 'I-TIM', "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC", "X", "[CLS]", "[SEP]"]
    #     return self.labels


    #BIOES标签+“X、CLS、SEP”
    def get_labels(self):
        return ["O",
                "B-PER", "I-PER","E-PER","S-PER",
                "B-ORG", "I-ORG", "E-ORG","S-ORG",
                "B-LOC", "I-LOC","E-LOC","S-LOC",
                "B-MISC", "I-MISC", "E-MISC", "S-MISC",
                "X", "[CLS]", "[SEP]"]


    def _create_example(self, lines, set_type):
        examples = []
        for (i, line) in enumerate(lines):
            guid = "%s-%s" % (set_type, i)
            text = tokenization.convert_to_unicode(line[1])
            label = tokenization.convert_to_unicode(line[0])
            # if i == 0:
            #     print('label: ', label)
            # print('text：',text)
            # print('label:',label)
            '''
            text： 我 们 变 而 以 书 会 友 ， 以 书 结 缘 ， 把 欧 美 、 港 台 流 行 的 食 品 类 图 谱 、 画 册 、 工 具 书 汇 集 一 堂 。
            label: O O O O O O O O O O O O O O O B-LOC B-LOC O B-LOC B-LOC O O O O O O O O O O O O O O O O O O O O
            text： 为 了 跟 踪 国 际 最 新 食 品 工 艺 、 流 行 趋 势 ， 大 量 搜 集 海 外 专 业 书 刊 资 料 是 提 高 技 艺 的 捷 径 。
            label: O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O
            text： 其 中 线 装 古 籍 逾 千 册 ； 民 国 出 版 物 几 百 种 ； 珍 本 四 册 、 稀 见 本 四 百 余 册 ， 出 版 时 间 跨 越 三 百 余 年 。
            label: O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O
            InputExample(guid=guid, text=text, label=label)是一个类的初始化，可通过
            a.guid,a.text,a.label,分别调用属性值
            '''
            examples.append(InputExample(guid=guid, text=text, label=label))
        return examples

    def _read_data(self, input_file):
        """Reads a BIO data."""
        with codecs.open(input_file, 'r', encoding='utf-8') as f:
            lines = []
            words = []
            labels = []
            for line in f:
                contends = line.strip()
                tokens = contends.split(' ')

                #正常情况
                '''
                韩 O
                国 O
                梦 O
                '''
                if len(tokens) == 2:
                    words.append(tokens[0])
                    labels.append(tokens[-1])
                else:
                    if len(contends) == 0 and len(words) > 0:
                        label = []
                        word = []
                        for l, w in zip(labels, words):
                            if len(l) > 0 and len(w) > 0:
                                label.append(l)
                                self.labels.add(l)
                                word.append(w)
                        lines.append([' '.join(label), ' '.join(word)])
                        words = []
                        labels = []
                        continue
                if contends.startswith("-DOCSTART-"):
                    continue
                if contends.startswith("-DOCEND-"):
                    continue
            return lines
    def _read_data_predict(self, input_file):
        """Reads a BIO data."""
        with codecs.open(input_file, 'r', encoding='utf-8') as f:
            lines = []
            words = []
            labels = []
            for line in f:
                contends = line.strip()
                tokens = contends.split(' ')

                #正常情况
                '''
                韩 O
                国 O
                梦 O
                '''
                if len(tokens) == 1:
                    words.append(tokens[0])
                    labels.append('O')
                elif len(tokens) == 2:
                    words.append(tokens[0])
                    labels.append(tokens[-1])
                else:
                    if len(contends) == 0 and len(words) > 0:
                        label = []
                        word = []
                        for l, w in zip(labels, words):
                            if len(l) > 0 and len(w) > 0:
                                label.append(l)
                                self.labels.add(l)
                                word.append(w)
                        lines.append([' '.join(label), ' '.join(word)])
                        words = []
                        labels = []
                        continue




                # if contends.startswith("-DOCSTART-"):
                #     continue
                # if contends.startswith("-DOCEND-"):
                #     continue
            return lines


def write_tokens(tokens, output_dir, mode):
    """
    将序列解析结果写入到文件中
    只在mode=test的时候启用
    :param tokens:
    :param mode:
    :return:
    """
    if mode == "test.txt":
        path = os.path.join(output_dir, "token_" + mode)# + ".txt")
        wf = codecs.open(path, 'a', encoding='utf-8')
        for token in tokens:
            if token != "**NULL**":
                wf.write(token + '\n')
        wf.close()

#####label_list可能是所有的label组成的一个集合（去除重复部分）
def convert_single_example(ex_index, example, label_list, max_seq_length, tokenizer, output_dir, mode):
    """
    将一个样本进行分析，然后将字转化为id, 标签转化为id,然后结构化到InputFeatures对象中
    :param ex_index: index
    :param example: 一个样本
    :param label_list: 标签列表
    :param max_seq_length:
    :param tokenizer:
    :param output_dir
    :param mode:
    :return:
    """
    label_map = {}
    # 1表示从1开始对label进行index化
    for (i, label) in enumerate(label_list, 1):
        label_map[label] = i
    # 保存label->index 的map
    if not os.path.exists(os.path.join(output_dir, 'label2id.pkl')):
        with codecs.open(os.path.join(output_dir, 'label2id.pkl'), 'wb') as w:
            pickle.dump(label_map, w)

    ######调用example初始化类的属性值
    textlist = example.text.split(' ')
    labellist = example.label.split(' ')
    tokens = []
    labels = []
    for i, word in enumerate(textlist):
        # 分词，如果是中文，就是分字,但是对于一些不在BERT的vocab.txt中得字符会被进行WordPice处理
        # （例如中文的引号），可以将所有的分字操作替换为list(input)
        token = tokenizer.tokenize(word)
        tokens.extend(token)
        label_1 = labellist[i]
        for m in range(len(token)):
            if m == 0:
                labels.append(label_1)
            else:  # 一般不会出现else
                labels.append("X")
    # tokens = tokenizer.tokenize(example.text)
    # 序列截断
    if len(tokens) >= max_seq_length - 1:
        tokens = tokens[0:(max_seq_length - 2)]  # -2 的原因是因为序列需要加一个句首和句尾标志
        labels = labels[0:(max_seq_length - 2)]
    ntokens = []
    segment_ids = []
    label_ids = []
    ntokens.append("[CLS]")  # 句子开始设置CLS 标志
    segment_ids.append(0)
    # append("O") or append("[CLS]") not sure!
    label_ids.append(label_map["[CLS]"])  # O OR CLS 没有任何影响，不过我觉得O 会减少标签个数,不过拒收和句尾使用不同的标志来标注，使用LCS 也没毛病
    for i, token in enumerate(tokens):
        ntokens.append(token)
        segment_ids.append(0)
        label_ids.append(label_map[labels[i]])
    ntokens.append("[SEP]")  # 句尾添加[SEP] 标志
    segment_ids.append(0)
    # append("O") or append("[SEP]") not sure!
    label_ids.append(label_map["[SEP]"])
    input_ids = tokenizer.convert_tokens_to_ids(ntokens)  # 将序列中的字(ntokens)转化为ID形式
    input_mask = [1] * len(input_ids)
    # label_mask = [1] * len(input_ids)
    # padding, 使用
    while len(input_ids) < max_seq_length:
        input_ids.append(0)
        input_mask.append(0)
        segment_ids.append(0)
        # we don't concerned about it!
        label_ids.append(0)
        ntokens.append("**NULL**")
        # label_mask.append(0)
    # print(len(input_ids))
    assert len(input_ids) == max_seq_length
    assert len(input_mask) == max_seq_length
    assert len(segment_ids) == max_seq_length
    assert len(label_ids) == max_seq_length
    # assert len(label_mask) == max_seq_length

    # 打印部分样本数据信息
    if ex_index < 5:
        tf.logging.info("*** Example ***")
        tf.logging.info("guid: %s" % (example.guid))
        tf.logging.info("tokens: %s" % " ".join(
            [tokenization.printable_text(x) for x in tokens]))
        tf.logging.info("input_ids: %s" % " ".join([str(x) for x in input_ids]))
        tf.logging.info("input_mask: %s" % " ".join([str(x) for x in input_mask]))
        tf.logging.info("segment_ids: %s" % " ".join([str(x) for x in segment_ids]))
        tf.logging.info("label_ids: %s" % " ".join([str(x) for x in label_ids]))
        # tf.logging.info("label_mask: %s" % " ".join([str(x) for x in label_mask]))

    # 结构化为一个类
    feature = InputFeatures(
        input_ids=input_ids,
        input_mask=input_mask,
        segment_ids=segment_ids,
        label_ids=label_ids,
        # label_mask = label_mask
    )
    # mode='test.txt'的时候才有效
    write_tokens(ntokens, output_dir, mode)
    return feature


def filed_based_convert_examples_to_features(
        examples, label_list, max_seq_length, tokenizer, output_file, output_dir, mode=None):
    """
    将数据转化为TF_Record 结构，作为模型数据输入
    :param examples:  样本
    :param label_list:标签list
    :param max_seq_length: 预先设定的最大序列长度
    :param tokenizer: tokenizer 对象
    :param output_file: tf.record 输出路径
    :param mode:
    :return:
    """
    writer = tf.python_io.TFRecordWriter(output_file)
    # 遍历训练数据
    #examples是所有的训练数据_create_example函数产生
    for (ex_index, example) in enumerate(examples):
        if ex_index % 5000 == 0:
            tf.logging.info("Writing example %d of %d" % (ex_index, len(examples)))
        # 对于每一个训练样本,
        feature = convert_single_example(ex_index, example, label_list, max_seq_length, tokenizer, output_dir, mode)

        def create_int_feature(values):
            f = tf.train.Feature(int64_list=tf.train.Int64List(value=list(values)))
            return f

        features = collections.OrderedDict()
        features["input_ids"] = create_int_feature(feature.input_ids)
        features["input_mask"] = create_int_feature(feature.input_mask)
        features["segment_ids"] = create_int_feature(feature.segment_ids)
        features["label_ids"] = create_int_feature(feature.label_ids)
        # features["label_mask"] = create_int_feature(feature.label_mask)
        # tf.train.Example/Feature 是一种协议，方便序列化？？？
        tf_example = tf.train.Example(features=tf.train.Features(feature=features))
        writer.write(tf_example.SerializeToString())


def file_based_input_fn_builder(input_file, seq_length, is_training, drop_remainder):
    name_to_features = {
        "input_ids": tf.FixedLenFeature([seq_length], tf.int64),
        "input_mask": tf.FixedLenFeature([seq_length], tf.int64),
        "segment_ids": tf.FixedLenFeature([seq_length], tf.int64),
        "label_ids": tf.FixedLenFeature([seq_length], tf.int64),
        # "label_ids":tf.VarLenFeature(tf.int64),
        # "label_mask": tf.FixedLenFeature([seq_length], tf.int64),
    }

    def _decode_record(record, name_to_features):
        example = tf.parse_single_example(record, name_to_features)
        for name in list(example.keys()):
            t = example[name]
            if t.dtype == tf.int64:
                t = tf.to_int32(t)
            example[name] = t
        return example

    def input_fn(params):

        ####这个地方读取tf_recard数据，进行_decode_record，并批量化batch_size大小的返回拿去训练
        batch_size = params["batch_size"]
        d = tf.data.TFRecordDataset(input_file)
        if is_training:
            d = d.repeat()
            d = d.shuffle(buffer_size=300)
        #没有该属性先注释掉
        #华为服务器1cpu 4core 8 logi_CPUS ；16g mem
        d = d.apply(tf.data.experimental.map_and_batch(lambda record: _decode_record(record, name_to_features),
                                                       batch_size=batch_size,
                                                       ##这里应该是物理cpu数目，不是核心数或者超线程数；只有一个物理cpu时，如何设置都会占满
                                                       num_parallel_calls=1,  # 并行处理数据的CPU核心数量，不要大于你机器的核心数
                                                       drop_remainder=drop_remainder))
        d = d.prefetch(buffer_size=4)
        return d

    return input_fn


def model_fn_builder(bert_config, num_labels, init_checkpoint, learning_rate,
                     num_train_steps, num_warmup_steps, args):
    """
    构建模型
    :param bert_config:
    :param num_labels:
    :param init_checkpoint:
    :param learning_rate:
    :param num_train_steps:
    :param num_warmup_steps:
    :param use_tpu:
    :param use_one_hot_embeddings:
    :return:
    """

    def model_fn(features, labels, mode, params):
        tf.logging.info("*** Features ***")

        #没有属性先注释掉
        for name in sorted(features.keys()):
            tf.logging.info("  name = %s, shape = %s" % (name, features[name].shape))

        input_ids = features["input_ids"]
        input_mask = features["input_mask"]
        segment_ids = features["segment_ids"]
        label_ids = features["label_ids"]

        print('shape of input_ids', input_ids.shape)
        # label_mask = features["label_mask"]
        is_training = (mode == tf.estimator.ModeKeys.TRAIN)

        # 使用参数构建模型,input_idx 就是输入的样本idx表示，label_ids 就是标签的idx表示
        total_loss, logits, trans, pred_ids = create_model(
            bert_config, is_training, input_ids, input_mask, segment_ids, label_ids,
            num_labels, False, args.dropout_rate, args.lstm_size, args.cell, args.num_layers)

        tvars = tf.trainable_variables()
        # 加载BERT模型
        if init_checkpoint:
            (assignment_map, initialized_variable_names) = \
                 modeling.get_assignment_map_from_checkpoint(tvars,
                                                             init_checkpoint)
            tf.train.init_from_checkpoint(init_checkpoint, assignment_map)

        # 打印变量名
        # logger.info("**** Trainable Variables ****")
        #
        # # 打印加载模型的参数
        # for var in tvars:
        #     init_string = ""
        #     if var.name in initialized_variable_names:
        #         init_string = ", *INIT_FROM_CKPT*"
        #     logger.info("  name = %s, shape = %s%s", var.name, var.shape,
        #                     init_string)

        output_spec = None
        if mode == tf.estimator.ModeKeys.TRAIN:
            #train_op = optimizer.optimizer(total_loss, learning_rate, num_train_steps)
            train_op = optimization.create_optimizer(
                 total_loss, learning_rate, num_train_steps, num_warmup_steps, False)
            hook_dict = {}
            hook_dict['loss'] = total_loss
            hook_dict['global_steps'] = tf.train.get_or_create_global_step()
            logging_hook = tf.train.LoggingTensorHook(
                hook_dict, every_n_iter=args.save_summary_steps)

            output_spec = tf.estimator.EstimatorSpec(
                mode=mode,
                loss=total_loss,
                train_op=train_op,
                training_hooks=[logging_hook])

        elif mode == tf.estimator.ModeKeys.EVAL:
            # 针对NER ,进行了修改
            def metric_fn(label_ids, pred_ids):
                return {
                    "eval_loss": tf.metrics.mean_squared_error(labels=label_ids, predictions=pred_ids),
                }

            eval_metrics = metric_fn(label_ids, pred_ids)
            output_spec = tf.estimator.EstimatorSpec(
                mode=mode,
                loss=total_loss,
                eval_metric_ops=eval_metrics
            )
        else:
            output_spec = tf.estimator.EstimatorSpec(
                mode=mode,
                predictions=pred_ids
            )
        return output_spec

    return model_fn


# def load_data():
#     processer = NerProcessor()
#     processer.get_labels()
#     example = processer.get_train_examples(FLAGS.data_dir)
#     print()

def get_last_checkpoint(model_path):
    if not os.path.exists(os.path.join(model_path, 'checkpoint')):
        tf.logging.info('checkpoint file not exits:'.format(os.path.join(model_path, 'checkpoint')))
        return None
    last = None
    with codecs.open(os.path.join(model_path, 'checkpoint'), 'r', encoding='utf-8') as fd:
        for line in fd:
            line = line.strip().split(':')
            if len(line) != 2:
                continue
            if line[0] == 'model_checkpoint_path':
                last = line[1][2:-1]
                break
    return last


def adam_filter(model_path):
    """
    去掉模型中的Adam相关参数，这些参数在测试的时候是没有用的
    :param model_path: 
    :return: 
    """
    last_name = get_last_checkpoint(model_path)
    if last_name is None:
        return
    sess = tf.Session()
    imported_meta = tf.train.import_meta_graph(os.path.join(model_path, last_name + '.meta'))
    imported_meta.restore(sess, os.path.join(model_path, last_name))
    need_vars = []
    for var in tf.global_variables():
        if 'adam_v' not in var.name and 'adam_m' not in var.name:
            need_vars.append(var)
    saver = tf.train.Saver(need_vars)
    saver.save(sess, os.path.join(model_path, 'model.ckpt'))


def train(args):
    os.environ['CUDA_VISIBLE_DEVICES'] = args.device_map
    tf.logging.set_verbosity(tf.logging.INFO)
    processors = {
        "ner": NerProcessor
    }
    bert_config = modeling.BertConfig.from_json_file(args.bert_config_file)

    if args.max_seq_length > bert_config.max_position_embeddings:
        raise ValueError(
            "Cannot use sequence length %d because the BERT model "
            "was only trained up to sequence length %d" %
            (args.max_seq_length, bert_config.max_position_embeddings))

    # 在re train 的时候，才删除上一轮产出的文件，在predicted 的时候不做clean
    #args.clean和do_train默认是true;
    #也就是训练一次之后，第二次再训练时会删除上次的文件
    if args.clean and args.do_train:
        if os.path.exists(args.output_dir):
            def del_file(path):
                ls = os.listdir(path)
                for i in ls:
                    c_path = os.path.join(path, i)
                    if os.path.isdir(c_path):
                        del_file(c_path)
                    else:
                        os.remove(c_path)

            try:
                del_file(args.output_dir)
            except Exception as e:
                print(e)
                print('pleace remove the files of output dir and data.conf')
                exit(-1)

    #check output dir exists
    #默认rootpaht+'output'
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    processor = processors[args.ner](args.output_dir)


    ####tokenizer的使用
    tokenizer = tokenization.FullTokenizer(
        vocab_file=args.vocab_file, do_lower_case=args.do_lower_case)

    session_config = tf.ConfigProto(
        #应该是物理cpu个数
        device_count={"CPU": 2},  # limit to num_cpu_core CPU usage

        #cpu 核心数*超线程数*物理cpu个数=逻辑cpu数
        log_device_placement=False,#True打印日志,false不打印日志
        inter_op_parallelism_threads=6,
        intra_op_parallelism_threads=6,
        allow_soft_placement=True)

    run_config = tf.estimator.RunConfig(
        model_dir=args.output_dir,
        save_summary_steps=500,##每隔500步保存tensorbaord的summary
        save_checkpoints_steps=500,##每隔500步保存checkpoints模型
        session_config=session_config
    )

    train_examples = None
    eval_examples = None
    num_train_steps = None
    num_warmup_steps = None

    # default args.do_train and args.do_eval are true
    if args.do_train and args.do_eval:
        # 加载训练数据
        train_examples = processor.get_train_examples(args.data_dir)
        num_train_steps = int(
            len(train_examples) *1.0 / args.batch_size * args.num_train_epochs)
        if num_train_steps < 1:
            raise AttributeError('training data is so small...')
        num_warmup_steps = int(num_train_steps * args.warmup_proportion)

        tf.logging.info("***** Running training *****")
        tf.logging.info("  Num examples = %d", len(train_examples))
        tf.logging.info("  Batch size = %d", args.batch_size)
        tf.logging.info("  Num steps = %d", num_train_steps)

        eval_examples = processor.get_dev_examples(args.data_dir)

        # 打印验证集数据信息
        tf.logging.info("***** Running evaluation *****")
        tf.logging.info("  Num examples = %d", len(eval_examples))
        tf.logging.info("  Batch size = %d", args.batch_size)

    tf.logging.info("get labels")
    label_list = processor.get_labels()
    # 返回的model_dn 是一个函数，其定义了模型，训练，评测方法，并且使用钩子参数，加载了BERT模型的参数进行了自己模型的参数初始化过程
    # tf 新的架构方法，通过定义model_fn 函数，定义模型，然后通过EstimatorAPI进行模型的其他工作，Es就可以控制模型的训练，预测，评估工作等。
    tf.logging.info('def model_fn_builer')
    model_fn = model_fn_builder(
        bert_config=bert_config,
        num_labels=len(label_list) + 1,
        init_checkpoint=args.init_checkpoint,
        learning_rate=args.learning_rate,
        num_train_steps=num_train_steps,
        num_warmup_steps=num_warmup_steps,
        args=args)

    params = {
        'batch_size': args.batch_size
    }

    tf.logging.info('def estimator')
    estimator = tf.estimator.Estimator(
        model_fn,
        params=params,
        config=run_config)

    #train和eval都为真时才会进行训练和评估
    if args.do_train and args.do_eval:
        # 1. 将数据转化为tf_record 数据
        tf.logging.info('convert data into train tf_record ')
        train_file = os.path.join(args.output_dir, "train.tf_record")
        if not os.path.exists(train_file):
            filed_based_convert_examples_to_features(
                train_examples, label_list, args.max_seq_length, tokenizer, train_file, args.output_dir)

        # 2.读取record 数据，组成batch
        tf.logging.info('read train record and convert to batch')
        train_input_fn = file_based_input_fn_builder(
            input_file=train_file,
            seq_length=args.max_seq_length,
            is_training=True,
            drop_remainder=True)


        tf.logging.info('convert data to eval tf_record 数据')
        eval_file = os.path.join(args.output_dir, "eval.tf_record")
        if not os.path.exists(eval_file):
            filed_based_convert_examples_to_features(
                eval_examples, label_list, args.max_seq_length, tokenizer, eval_file, args.output_dir)

        tf.logging.info('read eval record ，convert to batch')
        eval_input_fn = file_based_input_fn_builder(
            input_file=eval_file,
            seq_length=args.max_seq_length,
            is_training=False,
            drop_remainder=False)





        # train and eval togither
        tf.logging.info('call early stopping hook')
        early_stopping_hook = tf.contrib.estimator.stop_if_no_decrease_hook(
            estimator=estimator,
            metric_name='loss',
            max_steps_without_decrease=num_train_steps,
            eval_dir=None,
            min_steps=0,
            run_every_secs=None,
            run_every_steps=args.save_checkpoints_steps)###

        '''estimator.train(input_fn=lambda :my_input_fn(TRAIN_DATA),steps=300)
            #训练完后进行验证，这里传入我们的测试数据
            test_result = estimator.evaluate(input_fn=lambda :my_input_fn(TEST_DATA))
            #输出测试验证结果'''
        t0=time.time()
        estimator.train(input_fn=train_input_fn, max_steps=num_train_steps,hooks=[early_stopping_hook])  ##默认被注释掉

        t1=time.time()
        tf.logging.info('train spent time:{}s'.format(t1 - t0))
        # 自己添加的
        eval_loss = estimator.evaluate(input_fn=eval_input_fn)
        t2 = time.time()
        tf.logging.info('eval_loss=\n{}'.format(eval_loss))
        tf.logging.info('eval spent time:{}s'.format(t2 - t1))






        # tf.logging.info('call train_spec')
        # train_spec = tf.estimator.TrainSpec(input_fn=train_input_fn, max_steps=num_train_steps,
        #                                      hooks=[early_stopping_hook]
        #                                     )
        # tf.logging.info('call eval_spec')
        # eval_spec = tf.estimator.EvalSpec(input_fn=eval_input_fn)
        # tf.logging.info('call tf.estimator.train_and_evaluate')
        #单机上和分布式都可以使用
        # tf.estimator.train_and_evaluate(estimator, train_spec, eval_spec)

    #default do_predict is True
    if args.do_predict:
        token_path = os.path.join(args.output_dir, "token_test.txt")
        if os.path.exists(token_path):
            os.remove(token_path)

        with codecs.open(os.path.join(args.output_dir, 'label2id.pkl'), 'rb') as rf:
            label2id = pickle.load(rf)
            id2label = {value: key for key, value in label2id.items()}

        predict_examples = processor.get_test_examples(args.data_dir)

        predict_file = os.path.join(args.output_dir, "predict.tf_record")
        filed_based_convert_examples_to_features(predict_examples, label_list,
                                                 args.max_seq_length, tokenizer,
                                                 predict_file, args.output_dir, mode="test.txt")

        tf.logging.info("***** Running prediction*****")
        tf.logging.info("  Num examples = %d", len(predict_examples))
        tf.logging.info("  Batch size = %d", args.batch_size)

        predict_drop_remainder = False

        tf.logging.info('call pred predict_input_fn')
        predict_input_fn = file_based_input_fn_builder(
            input_file=predict_file,
            seq_length=args.max_seq_length,
            is_training=False,
            drop_remainder=predict_drop_remainder)

        #############prdict的时候也是以batch大小的形式
        tf.logging.info('start predict，estimator.predict')
        result = estimator.predict(input_fn=predict_input_fn)



        #####预测结果似乎是写在这里的；里面有三列第一列是内容，第二列是真实标签，第三列是预测标签
        output_predict_file = os.path.join(args.output_dir, "label_test.txt")


        def result_to_pair(writer):
            for predict_line, prediction in zip(predict_examples, result):
                idx = 0
                line = ''
                line_token = str(predict_line.text).split(' ')
                label_token = str(predict_line.label).split(' ')
                len_seq = len(label_token)
                if len(line_token) != len(label_token):
                    tf.logging.info('predict_line.text:\n{}'.format(predict_line.text))
                    tf.logging.info('predict_line.label:\n{}'.format(predict_line.label))
                    break
                for id in prediction:
                    if idx >= len_seq:
                        break
                    if id == 0:
                        continue
                    curr_labels = id2label[id]
                    if curr_labels in ['[CLS]', '[SEP]']:
                        continue
                    try:
                        line += line_token[idx] + ' ' + label_token[idx] + ' ' + curr_labels + '\n'
                    except Exception as e:
                        tf.logging.info('e:\n{}'.format(e))


                        tf.logging.info('predict_line.text:\n{}'.format(predict_line.text))
                        tf.logging.info('predict_line.label:\n{}'.format(predict_line.label))
                        line = ''
                        break
                    idx += 1
                writer.write(line + '\n')

        ###打开文件将结果写入
        tf.logging.info('save predicted result :label_test.txt')
        with codecs.open(output_predict_file, 'w', encoding='utf-8') as writer:
            result_to_pair(writer)

        tf.logging.info('import conlleval to eval and get eval_result ')
        from bert_base.train import conlleval
        eval_result = conlleval.return_report(output_predict_file)
        tf.logging.info('eval_result:\n{}'.format(''.join(eval_result)))
        # 写结果到文件中
        tf.logging.info('save predict_score.txt')
        with codecs.open(os.path.join(args.output_dir, 'predict_score.txt'), 'a', encoding='utf-8') as fd:
            fd.write(''.join(eval_result))
    # filter model
    if args.filter_adam_var:
        adam_filter(args.output_dir)


if __name__=='__main__':
    ################################
    # lines=DataProcessor()._read_data('../../NERdata/test.txt')
    # for each in lines:
    #     print(each)
    #################################
    lines=[
        ['O O O O O O O O O O O O O O O B-LOC B-LOC O B-LOC B-LOC O O O O O O O O O O O O O O O O O O O O',
         '我 们 变 而 以 书 会 友 ， 以 书 结 缘 ， 把 欧 美 、 港 台 流 行 的 食 品 类 图 谱 、 画 册 、 工 具 书 汇 集 一 堂 。'],
        [
            'O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O', '为 了 跟 踪 国 际 最 新 食 品 工 艺 、 流 行 趋 势 ， 大 量 搜 集 海 外 专 业 书 刊 资 料 是 提 高 技 艺 的 捷 径 。'],
        [
            'O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O O', '其 中 线 装 古 籍 逾 千 册 ； 民 国 出 版 物 几 百 种 ； 珍 本 四 册 、 稀 见 本 四 百 余 册 ， 出 版 时 间 跨 越 三 百 余 年 。'],

    ]
    examples=NerProcessor(DataProcessor)._create_example(lines, set_type='test')
    print('example:',examples)
    for each in examples:
        print('each',each.guid)