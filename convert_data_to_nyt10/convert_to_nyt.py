import json
path='../output/label_test.txt'
path_relation='../output/label_test_relation.json'
all_rel_data=[]
each_sentence_rel_data={}
with open(path,encoding='utf8') as f:
    each_point_text=[]
    each_point_label=[]
    right_amounts=0


    each_sentence_entitys = []
    eachs_entity = ''

    for each in f:
        each_list=each.strip().split(' ')
        length=len(each_list)
        if length<2:#说明在空行中
            if len(each_sentence_entitys)>1:

                    each_sentence_rel_data['head']={'word':each_sentence_entitys[0]}
                    each_sentence_rel_data['tail'] = {'word': each_sentence_entitys[1]}

                    sentence_text = ' '.join(each_point_text)
                    sentence_label = ' '.join(each_point_label)

                    each_sentence_rel_data['sentence'] = sentence_text

                    all_rel_data.append(each_sentence_rel_data)

                    # print('each_sentence_rel_data:',each_sentence_rel_data)
                    # print('all_rel_data:',all_rel_data)

                    #用完一次要清空，否则会保留上一次信息
                    each_sentence_rel_data = {}

                    print('each_sentence_entitys0',each_sentence_entitys)
                    #
                    print('sentence_text0:',sentence_text)
                    print('sentence_label0:',sentence_label)
                    print('\n*********************\n')
            else:
                    pass
                    print('each_sentence_entitys1', each_sentence_entitys)

                    print('sentence_text1:', sentence_text)
                    print('sentence_label1:', sentence_label)
                    print('\n*********************\n')

            ###添加一个个字组成一句话
            each_point_text=[]
            each_point_label=[]
            each_sentence_entitys = []
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
                    # print('each_sentence_entitys',each_sentence_entitys)
                    ####适用于包含E结尾的实体，如果都是s那么就不适合
                    eachs_entity=''
                    pass
                else:
                    continue

with open(path_relation,'w') as f:
    #两种效果一样
    # f.write(json.dumps(all_rel_data),indent=4)
    json.dump(all_rel_data,f,indent=4)

# for each in all_rel_data:
#     print('each',each)

# print('all_rel_data',all_rel_data)


