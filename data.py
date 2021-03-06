import os
import torch


class Corpus(object):
    def __init__(self, path, batch_size, max_sql):
        self.vocabulary = []  #词列表word2idx
        self.word_id = {}  #字典idx2word
        self.train = self.tokenize(os.path.join(path, 'train.txt'))
        self.valid = self.tokenize(os.path.join(path, 'valid.txt'))
        self.test = self.tokenize(os.path.join(path, 'test.txt'))
        self.dset_flag = "train"
        self.train_si = 0
        self.valid_si = 0
        
        self.max_sql = max_sql
        self.batch_size = batch_size
        self.train_batch_num = self.train.size(0) // self.batch_size
        self.valid_batch_num = self.valid.size(0) // self.batch_size
        self.test_batch_num = self.test.size(0) // self.batch_size
        self.train = self.train.narrow(0, 0, self.batch_size * self.train_batch_num)
        self.valid = self.valid.narrow(0, 0, self.batch_size * self.valid_batch_num)
        self.test = self.test.narrow(0, 0, self.batch_size * self.test_batch_num)
        self.train = self.train.view(self.batch_size, -1).t().contiguous()
        self.valid = self.valid.view(self.batch_size, -1).t().contiguous()
        self.test = self.test.view(self.batch_size, -1).t().contiguous()

    def set_train(self):
        self.dset_flag = "train"

    def set_valid(self):
        self.dset_flag = "valid"

    def tokenize(self, file_name):  #将语料转化为索引表示
        file_lines = open(file_name, 'r').readlines()
        num_of_words = 0  #词的个数，可以重复，即tokens
        for line in file_lines:
            words = line.split() + ['<eos>']
            num_of_words += len(words)
            for word in words:
                if word not in self.word_id:
                    self.word_id[word] = len(self.vocabulary)
                    self.vocabulary.append(word)
        file_tokens = torch.LongTensor(num_of_words)
        token_id = 0
        for line in file_lines:
            words = line.split() + ['<eos>']
            for word in words:
                file_tokens[token_id] = self.word_id[word]
                token_id += 1
        return file_tokens

    def get_batch(self, i):
        self.train_si = i
        self.valid_si = i
        if self.dset_flag == "train":
            start_index = self.train_si
            seq_len = min(self.max_sql, self.train.size(0)-self.train_si-1)
            data_loader = self.train
        else:
            start_index = self.valid_si
            seq_len = min(self.max_sql, self.valid.size(0)-self.valid_si-1)
            data_loader = self.valid
        data = data_loader[start_index:start_index+seq_len]
        target = data_loader[start_index+1:start_index+seq_len+1].view(-1)
        return data, target
