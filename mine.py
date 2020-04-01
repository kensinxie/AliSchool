# 加上大层日期循环
import pandas as pd
from datetime import datetime
import datetime as DateTime

vmCpu = {"ecs.c1.large": 2, "ecs.c1.xlarge": 4, "ecs.c1.2xlarge": 8, "ecs.g1.large": 2, "ecs.g1.xlarge": 4,
         "ecs.g1.2xlarge": 8, "ecs.r1.large": 2, "ecs.r1.xlarge": 4, "ecs.r1.2xlarge": 8}
vmMemory = {"ecs.c1.large": 4, "ecs.c1.xlarge": 8, "ecs.c1.2xlarge": 16, "ecs.g1.large": 8, "ecs.g1.xlarge": 16,
            "ecs.g1.2xlarge": 32, "ecs.r1.large": 16, "ecs.r1.xlarge": 32, "ecs.r1.2xlarge": 64}
incomePerHour = {"ecs.c1.large": 0.39, "ecs.c1.xlarge": 0.78, "ecs.c1.2xlarge": 1.56, "ecs.g1.large": 0.5,
                 "ecs.g1.xlarge": 1, "ecs.g1.2xlarge": 2, "ecs.r1.large": 0.66, "ecs.r1.xlarge": 1.33,
                 "ecs.r1.2xlarge": 2.65}


class NC(object):
    def __init__(self, ncID, machineType, state, maxCpu, maxMemory, price, supportProductType, freeCpu, freeMemory,
                 inVm, createTime):
        self.ncId = ncID
        self.machineType = machineType
        self.state, self.maxCpu, self.maxMemory, self.price, self.supportProductType, self.freeCpu, self.freeMemory, self.inVm = state, maxCpu, maxMemory, price, supportProductType, freeCpu, freeMemory, inVm
        self.createTime = createTime


def getVmCpu_Mem_Income(vmType):
    return vmCpu[vmType], vmMemory[vmType], incomePerHour[vmType]


class Vm(object):
    def __init__(self, vmId, vmType, createTime, releaseTime):
        self.vmId, self.vmType, self.createTime, self.releaseTime = vmId, vmType, createTime, releaseTime
        self.vmCpu, self.vmMemory, self.incomePerHour = getVmCpu_Mem_Income(vmType)


ncIndex = 0

# 服务器集群
c1_NC = []
r1_NC = []
g1_NC = []


# 申请NC，freeday为可投入使用时间
def applyNc(ncType, n, freeDay):
    global ncIndex
    if ncType == 'NT-1-2':
        for i in range(n):
            ncId = 'nc_' + str(ncIndex)
            ncIndex = ncIndex + 1
            Nt12 = NC(ncId, 'NT-1-2', 'free', 64, 128, 20000, ['c1'], 64, 128, [], freeDay)
            c1_NC.append(Nt12)
    if ncType == 'NT-1-4':
        for i in range(n):
            ncId = 'nc_' + str(ncIndex)
            ncIndex = ncIndex + 1
            Nt14 = NC(ncId, 'NT-1-4', 'free', 96, 256, 23500, ['c1', 'g1', 'r1'], 96, 256, [], freeDay)
            g1_NC.append(Nt14)
    if ncType == 'NT-1-8':
        for i in range(n):
            ncId = 'nc_' + str(ncIndex)
            ncIndex = ncIndex + 1
            Nt18 = NC(ncId, 'NT-1-8', 'free', 104, 516, 30000, ['r1'], 104, 516, [], freeDay)
            r1_NC.append(Nt18)


def ifEnoughSourece(vmtype, today):
    s = vmtype.split('.')
    jiqun = s[1] + '_NC'
    jiqun = eval(jiqun)
    cpu, memo = vmCpu[vmtype], vmMemory[vmtype]
    for i in range(len(jiqun)):
        createTime = jiqun[i].createTime
        createTime = datetime.date(datetime.strptime(createTime, '%Y-%m-%d'))
        if createTime <= today:  # 保证createtime小于today才能使用这个nc，即定createtime为可正式使用的那天，其报备时间为createTime-10
            if jiqun[i].freeCpu >= cpu and jiqun[i].freeMemory >= memo:
                return jiqun, i
    for i in range(len(g1_NC)):
        createTime = g1_NC[i].createTime
        createTime = datetime.date(datetime.strptime(createTime, '%Y-%m-%d'))
        if createTime <= today:
            if g1_NC[i].freeCpu >= cpu and g1_NC[i].freeMemory >= memo:
                return g1_NC, i
    return None


def getStatus(outputDate, vm):
    if vm.releaseTime == '\\N':
        return "running"
    releasetime = datetime.strptime(vm.releaseTime, '%Y-%m-%d')
    outputDate = datetime.strptime(outputDate, '%Y-%m-%d')
    if releasetime > outputDate:
        return "running"
    else:
        return "release"


if __name__ == '__main__':
    path = 'data/'
    allData = pd.read_csv(path + 'input_vm_1.csv')
    for i in range(2, 21, 1):
        data = pd.read_csv(path + 'input_vm_' + str(i) + '.csv')
        allData = allData.append(data)
    allData = allData.reset_index(drop=True)
    fristday=allData.loc[0, "createtime"]
    lastday = allData.loc[allData.shape[0] - 1, "createtime"]
    begin=datetime.date(datetime.strptime(fristday, '%Y-%m-%d'))
    end = datetime.date(datetime.strptime(lastday, '%Y-%m-%d'))

    zongshouyi = 0

    # 初始化NC
    applyNc('NT-1-2', 30, "2019-01-01")
    applyNc('NT-1-4', 30, "2019-01-01")
    applyNc('NT-1-8', 5, "2019-01-01")
    zongshouyi = zongshouyi - 30 * 20000 - 30 * 23500 - 5 * 30000

    vmId = 0  # vmid序号

    #begin = DateTime.date(2019, 4, 1)
    # end = DateTime.date(2019, 6, 30)
    duringDays = (end - begin).days

    shouyidata = pd.DataFrame(
        columns=["Date", "income", "duangongsunshi", "weihufei", "baobeiNC"])

    # 日期的大遍历
    for i in range((end - begin).days + 1):
        baobeiNc = 0  # 记录当日报备开销
        day = begin + DateTime.timedelta(days=i)
        data1 = allData.loc[allData['createtime'] == str(day)]
        data1 = data1.reset_index(drop=True)
        # 遍历订单
        duangong = 0
        for i in range(data1.shape[0]):
            vmtype = data1.loc[i, "vmtype"]
            createtime = data1.loc[i, "createtime"]
            releasetime = data1.loc[i, "releasetime"]
            # 检查是否有足够资源：
            if ifEnoughSourece(vmtype, day) != None:
                jiqun, ii = ifEnoughSourece(vmtype, day)
                vm = Vm(vmId, vmtype, createtime, releasetime)
                vmId = vmId + 1
                nc = jiqun[ii]
                nc.inVm.append(vm)
                nc.freeCpu = nc.freeCpu - vm.vmCpu
                nc.freeMemory = nc.freeMemory - vm.vmMemory
            else:  # 资源不足时
                duangong = duangong + vmCpu[vmtype] * 24

        # 当日订单全部处理结束后，进行成本、收益、断供损失的核算
        outputDate = str(day)
        # 遍历三个集群中所有NC，形成当日的nc.csv
        # 顺便累加nc的cpu数目，以计算维护成本
        ncdata = pd.DataFrame(
            columns=["outputDate", "ncId", "status", "totalCpu", "totalMemory", "machineType", "usedCpu", "usedMemory",
                     "createTime"])
        for i in range(len(c1_NC)):
            nc = c1_NC[i]
            # 排除掉createTime>today的服务器（即已申报但还未到位的服务器
            createTime = nc.createTime
            createTime = datetime.date(datetime.strptime(createTime, '%Y-%m-%d'))
            if createTime <= day:
                ncdata = ncdata.append([{'outputDate': outputDate, 'ncId': nc.ncId, 'status': nc.state,
                                         'totalCpu': nc.maxCpu, 'totalMemory': nc.maxMemory,
                                         'machineType': nc.machineType, 'usedCpu': nc.maxCpu - nc.freeCpu,
                                         'usedMemory': nc.maxMemory - nc.freeMemory,
                                         'createTime': nc.createTime}], ignore_index=True, sort=False)
        for i in range(len(g1_NC)):
            nc = g1_NC[i]
            createTime = nc.createTime
            createTime = datetime.date(datetime.strptime(createTime, '%Y-%m-%d'))
            if createTime <= day:
                ncdata = ncdata.append([{'outputDate': outputDate, 'ncId': nc.ncId, 'status': nc.state,
                                         'totalCpu': nc.maxCpu, 'totalMemory': nc.maxMemory,
                                         'machineType': nc.machineType, 'usedCpu': nc.maxCpu - nc.freeCpu,
                                         'usedMemory': nc.maxMemory - nc.freeMemory,
                                         'createTime': nc.createTime}], ignore_index=True, sort=False)
        for i in range(len(r1_NC)):
            nc = r1_NC[i]
            createTime = nc.createTime
            createTime = datetime.date(datetime.strptime(createTime, '%Y-%m-%d'))
            if createTime <= day:
                ncdata = ncdata.append([{'outputDate': outputDate, 'ncId': nc.ncId, 'status': nc.state,
                                         'totalCpu': nc.maxCpu, 'totalMemory': nc.maxMemory,
                                         'machineType': nc.machineType, 'usedCpu': nc.maxCpu - nc.freeCpu,
                                         'usedMemory': nc.maxMemory - nc.freeMemory,
                                         'createTime': nc.createTime}], ignore_index=True, sort=False)
        # 计算处于free状态的NC的总cpu数目
        freeNc = ncdata.loc[ncdata['status'] == 'free']
        freeNc = freeNc.reset_index(drop=True)
        totalCpu = freeNc['totalCpu'].sum()
        ncdata.to_csv("nc" + outputDate + ".csv", index=False)

        newncdata = pd.DataFrame(
            columns=["outputDate", "ncId", "status", "totalCpu", "totalMemory", "machineType", "usedCpu", "usedMemory",
                     "createTime"])
        # 检查每类NC的剩余memory，以决定是否报备,以5台富裕为标准
        Nc_12 = freeNc.loc[freeNc['machineType'] == 'NT-1-2']
        Nc_12_freeMemo = Nc_12['totalMemory'].sum() - Nc_12['usedMemory'].sum()
        nc12 = 0
        if Nc_12_freeMemo < 640:
            nc12 = 10
            if Nc_12_freeMemo < 320:
                nc12 = 15
                if Nc_12_freeMemo < 160:
                    nc12 = 20
        applyNc('NT-1-2', nc12, str(day + DateTime.timedelta(days=10)))
        baobeiNc = baobeiNc - (20000 + 16) * nc12
        for j in range(ncIndex - 1, ncIndex - 1 - nc12, -1):  # 为了处理报备机器的ID号
            newncdata = newncdata.append([{'outputDate': outputDate, 'ncId': j, 'status': 'init',
                                           'totalCpu': 64, 'totalMemory': 128,
                                           'machineType': 'NT-1-2', 'usedCpu': 0,
                                           'usedMemory': 0,
                                           'createTime': outputDate}], ignore_index=True, sort=False)

        Nc_14 = freeNc.loc[freeNc['machineType'] == 'NT-1-4']
        Nc_14_freeMemo = Nc_14['totalMemory'].sum() - Nc_14['usedMemory'].sum()
        nc14 = 0
        if Nc_14_freeMemo < 1280:
            nc14 = 30
            if Nc_14_freeMemo < 640:
                nc14 = 40
                if Nc_14_freeMemo < 320:
                    nc14 = 50
        applyNc('NT-1-4', nc14, str(day + DateTime.timedelta(days=10)))
        baobeiNc = baobeiNc - (23500 + 16) * nc14
        for j in range(ncIndex - 1, ncIndex - 1 - nc14, -1):
            newncdata = newncdata.append([{'outputDate': outputDate, 'ncId': j, 'status': 'init',
                                           'totalCpu': 96, 'totalMemory': 256,
                                           'machineType': 'NT-1-4', 'usedCpu': 0,
                                           'usedMemory': 0,
                                           'createTime': outputDate}], ignore_index=True, sort=False)

        Nc_18 = freeNc.loc[freeNc['machineType'] == 'NT-1-8']
        Nc_18_freeMemo = Nc_18['totalMemory'].sum() - Nc_18['usedMemory'].sum()
        nc18 = 0
        if Nc_18_freeMemo < 1548:
            nc18 = 2
            if Nc_18_freeMemo < 774:
                nc18 = 4
                if Nc_18_freeMemo < 387:
                    nc14 = 8
        applyNc('NT-1-8', nc18, str(day + DateTime.timedelta(days=10)))
        baobeiNc = baobeiNc - (30000 + 16) * nc18
        for j in range(ncIndex - 1, ncIndex - 1 - nc18, -1):
            newncdata = newncdata.append([{'outputDate': outputDate, 'ncId': j, 'status': 'init',
                                           'totalCpu': 104, 'totalMemory': 516,
                                           'machineType': 'NT-1-8', 'usedCpu': 0,
                                           'usedMemory': 0,
                                           'createTime': outputDate}], ignore_index=True, sort=False)
        newncdata.to_csv("new_nc" + outputDate + ".csv", index=False)

        # 遍历三个集群中所有NC，形成当日的vm.csv
        # 顺便计算今日虚拟机收益
        income = 0
        vmdata = pd.DataFrame(
            columns=["outputDate", "vmId", "status", "ncId", "vmType", "cpu", "memory", "createTime", "releaseTime"])
        for i in range(len(c1_NC)):
            vmList = c1_NC[i].inVm
            delIndex = []
            for ii in range(len(vmList)):
                vm = vmList[ii]
                status = getStatus(outputDate, vm)
                income = income + incomePerHour[vm.vmType] * 24
                # 如果status==release，则将该对象移出nc。
                if status == "release":
                    delIndex.append(ii)
                vmdata = vmdata.append([{'outputDate': outputDate, 'vmId': vm.vmId, 'status': status,
                                         'ncId': c1_NC[i].ncId, 'vmType': vm.vmType, 'cpu': vm.vmCpu,
                                         'memory': vm.vmMemory, 'createTime': vm.createTime,
                                         'releaseTime': vm.releaseTime}], ignore_index=True)
            # 按照待删除索引，释放掉vm资源
            for j in range(len(delIndex) - 1, -1, -1):
                k = delIndex[j]
                del vmList[k]

        for i in range(len(g1_NC)):
            vmList = g1_NC[i].inVm
            delIndex = []
            for ii in range(len(vmList)):
                vm = vmList[ii]
                status = getStatus(outputDate, vm)
                income = income + incomePerHour[vm.vmType] * 24
                # 如果status==release，则将该对象移出nc。
                if status == "release":
                    delIndex.append(ii)
                vmdata = vmdata.append([{'outputDate': outputDate, 'vmId': vm.vmId, 'status': status,
                                         'ncId': g1_NC[i].ncId, 'vmType': vm.vmType, 'cpu': vm.vmCpu,
                                         'memory': vm.vmMemory, 'createTime': vm.createTime,
                                         'releaseTime': vm.releaseTime}], ignore_index=True)
            # 按照待删除索引，释放掉vm资源
            for j in range(len(delIndex) - 1, -1, -1):
                k = delIndex[j]
                del vmList[k]

        for i in range(len(r1_NC)):
            vmList = r1_NC[i].inVm
            delIndex = []
            for ii in range(len(vmList)):
                vm = vmList[ii]
                status = getStatus(outputDate, vm)
                income = income + incomePerHour[vm.vmType] * 24
                # 如果status==release，则将该对象移出nc。
                if status == "release":
                    delIndex.append(ii)
                vmdata = vmdata.append([{'outputDate': outputDate, 'vmId': vm.vmId, 'status': status,
                                         'ncId': r1_NC[i].ncId, 'vmType': vm.vmType, 'cpu': vm.vmCpu,
                                         'memory': vm.vmMemory, 'createTime': vm.createTime,
                                         'releaseTime': vm.releaseTime}], ignore_index=True)
            # 按照待删除索引，释放掉vm资源
            for j in range(len(delIndex) - 1, -1, -1):
                k = delIndex[j]
                del vmList[k]

        vmdata.to_csv("vm" + outputDate + ".csv", index=False)
        # baobeiNc=income-duangong-totalCpu*3.6
        print(str(day) + "\t断供损失:" + str(duangong) + "\t今日收入:" + str(income) + "\t维护费用:" + str(
            totalCpu * 3.6) + "\t合计:" + str(income - duangong - totalCpu * 3.6 + baobeiNc))
        zongshouyi = zongshouyi + baobeiNc
        shouyidata = shouyidata.append([{'Date': outputDate, 'income': income, 'duangongsunshi': duangong,
                                         'weihufei': totalCpu * 3.6, 'baobeiNC': baobeiNc,
                                         'heji': income - duangong - totalCpu * 3.6 + baobeiNc}], ignore_index=True,
                                       sort=False)
    shouyidata.to_csv("每日明细.csv", index=False)

    print()
    print("总收益：" + zongshouyi + "\t平均收益率：" + zongshouyi / duringDays)
