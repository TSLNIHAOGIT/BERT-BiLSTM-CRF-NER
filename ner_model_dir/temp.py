import  pickle

fr = open('label_list.pkl',mode='rb+')    #open的参数是pkl文件的路径
inf = pickle.load(fr)       #读取pkl文件的内容
print(inf)
fr.close()

fr = open('label2id.pkl',mode='rb+')    #open的参数是pkl文件的路径
inf = pickle.load(fr)       #读取pkl文件的内容
print(inf)
fr.close()