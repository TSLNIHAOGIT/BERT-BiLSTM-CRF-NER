# import thulac
import jieba
import json

#加载自定义词典
jieba.load_userdict("../NERdata/self_dict.txt")
sentence= "韩国梦想演唱会第十届2004年:MC:金泰熙，金东万"
# sentence='林散之先生等当代名家对辛文山先生的书法均有精辟的点评，对书法爱好者自学书法有较高的参考价值。'

# thu1=thulac.thulac(seg_only=True)
# cut_words=thu1.cut(sentence,text=True)
# print(cut_words)

jieba_cut=jieba.cut(sentence)
print(' '.join(jieba_cut))


with open('../output/label_test_relation.json',encoding='utf8') as f:
    data=json.load(f)
    all_data=[]
    for each in data:
        each_split_sentenc=' '.join(jieba.cut(each['sentence']))
        each['sentence']=each_split_sentenc
        all_data.append(each)
    with open('../output/label_test_relation_split.json','w',encoding='utf8') as f:
        json.dump(all_data,f,ensure_ascii=False,indent=4)
