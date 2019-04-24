import json
import random
from convert_data_to_nyt10 import generate_id
with open('../output/rel2id.json') as f:
    relation_dict=json.load(f)

relations=list(relation_dict.keys())

path='../output/label_test.txt'
path_relation='../output/label_test_relation.json'
all_rel_data=[]
each_sentence_rel_data={}


##随机取会导致实体id重复，因此要将每个实体的分配唯一id
counts = 9000
all_ids=generate_id.generateid_list(counts)

# rel_count=52

counts_entity=0
all_ids_dict={}


with open(path,encoding='utf8') as f:
    each_point_text=[]
    each_point_label=[]
    right_amounts=0


    each_sentence_entitys = []
    each_sentence_entitys_label = []
    eachs_entity = ''

    for index, each in enumerate(f):
            each_list=each.strip().split(' ')
            length=len(each_list)


            if length<2:#说明在空行中
                # print('each_list',each_list)
                sentence_text = ' '.join(each_point_text)
                sentence_label = ' '.join(each_point_label)

                if len(each_sentence_entitys)>1:
                        if each_sentence_entitys[0] not in all_ids_dict:
                            all_ids_dict[each_sentence_entitys[0]]=all_ids[counts_entity]
                            counts_entity = counts_entity + 1
                        if each_sentence_entitys[1] not in all_ids_dict:
                            all_ids_dict[each_sentence_entitys[1]]= all_ids[counts_entity]
                            counts_entity = counts_entity + 1

                        # print('all_ids_dict',all_ids_dict)



                        #随机取的id会导致id重复
                        each_sentence_rel_data['head']={'word':each_sentence_entitys[0],'label':each_sentence_entitys_label[0],'id':all_ids_dict[each_sentence_entitys[0]]}
                        each_sentence_rel_data['tail'] = {'word': each_sentence_entitys[1],'label':each_sentence_entitys_label[1],'id':all_ids_dict[each_sentence_entitys[1]]}




                        each_sentence_rel_data['sentence'] = sentence_text
                        # each_sentence_rel_data['relation'] = relations[int(random.random()*rel_count)]
                        each_sentence_rel_data['relation'] =''

                        all_rel_data.append(each_sentence_rel_data)

                        # print('each_sentence_rel_data:',each_sentence_rel_data)
                        # print('all_rel_data:',all_rel_data)

                        #用完一次要清空，否则会保留上一次信息
                        each_sentence_rel_data = {}

                        # print('each_sentence_entitys0',each_sentence_entitys)
                        # #
                        # print('sentence_text0:',sentence_text)
                        # print('sentence_label0:',sentence_label)

                        #此时只有两个实体一个是head另一个是tail,单纯实体识别时会出现多个实体的情况
                        #此时取前两个一个head另一个为tail
                        if len(each_sentence_entitys)>2:
                            print('each_sentence_entitys:',each_sentence_entitys)
                            print('each_sentence_entitys_label',each_sentence_entitys_label)
                            '''
                            sentence_text0: The Little Comedy , '' a mannered operetta based on a short story by Arthur Schnitzler set in fin-de-si ècle Vienna , opens the evening .
                            sentence_label0: O B-PER E-PER O O O O O O O O O O O B-PER E-PER O O O O S-LOC O O O O O
                            each_sentence_entitys: ['Little Comedy', 'Arthur Schnitzler', 'Vienna']
                            '''
                            print('\n*********************\n')
                else:
                        ##只含有一个实体是因为以"."分隔行，这样可能只有一个实体，可能两个实体名称相同造成
                        pass
                        # print('sentence_text1:', sentence_text)
                        # print('sentence_label1:', sentence_label)
                        # print('each_sentence_entitys1', each_sentence_entitys)
                        #
                        # # print('sentence_text1:', sentence_text)
                        # # print('sentence_label1:', sentence_label)
                        # print('\n*********************\n')

                ###添加一个个字组成一句话
                each_point_text=[]
                each_point_label=[]
                each_sentence_entitys = []
                each_sentence_entitys_label=[]
                # print("right_amounts",right_amounts)

            else:
                # print('each_list', each_list)
                text = each_list[0]
                true_label = each_list[1]
                predicted_label=each_list[2]

                each_point_text.append(text)
                each_point_label.append(true_label)

                # if true_label==predicted_label and true_label!='O':
                #     right_amounts=right_amounts+1
                #     print("right_amounts",right_amounts)
                #     print('each_list', each_list)


                ll=true_label.split('-')
                # print('ll',ll)
                if len(ll)<2:
                    continue
                else:
                    if ll[0]=='S':
                        if text not in each_sentence_entitys:
                            each_sentence_entitys.append(text)
                            each_sentence_entitys_label.append(ll[1])
                    elif ll[0]=='B':
                        eachs_entity=eachs_entity +text
                        pass
                    elif ll[0]=='I':
                        eachs_entity = eachs_entity+' ' + text
                        pass
                    elif ll[0]=='E':
                        eachs_entity = eachs_entity+' '  + text
                        if eachs_entity not in each_sentence_entitys:
                            each_sentence_entitys.append(eachs_entity)
                            each_sentence_entitys_label.append(ll[1])
                        # print('each_sentence_entitys',each_sentence_entitys)
                        ####适用于包含E结尾的实体，如果都是s那么就不适合
                        eachs_entity=''
                        pass
                    else:
                        continue

print('all_rel_data',all_rel_data)
print('len(all_ids_dict)',len(all_ids_dict))

with open(path_relation,'w') as f:
    #两种效果一样
    ## f.write(json.dumps(all_rel_data,indent=4))
    json.dump(all_rel_data,f,indent=4)

# for each in all_rel_data:
#     print('each',each)

# print('all_rel_data',all_rel_data)


