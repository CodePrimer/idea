import os


if __name__ == '__main__':
    rootDir = r'C:\Users\Administrator\Desktop\归一参数'
    paramList = os.listdir(rootDir)
    maxTotalList = []
    minTotalList = []
    for param in paramList:
        maxList = []
        minList = []
        paramDir = os.path.join(rootDir, param)
        maxTxt = os.path.join(paramDir, param + '_max.txt')
        minTxt = os.path.join(paramDir, param + '_min.txt')
        with open(maxTxt, 'r') as f:
            data = f.readlines()
            for each in data:
                maxList.append(each.strip() + 'f')
        with open(minTxt, 'r') as f:
            data = f.readlines()
            for each in data:
                minList.append(each.strip() + 'f')
        maxStr = '{' + ','.join(maxList) + '}'
        minStr = '{' + ','.join(minList) + '}'
        maxTotalList.append(maxStr)
        minTotalList.append(minStr)
    a = '{' + ','.join(maxTotalList) + '}'
    b = '{' + ','.join(minTotalList) + '}'
    print('F')