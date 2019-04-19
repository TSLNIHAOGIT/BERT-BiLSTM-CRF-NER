path='../NERdata/dev.txt'
with open(path,encoding='utf8') as f:
    each_point_text=[]
    each_point_label=[]

    for each in f:
        each_entity=[]
        each_list=each.strip().split(' ')

        length=len(each_list)
        if length<2:
            print(' '.join(each_point_text))
            print(' '.join(each_point_label))
            each_point_text=[]
            each_point_label=[]
            print('\n*********************\n')
        else:
            # print('each_list', each_list)
            text = each_list[0]
            true_label = each_list[1]
            each_point_text.append(text)
            each_point_label.append(true_label)
            ll=each_point_label.split('-')
            if len(ll)<2:
                continue
            else:
                
                if ll[0]=='B':
                    each_entity.append(each_point_text)
            # if each_point_label in ['B-PER','I-PER','B-LOC','I-LOC','B-ORG','I-ORG']:


            # print('each list',each_list)