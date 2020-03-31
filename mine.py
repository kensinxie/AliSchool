

vmCpu={"ecs.c1.large":2,"ecs.c1.xlarge":4,"ecs.c1.2xlarge":8,"ecs.g1.large":2,"ecs.g1.xlarge":4,"ecs.g1.2xlarge":8,"ecs.r1.large":2,"ecs.r1.xlarge":4,"ecs.r1.2xlarge":8}
vmMemory={"ecs.c1.large":4,"ecs.c1.xlarge":8,"ecs.c1.2xlarge":16,"ecs.g1.large":8,"ecs.g1.xlarge":16,"ecs.g1.2xlarge":32,"ecs.r1.large":16,"ecs.r1.xlarge":32,"ecs.r1.2xlarge":64}
incomePerHour={"ecs.c1.large":0.39,"ecs.c1.xlarge":0.78,"ecs.c1.2xlarge":1.56,"ecs.g1.large":0.5,"ecs.g1.xlarge":1,"ecs.g1.2xlarge":2,"ecs.r1.large":0.66,"ecs.r1.xlarge":1.33,"ecs.r1.2xlarge":2.65}


class NC(object):
    def __init__(self,ncID,machineType,state,maxCpu,maxMemory,price,supportProductType,freeCpu,freeMemory,inVm):
        self.ncId=ncID
        self.machineType=machineType
        self.state,self.maxCpu,self.maxMemory,self.price,self.supportProductType,self.freeCpu,self.freeMemory,self.inVm=state,maxCpu,maxMemory,price,supportProductType,freeCpu,freeMemory,inVm


def getVmCpu_Mem_Income(vmType):
    return vmCpu[vmType],vmMemory[vmType],incomePerHour[vmType]


class Vm(object):
    def __init__(self,vmType,vmCpu,vmMemory,incomePerHour,createTime,releaseTime):
        self.vmType,self.createTime,self.releaseTime=vmType,createTime,releaseTime
        self.vmCpu, self.vmMemory, self.incomePerHour=getVmCpu_Mem_Income(vmType)
