path='../output/label_test.txt'
with open(path,encoding='utf8') as f:
    each_point_text=[]
    each_point_label=[]
    right_amounts=0


    each_sentence_entitys = []
    eachs_entity = ''

    for each in f:


        each_list=each.strip().split(' ')

        length=len(each_list)
        if length<2:
            if len(each_sentence_entitys)>0:
                 print('each_sentence_entitys',each_sentence_entitys)
                 print('\n*********************\n')
            print(' '.join(each_point_text))
            print(' '.join(each_point_label))
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
                    each_sentence_entitys.append(text)
                elif ll[0]=='B':
                    eachs_entity=eachs_entity+' ' +text
                    pass
                elif ll[0]=='I':
                    eachs_entity = eachs_entity+' ' + text
                    pass
                elif ll[0]=='E':
                    eachs_entity = eachs_entity+' '  + text
                    each_sentence_entitys.append(eachs_entity)
                    # print('each_sentence_entitys',each_sentence_entitys)
                    eachs_entity=''
                    pass
                else:
                    continue

