import string
import hashlib
import random

def generateid_list(counts=1000):
    id_set=set()
    for each in range(counts):

        n = ''.join(random.sample(string.ascii_letters+string.digits,32))

        # print(n)  #结果是：WIxj4L605dowP9t3g7fbSircqpTOZ2VK


        m = hashlib.md5() #创建Md5对象
        m.update(n.encode('utf-8')) #生成加密串，其中n是要加密的字符串

        result = m.hexdigest() #经过md5加密的字符串赋值

        # print('结果是：',result,len(result)) #输出：47cb31ad09b0fe5d75688e26ad7fd000

        a=result[0:8]
        b=result[8:12]
        c=result[12:16]
        d=result[16:20]
        e=result[20:32]
        id='{}-{}-{}-{}-{}'.format(a,b,c,d,e)
        # print('id',id)
        id_set.add(id)
    print('len(id_set)',len(id_set))
    return list(id_set)


if __name__=='__main__':
    counts=1000
    all_ids=generateid_list(counts)

    print(all_ids[int(random.random()*counts)])
    print(all_ids[int(random.random() * counts)])
    print(all_ids[int(random.random() * counts)])
    print(all_ids[int(random.random() * counts)])

    # print(all_ids)
    # it = iter(all_ids)
    # print(next(it))


    # # 循环:
    # while True:
    #     try:
    #         # 获得下一个值:
    #         x = next(it)
    #         print(x)
    #     except StopIteration:
    #         # 遇到StopIteration就退出循环
    #         break